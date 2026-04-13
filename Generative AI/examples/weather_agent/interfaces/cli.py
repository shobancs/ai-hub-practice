"""
Rich-powered CLI interface for the Weather Forecasting Agent.

Features:
  • Live dashboard showing current conditions, alerts, and safety guidelines
  • Interactive chat mode for asking weather questions
  • Severity-colour coded alert banners
  • Auto-refreshing display via Rich Live
"""

import logging
import signal
import sys
import time
from datetime import datetime

from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich import box

from core.agent import WeatherForecastAgent
from core.config import WeatherAgentConfig
from core.models import (
    AgentState,
    AlertSeverity,
    GeoPoint,
    SafetyGuideline,
    WeatherAlert,
    WeatherForecast,
)
from core.scheduler import WeatherScheduler

console = Console()
logger  = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Colour palette per severity
# ---------------------------------------------------------------------------

SEVERITY_STYLE: dict[AlertSeverity, str] = {
    AlertSeverity.EXTREME:  "bold white on red",
    AlertSeverity.SEVERE:   "bold black on yellow",
    AlertSeverity.MODERATE: "bold white on dark_orange",
    AlertSeverity.MINOR:    "bold white on blue",
    AlertSeverity.UNKNOWN:  "dim",
}

SEVERITY_EMOJI: dict[AlertSeverity, str] = {
    AlertSeverity.EXTREME:  "🆘",
    AlertSeverity.SEVERE:   "🚨",
    AlertSeverity.MODERATE: "⚠️",
    AlertSeverity.MINOR:    "ℹ️",
    AlertSeverity.UNKNOWN:  "❓",
}


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def render_alert_banner(alert: WeatherAlert) -> Panel:
    """Render a single weather alert as a rich Panel."""
    style = SEVERITY_STYLE.get(alert.severity, "")
    emoji = SEVERITY_EMOJI.get(alert.severity, "⚠️")

    content = Text()
    content.append(f"{emoji}  {alert.event}\n", style="bold")
    content.append(f"Area:     {alert.area_description}\n")
    content.append(f"Severity: {alert.severity.value}  |  Urgency: {alert.urgency.value}\n")
    content.append(
        f"Effective: {alert.effective.strftime('%b %d %H:%M UTC')}  →  "
        f"Expires: {alert.expires.strftime('%b %d %H:%M UTC')}\n"
    )
    if alert.instruction:
        content.append(f"\nOfficial NWS Instructions:\n{alert.instruction[:400]}", style="italic")

    return Panel(
        content,
        title=f"[bold]{alert.headline[:80]}[/bold]",
        border_style=style.split(" ")[-1] if style else "yellow",
        padding=(0, 1),
    )


