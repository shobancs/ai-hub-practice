"""
Safety Advisor
Generates AI-powered, public-facing safety guidelines for weather hazards.

For every active alert (severity ≥ Moderate) the advisor calls OpenAI
to produce structured, plain-language instructions people can follow
immediately to stay safe.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from openai import OpenAI, OpenAIError

from .config import WeatherAgentConfig, config as default_config
from .models import (
    HazardCategory,
    SafetyAction,
    SafetyGuideline,
    WeatherAlert,
    AlertSeverity,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Built-in (offline) safety guidelines
# Used as fallback when OpenAI is unavailable
# ---------------------------------------------------------------------------

STATIC_GUIDELINES: dict[HazardCategory, dict] = {
    HazardCategory.TORNADO: {
        "headline": "Tornado Warning — Take Shelter NOW",
        "summary": (
            "A tornado has been spotted or indicated by radar. "
            "Move to a safe location immediately — do not wait."
        ),
        "immediate_actions": [
            (1, "Go to the lowest floor of a sturdy building immediately.", "🌪️"),
            (2, "Move to an interior room or hallway away from windows.", "🏠"),
            (3, "If outside, lie flat in a ditch or low-lying area; cover your head.", "🌿"),
            (4, "NEVER shelter under a highway overpass or bridge.", "🚫"),
            (5, "Abandon mobile homes — move to a permanent structure.", "🚗"),
            (6, "If in a vehicle, drive at right angles to the tornado's path if safe.", "🚙"),
        ],
        "preparedness_tips": [
            "Identify your safe room before severe weather season.",
            "Keep a weather-alert radio with fresh batteries.",
            "Practice tornado drills with your family.",
            "Assemble an emergency kit: water, food, medications, documents.",
        ],
        "after_event_tips": [
            "Watch for downed power lines — never touch them.",
            "Check for gas leaks before entering damaged structures.",
            "Photograph damage for insurance before cleanup.",
            "Watch for injured people but do not enter unsafe structures.",
        ],
        "vulnerable_populations": [
            "People in mobile homes or RVs — evacuate to sturdy structures.",
            "People with mobility challenges — know your community's shelter plan.",
            "Children — keep them away from windows and in a safe room.",
            "Pets — bring indoors; secure carriers in advance.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "FEMA: 1-800-621-3362",
            "Red Cross: 1-800-733-2767",
            "Poison Control: 1-800-222-1222",
        ],
    },
    HazardCategory.FLOOD: {
        "headline": "Flood Warning — Never Drive Through Flood Water",
        "summary": (
            "Flooding is occurring or imminent. Even 6 inches of moving water "
            "can knock a person down; 2 feet can carry away most vehicles."
        ),
        "immediate_actions": [
            (1, "NEVER drive or walk through flooded roads. Turn Around, Don't Drown®.", "🚫"),
            (2, "Move to higher ground immediately if flooding is likely.", "⛰️"),
            (3, "If trapped in a building, go to the highest floor.", "🏢"),
            (4, "Disconnect electrical appliances if flooding is imminent.", "⚡"),
            (5, "Evacuate if ordered by local officials — do not hesitate.", "🏃"),
        ],
        "preparedness_tips": [
            "Know your flood zone — check FEMA's Flood Map Service.",
            "Purchase flood insurance (standard homeowners insurance doesn't cover floods).",
            "Keep important documents in a waterproof container.",
            "Have a 72-hour emergency supply kit ready.",
        ],
        "after_event_tips": [
            "Do not return home until authorities declare it safe.",
            "Avoid floodwater — it may be contaminated with sewage.",
            "Document all damage before cleanup.",
            "Watch for road damage, sinkholes, and unstable banks.",
        ],
        "vulnerable_populations": [
            "Elderly residents — may need assistance evacuating.",
            "People in low-lying areas or near rivers.",
            "People with disabilities — register with local emergency services.",
            "Children — keep them away from floodwater entirely.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "FEMA: 1-800-621-3362  |  DisasterAssistance.gov",
            "Red Cross: 1-800-733-2767",
            "National Flood Insurance Program: 1-800-427-4661",
        ],
    },
    HazardCategory.HEAT_WAVE: {
        "headline": "Excessive Heat Warning — Stay Cool and Hydrated",
        "summary": (
            "Dangerously hot conditions are expected. Heat is the #1 "
            "weather-related killer in the US. Stay cool and check on others."
        ),
        "immediate_actions": [
            (1, "Stay in air-conditioned spaces as much as possible.", "❄️"),
            (2, "Drink water every 15–20 minutes — don't wait until thirsty.", "💧"),
            (3, "Avoid strenuous activity during peak heat (10 AM–4 PM).", "🌡️"),
            (4, "Wear lightweight, light-colored, loose-fitting clothing.", "👕"),
            (5, "NEVER leave children or pets in parked vehicles.", "🚗"),
            (6, "Check on elderly neighbors, family, and people living alone.", "🏠"),
        ],
        "preparedness_tips": [
            "Locate your nearest cooling center (call 211 for help).",
            "Install window reflectors to keep indoor temperatures down.",
            "Know the signs of heat exhaustion and heat stroke.",
        ],
        "after_event_tips": [
            "Continue monitoring for heat-related illness for 24 hours.",
            "Rehydrate gradually after prolonged exposure.",
        ],
        "vulnerable_populations": [
            "Adults 65+ — less able to regulate body temperature.",
            "Infants and young children.",
            "People with chronic conditions (heart disease, diabetes).",
            "Outdoor workers and athletes.",
            "People without air conditioning.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "Cooling centers: Call 211",
            "Poison Control: 1-800-222-1222",
        ],
    },
    HazardCategory.WINTER_STORM: {
        "headline": "Winter Storm Warning — Stay Off Roads if Possible",
        "summary": (
            "Heavy snow, ice, or blizzard conditions are expected. "
            "Travel may be dangerous or impossible."
        ),
        "immediate_actions": [
            (1, "Stay indoors and off roads unless absolutely necessary.", "🏠"),
            (2, "If you must drive, keep emergency supplies in your vehicle.", "🚗"),
            (3, "Keep pipes from freezing — let faucets drip slowly.", "🚿"),
            (4, "Watch for carbon monoxide if using a generator or heater.", "⚠️"),
            (5, "Dress in layers; keep head, hands, and feet covered outdoors.", "🧥"),
        ],
        "preparedness_tips": [
            "Stock at least 3 days of food, water, and medications.",
            "Keep a battery-powered or hand-crank radio.",
            "Have rock salt or sand for icy walkways.",
            "Know the symptoms of hypothermia and frostbite.",
        ],
        "after_event_tips": [
            "Clear snow from roof to prevent structural collapse.",
            "Shovel carefully — overexertion causes heart attacks.",
            "Check on neighbors, especially the elderly.",
        ],
        "vulnerable_populations": [
            "Elderly and very young children.",
            "People experiencing homelessness — direct to warming centers.",
            "People with cardiovascular or respiratory conditions.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "Warming centers: Call 211",
            "FEMA: 1-800-621-3362",
        ],
    },
    HazardCategory.HURRICANE: {
        "headline": "Hurricane Warning — Follow Evacuation Orders Immediately",
        "summary": (
            "A hurricane is approaching. Storm surge is the deadliest hazard — "
            "evacuate coastal areas when ordered."
        ),
        "immediate_actions": [
            (1, "EVACUATE immediately if ordered by local officials.", "🚗"),
            (2, "Board up windows and secure outdoor objects.", "🔨"),
            (3, "Fill bathtubs with water for emergency sanitation use.", "🛁"),
            (4, "Keep a full tank of gas — stations may run out.", "⛽"),
            (5, "Take medications, documents, and irreplaceable items.", "📄"),
            (6, "Never enter flooded areas during or after the storm.", "🚫"),
        ],
        "preparedness_tips": [
            "Know your hurricane evacuation zone and route.",
            "Have a family communication plan and meeting point.",
            "Stock at least 7 days of supplies for a hurricane.",
        ],
        "after_event_tips": [
            "Wait for official all-clear before returning home.",
            "Beware of downed power lines, contaminated water, weakened structures.",
            "Document damage and contact your insurance company promptly.",
        ],
        "vulnerable_populations": [
            "Coastal residents in storm surge zones.",
            "Mobile home residents — evacuate regardless of storm category.",
            "People with medical equipment requiring electricity.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "FEMA: 1-800-621-3362  |  DisasterAssistance.gov",
            "Red Cross: 1-800-733-2767",
            "National Hurricane Center: www.nhc.noaa.gov",
        ],
    },
    HazardCategory.THUNDERSTORM: {
        "headline": "Severe Thunderstorm Warning — Seek Shelter",
        "summary": (
            "Damaging winds, large hail, and frequent lightning are possible. "
            "Lightning strikes anywhere it can — indoors is safest."
        ),
        "immediate_actions": [
            (1, "Go indoors immediately — lightning kills in open areas.", "⚡"),
            (2, "Stay away from windows, doors, porches, and electrical equipment.", "🚫"),
            (3, "Avoid plumbing — don't shower or wash dishes during storms.", "🚿"),
            (4, "If caught outside, crouch low — do NOT lie flat on the ground.", "🌿"),
            (5, "If in a vehicle, stay inside — cars protect from lightning.", "🚗"),
        ],
        "preparedness_tips": [
            "Wait 30 minutes after the last thunder before going outside.",
            "Trim trees near your home to reduce damage from falling branches.",
            "Unplug sensitive electronics when a storm approaches.",
        ],
        "after_event_tips": [
            "Check for structural damage before re-entering buildings.",
            "Photograph property damage for insurance.",
        ],
        "vulnerable_populations": [
            "People working outdoors (construction, agriculture, golf).",
            "Hikers and campers in open terrain.",
            "Swimmers and boaters — get off the water immediately.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "Lightning strike victim: Start CPR immediately and call 911.",
        ],
    },
    HazardCategory.WILDFIRE: {
        "headline": "Wildfire Warning — Evacuate Immediately If Ordered",
        "summary": (
            "Wildfire danger is extreme. Fire can spread faster than you can run. "
            "Do not wait to evacuate if told to do so."
        ),
        "immediate_actions": [
            (1, "EVACUATE immediately when ordered — don't wait for confirmation.", "🏃"),
            (2, "Close all windows, vents, and doors before leaving.", "🚪"),
            (3, "Move flammable furniture away from windows.", "🛋️"),
            (4, "Wear a N95 mask or damp cloth to filter smoke.", "😷"),
            (5, "Keep headlights on — smoke reduces visibility severely.", "🚗"),
        ],
        "preparedness_tips": [
            "Create a defensible space: clear 30 ft of vegetation around your home.",
            "Keep gutters and roof clear of dry debris.",
            "Have a go-bag ready to leave within 2 minutes.",
            "Know at least two evacuation routes.",
        ],
        "after_event_tips": [
            "Return home only when officially declared safe.",
            "Check for hot spots, embers, and structural damage.",
            "Air out your home; wildfire smoke lingers and is harmful.",
        ],
        "vulnerable_populations": [
            "People with asthma and respiratory conditions — air quality critical.",
            "Elderly and people with limited mobility — may need evacuation help.",
            "Livestock owners — have a plan to evacuate animals.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "USFS Wildfire Info: 1-800-832-1355",
            "Air Quality Index: airnow.gov",
            "Red Cross: 1-800-733-2767",
        ],
    },
    HazardCategory.EXTREME_COLD: {
        "headline": "Extreme Cold Warning — Prevent Hypothermia and Frostbite",
        "summary": (
            "Life-threatening cold is expected. Exposed skin can develop frostbite "
            "in as little as 30 minutes. Stay warm and check on others."
        ),
        "immediate_actions": [
            (1, "Layer up — base layer, insulating layer, and wind/waterproof outer layer.", "🧥"),
            (2, "Cover all exposed skin: gloves, hat covering ears, scarf.", "🧤"),
            (3, "Limit time outdoors — take warm-up breaks indoors.", "🏠"),
            (4, "Never use a gas oven or grill to heat your home.", "⚠️"),
            (5, "Know the signs of hypothermia: shivering, confusion, slurred speech.", "🌡️"),
        ],
        "preparedness_tips": [
            "Insulate pipes to prevent freezing and bursting.",
            "Stock extra food, water, blankets, and warm clothing.",
            "Have a backup heat source and CO detector.",
        ],
        "after_event_tips": [
            "Gradually rewarm frostbitten skin — don't rub it.",
            "Seek medical attention for hypothermia immediately.",
        ],
        "vulnerable_populations": [
            "Homeless individuals — direct to warming shelters (call 211).",
            "Adults 65+ and infants — lose body heat faster.",
            "People with heart and circulation problems.",
        ],
        "emergency_contacts": [
            "Emergency: 911",
            "Warming shelters: Call 211",
            "Poison Control (CO exposure): 1-800-222-1222",
        ],
    },
}


# ---------------------------------------------------------------------------
# Safety Advisor Class
# ---------------------------------------------------------------------------

class SafetyAdvisor:
    """
    Generates AI-powered safety guidelines for active weather alerts.

    If OpenAI is available, guidelines are dynamically tailored to the
    specific alert text. Otherwise, static pre-written guidelines are used.
    """

    def __init__(self, cfg: WeatherAgentConfig = default_config):
        self.cfg = cfg
        self._openai_available = bool(cfg.openai_api_key)

        if self._openai_available:
            self._client = OpenAI(api_key=cfg.openai_api_key)
        else:
            self._client = None
            logger.warning(
                "OpenAI API key not found — using static safety guidelines."
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_guideline(self, alert: WeatherAlert) -> SafetyGuideline:
        """
        Generate a safety guideline for a given weather alert.

        Uses OpenAI if available, otherwise returns a pre-written static guideline.

        Args:
            alert: The WeatherAlert to generate a guideline for.

        Returns:
            SafetyGuideline with actionable public safety instructions.
        """
        category = alert.hazard_category

        if self._openai_available:
            try:
                return self._ai_guideline(alert, category)
            except OpenAIError as exc:
                logger.warning(
                    "OpenAI guideline generation failed (%s) — falling back to static.",
                    exc,
                )

        return self._static_guideline(alert, category)

    def should_generate_guideline(self, alert: WeatherAlert) -> bool:
        """
        Decide whether an alert warrants a new safety guideline.

        Only generates for Moderate severity and above.
        """
        severity_threshold = {
            AlertSeverity.EXTREME: 0,
            AlertSeverity.SEVERE: 1,
            AlertSeverity.MODERATE: 2,
            AlertSeverity.MINOR: 3,
            AlertSeverity.UNKNOWN: 4,
        }
        cfg_severity = AlertSeverity(self.cfg.auto_guideline_severity)
        return (
            severity_threshold.get(alert.severity, 5)
            <= severity_threshold.get(cfg_severity, 2)
        )

    # ------------------------------------------------------------------
    # AI-powered guideline
    # ------------------------------------------------------------------

    def _ai_guideline(
        self, alert: WeatherAlert, category: HazardCategory
    ) -> SafetyGuideline:
        """Call OpenAI to generate a structured, context-aware guideline."""

        system_prompt = """You are an expert emergency management specialist and public safety communicator
