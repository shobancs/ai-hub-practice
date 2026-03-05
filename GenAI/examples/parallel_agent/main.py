"""
Parallel Agent Pattern — Business Intelligence Platform
=======================================================
PATTERN : PARALLEL  (Fan-Out → Fan-In)
SDK     : OpenAI Python SDK (async)
LEVEL   : Intermediate → Advanced

╔══════════════════════════════════════════════════════════════╗
║              PARALLEL PATTERN — AT A GLANCE                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║         INPUT                                                ║
║           │                                                  ║
║     ┌─────┼──────┬──────┬──────┐                            ║
║     ▼     ▼      ▼      ▼      ▼      ← Fan-Out (concurrent) ║
║  [Mkt] [Fin] [Tech] [Comp] [Risk]                            ║
║     │     │      │      │      │                             ║
║     └─────┴──────┴──────┴──────┘                            ║
║                   │                                          ║
║            [Aggregator]           ← Fan-In (sequential)      ║
║                   │                                          ║
║               FINAL BRIEF                                    ║
╚══════════════════════════════════════════════════════════════╝

BEST USES  ✅
  • Independent multi-perspective analysis  (market + tech + legal + risk)
  • Speed-critical tasks with no dependencies between sub-tasks
  • Ensemble / voting for higher reliability
  • Large document processing (split into chunks, summarise in parallel)
  • Multi-criteria evaluation (audits, scorecards, due-diligence)

AVOID WHEN ❌
  • Stages depend on each other (→ Sequential pattern)
  • Dynamic routing needed   (→ Routing pattern)
  • Budget / API rate limits are tight  (parallel = N simultaneous calls)
  • Agents need to debate or revise each other (→ Multi-Agent / Reflection)

THIS DEMO  Pipeline: Business Intelligence Platform
  Worker 1  Market Analyst        — TAM, SAM, SOM, trends, timing
  Worker 2  Financial Analyst     — Revenue model, costs, path to profit
  Worker 3  Technology Analyst    — Feasibility, stack, build timeline
  Worker 4  Competitive Intel     — Competitor map, moats, white space
  Worker 5  Risk Analyst          — Risk matrix with likelihood & impact
  ──────────────────────────────────────────────────────────────────────
  Aggregator  Chief Intelligence Officer — Synthesises all 5 reports
              into an executive-ready GO / NO-GO brief

HOW CONTEXT FLOWS (Fan-Out → Fan-In):
  topic (str)
    ├──► [Market Analyst]    ──► report_market      ─┐
    ├──► [Financial Analyst] ──► report_financial    │
    ├──► [Tech Analyst]      ──► report_tech         ├──► [CIO Aggregator] ──► final brief
    ├──► [Competitive Intel] ──► report_competitive  │
    └──► [Risk Analyst]      ──► report_risk        ─┘

  All 5 workers launch at the same instant via asyncio.gather().
  Aggregator runs only after ALL workers complete (fan-in).

SETUP:
  pip install -r requirements.txt
  Uses OPENAI_API_KEY from GenAI/.env

RUN:
  python main.py
"""

import asyncio
import os
import pathlib
import time

from openai import AsyncOpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

# ─── Load .env from the GenAI parent directory ────────────────────────────────
_env_path = pathlib.Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)

console = Console()

# ─── Configuration ────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL          = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
#  AGENT SYSTEM PROMPTS
#  Each worker is a specialist with a focused lens on the same input
# ══════════════════════════════════════════════════════════════════════════════

MARKET_ANALYST_PROMPT = """\
You are a Senior Market Research Analyst. Given a business topic or idea, provide:
- Total Addressable Market (TAM), SAM, and SOM estimates with reasoning
- Primary customer segments and their key unmet needs
- Market trends driving (or hindering) adoption right now
- Market entry barriers (regulatory, network effects, capital, etc.)
- Overall market opportunity score (1-10) with a one-line rationale
Be specific with numbers and percentages. Avoid vague generalities."""

FINANCIAL_ANALYST_PROMPT = """\
You are a Senior Financial Analyst specialising in business evaluation. Provide:
- Likely revenue model(s) with example unit economics (e.g. ARPU, CAC, LTV)
- Estimated cost structure — top 3-5 cost drivers with relative proportions
- Realistic path to break-even / profitability with timeline estimate
- Key financial KPIs to track from day one
- Financial viability score (1-10) with a one-line rationale
Be specific and realistic. Do NOT be overly optimistic."""

TECH_ANALYST_PROMPT = """\
You are a Chief Technology Officer evaluating technical feasibility. Provide:
- Technical complexity rating (1=trivial, 10=moonshot) with justification
- Core technology stack and the 3-5 most critical technical components
- Realistic MVP build timeline (weeks/months) for a lean team of 3-5 engineers
- Top 3 technical risks and their mitigations
- Build-vs-buy decision for each core component
- Technical feasibility score (1-10) with a one-line rationale"""

