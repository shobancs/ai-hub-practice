"""
Weather Forecasting Agent — Core Orchestrator

Implements an OpenAI function-calling agent loop that:
1. Decides which weather data to fetch based on user questions
2. Calls weather.gov tools to retrieve live data
3. Generates safety guidelines for active alerts
4. Answers questions using real-time weather context

Tool definitions follow the OpenAI function-calling schema.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from openai import OpenAI, OpenAIError

from .config import WeatherAgentConfig, config as default_config
from .models import AgentState, GeoPoint, WeatherAlert
from .safety_advisor import SafetyAdvisor
from .weather_client import WeatherGovClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# OpenAI Tool Definitions
# ---------------------------------------------------------------------------

TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": (
                "Fetch the current 7-day weather forecast for a specific location "
                "using the National Weather Service (NWS) API. "
                "Use this when asked about future weather conditions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of the location (e.g. 40.7128 for New York)",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of the location (e.g. -74.0060 for New York)",
                    },
                    "location_name": {
                        "type": "string",
                        "description": "Human-readable name of the location",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_hourly_forecast",
            "description": (
                "Fetch the hourly weather forecast for a location. "
                "Use when asked about weather in the next few hours."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude":      {"type": "number"},
                    "longitude":     {"type": "number"},
                    "location_name": {"type": "string"},
                    "hours":         {
                        "type": "integer",
                        "description": "Number of hours to return (default 12, max 156)",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_alerts",
            "description": (
                "Retrieve all active NWS weather alerts, watches, and warnings "
                "for a location or US state. Always call this when asked about "
                "dangerous weather, emergencies, warnings, or public safety."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude":      {"type": "number"},
                    "longitude":     {"type": "number"},
                    "state":         {
                        "type": "string",
                        "description": "Two-letter US state code (e.g. 'NY'). "
                                       "Use either state OR lat/lon, not both.",
                    },
                    "location_name": {"type": "string"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_safety_guidelines",
            "description": (
                "Generate AI-powered public safety guidelines for a specific "
                "weather hazard or active alert. Use when asked about safety, "
                "what to do during severe weather, or how to prepare."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Alert ID from a previous get_active_alerts call",
                    },
                    "hazard_type": {
                        "type": "string",
                        "enum": [
                            "tornado", "hurricane", "flood", "winter_storm",
                            "heat_wave", "thunderstorm", "wildfire",
                            "extreme_cold", "high_wind", "fog", "general",
                        ],
                        "description": "Type of weather hazard (required if alert_id not given)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_monitored_locations",
            "description": (
                "List all locations currently being monitored by the agent. "
                "Use when asked 'what locations are you tracking?' or similar."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class WeatherForecastAgent:
    """
    Agentic weather assistant using OpenAI function calling.

    The agent maintains a shared AgentState that is also updated by the
    background Scheduler — ensuring the latest data is always available.

    Usage:
        agent = WeatherForecastAgent()
        response = agent.chat("Are there any tornado warnings near Chicago?")
        print(response)
    """

    def __init__(
        self,
        cfg: WeatherAgentConfig = default_config,
        state: Optional[AgentState] = None,
    ):
        self.cfg = cfg
        self.state = state or AgentState()
        self.weather_client = WeatherGovClient(cfg)
        self.safety_advisor = SafetyAdvisor(cfg)
        self.conversation_history: list[dict] = []

        if cfg.openai_api_key:
            self._openai = OpenAI(api_key=cfg.openai_api_key)
        else:
            self._openai = None
            logger.warning("OpenAI unavailable — agent will use direct tool responses only.")

        # Seed with configured locations
        for lat, lon, name in cfg.default_locations:
            self.state.locations.append(
                GeoPoint(latitude=lat, longitude=lon, location_name=name)
            )

        # System prompt
        self.conversation_history.append({
            "role": "system",
            "content": (
                "You are WeatherGuard, an AI-powered weather forecasting and public safety agent "
                "backed by the National Weather Service (NWS) API.\n\n"
                "Your responsibilities:\n"
                "1. Provide accurate, real-time weather forecasts and alerts\n"
                "2. Generate clear, life-saving public safety guidelines for severe weather\n"
                "3. Help people understand what actions to take during weather emergencies\n"
                "4. Always prioritize public safety — escalate extreme alerts prominently\n\n"
                "Guidelines:\n"
                "- Always call the appropriate weather tools before answering — never guess\n"
                "- When severe alerts exist, lead with safety information\n"
                "- Use plain language; avoid meteorological jargon unless asked\n"
                "- Reference official NWS instructions when available\n"
                "- Always recommend calling 911 in life-threatening situations\n"
                f"\nCurrent time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            ),
        })

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response.

        The agent may call multiple weather tools internally before
        composing its final answer.

        Args:
            user_message: The user's question or request.

        Returns:
            The agent's response as a string.
        """
        if not self._openai:
            return self._fallback_response(user_message)

        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        # Agentic loop — keep running until the model stops calling tools
        max_tool_rounds = 5
        for round_num in range(max_tool_rounds):
            try:
                response = self._openai.chat.completions.create(
                    model=self.cfg.openai_model,
                    messages=self.conversation_history,
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=0.4,
                    max_tokens=2000,
                )
            except OpenAIError as exc:
                logger.error("OpenAI API error: %s", exc)
                return f"I encountered an error while processing your request: {exc}"

            message = response.choices[0].message
            self.conversation_history.append(message.model_dump())

            # If no tool calls — we have the final answer
            if not message.tool_calls:
                return message.content or "I couldn't generate a response."

            # Execute each tool call
            for tool_call in message.tool_calls:
                result = self._execute_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments),
                )
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                })

        return "I reached the maximum number of tool calls without a final answer."

    def get_state_summary(self) -> dict:
        """Return a JSON-serializable summary of the agent's current state."""
        return {
            "monitored_locations": [
                {"name": loc.location_name, "lat": loc.latitude, "lon": loc.longitude}
                for loc in self.state.locations
            ],
            "active_alerts_count": len(self.state.active_alerts),
            "has_extreme_alerts": self.state.has_extreme_alerts,
            "last_data_fetch": str(self.state.last_data_fetch),
            "total_fetches": self.state.total_fetches,
        }

    def clear_history(self) -> None:
        """Reset conversation history (keep system prompt)."""
        self.conversation_history = [self.conversation_history[0]]

    # ------------------------------------------------------------------
    # Tool Execution
    # ------------------------------------------------------------------

    def _execute_tool(self, tool_name: str, args: dict) -> Any:
        """Dispatch a tool call and return a JSON-serializable result."""
        logger.debug("Executing tool: %s  args=%s", tool_name, args)

        try:
            if tool_name == "get_weather_forecast":
                return self._tool_get_forecast(args)

            if tool_name == "get_hourly_forecast":
                return self._tool_get_hourly(args)

            if tool_name == "get_active_alerts":
                return self._tool_get_alerts(args)

            if tool_name == "get_safety_guidelines":
                return self._tool_get_safety(args)

            if tool_name == "get_monitored_locations":
                return self._tool_get_locations()

            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as exc:
            logger.exception("Tool %s failed: %s", tool_name, exc)
            self.state.errors.append(f"{tool_name}: {exc}")
            return {"error": str(exc)}

    def _tool_get_forecast(self, args: dict) -> dict:
        lat  = args["latitude"]
        lon  = args["longitude"]
        name = args.get("location_name", f"{lat},{lon}")
        location = GeoPoint(latitude=lat, longitude=lon, location_name=name)

        grid     = self.weather_client.get_grid_point(lat, lon)
        forecast = self.weather_client.get_forecast(grid, location)

        # Cache in state
        self.state.latest_forecasts[name] = forecast
        self.state.last_data_fetch = datetime.utcnow()
        self.state.total_fetches += 1

        return {
            "location": name,
            "city": grid.city,
            "state": grid.state,
            "time_zone": grid.time_zone,
            "updated": str(forecast.update_time),
            "periods": [
                {
                    "name": p.name,
                    "temperature": f"{p.temperature}°{p.temperature_unit}",
                    "wind": f"{p.wind_speed} {p.wind_direction}",
                    "short_forecast": p.short_forecast,
                    "precipitation_chance": (
                        f"{p.probability_of_precipitation}%"
                        if p.probability_of_precipitation is not None
                        else "N/A"
                    ),
                    "detailed": p.detailed_forecast,
                }
                for p in forecast.periods[:14]
            ],
        }

    def _tool_get_hourly(self, args: dict) -> dict:
        lat   = args["latitude"]
        lon   = args["longitude"]
        name  = args.get("location_name", f"{lat},{lon}")
        hours = min(args.get("hours", 12), 156)
        location = GeoPoint(latitude=lat, longitude=lon, location_name=name)

        grid     = self.weather_client.get_grid_point(lat, lon)
        forecast = self.weather_client.get_forecast(grid, location, hourly=True)

        self.state.total_fetches += 1

        return {
            "location": name,
            "updated": str(forecast.update_time),
            "hourly": [
                {
                    "time": p.start_time.strftime("%Y-%m-%d %H:%M"),
                    "temperature": f"{p.temperature}°{p.temperature_unit}",
                    "wind": f"{p.wind_speed} {p.wind_direction}",
                    "short_forecast": p.short_forecast,
                    "precipitation_chance": (
                        f"{p.probability_of_precipitation}%"
                        if p.probability_of_precipitation is not None
                        else "N/A"
                    ),
                }
                for p in forecast.periods[:hours]
            ],
        }

    def _tool_get_alerts(self, args: dict) -> dict:
        lat   = args.get("latitude")
        lon   = args.get("longitude")
        state = args.get("state")
        name  = args.get("location_name", "requested area")

        alerts = self.weather_client.get_active_alerts(
            state=state,
            lat=lat,
            lon=lon,
        )

        # Update shared state
        self.state.active_alerts = alerts
        self.state.last_alert_check = datetime.utcnow()

        if not alerts:
            return {
                "location": name,
                "alert_count": 0,
                "message": "No active weather alerts at this time.",
            }

        return {
            "location": name,
            "alert_count": len(alerts),
            "alerts": [
                {
                    "id": a.alert_id,
                    "event": a.event,
                    "severity": a.severity.value,
                    "urgency": a.urgency.value,
                    "headline": a.headline,
                    "area": a.area_description,
                    "effective": str(a.effective),
                    "expires": str(a.expires),
                    "description": a.description[:500] + "..." if len(a.description) > 500 else a.description,
                    "instruction": a.instruction,
                    "hazard_category": a.hazard_category.value,
                }
                for a in alerts
            ],
        }

    def _tool_get_safety(self, args: dict) -> dict:
        alert_id   = args.get("alert_id")
        hazard_str = args.get("hazard_type", "general")

        # Find alert in state if ID provided
        alert: Optional[WeatherAlert] = None
        if alert_id:
            alert = next(
                (a for a in self.state.active_alerts if a.alert_id == alert_id),
                None,
            )

        if alert:
            guideline = self.safety_advisor.generate_guideline(alert)
        else:
            # Create a synthetic alert to drive static/AI guideline
            from .models import HazardCategory, AlertSeverity, AlertUrgency, AlertCertainty
            try:
                category = HazardCategory(hazard_str)
            except ValueError:
                category = HazardCategory.GENERAL

            synthetic = WeatherAlert(
                alert_id="synthetic",
                headline=f"{hazard_str.replace('_', ' ').title()} Safety Guidelines",
                event=hazard_str.replace("_", " ").title(),
                severity=AlertSeverity.MODERATE,
                urgency=AlertUrgency.EXPECTED,
                certainty=AlertCertainty.LIKELY,
                area_description="Requested area",
                sent=datetime.utcnow(),
                effective=datetime.utcnow(),
                expires=datetime.utcnow(),
                description=f"Safety guidelines for {hazard_str}",
            )
            guideline = self.safety_advisor._static_guideline(synthetic, category)

        # Cache guideline
        self.state.safety_guidelines.append(guideline)

        return {
            "hazard_category": guideline.hazard_category.value,
            "headline": guideline.headline,
            "summary": guideline.summary,
            "immediate_actions": [
                {"priority": a.priority, "action": a.action, "emoji": a.emoji}
                for a in sorted(guideline.immediate_actions, key=lambda x: x.priority)
            ],
            "preparedness_tips": guideline.preparedness_tips,
            "after_event_tips": guideline.after_event_tips,
            "vulnerable_populations": guideline.vulnerable_populations,
            "emergency_contacts": guideline.emergency_contacts,
            "generated_by": guideline.ai_model_used,
        }

    def _tool_get_locations(self) -> dict:
        return {
            "monitored_locations": [
                {
                    "name": loc.location_name,
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                }
                for loc in self.state.locations
            ]
        }

    # ------------------------------------------------------------------
    # Fallback (no OpenAI key)
    # ------------------------------------------------------------------

    def _fallback_response(self, user_message: str) -> str:
        """Direct tool execution without AI — for no-API-key mode."""
        msg_lower = user_message.lower()

        if any(kw in msg_lower for kw in ["alert", "warning", "danger", "severe"]):
            alerts = self.weather_client.get_active_alerts()
            if not alerts:
                return "✅ No active weather alerts nationwide at this time."
            lines = [f"🚨 {len(alerts)} Active Alert(s):\n"]
            for a in alerts[:5]:
                lines.append(f"  • [{a.severity.value}] {a.event} — {a.area_description}")
            return "\n".join(lines)

        return (
            "I need an OpenAI API key to answer free-form questions. "
            "Set OPENAI_API_KEY in your .env file. "
            "I can still fetch raw weather data — try the CLI with --raw-data."
        )
