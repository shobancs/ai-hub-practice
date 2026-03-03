"""
Weather Forecasting Agent — Entry Point

Initialises all components and launches the CLI.

Usage:
    python main.py              # Interactive menu (default)
    python main.py --chat       # Jump straight to chat mode
    python main.py --alerts     # Show current alerts and exit
    python main.py --forecast   # Show forecasts and exit
    python main.py --safety tornado   # Show tornado safety guidelines
    python main.py --location "Seattle WA" --lat 47.6062 --lon -122.3321
"""

import argparse
import logging
import signal
import sys

from rich.console import Console
from rich.panel import Panel

from core.agent import WeatherForecastAgent
from core.config import config
from core.models import AgentState, GeoPoint
from core.scheduler import WeatherScheduler
from interfaces.cli import WeatherCLI

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s  [%(levelname)-8s]  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Suppress noisy third-party logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger  = logging.getLogger(__name__)
console = Console()


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def build_locations(args: argparse.Namespace) -> list[GeoPoint]:
    """
    Build the list of monitored locations from CLI args + config defaults.
    """
    locations: list[GeoPoint] = []

    # Add extra location from CLI flags
    if args.lat and args.lon:
        name = args.location or f"{args.lat},{args.lon}"
        locations.append(GeoPoint(
            latitude=float(args.lat),
            longitude=float(args.lon),
            location_name=name,
        ))

    # Add all configured default locations
    for lat, lon, name in config.default_locations:
        locations.append(GeoPoint(latitude=lat, longitude=lon, location_name=name))

    return locations


def bootstrap(args: argparse.Namespace) -> tuple[WeatherForecastAgent, WeatherScheduler]:
    """
    Initialise all components, validate config, run initial data fetch,
    and start the background scheduler.

    Returns:
        (agent, scheduler) tuple ready to use.
    """
    # Validate configuration
    warnings = config.validate()
    for warning in warnings:
        console.print(f"[yellow]⚠️  Config warning: {warning}[/yellow]")

    # Build shared state
    state = AgentState()

    # Build location list
    locations = build_locations(args)
    if not locations:
        console.print("[red]No locations configured. Use --lat/--lon or set WEATHER_LOCATIONS.[/red]")
        sys.exit(1)

    # New alert callback — prints a prominent banner in the terminal
    def on_new_alert(alert):
        console.print(
            Panel(
                f"[bold]{alert.event}[/bold]\n"
                f"Area: {alert.area_description}\n"
                f"Severity: {alert.severity.value}  |  "
                f"Expires: {alert.expires.strftime('%b %d %H:%M UTC')}",
                title=f"[bold red]🚨 NEW ALERT: {alert.severity.value.upper()}[/bold red]",
                border_style="red",
            )
        )

    # Initialise scheduler
    scheduler = WeatherScheduler(
        state=state,
        locations=locations,
        cfg=config,
        on_new_alert=on_new_alert,
    )

    # Initialise agent with the same shared state
    agent = WeatherForecastAgent(cfg=config, state=state)
    agent.state.locations = locations

    # Initial data fetch (blocking — shows progress)
    console.print("[cyan]🌐 Fetching initial data from weather.gov...[/cyan]")
    summary = scheduler.run_once()
    console.print(
        f"[green]✅ Ready — {summary['alerts_fetched']} alert(s), "
        f"{summary['forecasts_fetched']} forecast(s) loaded.[/green]"
    )

    # Start background polling threads
    if not args.no_background:
        scheduler.start()
        console.print(
            f"[dim]Background scheduler started "
            f"(alerts every {config.alert_poll_interval}s, "
            f"forecasts every {config.forecast_poll_interval}s)[/dim]"
        )

    return agent, scheduler


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weather_agent",
        description="WeatherGuard — AI Weather Forecasting & Safety Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Interactive menu
  python main.py --chat                       # Jump to chat mode
  python main.py --alerts                     # Show active alerts and quit
  python main.py --forecast                   # Show forecasts and quit
  python main.py --safety tornado             # Tornado safety guidelines
  python main.py --lat 47.61 --lon -122.33 --location "Seattle WA"
""",
    )

    # Mode flags
    mode = parser.add_argument_group("Modes (default: interactive menu)")
    mode.add_argument("--chat",     action="store_true", help="Start in chat mode")
    mode.add_argument("--alerts",   action="store_true", help="Show active alerts and exit")
    mode.add_argument("--forecast", action="store_true", help="Show forecasts and exit")
    mode.add_argument("--safety",   metavar="HAZARD",
                      help="Show safety guidelines for hazard type and exit "
                           "(e.g. tornado, flood, heat_wave)")
    mode.add_argument("--dashboard", action="store_true", help="Launch live dashboard")

    # Location override
    loc = parser.add_argument_group("Location override")
    loc.add_argument("--lat",      type=float, help="Latitude")
    loc.add_argument("--lon",      type=float, help="Longitude")
    loc.add_argument("--location", type=str,   help="Human-readable location name")

    # Behaviour flags
    flags = parser.add_argument_group("Behaviour")
    flags.add_argument("--no-background", action="store_true",
                       help="Disable background polling (run once only)")
    flags.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Bootstrap
    agent, scheduler = bootstrap(args)
    cli = WeatherCLI(agent=agent, scheduler=scheduler)

    # Graceful shutdown on Ctrl+C / SIGTERM
    def shutdown(sig, frame):
        console.print("\n[dim]Shutting down WeatherGuard...[/dim]")
        scheduler.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT,  shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # --- Dispatch to the requested mode ---

    if args.alerts:
        cli.show_alerts()
        scheduler.stop()
        return

    if args.forecast:
        cli.show_forecasts()
        scheduler.stop()
        return

    if args.safety:
        response = agent.chat(
            f"Provide complete public safety guidelines for {args.safety.replace('_', ' ')}."
        )
        console.print(Panel(
            response,
            title=f"🛡️ Safety Guidelines — {args.safety.replace('_', ' ').title()}",
            border_style="red",
        ))
        scheduler.stop()
        return

    if args.dashboard:
        cli.show_dashboard()
        scheduler.stop()
        return

    if args.chat:
        cli.start_chat()
        scheduler.stop()
        return

    # Default: interactive menu
    try:
        cli.run()
    finally:
        scheduler.stop()


if __name__ == "__main__":
    main()
