"""
CLI interface for the Research Assistant Agent.

Provides an interactive Rich-powered terminal UI with:
  - Research mode (full research cycle on a topic)
  - Chat mode (follow-up questions on the current topic)
  - Notes viewer (see all notes from the session)
  - Session stats
"""

import asyncio
import logging

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from ..core.agent import ResearchAgent
from ..core.config import config

logger = logging.getLogger(__name__)
console = Console()


# ─────────────────────────────────────────────────────────────────────
# Tool-call display icons
# ─────────────────────────────────────────────────────────────────────

TOOL_ICONS = {
    "search_web": "🔍",
    "read_webpage": "📖",
    "save_note": "📝",
    "get_notes": "📋",
    "calculate": "🧮",
}


def _on_tool_call(name: str, args: dict) -> None:
    """Pretty-print each tool call as it happens."""
    icon = TOOL_ICONS.get(name, "🔧")
    detail = ""
    if name == "search_web":
        detail = f'query="{args.get("query", "")}"'
    elif name == "read_webpage":
        detail = f'url="{args.get("url", "")}"'
    elif name == "save_note":
        content = args.get("content", "")
        detail = f'"{content[:50]}..."' if len(content) > 50 else f'"{content}"'
    elif name == "calculate":
        detail = args.get("expression", "")

    console.print(f"  {icon}  [dim]{name}[/dim]  {detail}")


# ─────────────────────────────────────────────────────────────────────
# Interactive menu
# ─────────────────────────────────────────────────────────────────────

async def run_interactive() -> None:
    """Main interactive loop."""
    agent = ResearchAgent()

    console.print(Panel.fit(
        "[bold cyan]🔬 AI Research Assistant Agent[/bold cyan]\n"
        "[dim]Powered by OpenAI function-calling + ReAct pattern[/dim]",
        border_style="cyan",
    ))

    while True:
        console.print()
        console.print("[bold]Choose an option:[/bold]")
        console.print("  [cyan]1[/cyan]  Research a new topic")
        console.print("  [cyan]2[/cyan]  Ask a follow-up question")
        console.print("  [cyan]3[/cyan]  View research notes")
        console.print("  [cyan]4[/cyan]  View session stats")
        console.print("  [cyan]q[/cyan]  Quit")
        console.print()

        choice = console.input("[bold cyan]›[/bold cyan] ").strip().lower()

        if choice == "1":
            await _do_research(agent)
        elif choice == "2":
            await _do_followup(agent)
        elif choice == "3":
            _show_notes(agent)
        elif choice == "4":
            _show_stats(agent)
        elif choice in ("q", "quit", "exit"):
            console.print("[dim]Goodbye! 👋[/dim]")
            break
        else:
            console.print("[red]Invalid choice. Try 1-4 or q.[/red]")


async def _do_research(agent: ResearchAgent) -> None:
    """Run a full research cycle."""
    topic = console.input("\n[bold]Enter research topic:[/bold] ").strip()
    if not topic:
        console.print("[yellow]No topic entered.[/yellow]")
        return

    console.print()
    console.print(Panel(
        f"[bold]Researching:[/bold] {topic}",
        border_style="green",
        subtitle="Agent is working — watch the tool calls below",
    ))
    console.print()

    result = await agent.research(
        query=topic,
        on_tool_call=_on_tool_call,
    )

    console.print()
    console.print(Panel(
        Markdown(result),
        title="[bold green]📄 Research Brief[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))


async def _do_followup(agent: ResearchAgent) -> None:
    """Ask a follow-up question on the current topic."""
    if not agent.session:
        console.print("[yellow]No active research session. Start one first (option 1).[/yellow]")
        return

    console.print(f"\n[dim]Current topic: {agent.session.topic}[/dim]")
    question = console.input("[bold]Follow-up question:[/bold] ").strip()
    if not question:
        return

    with console.status("[bold cyan]Thinking...[/bold cyan]"):
        answer = await agent.ask(question)

    console.print()
    console.print(Panel(
        Markdown(answer),
        title="[bold blue]💬 Answer[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    ))


def _show_notes(agent: ResearchAgent) -> None:
    """Display all research notes in a table."""
    if not agent.session or not agent.session.notes:
        console.print("[yellow]No notes yet. Run a research first (option 1).[/yellow]")
        return

    table = Table(
        title=f"📝 Research Notes — {agent.session.topic}",
        show_lines=True,
    )
    table.add_column("#", style="bold", width=4)
    table.add_column("Note", style="white", max_width=60)
    table.add_column("Tags", style="cyan", max_width=20)
    table.add_column("Source", style="dim", max_width=30)

    for note in agent.session.notes:
        table.add_row(
            str(note.id),
            note.content[:80] + ("..." if len(note.content) > 80 else ""),
            ", ".join(note.tags) if note.tags else "—",
            (note.source[:30] + "...") if note.source and len(note.source) > 30 else (note.source or "—"),
        )

    console.print()
    console.print(table)


def _show_stats(agent: ResearchAgent) -> None:
    """Display session statistics."""
    if not agent.session:
        console.print("[yellow]No active session.[/yellow]")
        return

    s = agent.session
    console.print()
    console.print(Panel(
        f"[bold]Topic:[/bold]         {s.topic}\n"
        f"[bold]Started at:[/bold]    {s.started_at}\n"
        f"[bold]Notes taken:[/bold]   {len(s.notes)}\n"
        f"[bold]Searches:[/bold]      {len(s.searches_performed)}\n"
        f"[bold]Sources read:[/bold]  {len(s.sources_consulted)}\n"
        f"\n[dim]Searches: {', '.join(s.searches_performed) or 'none'}[/dim]\n"
        f"[dim]Sources:  {', '.join(s.sources_consulted) or 'none'}[/dim]",
        title="[bold]📊 Session Stats[/bold]",
        border_style="magenta",
    ))


# ─────────────────────────────────────────────────────────────────────
# Direct research mode (for --research flag)
# ─────────────────────────────────────────────────────────────────────

async def run_direct_research(topic: str) -> None:
    """Run research on a topic and print the result."""
    agent = ResearchAgent()

    console.print(Panel(
        f"[bold]Researching:[/bold] {topic}",
        border_style="green",
    ))
    console.print()

    result = await agent.research(
        query=topic,
        on_tool_call=_on_tool_call,
    )

    console.print()
    console.print(Panel(
        Markdown(result),
        title="[bold green]📄 Research Brief[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))
