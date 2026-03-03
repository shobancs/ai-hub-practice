"""
Background Scheduler
Continuously polls weather.gov on configurable intervals and keeps
the shared AgentState up to date.

Uses Python's threading module to run collection loops in the background
without blocking the main application thread.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Callable, Optional

from .config import WeatherAgentConfig, config as default_config
from .models import AgentState, GeoPoint, WeatherAlert
from .safety_advisor import SafetyAdvisor
from .weather_client import WeatherGovClient

logger = logging.getLogger(__name__)


class WeatherScheduler:
    """
    Background data-collection scheduler.

    Runs three periodic loops:
    ┌────────────────────────────┬──────────────────────────────┐
    │ Loop                       │ Default interval             │
    ├────────────────────────────┼──────────────────────────────┤
    │ Alert check                │ every  5 minutes (300s)      │
    │ 7-day forecast refresh     │ every 30 minutes (1800s)     │
    │ Hourly forecast refresh    │ every  1 hour   (3600s)      │
    └────────────────────────────┴──────────────────────────────┘

    Usage:
        scheduler = WeatherScheduler(state, locations)
        scheduler.start()
        # ... main program runs ...
        scheduler.stop()
    """

    def __init__(
        self,
        state: AgentState,
        locations: list[GeoPoint],
        cfg: WeatherAgentConfig = default_config,
        on_new_alert: Optional[Callable[[WeatherAlert], None]] = None,
    ):
        """
        Args:
            state:        Shared AgentState updated by the scheduler.
            locations:    List of GeoPoints to monitor.
            cfg:          WeatherAgentConfig controlling intervals.
            on_new_alert: Optional callback invoked when a new alert appears.
                          Receives the WeatherAlert object.
        """
        self.state = state
        self.locations = locations
        self.cfg = cfg
        self.on_new_alert = on_new_alert

        self._client  = WeatherGovClient(cfg)
        self._advisor = SafetyAdvisor(cfg)
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

        # Track known alert IDs to detect new arrivals
        self._known_alert_ids: set[str] = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start all background collection threads (non-blocking)."""
        if self._threads:
            logger.warning("Scheduler is already running.")
            return

        self._stop_event.clear()

        loops = [
            ("alert-check",    self._alert_loop,    self.cfg.alert_poll_interval),
            ("forecast-check", self._forecast_loop, self.cfg.forecast_poll_interval),
            ("hourly-check",   self._hourly_loop,   self.cfg.hourly_poll_interval),
        ]

        for name, target, interval in loops:
            t = threading.Thread(
                target=target,
                args=(interval,),
                name=name,
                daemon=True,   # Threads die when the main program exits
            )
            t.start()
            self._threads.append(t)
            logger.info("Started %s thread (interval=%ds)", name, interval)

    def stop(self, timeout: float = 5.0) -> None:
        """Signal all threads to stop and wait for them to finish."""
        logger.info("Stopping scheduler...")
        self._stop_event.set()
        for t in self._threads:
            t.join(timeout=timeout)
        self._threads.clear()
        logger.info("Scheduler stopped.")

    @property
    def is_running(self) -> bool:
        return bool(self._threads) and not self._stop_event.is_set()

    def run_once(self) -> dict:
        """
        Run a single immediate fetch cycle (alerts + forecasts).
        Useful for initial data load or testing.

        Returns:
            Summary dict with counts of fetched items.
        """
        logger.info("Running immediate data fetch for %d location(s)...", len(self.locations))
        alert_count    = self._fetch_alerts()
        forecast_count = self._fetch_forecasts(hourly=False)
        return {
            "alerts_fetched": alert_count,
            "forecasts_fetched": forecast_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------------
    # Background loops
    # ------------------------------------------------------------------

    def _alert_loop(self, interval: int) -> None:
        """Continuously check for new/updated alerts."""
        while not self._stop_event.is_set():
            try:
                count = self._fetch_alerts()
                removed = self.state.clear_expired_alerts()
                if count or removed:
                    logger.info(
                        "Alert cycle: %d active, %d expired removed", count, removed
                    )
            except Exception as exc:
                logger.error("Alert loop error: %s", exc)
                self.state.errors.append(f"alert_loop: {exc}")

            self._stop_event.wait(interval)

    def _forecast_loop(self, interval: int) -> None:
        """Continuously refresh 7-day forecasts."""
        while not self._stop_event.is_set():
            try:
                count = self._fetch_forecasts(hourly=False)
                logger.info("Forecast cycle: %d location(s) refreshed", count)
            except Exception as exc:
                logger.error("Forecast loop error: %s", exc)
                self.state.errors.append(f"forecast_loop: {exc}")

            self._stop_event.wait(interval)

    def _hourly_loop(self, interval: int) -> None:
        """Continuously refresh hourly forecasts."""
        while not self._stop_event.is_set():
            try:
                count = self._fetch_forecasts(hourly=True)
                logger.info("Hourly forecast cycle: %d location(s) refreshed", count)
            except Exception as exc:
                logger.error("Hourly loop error: %s", exc)
                self.state.errors.append(f"hourly_loop: {exc}")

            self._stop_event.wait(interval)

    # ------------------------------------------------------------------
    # Fetch helpers
    # ------------------------------------------------------------------

    def _fetch_alerts(self) -> int:
        """
        Fetch active alerts for all monitored locations.

        Deduplicates alerts across locations so the same national alert
        isn't listed multiple times.  Returns the total unique alert count.
        """
        seen_ids:   set[str]          = set()
        all_alerts: list[WeatherAlert] = []

        for location in self.locations:
            try:
                alerts = self._client.get_active_alerts_for_point(
                    location.latitude, location.longitude
                )
                for alert in alerts:
                    if alert.alert_id not in seen_ids:
                        seen_ids.add(alert.alert_id)
                        all_alerts.append(alert)

                        # Detect new alerts and fire callback
                        if alert.alert_id not in self._known_alert_ids:
                            self._known_alert_ids.add(alert.alert_id)
                            self._handle_new_alert(alert)

            except Exception as exc:
                logger.warning(
                    "Could not fetch alerts for %s: %s", location.location_name, exc
                )

        self.state.active_alerts = all_alerts
        self.state.last_alert_check = datetime.utcnow()
        return len(all_alerts)

    def _fetch_forecasts(self, hourly: bool = False) -> int:
        """
        Fetch 7-day (or hourly) forecasts for all monitored locations.
        Returns the number of successfully fetched forecasts.
        """
        fetched = 0
        label   = "hourly" if hourly else "7-day"

        for location in self.locations:
            try:
                grid     = self._client.get_grid_point(location.latitude, location.longitude)
                forecast = self._client.get_forecast(grid, location, hourly=hourly)

                key = f"{location.location_name}_{label}"
                self.state.latest_forecasts[key] = forecast
                self.state.last_data_fetch = datetime.utcnow()
                self.state.total_fetches  += 1
                fetched += 1

            except Exception as exc:
                logger.warning(
                    "Could not fetch %s forecast for %s: %s",
                    label, location.location_name, exc
                )

        return fetched

    def _handle_new_alert(self, alert: WeatherAlert) -> None:
        """
        Process a newly detected alert.

        1. Auto-generate safety guidelines for qualifying alerts.
        2. Fire the optional on_new_alert callback.
        """
        logger.warning(
            "🚨 NEW ALERT [%s] %s — %s",
            alert.severity.value, alert.event, alert.area_description
        )

        # Auto-generate safety guidelines for significant alerts
        if self._advisor.should_generate_guideline(alert):
            try:
                guideline = self._advisor.generate_guideline(alert)
                self.state.safety_guidelines.append(guideline)

                # Trim cache if too large
                if len(self.state.safety_guidelines) > self.cfg.max_cached_guidelines:
                    self.state.safety_guidelines = self.state.safety_guidelines[-self.cfg.max_cached_guidelines:]

                logger.info(
                    "Safety guideline generated for alert: %s", alert.event
                )
            except Exception as exc:
                logger.error("Failed to generate safety guideline: %s", exc)

        # Fire external callback (e.g. push notification, webhook)
        if self.on_new_alert:
            try:
                self.on_new_alert(alert)
            except Exception as exc:
                logger.error("on_new_alert callback failed: %s", exc)