COMPETITIVE_INTEL_PROMPT = """\
You are a Competitive Intelligence Specialist. Provide:
- Top 3-5 direct competitors with brief profiles (founded, funding, key differentiator)
- Top 2-3 indirect competitors / substitutes customers currently use
- Dominant competitive moats in the space (data, network effects, switching costs, etc.)
- Where the market is underserved or overserved — the white space
- Top 3 defensible differentiation angles for a new entrant
- Competitive opportunity score (1-10) where 10 = easy to differentiate"""

RISK_ANALYST_PROMPT = """\
You are a Risk Management Director. Produce a risk matrix with 6-8 risks covering:
  Regulatory & compliance | Market/demand | Operational | Technology | Financial | Reputational
For each risk:
  - Risk name and short description
  - Likelihood: High / Medium / Low
  - Impact: High / Medium / Low
  - Mitigation strategy (1-2 sentences)
Close with an Overall Risk Score (1-10) where 10 = extremely risky, 1 = minimal risk."""

AGGREGATOR_PROMPT = """\
You are a Chief Intelligence Officer synthesising multi-disciplinary analyst reports
into a crisp, executive-ready intelligence brief. Your output MUST follow this structure:

## 🏁 Recommendation
State clearly: GO / NO-GO / CONDITIONAL GO
If CONDITIONAL GO, list the 2-3 conditions that must be met first.

## 💪 Top 3 Strengths
Bullet the three most compelling reasons to move forward.

## ⚠️ Top 3 Concerns
Bullet the three most important risks or weaknesses.

## 🗺️ Priority Action Plan
Number the 5 next concrete steps in priority order.

## 📊 Opportunity Matrix (2×2: Impact vs Effort)
| Initiative | Impact | Effort | Quadrant |
List 4 key initiatives using this table.

## 🎯 Overall Confidence Score
Single percentage (0–100 %) followed by a one-sentence rationale.

Be executive-ready: data-driven, decisive, and immediately actionable."""


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED HELPER
# ══════════════════════════════════════════════════════════════════════════════

async def call_agent(system_prompt: str, user_msg: str, label: str, style: str) -> dict:
    """
    Call the OpenAI chat API with a focused system prompt + user message.
    Prints a rich panel with the result and returns a dict with label, content, elapsed.
    """
    t_start = time.perf_counter()
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.6,
    )
    elapsed = time.perf_counter() - t_start
    text = response.choices[0].message.content
    console.print(Panel(
        text,
        title=f"[{style}]{label}[/{style}]",
        border_style=style,
        padding=(0, 1),
    ))
    return {"label": label, "content": text, "elapsed": elapsed}


# ══════════════════════════════════════════════════════════════════════════════
#  PARALLEL WORKERS
#  Each worker runs independently — no shared state, no ordering dependency.
#  All launched simultaneously via asyncio.gather() in run_intelligence_platform()
# ══════════════════════════════════════════════════════════════════════════════

async def worker_market(topic: str) -> dict:
    """Worker 1 — Market Analysis (TAM/SAM/SOM, trends, entry barriers)."""
    console.print("[dim cyan]  ⚡ Market Analyst started[/dim cyan]")
    return await call_agent(
        MARKET_ANALYST_PROMPT,
        f"Business topic: {topic}",
        "📊 Market Analysis",
        "cyan",
    )


async def worker_financial(topic: str) -> dict:
    """Worker 2 — Financial Analysis (revenue model, costs, path to profit)."""
    console.print("[dim green]  ⚡ Financial Analyst started[/dim green]")
    return await call_agent(
        FINANCIAL_ANALYST_PROMPT,
        f"Business topic: {topic}",
        "💰 Financial Analysis",
        "green",
    )


async def worker_tech(topic: str) -> dict:
    """Worker 3 — Technology Analysis (feasibility, stack, build timeline)."""
    console.print("[dim yellow]  ⚡ Technology Analyst started[/dim yellow]")
    return await call_agent(
        TECH_ANALYST_PROMPT,
        f"Business topic: {topic}",
        "🔧 Technology Analysis",
        "yellow",
    )


async def worker_competitive(topic: str) -> dict:
    """Worker 4 — Competitive Intelligence (competitor map, moats, white space)."""
    console.print("[dim magenta]  ⚡ Competitive Intel started[/dim magenta]")
    return await call_agent(
        COMPETITIVE_INTEL_PROMPT,
        f"Business topic: {topic}",
        "🏆 Competitive Intelligence",
        "magenta",
    )


