"""
Data Models for the Weather Forecasting Agent
Uses Pydantic for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AlertSeverity(str, Enum):
    """NWS alert severity levels (most → least severe)."""
    EXTREME   = "Extreme"
    SEVERE    = "Severe"
    MODERATE  = "Moderate"
    MINOR     = "Minor"
    UNKNOWN   = "Unknown"


class AlertUrgency(str, Enum):
    """How quickly the public should respond."""
    IMMEDIATE = "Immediate"
    EXPECTED  = "Expected"
    FUTURE    = "Future"
    PAST      = "Past"
    UNKNOWN   = "Unknown"


class AlertCertainty(str, Enum):
    """Confidence level of the alert."""
    OBSERVED  = "Observed"
    LIKELY    = "Likely"
    POSSIBLE  = "Possible"
    UNLIKELY  = "Unlikely"
    UNKNOWN   = "Unknown"


class HazardCategory(str, Enum):
    """High-level hazard categories for safety guidelines."""
    TORNADO        = "tornado"
    HURRICANE      = "hurricane"
    FLOOD          = "flood"
    WINTER_STORM   = "winter_storm"
    HEAT_WAVE      = "heat_wave"
    THUNDERSTORM   = "thunderstorm"
    WILDFIRE       = "wildfire"
    EXTREME_COLD   = "extreme_cold"
    HIGH_WIND      = "high_wind"
    FOG            = "fog"
    DROUGHT        = "drought"
    GENERAL        = "general"


# ---------------------------------------------------------------------------
# Weather Data Models
# ---------------------------------------------------------------------------

class GeoPoint(BaseModel):
    """A geographic coordinate pair."""
    latitude: float  = Field(..., ge=-90,  le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_name: str = Field(default="Unknown Location")


class GridPoint(BaseModel):
    """NWS grid reference returned by /points/{lat},{lon}."""
    office: str          # e.g. "OKX"
    grid_x: int
    grid_y: int
    forecast_zone: Optional[str] = None
    county_zone: Optional[str]   = None
    fire_weather_zone: Optional[str] = None
    time_zone: str = "UTC"
    city: Optional[str] = None
    state: Optional[str] = None


class ForecastPeriod(BaseModel):
    """A single period in a 7-day or hourly forecast."""
    number: int
    name: str                        # e.g. "Tonight", "Monday"
    start_time: datetime
    end_time: datetime
    is_daytime: bool
    temperature: int
    temperature_unit: str            # "F" or "C"
    temperature_trend: Optional[str] = None   # "rising" | "falling"
    wind_speed: str                  # e.g. "10 to 15 mph"
    wind_direction: str              # e.g. "NW"
    short_forecast: str              # e.g. "Mostly Cloudy"
    detailed_forecast: str
    probability_of_precipitation: Optional[int] = None   # 0-100 %
    relative_humidity: Optional[int] = None              # 0-100 %
    dewpoint_fahrenheit: Optional[float] = None


class WeatherForecast(BaseModel):
    """Full forecast for a location."""
    location: GeoPoint
    grid_point: GridPoint
    generated_at: datetime
    update_time: datetime
    periods: list[ForecastPeriod]
    elevation_meters: Optional[float] = None


class WeatherAlert(BaseModel):
    """A single NWS weather alert / warning / watch / advisory."""
    alert_id: str
    headline: str
    event: str                        # e.g. "Tornado Warning"
    severity: AlertSeverity
    urgency: AlertUrgency
    certainty: AlertCertainty
    area_description: str
    sent: datetime
    effective: datetime
    expires: datetime
    onset: Optional[datetime] = None
    ends: Optional[datetime] = None
    description: str
    instruction: Optional[str] = None   # Official NWS action instructions
    affected_zones: list[str] = Field(default_factory=list)
    is_active: bool = True

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow().replace(tzinfo=self.expires.tzinfo) > self.expires

    @property
    def hazard_category(self) -> HazardCategory:
        """Infer hazard category from the event name."""
        evt = self.event.lower()
        mapping = {
            "tornado":      HazardCategory.TORNADO,
            "hurricane":    HazardCategory.HURRICANE,
            "tropical":     HazardCategory.HURRICANE,
            "flood":        HazardCategory.FLOOD,
            "blizzard":     HazardCategory.WINTER_STORM,
            "winter storm": HazardCategory.WINTER_STORM,
            "winter weather": HazardCategory.WINTER_STORM,
            "ice storm":    HazardCategory.WINTER_STORM,
            "freeze":       HazardCategory.EXTREME_COLD,
            "wind chill":   HazardCategory.EXTREME_COLD,
            "heat":         HazardCategory.HEAT_WAVE,
            "excessive heat": HazardCategory.HEAT_WAVE,
            "thunderstorm": HazardCategory.THUNDERSTORM,
            "severe thunderstorm": HazardCategory.THUNDERSTORM,
            "fire":         HazardCategory.WILDFIRE,
            "red flag":     HazardCategory.WILDFIRE,
            "high wind":    HazardCategory.HIGH_WIND,
            "wind advisory": HazardCategory.HIGH_WIND,
            "fog":          HazardCategory.FOG,
            "dense fog":    HazardCategory.FOG,
            "drought":      HazardCategory.DROUGHT,
        }
        for keyword, category in mapping.items():
            if keyword in evt:
                return category
        return HazardCategory.GENERAL


# ---------------------------------------------------------------------------
# Safety Models
# ---------------------------------------------------------------------------

class SafetyAction(BaseModel):
    """A single, actionable safety step."""
    priority: int           # 1 = most critical
    action: str             # Plain-language instruction
    emoji: str = "⚠️"       # Visual indicator for CLI/web output


class SafetyGuideline(BaseModel):
    """AI-generated safety guideline for a specific hazard/alert."""
    alert_id: Optional[str] = None
    hazard_category: HazardCategory
    headline: str
    summary: str                         # 1-2 sentence AI summary
    immediate_actions: list[SafetyAction]  # Do RIGHT NOW
    preparedness_tips: list[str]           # Before the event
    after_event_tips: list[str]            # After the event ends
    vulnerable_populations: list[str]      # Groups needing extra care
    emergency_contacts: list[str]          # 911, Red Cross, etc.
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    ai_model_used: str = "gpt-4o"


# ---------------------------------------------------------------------------
# Agent State
# ---------------------------------------------------------------------------

class AgentState(BaseModel):
    """Snapshot of the agent's current knowledge and status."""
    locations: list[GeoPoint] = Field(default_factory=list)
    latest_forecasts: dict[str, WeatherForecast] = Field(default_factory=dict)
    active_alerts: list[WeatherAlert] = Field(default_factory=list)
    safety_guidelines: list[SafetyGuideline] = Field(default_factory=list)
    last_data_fetch: Optional[datetime] = None
    last_alert_check: Optional[datetime] = None
    total_fetches: int = 0
    errors: list[str] = Field(default_factory=list)

    def clear_expired_alerts(self) -> int:
        """Remove expired alerts. Returns count removed."""
        before = len(self.active_alerts)
        self.active_alerts = [a for a in self.active_alerts if not a.is_expired]
        return before - len(self.active_alerts)

    @property
    def has_extreme_alerts(self) -> bool:
        return any(
            a.severity in (AlertSeverity.EXTREME, AlertSeverity.SEVERE)
            for a in self.active_alerts
        )