working for a National Weather Service partner organization.

Your job is to generate CLEAR, ACTIONABLE, and LIFE-SAVING safety guidelines for the public
based on active NWS weather alerts.

Guidelines must:
- Use plain, easy-to-understand language (6th-grade reading level)
- Be ordered by urgency (most critical actions FIRST)
- Include specific numbers and thresholds when possible
- Address vulnerable populations explicitly
- Never cause panic — be calm, authoritative, and reassuring
- Always emphasize calling 911 in life-threatening situations

Return your response as a valid JSON object exactly matching this schema:
{
  "headline": "string — 10 words max, action-oriented",
  "summary": "string — 2 sentences, what's happening and top priority",
  "immediate_actions": [
    {"priority": 1, "action": "string", "emoji": "string"}
  ],
  "preparedness_tips": ["string"],
  "after_event_tips": ["string"],
  "vulnerable_populations": ["string"],
  "emergency_contacts": ["string — include phone number"]
}"""

        user_prompt = f"""Active NWS Weather Alert:

Event: {alert.event}
Severity: {alert.severity.value}
Urgency: {alert.urgency.value}
Area: {alert.area_description}
Headline: {alert.headline}
Effective: {alert.effective.strftime('%Y-%m-%d %H:%M UTC')}
Expires: {alert.expires.strftime('%Y-%m-%d %H:%M UTC')}