async def worker_risk(topic: str) -> dict:
    """Worker 5 — Risk Analysis (risk matrix with likelihood, impact, mitigation)."""
    console.print("[dim red]  ⚡ Risk Analyst started[/dim red]")
    return await call_agent(
        RISK_ANALYST_PROMPT,
        f"Business topic: {topic}",
        "⚠️  Risk Analysis",
        "red",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  AGGREGATOR  (fan-in — runs after ALL workers complete)
# ══════════════════════════════════════════════════════════════════════════════

async def aggregator_cio(topic: str, reports: list[dict]) -> str:
    """
    Fan-In: Synthesise all 5 worker reports into a single executive brief.
    Receives the full text of every worker — has complete context.
    """
    console.print(Rule("🧠  Aggregator — Chief Intelligence Officer", style="bold white"))

    combined = "\n\n".join(
        f"---\n### {r['label']}\n{r['content']}" for r in reports
    )
    user_msg = (
        f"Business Topic: **{topic}**\n\n"
        f"Analyst Reports:\n\n{combined}\n\n"
        "Synthesise the above into a final Executive Intelligence Brief."
    )

    t_start = time.perf_counter()
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": AGGREGATOR_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.5,
    )
    elapsed = time.perf_counter() - t_start
    text = response.choices[0].message.content
    console.print(Panel(
        text,
        title="[bold white]📋 Executive Intelligence Brief[/bold white]",
        border_style="white",
        padding=(0, 1),
    ))
    return text


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE RUNNER
# ══════════════════════════════════════════════════════════════════════════════

async def run_intelligence_platform(topic: str) -> None:
    """
    Executes the full parallel intelligence platform:

        Fan-Out ──► [Market] [Financial] [Tech] [Competitive] [Risk]  (concurrent)
                                           │
        Fan-In  ──────────────────────► [CIO Aggregator]              (sequential)
                                           │
                                    Executive Brief
    """
    console.print(
        Panel.fit(
            f"[bold cyan]Business Intelligence Platform[/bold cyan]\n"
            f"[dim]Parallel Agent Pattern — OpenAI SDK[/dim]\n\n"
            f"Topic  : [bold white]{topic}[/bold white]\n"
            f"Model  : [dim]{MODEL}[/dim]\n"
            f"Workers: [bold]5 specialist agents launching concurrently[/bold]",
            border_style="cyan",
        )
    )

    # ── FAN-OUT: All 5 workers start at the same instant ─────────────────────
    console.print(Rule("⚡  Fan-Out — 5 Agents Running in Parallel", style="bold cyan"))

    t_wall_start = time.perf_counter()
    reports: list[dict] = await asyncio.gather(
        worker_market(topic),
        worker_financial(topic),
        worker_tech(topic),
        worker_competitive(topic),
        worker_risk(topic),
    )
    t_wall_total = time.perf_counter() - t_wall_start

    # ── Timing summary ────────────────────────────────────────────────────────
    table = Table(
        title="⏱  Parallel Execution Timing",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Agent",           style="bold")
    table.add_column("Individual Time", justify="right")

    sequential_total = sum(r["elapsed"] for r in reports)
    for r in reports:
        table.add_row(r["label"], f"{r['elapsed']:.1f}s")

    table.add_row(
        "[bold green]Wall-clock (parallel)[/bold green]",
        f"[bold green]{t_wall_total:.1f}s[/bold green]",
    )
    table.add_row(
        "[dim red]Sequential would take ≈[/dim red]",
        f"[dim red]{sequential_total:.1f}s[/dim red]",
    )
    table.add_row(
        "[bold]Speedup[/bold]",
        f"[bold yellow]{sequential_total / t_wall_total:.1f}×[/bold yellow]",
    )
    console.print(table)

    # ── FAN-IN: Aggregator receives all 5 reports ─────────────────────────────
    final = await aggregator_cio(topic, reports)

    # ── Final render + save ───────────────────────────────────────────────────
    console.print(Rule("📄  FINAL EXECUTIVE BRIEF", style="bold white"))
    console.print(Markdown(final))
    _save_output(topic, reports, final)


def _save_output(topic: str, reports: list[dict], final: str) -> None:
    """Persist individual worker reports + final brief to a markdown file."""
    output_file = "intelligence_brief.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Business Intelligence Brief\n\n")
        f.write(f"**Topic**: {topic}\n\n---\n\n")
        for r in reports:
            f.write(f"## {r['label']}\n\n{r['content']}\n\n---\n\n")
        f.write("## Executive Intelligence Brief\n\n")
        f.write(final)
    console.print(f"\n[dim]💾  Saved to [bold]{output_file}[/bold][/dim]")


# ══════════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

SAMPLE_TOPICS = {
    "1": "AI-powered personal finance app for Gen Z",
    "2": "On-demand electric vehicle charging network",
    "3": "B2B marketplace for freelance AI/ML engineers",
    "4": "Subscription mental health coaching powered by AI",
    "5": "Autonomous drone delivery for last-mile logistics",
}


async def main() -> None:
    console.print(
        "\n[bold]🚀  Business Intelligence Platform[/bold]\n"
        "[dim]Parallel Agent Pattern | 5 Concurrent Specialist Analysts[/dim]\n"
    )

    console.print("[bold]Sample Topics:[/bold]")
    for key, t in SAMPLE_TOPICS.items():
        console.print(f"  [cyan]{key}[/cyan].  {t}")

    console.print("\n[dim]Or type a custom topic and press Enter.[/dim]\n")
    choice = input("Select (1-5) or enter custom topic: ").strip()

    topic = SAMPLE_TOPICS.get(choice, choice or SAMPLE_TOPICS["1"])
    await run_intelligence_platform(topic)


if __name__ == "__main__":
    asyncio.run(main())
