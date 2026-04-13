"""
WeatherGuard — Streamlit Web UI
================================
Run:  streamlit run app.py
"""

import time
from datetime import datetime, timedelta

import streamlit as st

st.set_page_config(
    page_title="WeatherGuard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Core imports ──────────────────────────────────────────────────────────
from core.agent import WeatherForecastAgent
from core.config import config
from core.models import (
    AgentState, AlertCertainty, AlertSeverity, AlertUrgency,
    GeoPoint, HazardCategory, SafetyGuideline, WeatherAlert, WeatherForecast,
)
from core.safety_advisor import SafetyAdvisor
from core.scheduler import WeatherScheduler
import pandas as pd

# ── Global CSS ────────────────────────────────────────────────────────────
st.markdown("""<style>
  .block-container { padding-top: 1.5rem !important; }
  [data-testid="stMetricLabel"] { font-size: 0.72rem !important; }
  footer, #MainMenu { visibility: hidden; }
</style>""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────
SEVERITY_META = {
    AlertSeverity.EXTREME:  {"bg":"#450a0a","border":"#ef4444","text":"#fca5a5","badge":"🔴 EXTREME"},
    AlertSeverity.SEVERE:   {"bg":"#431407","border":"#f97316","text":"#fdba74","badge":"🟠 SEVERE"},
    AlertSeverity.MODERATE: {"bg":"#172554","border":"#3b82f6","text":"#93c5fd","badge":"🔵 MODERATE"},
    AlertSeverity.MINOR:    {"bg":"#052e16","border":"#22c55e","text":"#86efac","badge":"🟢 MINOR"},
    AlertSeverity.UNKNOWN:  {"bg":"#1e293b","border":"#94a3b8","text":"#cbd5e1","badge":"⚪ UNKNOWN"},
}
WEATHER_ICONS = {
    "sunny":"☀️","clear":"☀️","mostly sunny":"🌤️","mostly clear":"🌤️",
    "partly cloudy":"⛅","partly sunny":"⛅","mostly cloudy":"🌥️",
    "cloudy":"☁️","overcast":"☁️","rain":"🌧️","showers":"🌦️",
    "drizzle":"🌦️","thunder":"⛈️","lightning":"⛈️","snow":"❄️",
    "blizzard":"🌨️","sleet":"🌨️","ice":"🧊","fog":"🌫️","haze":"🌫️","wind":"💨",
}
HAZARD_LABELS = {
    HazardCategory.TORNADO:"🌪️ Tornado", HazardCategory.HURRICANE:"🌀 Hurricane",
    HazardCategory.FLOOD:"🌊 Flood", HazardCategory.WINTER_STORM:"❄️ Winter Storm",
    HazardCategory.HEAT_WAVE:"🌡️ Heat Wave", HazardCategory.THUNDERSTORM:"⛈️ Thunderstorm",
    HazardCategory.WILDFIRE:"🔥 Wildfire", HazardCategory.EXTREME_COLD:"🥶 Extreme Cold",
    HazardCategory.HIGH_WIND:"💨 High Wind", HazardCategory.FOG:"🌫️ Dense Fog",
}

# ── Helpers ───────────────────────────────────────────────────────────────
def wx_icon(text):
    t = text.lower()
    for kw, icon in WEATHER_ICONS.items():
        if kw in t:
            return icon
    return "🌡️"

def temp_color(f):
    if f >= 95: return "#ef4444"
    if f >= 80: return "#f97316"
    if f >= 60: return "#4ade80"
    if f >= 40: return "#60a5fa"
    return "#c084fc"

def card(html, border="#334155"):
    st.markdown(
        f'<div style="background:#1e293b;border:1px solid {border};border-radius:12px;'
        f'padding:16px 12px;text-align:center;line-height:1.5">{html}</div>',
        unsafe_allow_html=True,
    )

def _build_locations():
    return [GeoPoint(latitude=lat, longitude=lon, location_name=name)
            for lat, lon, name in config.default_locations]

# ── Bootstrap session ─────────────────────────────────────────────────────
if "bootstrapped" not in st.session_state:
    _state = AgentState()
    _locs  = _build_locations()
    _sched = WeatherScheduler(_state, _locs, config)
    with st.spinner("🌐 Connecting to weather.gov — fetching initial data…"):
        _sched.run_once()
    _sched.start()
    st.session_state.bootstrapped  = True
    st.session_state.scheduler     = _sched
    st.session_state.locations     = _locs
    st.session_state.agent         = WeatherForecastAgent(config, _state)
    st.session_state.chat_history  = []
    st.session_state.safety_result = None

scheduler = st.session_state.scheduler
agent     = st.session_state.agent
state     = scheduler.state

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌤️ WeatherGuard")
    st.caption("weather.gov · GPT-4o · Live data")
    st.divider()
    alert_count = len(state.active_alerts)
    if state.has_extreme_alerts:
        st.error(f"🔴 {alert_count} SEVERE ALERT(S) ACTIVE")
    elif alert_count:
        st.warning(f"🟠 {alert_count} Active Alert(s)")
    else:
        st.success("🟢 All Clear — No Active Alerts")
    if state.last_data_fetch:
        st.caption(f"Last update: {state.last_data_fetch.strftime('%H:%M:%S UTC')}")
    st.divider()
    location_names = [loc.location_name for loc in st.session_state.locations]
    selected_city  = st.selectbox("📍 Select City", location_names)
    st.divider()
    if st.button("🔄 Refresh Now", use_container_width=True, type="primary"):
        with st.spinner("Fetching…"):
            scheduler.run_once()
        st.rerun()
    auto_refresh = st.checkbox("⏱ Auto-refresh every 60 s", value=False)
    st.divider()
    st.caption(f"Monitoring **{len(st.session_state.locations)}** cities")
    st.caption("Alerts every **5 min** · Forecasts every **30 min**")

# ── Header ────────────────────────────────────────────────────────────────
col_t, col_s = st.columns([4, 1])
with col_t:
    st.markdown("# 🌤️ WeatherGuard")
    st.caption("Real-time weather monitoring & AI-powered public safety guidelines")
with col_s:
    st.metric("Monitored Cities", len(st.session_state.locations))
    st.metric("Active Alerts", alert_count)
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────
alert_label = f"🚨 Alerts ({alert_count})" if alert_count else "🚨 Alerts"
tab_fc, tab_al, tab_chat, tab_safety = st.tabs(
    ["🌤️ Forecast", alert_label, "💬 Chat", "🛡️ Safety"]
)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — FORECAST
# ════════════════════════════════════════════════════════════════════════════

def _city_alerts(city_name, fcast, all_alerts):
    """Return alerts whose area_description matches the selected city."""
    terms = {w.lower() for w in city_name.replace(",", " ").split() if len(w) > 2}
    if fcast and fcast.grid_point.city:
        terms.add(fcast.grid_point.city.lower())
    if fcast and fcast.grid_point.state:
        terms.add(fcast.grid_point.state.lower())
    return sorted(
        [a for a in all_alerts if any(t in a.area_description.lower() for t in terms)],
        key=lambda a: list(AlertSeverity).index(a.severity),
    )

with tab_fc:
    forecast = state.latest_forecasts.get(f"{selected_city}_7-day") or state.latest_forecasts.get(selected_city)
    if forecast is None:
        st.info(f"⏳ No forecast for **{selected_city}** yet. Click **Refresh Now**.")
    else:
        grid = forecast.grid_point
        sub  = f"{grid.city}, {grid.state}" if grid.city and grid.state else ""

        # ── City header ────────────────────────────────────────────────────
        h_left, h_right = st.columns([3, 1])
        with h_left:
            st.markdown(
                f"### 📍 {selected_city}"
                + (f" <span style='color:#64748b;font-size:0.85em'>— {sub}</span>" if sub else ""),
                unsafe_allow_html=True,
            )
            st.caption(f"NWS Office: **{grid.office}** &nbsp;·&nbsp; Updated: {forecast.update_time.strftime('%b %d, %H:%M UTC')}")
        with h_right:
            local_alerts = _city_alerts(selected_city, forecast, state.active_alerts)
            if local_alerts:
                worst = local_alerts[0]
                m = SEVERITY_META.get(worst.severity, SEVERITY_META[AlertSeverity.UNKNOWN])
                st.markdown(
                    f'<div style="background:{m["bg"]};border:1px solid {m["border"]};'
                    f'border-radius:8px;padding:8px 12px;text-align:center">'
                    f'<span style="font-weight:700;color:{m["text"]}">{m["badge"]}</span><br/>'
                    f'<span style="font-size:0.78rem;color:{m["text"]}">{len(local_alerts)} alert(s)</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="background:#052e16;border:1px solid #22c55e;border-radius:8px;'
                    'padding:8px 12px;text-align:center">'
                    '<span style="color:#86efac;font-weight:700">🟢 All Clear</span><br/>'
                    '<span style="font-size:0.78rem;color:#86efac">No active alerts</span></div>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # ── Active alerts for this city ────────────────────────────────────
        if local_alerts:
            st.markdown("#### 🚨 Active Alerts for This Location")
            for alert in local_alerts:
                m = SEVERITY_META.get(alert.severity, SEVERITY_META[AlertSeverity.UNKNOWN])
                st.markdown(
                    f'<div style="background:{m["bg"]};border-left:5px solid {m["border"]};'
                    f'border-radius:8px;padding:12px 16px;margin:6px 0;line-height:1.6">'
                    f'<span style="font-weight:700;color:{m["text"]};font-size:0.95rem">'
                    f'{m["badge"]} — {alert.event}</span><br/>'
                    f'<span style="color:#94a3b8;font-size:0.82rem">'
                    f'📍 {alert.area_description[:120]}{"…" if len(alert.area_description) > 120 else ""}'
                    f'&nbsp;·&nbsp; ⏰ Expires {alert.expires.strftime("%b %d, %H:%M UTC")}'
                    f'</span></div>',
                    unsafe_allow_html=True,
                )
                hl = alert.headline[:100] + "…" if len(alert.headline) > 100 else alert.headline
                with st.expander(f"📄 {hl}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Urgency",   alert.urgency.value)
                    c2.metric("Certainty", alert.certainty.value)
                    c3.metric("Expires",   alert.expires.strftime("%b %d, %H:%M UTC"))
                    st.markdown("---")
                    st.markdown(alert.description)
                    if alert.instruction:
                        st.warning(f"📢 **NWS Instructions:** {alert.instruction}")
            st.divider()

        # ── Current conditions ──────────────────────────────────────────────
        if forecast.periods:
            cur    = forecast.periods[0]
            precip = cur.probability_of_precipitation or 0
            st.markdown("#### 🌡️ Current Conditions")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                card(
                    f'<div style="font-size:2.8rem">{wx_icon(cur.short_forecast)}</div>'
                    f'<div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase;margin-top:6px">{cur.name}</div>'
                    f'<div style="font-size:0.85rem;color:#cbd5e1;margin-top:4px">{cur.short_forecast}</div>'
                )
            with c2:
                tc = temp_color(cur.temperature)
                card(
                    f'<div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase">Temperature</div>'
                    f'<div style="font-size:2.4rem;font-weight:700;color:{tc};margin-top:6px">{cur.temperature}°F</div>',
                    border=tc,
                )
            with c3:
                card(
                    f'<div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase">Wind</div>'
                    f'<div style="font-size:1.3rem;font-weight:600;color:#e2e8f0;margin-top:6px">{cur.wind_speed}</div>'
                    f'<div style="font-size:0.82rem;color:#94a3b8;margin-top:4px">from {cur.wind_direction}</div>'
                )
            with c4:
                pc = "#60a5fa" if precip >= 50 else "#94a3b8"
                card(
                    f'<div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase">Precip. Chance</div>'
                    f'<div style="font-size:2.4rem;font-weight:700;color:{pc};margin-top:6px">{precip}%</div>',
                    border=pc,
                )
            # Detailed description of current period
            st.markdown(
                f'<div style="background:#1e293b;border-left:3px solid #334155;border-radius:6px;'
                f'padding:10px 14px;margin-top:10px;color:#94a3b8;font-size:0.85rem">'
                f'📋 {cur.detailed_forecast}</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── 7-Day Forecast (day + night rows) ──────────────────────────────
        st.markdown("#### 📅 7-Day Forecast")
        periods = forecast.periods

        # Pair day + night together
        day_pairs: list[tuple] = []
        i = 0
        while i < len(periods) and len(day_pairs) < 7:
            dp = periods[i]
            np_ = periods[i + 1] if i + 1 < len(periods) else None
            # If first period is nighttime, show it alone then pair from next
            if not dp.is_daytime and len(day_pairs) == 0:
                day_pairs.append((None, dp))
                i += 1
            else:
                day_pairs.append((dp, np_))
                i += 2

        for day_p, night_p in day_pairs:
            ref     = day_p if day_p else night_p
            tc_day  = temp_color(ref.temperature)
            p_day   = ref.probability_of_precipitation or 0

            # Temperature display
            if day_p and night_p:
                tc_night = temp_color(night_p.temperature)
                temp_html = (
                    f'<span style="font-size:1.3rem;font-weight:700;color:{tc_day}">{day_p.temperature}°F</span>'
                    f'<span style="color:#475569;font-size:1rem"> / </span>'
                    f'<span style="font-size:1.1rem;font-weight:600;color:{tc_night}">{night_p.temperature}°F</span>'
                )
                night_html = (
                    f'🌙 <em style="color:#7c93b0">{night_p.short_forecast}</em>'
                    f' &nbsp;·&nbsp; 💧 {night_p.probability_of_precipitation or 0}%'
                    f' &nbsp;·&nbsp; 💨 {night_p.wind_speed} {night_p.wind_direction}'
                )
            elif day_p:
                temp_html  = f'<span style="font-size:1.3rem;font-weight:700;color:{tc_day}">{day_p.temperature}°F</span>'
                night_html = ""
            else:
                temp_html  = f'<span style="font-size:1.3rem;font-weight:700;color:{tc_day}">{night_p.temperature}°F</span>'
                night_html = ""

            date_str = ref.start_time.strftime("%b %d")
            detail   = ref.detailed_forecast
            if len(detail) > 160:
                detail = detail[:157] + "…"

            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #334155;border-radius:12px;'
                f'padding:14px 18px;margin:6px 0">'
                # Row 1: day label | icon | temps | wind | precip | short desc
                f'<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">'
                f'  <div style="min-width:120px">'
                f'    <div style="font-weight:700;color:#e2e8f0;font-size:0.95rem">{ref.name}</div>'
                f'    <div style="color:#475569;font-size:0.74rem">{date_str}</div>'
                f'  </div>'
                f'  <div style="font-size:2.2rem;min-width:44px;text-align:center">{wx_icon(ref.short_forecast)}</div>'
                f'  <div style="min-width:120px">{temp_html}</div>'
                f'  <div style="min-width:130px;color:#94a3b8;font-size:0.82rem">💨 {ref.wind_speed} {ref.wind_direction}</div>'
                f'  <div style="min-width:60px;text-align:center">'
                f'    <span style="color:{"#60a5fa" if p_day >= 50 else "#94a3b8"};font-size:0.85rem">💧 {p_day}%</span>'
                f'  </div>'
                f'  <div style="flex:1;color:#cbd5e1;font-size:0.85rem">{ref.short_forecast}</div>'
                f'</div>'
                # Row 2: detailed forecast + night summary
                + (f'<div style="margin-top:8px;padding-top:8px;border-top:1px solid #334155">'
                   f'  <div style="color:#64748b;font-size:0.8rem">{detail}</div>'
                   + (f'  <div style="color:#475569;font-size:0.78rem;margin-top:4px">{night_html}</div>' if night_html else "")
                   + '</div>'
                   )
                + '</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Full data table ─────────────────────────────────────────────────
        with st.expander("📋 Full Forecast Table (all periods)"):
            rows = [
                {
                    "Period":   p.name,
                    "Day?":     "☀️" if p.is_daytime else "🌙",
                    "Temp °F":  p.temperature,
                    "Wind":     f"{p.wind_speed} {p.wind_direction}",
                    "Precip %": f"{p.probability_of_precipitation or 0}%",
                    "Humidity": f"{p.relative_humidity or '—'}%",
                    "Summary":  p.short_forecast,
                }
                for p in forecast.periods
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — ALERTS
# ════════════════════════════════════════════════════════════════════════════
with tab_al:
    if not state.active_alerts:
        st.success("✅ **No active weather alerts** across all monitored cities right now.")
        st.markdown("> Polling weather.gov every **5 minutes** for new advisories, watches, warnings, and emergency alerts.")
    else:
        sorted_alerts = sorted(state.active_alerts, key=lambda a: list(AlertSeverity).index(a.severity))
        st.markdown(f"### {len(sorted_alerts)} Active Alert(s)")
        st.caption("Sorted by severity — most critical first")
        for alert in sorted_alerts:
            m = SEVERITY_META.get(alert.severity, SEVERITY_META[AlertSeverity.UNKNOWN])
            st.markdown(
                f'<div style="background:{m["bg"]};border-left:5px solid {m["border"]};'
                f'border-radius:8px;padding:14px 18px;margin:8px 0;line-height:1.6">'
                f'<span style="font-weight:700;color:{m["text"]};font-size:1rem">{m["badge"]} — {alert.event}</span><br/>'
                f'<span style="color:#94a3b8;font-size:0.85rem">{alert.area_description}</span></div>',
                unsafe_allow_html=True,
            )
            headline = alert.headline[:90] + "…" if len(alert.headline) > 90 else alert.headline
            with st.expander(f"📄 {headline}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Urgency",   alert.urgency.value)
                c2.metric("Certainty", alert.certainty.value)
                c3.metric("Expires",   alert.expires.strftime("%b %d, %H:%M UTC"))
                st.markdown("---")
                st.markdown(alert.description)
                if alert.instruction:
                    st.warning(f"📢 **NWS Instructions:** {alert.instruction}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHAT
# ════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("### 💬 Chat with WeatherGuard")
    st.caption("Ask about forecasts, alerts, safety, or anything weather-related. Uses live weather.gov data.")
    with st.expander("💡 Example questions", expanded=False):
        st.markdown("""
- What's the weather in Chicago this week?
- Are there tornado warnings near Kansas?
- Is it safe to drive in New York today?
- What should I do during a flood?
- Compare Houston vs Phoenix weather tomorrow.
        """)
    st.divider()
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🌤️" if msg["role"] == "assistant" else "🧑"):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Ask about weather, alerts, or safety…"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🌤️"):
            with st.spinner("Thinking…"):
                response = agent.chat(prompt)
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.chat_history = []
            agent.clear_history()
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — SAFETY
# ════════════════════════════════════════════════════════════════════════════
with tab_safety:
    st.markdown("### 🛡️ Safety Guidelines")
    st.markdown("Select a hazard to generate AI-powered safety guidelines — immediate actions, prep tips, and emergency contacts.")
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        hazard_choice = st.selectbox(
            "Hazard:", options=list(HAZARD_LABELS.keys()),
            format_func=lambda h: HAZARD_LABELS[h],
            label_visibility="collapsed",
        )
    with col_btn:
        generate = st.button("🛡️ Generate", type="primary", use_container_width=True)

    if generate:
        fake_alert = WeatherAlert(
            alert_id=f"ui-{hazard_choice.value}",
            headline=f"{HAZARD_LABELS[hazard_choice]} Safety Guidelines",
            event=hazard_choice.value.replace("_", " ").title(),
            severity=AlertSeverity.SEVERE, urgency=AlertUrgency.EXPECTED,
            certainty=AlertCertainty.LIKELY, area_description="User-selected hazard",
            sent=datetime.utcnow(), effective=datetime.utcnow(),
            expires=datetime.utcnow() + timedelta(hours=12),
            description=f"User-requested {hazard_choice.value} safety information.",
        )
        with st.spinner(f"Generating {HAZARD_LABELS[hazard_choice]} guidelines…"):
            st.session_state.safety_result = SafetyAdvisor(config).generate_guideline(fake_alert)

    if st.session_state.safety_result:
        g = st.session_state.safety_result
        st.divider()
        st.markdown(f"## {g.headline}")
        st.info(g.summary)
        left, right = st.columns(2)
        with left:
            st.markdown("#### ⚡ Immediate Actions")
            for a in sorted(g.immediate_actions, key=lambda x: x.priority):
                st.markdown(
                    f'<div style="background:#1e3a5f;border-radius:8px;padding:10px 14px;'
                    f'margin:4px 0;border-left:3px solid #3b82f6">'
                    f'<strong style="color:#93c5fd">{a.emoji} {a.priority}.</strong>'
                    f' <span style="color:#e2e8f0">{a.action}</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("#### 📋 Preparedness Tips")
            for tip in g.preparedness_tips:
                st.markdown(f"- {tip}")
        with right:
            st.markdown("#### 🔄 After the Event")
            for tip in g.after_event_tips:
                st.markdown(f"- {tip}")
            st.markdown("#### ⚠️ Vulnerable Populations")
            for group in g.vulnerable_populations:
                st.markdown(f"- {group}")
            st.markdown("#### 📞 Emergency Contacts")
            for contact in g.emergency_contacts:
                st.markdown(
                    f'<div style="background:#1e293b;border:1px solid #334155;'
                    f'border-radius:6px;padding:8px 12px;margin:4px 0;color:#e2e8f0">📞 {contact}</div>',
                    unsafe_allow_html=True,
                )
        st.caption(f"Generated by {g.ai_model_used} · {g.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")

# ── Auto-refresh ──────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(60)
    scheduler.run_once()
    st.rerun()
