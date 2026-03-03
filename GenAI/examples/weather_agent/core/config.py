"""
Configuration for the Weather Forecasting Agent.

Values are loaded from environment variables first, then fall back to
sensible defaults.  Copy .env.example → .env and fill in your keys.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class WeatherAgentConfig:
    """Central configuration object for the entire agent."""

    # ------------------------------------------------------------------ #
    # OpenAI
    # ------------------------------------------------------------------ #
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o")
    )

    # ------------------------------------------------------------------ #
    # Weather.gov API
    # ------------------------------------------------------------------ #
    nws_base_url: str = "https://api.weather.gov"
    # NWS requires a descriptive User-Agent identifying your application
    nws_user_agent: str = field(
        default_factory=lambda: os.getenv(
            "NWS_USER_AGENT",
            "WeatherForecastAgent/1.0 (ai-hub-practice; contact@example.com)"
        )
    )
    nws_request_timeout: int = 30   # seconds per request
    nws_max_retries: int = 3

    # ------------------------------------------------------------------ #
    # Polling / Scheduler
    # ------------------------------------------------------------------ #
    # How often (seconds) to fetch full 7-day forecasts
    forecast_poll_interval: int = field(
        default_factory=lambda: int(os.getenv("FORECAST_POLL_INTERVAL", "1800"))   # 30 min
    )
    # How often (seconds) to check for new / updated alerts  
    alert_poll_interval: int = field(
        default_factory=lambda: int(os.getenv("ALERT_POLL_INTERVAL", "300"))       # 5 min
    )
    # How often (seconds) to check for hourly forecasts
    hourly_poll_interval: int = field(
        default_factory=lambda: int(os.getenv("HOURLY_POLL_INTERVAL", "3600"))     # 1 hour
    )

    # ------------------------------------------------------------------ #
    # Monitored Locations  (lat, lon, friendly name)
    # ------------------------------------------------------------------ #
    # Override via env: WEATHER_LOCATIONS="40.71,-74.01,New York;34.05,-118.24,Los Angeles"
    default_locations: list[tuple[float, float, str]] = field(
        default_factory=lambda: WeatherAgentConfig._parse_locations(
            os.getenv(
                "WEATHER_LOCATIONS",
                "40.7128,-74.0060,New York NY;"
                "34.0522,-118.2437,Los Angeles CA;"
                "41.8781,-87.6298,Chicago IL;"
                "29.7604,-95.3698,Houston TX;"
                "33.4484,-112.0740,Phoenix AZ"
            )
        )
    )

    # ------------------------------------------------------------------ #
    # Safety Guidelines
    # ------------------------------------------------------------------ #
    # Minimum alert severity to auto-generate AI safety guidelines
    auto_guideline_severity: str = field(
        default_factory=lambda: os.getenv("AUTO_GUIDELINE_SEVERITY", "Moderate")
    )
    # Max cached guidelines to keep in memory
    max_cached_guidelines: int = 50

    # ------------------------------------------------------------------ #
    # Logging & Output
    # ------------------------------------------------------------------ #
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    enable_rich_output: bool = True

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_locations(raw: str) -> list[tuple[float, float, str]]:
        """
        Parse semicolon-separated 'lat,lon,name' strings.
        Returns list of (lat, lon, name) tuples.
        """
        locations = []
        for entry in raw.split(";"):
            entry = entry.strip()
            if not entry:
                continue
            parts = entry.split(",", 2)
            if len(parts) < 2:
                continue
            try:
                lat  = float(parts[0].strip())
                lon  = float(parts[1].strip())
                name = parts[2].strip() if len(parts) > 2 else f"{lat},{lon}"
                locations.append((lat, lon, name))
            except ValueError:
                continue
        return locations

    def validate(self) -> list[str]:
        """Return list of configuration warnings (non-fatal issues)."""
        warnings = []
        if not self.openai_api_key:
            warnings.append(
                "OPENAI_API_KEY is not set — AI safety guidelines will be unavailable."
            )
        if not self.default_locations:
            warnings.append(
                "No monitored locations configured. "
                "Set WEATHER_LOCATIONS in your .env file."
            )
        if self.alert_poll_interval < 60:
            warnings.append(
                f"Alert poll interval ({self.alert_poll_interval}s) is very aggressive. "
                "NWS asks for at least 60 s between requests."
            )
        return warnings


# Module-level singleton — import this directly in other modules
config = WeatherAgentConfig()
