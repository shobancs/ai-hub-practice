# 🌤️ WeatherGuard — AI Weather Forecasting & Safety Agent

An intelligent weather agent that **continuously collects live data from the National Weather Service** (weather.gov) and provides **AI-powered public safety guidelines** for severe weather events.

> **No weather.gov API key required** — the NWS API is free and open to the public.

---

## Features

| Feature | Description |
|---|---|
| 🌐 **Live NWS Data** | Continuously polls weather.gov for forecasts & alerts |
| 🚨 **Real-time Alerts** | Receives tornado warnings, flood watches, winter advisories, etc. |
| 🛡️ **AI Safety Guidelines** | GPT-4o generates context-aware, plain-language safety instructions |
| 📍 **Multi-location Monitoring** | Track multiple cities simultaneously |
| ⚡ **Background Scheduler** | Three independent polling threads (alerts every 5 min) |
| 💬 **Chat Interface** | Ask free-form questions about weather and safety |
| 📊 **Live Dashboard** | Rich terminal dashboard with auto-refresh |
| 🔌 **Offline Fallback** | Pre-written safety guidelines for all major hazard types |

---

## Architecture

```
weather_agent/
├── main.py                     # Entry point — CLI argument parsing & bootstrap
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
│
├── core/
│   ├── models.py               # Pydantic data models (WeatherAlert, Forecast, etc.)
│   ├── config.py               # Configuration (env vars + defaults)
│   ├── weather_client.py       # weather.gov REST API client
│   ├── safety_advisor.py       # AI/static safety guideline generator
│   ├── agent.py                # OpenAI function-calling agent orchestrator
│   └── scheduler.py            # Background data collection threads
│
└── interfaces/
    └── cli.py                  # Rich terminal UI — dashboard, alerts, chat
```

### Data Flow

```
weather.gov API
      │
      ▼
WeatherGovClient ─────────────────────────┐
  • /points/{lat},{lon}                   │
  • /gridpoints/{office}/forecast          │ WeatherScheduler
  • /alerts/active                        │ (background threads)
                                          │
                                          ▼
                                     AgentState ◄── WeatherForecastAgent
                                       • active_alerts              │
                                       • latest_forecasts           │ OpenAI
                                       • safety_guidelines          │ function-calling
                                                                    │ loop
SafetyAdvisor ──────────────────────────────────────────────────────┘
  • AI: GPT-4o structured JSON output
  • Fallback: 8 pre-written hazard templates
        │
        ▼
   WeatherCLI (Rich terminal)
   • Dashboard, Alerts, Chat
```

---

## Quick Start

### 1. Install dependencies

```bash
cd GenAI/examples/weather_agent
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

**Minimum required** (OpenAI key is optional — agent works without it using static guidelines):
```bash
# .env
NWS_USER_AGENT=WeatherAgent/1.0 (myapp; me@example.com)   # REQUIRED by NWS
OPENAI_API_KEY=sk-...                                       # Optional but recommended
```

### 3. Run the agent

```bash
python main.py                    # Interactive menu
python main.py --chat             # Chat mode
python main.py --alerts           # Show current alerts and exit
python main.py --forecast         # Show forecasts and exit
python main.py --safety tornado   # Tornado safety guidelines
python main.py --dashboard        # Live auto-refreshing dashboard
```

### Add a custom location

```bash
python main.py --lat 47.6062 --lon -122.3321 --location "Seattle WA"
```

---

## Usage Examples

### Chat Mode

```
You: Are there any tornado warnings near Kansas City?

WeatherGuard: I checked the National Weather Service and found 2 active alerts
for the Kansas City metro area:

🚨 TORNADO WARNING (Extreme) — Johnson County, KS and Jackson County, MO
  Effective until 8:45 PM CDT. A confirmed tornado was reported near Olathe
  moving northeast at 35 mph.

🛡️ IMMEDIATE ACTIONS:
  1. 🌪️  Go to the LOWEST floor of a sturdy building — interior room, away from windows
  2. 🏠  If in a mobile home, evacuate immediately to a sturdy structure
  3. 🚗  If driving, do NOT shelter under an overpass — move perpendicular to storm
  4. 📻  Monitor NWS alerts at weather.gov or via NOAA Weather Radio