Official NWS Description:
{alert.description[:2000]}

Official NWS Instructions:
{alert.instruction or "No specific instructions provided."}

Generate comprehensive public safety guidelines for this alert."""

        response = self._client.chat.completions.create(
            model=self.cfg.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,     # Low temperature for authoritative safety content
            max_tokens=1500,
        )

        raw = json.loads(response.choices[0].message.content)

        immediate_actions = [
            SafetyAction(
                priority=item.get("priority", idx + 1),
                action=item["action"],
                emoji=item.get("emoji", "⚠️"),
            )
            for idx, item in enumerate(raw.get("immediate_actions", []))
        ]

        return SafetyGuideline(
            alert_id=alert.alert_id,
            hazard_category=category,
            headline=raw.get("headline", alert.event),
            summary=raw.get("summary", ""),
            immediate_actions=immediate_actions,
            preparedness_tips=raw.get("preparedness_tips", []),
            after_event_tips=raw.get("after_event_tips", []),
            vulnerable_populations=raw.get("vulnerable_populations", []),
            emergency_contacts=raw.get("emergency_contacts", ["Emergency: 911"]),
            generated_at=datetime.utcnow(),
            ai_model_used=self.cfg.openai_model,
        )

    # ------------------------------------------------------------------
    # Static (offline) fallback guideline
    # ------------------------------------------------------------------

    def _static_guideline(
        self,
        alert: WeatherAlert,
        category: HazardCategory,
    ) -> SafetyGuideline:
        """Return a pre-written guideline for the given hazard category."""

        # Fall back to GENERAL if we don't have a specific static entry
        template = STATIC_GUIDELINES.get(
            category, STATIC_GUIDELINES.get(HazardCategory.GENERAL, {})
        )

        if not template:
            template = {
                "headline": f"{alert.event} — Follow Official Instructions",
                "summary": (
                    f"A {alert.event} is in effect for {alert.area_description}. "
                    "Follow instructions from your local emergency management office."
                ),
                "immediate_actions": [
                    (1, "Monitor local news and official weather sources.", "📻"),
                    (2, "Follow all instructions from local emergency management.", "📢"),
                    (3, "Call 911 if you are in immediate danger.", "🚨"),
                ],
                "preparedness_tips": ["Keep a 72-hour emergency supply kit ready."],
                "after_event_tips": ["Follow official guidance before returning to normal activities."],
                "vulnerable_populations": ["Check on elderly and disabled neighbors."],
                "emergency_contacts": ["Emergency: 911", "Red Cross: 1-800-733-2767"],
            }

        immediate_actions = [
            SafetyAction(priority=p, action=a, emoji=e)
            for p, a, e in template.get("immediate_actions", [])
        ]

        return SafetyGuideline(
            alert_id=alert.alert_id,
            hazard_category=category,
            headline=template.get("headline", alert.event),
            summary=template.get("summary", ""),
            immediate_actions=immediate_actions,
            preparedness_tips=template.get("preparedness_tips", []),
            after_event_tips=template.get("after_event_tips", []),
            vulnerable_populations=template.get("vulnerable_populations", []),
            emergency_contacts=template.get("emergency_contacts", ["Emergency: 911"]),
            generated_at=datetime.utcnow(),
            ai_model_used="static",
        )
