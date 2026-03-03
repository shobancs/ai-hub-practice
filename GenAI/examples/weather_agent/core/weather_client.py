"""
Weather.gov API Client
Wraps the National Weather Service (NWS) public REST API.

No API key required — NWS is completely free.
API docs: https://www.weather.gov/documentation/services-web-api

Key endpoints used:
  GET /points/{lat},{lon}                              → grid metadata
  GET /gridpoints/{office}/{x},{y}/forecast           → 7-day forecast
  GET /gridpoints/{office}/{x},{y}/forecast/hourly    → hourly forecast
  GET /alerts/active                                  → all active alerts
  GET /alerts/active?point={lat},{lon}                → point alerts
  GET /alerts/active?area={state}                     → state alerts
"""

import logging
import time
from datetime import datetime
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import WeatherAgentConfig, config as default_config
from .models import (
    AlertCertainty,
    AlertSeverity,
    AlertUrgency,
    ForecastPeriod,
    GeoPoint,
    GridPoint,
    WeatherAlert,
    WeatherForecast,
)

logger = logging.getLogger(__name__)


def _build_session(cfg: WeatherAgentConfig) -> requests.Session:
    """Create a requests Session with retry logic and NWS headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": cfg.nws_user_agent,
        "Accept": "application/geo+json",
    })
    retry = Retry(
        total=cfg.nws_max_retries,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


class WeatherGovClient:
    """
    Client for the National Weather Service API (api.weather.gov).

    Usage:
        client = WeatherGovClient()
        grid   = client.get_grid_point(40.71, -74.00)
        fcst   = client.get_forecast(grid, GeoPoint(latitude=40.71, longitude=-74.00))
        alerts = client.get_active_alerts_for_point(40.71, -74.00)
    """

    def __init__(self, cfg: WeatherAgentConfig = default_config):
        self.cfg = cfg
        self._session = _build_session(cfg)
        self._cache: dict[str, tuple[float, object]] = {}   # key → (timestamp, value)
        self._cache_ttl = 60   # seconds — avoids hammering the API

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        """
        Perform a GET request against the NWS base URL.
        Raises requests.HTTPError on 4xx/5xx responses.
        """
        url = f"{self.cfg.nws_base_url}{path}"
        cache_key = f"{url}?{params}"

        # Serve from in-memory cache if fresh
        if cache_key in self._cache:
            cached_at, cached_data = self._cache[cache_key]
            if time.time() - cached_at < self._cache_ttl:
                logger.debug("Cache hit: %s", path)
                return cached_data

        logger.debug("GET %s  params=%s", url, params)
        response = self._session.get(
            url,
            params=params,
            timeout=self.cfg.nws_request_timeout,
        )
        response.raise_for_status()
        data = response.json()
        self._cache[cache_key] = (time.time(), data)
        return data

    @staticmethod
    def _parse_iso(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse an ISO-8601 string that may include a timezone offset."""
        if not dt_str:
            return None
        try:
            # Python 3.11+ handles this natively; handle older versions too
            return datetime.fromisoformat(dt_str)
        except ValueError:
            # Try truncating sub-second precision
            return datetime.fromisoformat(dt_str[:19])

    # ------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------

    def get_grid_point(self, lat: float, lon: float) -> GridPoint:
        """
        Resolve a lat/lon to an NWS grid point.

        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)

        Returns:
            GridPoint with office, grid_x, grid_y, and location metadata.

        Raises:
            requests.HTTPError: if the point is outside the NWS coverage area
                               (i.e. not in the continental US, AK, HI, etc.)
        """
        data = self._get(f"/points/{lat:.4f},{lon:.4f}")
        props = data["properties"]

        rel_location = props.get("relativeLocation", {}).get("properties", {})
        return GridPoint(
            office=props["gridId"],
            grid_x=props["gridX"],
            grid_y=props["gridY"],
            forecast_zone=props.get("forecastZone"),
            county_zone=props.get("county"),
            fire_weather_zone=props.get("fireWeatherZone"),
            time_zone=props.get("timeZone", "UTC"),
            city=rel_location.get("city"),
            state=rel_location.get("state"),
        )

    def get_forecast(
        self,
        grid: GridPoint,
        location: GeoPoint,
        hourly: bool = False,
    ) -> WeatherForecast:
        """
        Fetch the 7-day (or hourly) forecast for a grid point.

        Args:
            grid:     GridPoint returned by get_grid_point()
            location: Original GeoPoint for metadata
            hourly:   True for hourly detail, False for 7-day periods

        Returns:
            WeatherForecast populated with ForecastPeriods.
        """
        endpoint = (
            f"/gridpoints/{grid.office}/{grid.grid_x},{grid.grid_y}/forecast"
            + ("/hourly" if hourly else "")
        )
        data  = self._get(endpoint)
        props = data["properties"]

        periods: list[ForecastPeriod] = []
        for p in props.get("periods", []):
            pop = p.get("probabilityOfPrecipitation", {})
            rh  = p.get("relativeHumidity", {})
            dp  = p.get("dewpoint", {})

            periods.append(ForecastPeriod(
                number=p["number"],
                name=p["name"],
                start_time=self._parse_iso(p["startTime"]),
                end_time=self._parse_iso(p["endTime"]),
                is_daytime=p.get("isDaytime", True),
                temperature=p["temperature"],
                temperature_unit=p.get("temperatureUnit", "F"),
                temperature_trend=p.get("temperatureTrend"),
                wind_speed=p.get("windSpeed", ""),
                wind_direction=p.get("windDirection", ""),
                short_forecast=p.get("shortForecast", ""),
                detailed_forecast=p.get("detailedForecast", ""),
                probability_of_precipitation=(
                    pop.get("value") if isinstance(pop, dict) else None
                ),
                relative_humidity=(
                    rh.get("value") if isinstance(rh, dict) else None
                ),
                dewpoint_fahrenheit=(
                    dp.get("value") if isinstance(dp, dict) else None
                ),
            ))

        elevation = props.get("elevation", {})
        elev_m = elevation.get("value") if isinstance(elevation, dict) else None

        return WeatherForecast(
            location=location,
            grid_point=grid,
            generated_at=datetime.utcnow(),
            update_time=self._parse_iso(props.get("updateTime")) or datetime.utcnow(),
            periods=periods,
            elevation_meters=elev_m,
        )

    def get_active_alerts(
        self,
        state: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        limit: int = 50,
    ) -> list[WeatherAlert]:
        """
        Fetch active NWS weather alerts.

        Priority: point (lat/lon) > state > nationwide.

        Args:
            state:  Two-letter US state code (e.g. "NY")
            lat:    Latitude for point-based query
            lon:    Longitude for point-based query
            limit:  Maximum number of alerts to return

        Returns:
            List of WeatherAlert objects sorted by severity (most severe first).
        """
        params: dict = {}
        if lat is not None and lon is not None:
            params["point"] = f"{lat:.4f},{lon:.4f}"
        elif state:
            params["area"] = state.upper()

        try:
            data = self._get("/alerts/active", params=params)
        except requests.HTTPError as exc:
            logger.warning("Alert fetch failed: %s", exc)
            return []

        alerts: list[WeatherAlert] = []
        for feature in data.get("features", [])[:limit]:
            props = feature.get("properties", {})
            try:
                alert = WeatherAlert(
                    alert_id=props.get("id", feature.get("id", "unknown")),
                    headline=props.get("headline") or props.get("event", ""),
                    event=props.get("event", ""),
                    severity=AlertSeverity(
                        props.get("severity", AlertSeverity.UNKNOWN)
                    ),
                    urgency=AlertUrgency(
                        props.get("urgency", AlertUrgency.UNKNOWN)
                    ),
                    certainty=AlertCertainty(
                        props.get("certainty", AlertCertainty.UNKNOWN)
                    ),
                    area_description=props.get("areaDesc", ""),
                    sent=self._parse_iso(props.get("sent")) or datetime.utcnow(),
                    effective=self._parse_iso(props.get("effective")) or datetime.utcnow(),
                    expires=self._parse_iso(props.get("expires")) or datetime.utcnow(),
                    onset=self._parse_iso(props.get("onset")),
                    ends=self._parse_iso(props.get("ends")),
                    description=props.get("description", ""),
                    instruction=props.get("instruction"),
                    affected_zones=props.get("affectedZones", []),
                )
                alerts.append(alert)
            except Exception as exc:
                logger.debug("Skipped malformed alert %s: %s", props.get("id"), exc)

        # Sort: Extreme → Severe → Moderate → Minor
        severity_order = {
            AlertSeverity.EXTREME: 0,
            AlertSeverity.SEVERE: 1,
            AlertSeverity.MODERATE: 2,
            AlertSeverity.MINOR: 3,
            AlertSeverity.UNKNOWN: 4,
        }
        alerts.sort(key=lambda a: severity_order.get(a.severity, 5))
        return alerts

    def get_active_alerts_for_point(
        self, lat: float, lon: float
    ) -> list[WeatherAlert]:
        """Convenience wrapper: alerts affecting a specific lat/lon."""
        return self.get_active_alerts(lat=lat, lon=lon)

    def get_active_alerts_for_state(self, state: str) -> list[WeatherAlert]:
        """Convenience wrapper: all active alerts in a US state."""
        return self.get_active_alerts(state=state)

    def health_check(self) -> bool:
        """
        Ping the NWS API to confirm it is reachable.

        Returns:
            True if the API responds normally, False otherwise.
        """
        try:
            self._get("/")
            return True
        except Exception as exc:
            logger.error("NWS API health check failed: %s", exc)
            return False