Emergency: 911 | Red Cross: 1-800-733-2767
```

### Alert Dashboard

```
┌──────────────────────────────────────────────────────────────────┐
│ 🕐 2026-02-28 14:32 UTC  🆘 2 EXTREME ALERT(S) ACTIVE           │
└──────────────────────────────────────────────────────────────────┘
┌─ 🚨 Active Alerts ────────┐  ┌─ 📅 Weather Forecasts ──────────┐
│ 🆘 Tornado Warning        │  │ 📍 New York, NY                 │
│ Johnson County, KS        │  │ Tonight: Partly Cloudy  34°F   │
│ EXTREME | IMMEDIATE       │  │ Monday:  Mostly Sunny   42°F   │
│                           │  │ Tuesday: Rain           38°F   │
│ 🚨 Flash Flood Warning    │  │                                 │
│ Jackson County, MO        │  │ 📍 Los Angeles, CA             │
│ SEVERE | IMMEDIATE        │  │ Tonight: Clear          62°F   │
└───────────────────────────┘  └─────────────────────────────────┘
```

---

## Safety Guidelines Coverage

The agent includes pre-written + AI-enhanced safety guidelines for:

| Hazard | Severity Examples | Key Guidance |
|---|---|---|
| 🌪️ **Tornado** | Tornado Warning/Watch | Shelter on lowest floor, away from windows |
| 🌊 **Flood** | Flash Flood Warning | Never drive through flood water |
| 🌀 **Hurricane** | Hurricane Warning/Watch | Evacuate coastal zones when ordered |
| 🌡️ **Heat Wave** | Excessive Heat Warning | Stay cool, hydrate, check on elderly |
| ❄️ **Winter Storm** | Blizzard/Winter Storm Warning | Stay off roads, prevent pipe freezing |
| ⛈️ **Thunderstorm** | Severe Thunderstorm Warning | Go indoors, avoid tall trees |
| 🔥 **Wildfire** | Red Flag/Fire Warning | Evacuate immediately, N95 masks |
| 🥶 **Extreme Cold** | Wind Chill Warning | Layer clothing, warming shelters |

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(none)* | OpenAI API key — optional but enables AI guidelines |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model for safety guideline generation |
| `NWS_USER_AGENT` | See `.env.example` | **Required by NWS** — identify your application |
| `WEATHER_LOCATIONS` | 5 major US cities | `"lat,lon,Name;lat,lon,Name;..."` |
| `ALERT_POLL_INTERVAL` | `300` | Seconds between alert checks (min 60) |
| `FORECAST_POLL_INTERVAL` | `1800` | Seconds between forecast refreshes |
| `AUTO_GUIDELINE_SEVERITY` | `Moderate` | Minimum severity for auto-generating guidelines |
| `LOG_LEVEL` | `INFO` | `DEBUG / INFO / WARNING / ERROR` |

---

## weather.gov API Notes

- **Free and no API key required** — maintained by NOAA/NWS
- **Coverage**: Continental US, Alaska, Hawaii, US territories
- **Rate limits**: NWS requests you identify your app via `User-Agent` header
- **Reliability**: NWS recommends implementing retries (already handled in `weather_client.py`)
- **Alert latency**: Alerts are typically published within 1–2 minutes of issuance

Official docs: https://www.weather.gov/documentation/services-web-api

---

## Extending the Agent

### Add a new monitored location

```python
from core.config import config
config.default_locations.append((47.6062, -122.3321, "Seattle WA"))
```

### Add a custom alert callback (e.g. SMS or webhook)

```python
def send_sms_alert(alert):
    if alert.severity == AlertSeverity.EXTREME:
        sms_client.send(f"🆘 {alert.event}: {alert.area_description}")

scheduler = WeatherScheduler(state, locations, on_new_alert=send_sms_alert)
```

### Query the agent programmatically

```python
from core.agent import WeatherForecastAgent

agent = WeatherForecastAgent()
response = agent.chat("What's the flood risk in Houston this week?")
print(response)
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## License

This project is for educational purposes. Weather data is provided by the
**National Weather Service (NOAA)** — a US government agency providing free,
authoritative weather information to protect life and property.