def render_forecast_table(forecast: WeatherForecast, max_periods: int = 6) -> Table:
    """Render a forecast as a rich Table."""
    table = Table(
        title=f"📍 {forecast.location.location_name}  "
              f"({forecast.grid_point.city}, {forecast.grid_point.state})",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Period",     style="bold", width=16)
    table.add_column("Temp",       justify="center", width=8)
    table.add_column("Wind",       width=18)
    table.add_column("Precip %",   justify="center", width=8)
    table.add_column("Forecast",   width=40)

    for period in forecast.periods[:max_periods]:
        temp_str = f"{period.temperature}°{period.temperature_unit}"
        temp_style = (
            "red bold"   if period.temperature >= 95 else
            "yellow"     if period.temperature >= 80 else
            "cyan"       if period.temperature <= 32 else
            "green"
        )
        pop = (
            f"{period.probability_of_precipitation}%"
            if period.probability_of_precipitation is not None
            else "—"
        )
        table.add_row(
            period.name,
            Text(temp_str, style=temp_style),
            f"{period.wind_speed} {period.wind_direction}",
            pop,
            period.short_forecast,
        )

    return table


def render_safety_guideline(guideline: SafetyGuideline) -> Panel:
    """Render a safety guideline as a detailed rich Panel."""
    body = Text()

    body.append("📋 SITUATION\n", style="bold yellow")
    body.append(f"{guideline.summary}\n\n")

    body.append("🚨 IMMEDIATE ACTIONS\n", style="bold red")
    for action in sorted(guideline.immediate_actions, key=lambda a: a.priority):
        body.append(f"  {action.emoji}  {action.priority}. {action.action}\n")

    if guideline.preparedness_tips:
        body.append("\n📦 HOW TO PREPARE\n", style="bold blue")
        for tip in guideline.preparedness_tips:
            body.append(f"  • {tip}\n")

    if guideline.after_event_tips:
        body.append("\n🔄 AFTER THE EVENT\n", style="bold green")
        for tip in guideline.after_event_tips:
            body.append(f"  • {tip}\n")

    if guideline.vulnerable_populations:
        body.append("\n👥 VULNERABLE GROUPS — EXTRA CARE NEEDED\n", style="bold magenta")
        for group in guideline.vulnerable_populations:
            body.append(f"  ⚠️  {group}\n")

    body.append("\n🆘 EMERGENCY CONTACTS\n", style="bold red")
    for contact in guideline.emergency_contacts:
        body.append(f"  📞 {contact}\n", style="bold")

    body.append(
        f"\n[dim]Generated by {guideline.ai_model_used} at "
        f"{guideline.generated_at.strftime('%Y-%m-%d %H:%M UTC')}[/dim]"
    )

    return Panel(
        body,
        title=f"[bold red]🛡️  SAFETY GUIDELINES — {guideline.headline}[/bold red]",
        border_style="red",
        padding=(1, 2),
    )


def render_status_bar(state: AgentState) -> Text:
    """Render a one-line status bar."""
    status = Text()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    status.append(f"🕐 {now}  ", style="dim")

    alert_count = len(state.active_alerts)
    if state.has_extreme_alerts:
        status.append(f"🆘 {alert_count} EXTREME/SEVERE ALERT(S) ACTIVE", style="bold red blink")
    elif alert_count > 0:
        status.append(f"⚠️  {alert_count} alert(s) active", style="yellow")
    else:
        status.append("✅ No active alerts", style="green")

    status.append(f"  |  Locations monitored: {len(state.locations)}", style="dim")
    status.append(f"  |  Total fetches: {state.total_fetches}", style="dim")

    if state.last_alert_check:
        elapsed = int((datetime.utcnow() - state.last_alert_check.replace(tzinfo=None)).total_seconds())
        status.append(f"  |  Last alert check: {elapsed}s ago", style="dim")

    return status


# ---------------------------------------------------------------------------
# Main CLI Views
# ---------------------------------------------------------------------------

class WeatherCLI:
    """Interactive CLI controller."""

    def __init__(self, agent: WeatherForecastAgent, scheduler: WeatherScheduler):
        self.agent     = agent
        self.scheduler = scheduler
        self.state     = agent.state

    # ---- Dashboard -------------------------------------------------------

    def show_dashboard(self, refresh_seconds: int = 30) -> None:
        """
        Display a live auto-refreshing dashboard.
        Press Ctrl+C to exit.
        """
        console.print(
            Panel(
                "[bold cyan]WeatherGuard Dashboard[/bold cyan]\n"
                "[dim]Press Ctrl+C to return to the menu[/dim]",
                border_style="cyan",
            )
        )
        time.sleep(1)

        try:
            with Live(console=console, refresh_per_second=1) as live:
                while True:
                    layout = self._build_dashboard_layout()
                    live.update(layout)
                    time.sleep(refresh_seconds)
        except KeyboardInterrupt:
            console.print("\n[dim]Dashboard closed.[/dim]")

    def _build_dashboard_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="status",    size=3),
            Layout(name="main",      ratio=1),
            Layout(name="footer",    size=3),
        )
        layout["main"].split_row(
            Layout(name="alerts",    ratio=1),
            Layout(name="forecasts", ratio=2),
        )

        # Status bar
        layout["status"].update(
            Panel(render_status_bar(self.state), border_style="dim")
        )

        # Active alerts
        if self.state.active_alerts:
            alert_panels = [
                render_alert_banner(a)
                for a in self.state.active_alerts[:4]
            ]
            layout["alerts"].update(
                Panel(
                    Columns(alert_panels, equal=True, expand=True),
                    title="🚨 Active Alerts",
                    border_style="red",
                )
            )
        else:
            layout["alerts"].update(
                Panel(
                    "[green]✅ No active weather alerts.[/green]",
                    title="🚨 Active Alerts",
                    border_style="green",
                )
            )

        # Forecasts
        forecast_tables = []
        for key, forecast in list(self.state.latest_forecasts.items())[:2]:
            if "_7-day" in key or "hourly" not in key:
                forecast_tables.append(render_forecast_table(forecast))

        if forecast_tables:
            layout["forecasts"].update(
                Panel(
                    Columns(forecast_tables, equal=True, expand=True),
                    title="📅 Weather Forecasts",
                    border_style="cyan",
                )
            )
        else:
            layout["forecasts"].update(
                Panel(
                    "[dim]Forecasts loading... (first fetch may take ~10 seconds)[/dim]",
                    title="📅 Weather Forecasts",
                    border_style="dim",
                )
            )

        # Footer
        layout["footer"].update(
            Panel(
                "[dim]Data source: National Weather Service (weather.gov) — "
                "Refresh every 30s  |  Alert checks every 5 min[/dim]",
                border_style="dim",
            )
        )

        return layout

    # ---- Alerts view -----------------------------------------------------

    def show_alerts(self) -> None:
        """Display all currently active alerts with safety guidelines."""
        if not self.state.active_alerts:
            console.print(Panel(
                "[green bold]✅ No active weather alerts at this time.[/green bold]\n"
                "[dim]The agent continuously monitors weather.gov for new alerts.[/dim]",
                title="Active Alerts",
                border_style="green",
            ))
            return

        console.print(Rule(f"[red bold]🚨 {len(self.state.active_alerts)} Active Alert(s)[/red bold]"))
        for alert in self.state.active_alerts:
            console.print(render_alert_banner(alert))

            # Show safety guideline if one was auto-generated
            guideline = next(
                (g for g in self.state.safety_guidelines if g.alert_id == alert.alert_id),
                None,
            )
            if guideline:
                console.print(render_safety_guideline(guideline))

            console.print()

    # ---- Forecasts view --------------------------------------------------

    def show_forecasts(self) -> None:
        """Display all cached forecasts."""
        seven_day = {
            k: v for k, v in self.state.latest_forecasts.items()
            if "hourly" not in k
        }
        if not seven_day:
            console.print("[dim]No forecasts cached yet — run a data fetch first.[/dim]")
            return

        for key, forecast in seven_day.items():
            console.print(render_forecast_table(forecast, max_periods=8))
            console.print()

    # ---- Safety guidelines view -----------------------------------------

    def show_safety_menu(self) -> None:
        """Interactive menu for browsing safety guidelines."""
        options = [
            ("1", "Tornado"),
            ("2", "Flood"),
            ("3", "Hurricane"),
            ("4", "Extreme Heat"),
            ("5", "Winter Storm"),
            ("6", "Thunderstorm"),
            ("7", "Wildfire"),
            ("8", "Extreme Cold"),
            ("B", "Back to menu"),
        ]

        table = Table(title="🛡️  Public Safety Guidelines", box=box.SIMPLE)
        table.add_column("Key", style="bold cyan", width=4)
        table.add_column("Hazard")
        for key, label in options:
            table.add_row(key, label)
        console.print(table)

        choice = Prompt.ask("Select a hazard type", default="B").upper()

        hazard_map = {
            "1": "tornado",
            "2": "flood",
            "3": "hurricane",
            "4": "heat_wave",
            "5": "winter_storm",
            "6": "thunderstorm",
            "7": "wildfire",
            "8": "extreme_cold",
        }

        if choice in hazard_map:
            hazard = hazard_map[choice]
            response = self.agent.chat(
                f"Show me complete safety guidelines for {hazard.replace('_', ' ')}."
            )
            console.print(Panel(response, title=f"🛡️ {hazard.replace('_', ' ').title()} Safety", border_style="red"))

    # ---- Chat mode -------------------------------------------------------

    def start_chat(self) -> None:
        """Interactive natural-language chat with the agent."""
        console.print(Panel(
            "[bold cyan]💬 WeatherGuard Chat Mode[/bold cyan]\n"
            "[dim]Ask me anything about weather forecasts, alerts, or safety guidelines.\n"
            "Type 'quit' or press Ctrl+C to exit.\n\n"
            "Example questions:\n"
            "  • Are there any tornado warnings in Kansas?\n"
            "  • What's the weather like in Chicago this week?\n"
            "  • What should I do during a flood?\n"
            "  • Is it safe to drive in New York today?[/dim]",
            border_style="cyan",
        ))

        try:
            while True:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "q"):
                    break

                console.print("[dim]Thinking...[/dim]")
                response = self.agent.chat(user_input)
                console.print(Panel(response, title="[bold green]WeatherGuard[/bold green]", border_style="green"))

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Chat ended.[/dim]")

    # ---- Main menu -------------------------------------------------------

    def run(self) -> None:
        """Display the main interactive menu."""
        # Print welcome banner
        console.print(Panel(
            "[bold cyan]🌤️  WeatherGuard — AI Weather Forecasting Agent[/bold cyan]\n"
            "[dim]Powered by National Weather Service (weather.gov) + OpenAI[/dim]\n\n"
            f"[dim]Monitoring {len(self.state.locations)} location(s) | "
            f"Background scheduler {'running ✅' if self.scheduler.is_running else 'stopped ❌'}[/dim]",
            border_style="cyan",
            padding=(1, 4),
        ))

        menu_items = [
            ("1", "Live Dashboard          (auto-refreshes)"),
            ("2", "View Active Alerts       + Safety Guidelines"),
            ("3", "View Weather Forecasts"),
            ("4", "Safety Guidelines Browser"),
            ("5", "💬 Chat with WeatherGuard"),
            ("6", "Refresh Data Now"),
            ("Q", "Quit"),
        ]

        while True:
            console.print(Rule("[cyan]Main Menu[/cyan]"))
            for key, label in menu_items:
                console.print(f"  [bold cyan]{key}[/bold cyan]  {label}")
            console.print()

            choice = Prompt.ask("Choose an option", default="1").upper()

            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.show_alerts()
            elif choice == "3":
                self.show_forecasts()
            elif choice == "4":
                self.show_safety_menu()
            elif choice == "5":
                self.start_chat()
            elif choice == "6":
                with console.status("[bold green]Fetching latest data from weather.gov...[/bold green]"):
                    summary = self.scheduler.run_once()
                console.print(
                    f"[green]✅ Fetched {summary['alerts_fetched']} alert(s) and "
                    f"{summary['forecasts_fetched']} forecast(s)[/green]"
                )
            elif choice in ("Q", "QUIT", "EXIT"):
                console.print("[dim]Shutting down...[/dim]")
                break
            else:
                console.print("[yellow]Invalid option — please try again.[/yellow]")
