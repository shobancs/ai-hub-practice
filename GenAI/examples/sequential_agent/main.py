"""
Sequential Agent Pattern — Content Intelligence Pipeline
=========================================================
PATTERN : SEQUENTIAL  (Linear Pipeline)
SDK     : OpenAI Python SDK (async)
LEVEL   : Intermediate → Advanced

╔══════════════════════════════════════════════════════════════╗
║              SEQUENTIAL PATTERN — AT A GLANCE                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  INPUT → [Stage 1] → [Stage 2] → [Stage 3] → [Stage N] → OUTPUT
║                                                              ║
║  • Each stage receives the full context of all prior stages  ║
║  • Stages run strictly one-at-a-time (no parallelism)        ║
║  • Output of stage N becomes enriched input for stage N+1    ║
╚══════════════════════════════════════════════════════════════╝

BEST USES  ✅
  • Multi-step transformation     (research → draft → polish → publish)
  • Quality-refinement pipelines  (write → edit → proofread → approve)
  • Data enrichment chains        (extract → classify → enrich → validate)
  • Decision-support pipelines    (gather → analyse → recommend → explain)
  • Document processing           (parse → summarise → translate → store)

AVOID WHEN ❌
  • Tasks are independent (→ Parallelization pattern instead)
  • Flow depends on dynamic conditions (→ Routing pattern)
  • You need iterative self-improvement loops (→ Reflection pattern)
  • Many agents collaborate without fixed order (→ Multi-Agent pattern)

THIS DEMO  Pipeline: Content Intelligence
  Stage 1  Researcher  — Extracts key facts, trends & insights
  Stage 2  Strategist  — Builds a content outline & strategy
  Stage 3  Writer      — Writes the full polished article
  Stage 4  Reviewer    — Scores quality & delivers final version

HOW CONTEXT FLOWS:
  topic (str)
    ↓
  [Researcher]   → messages (research findings appended)
    ↓
  [Strategist]   → messages (strategy appended)
    ↓
  [Writer]       → messages (draft article appended)
    ↓
  [Reviewer]     → str      (final reviewed output)

SETUP:
  pip install -r requirements.txt
  Uses OPENAI_API_KEY from GenAI/.env

RUN:
  python main.py
"""

import asyncio
import os
import pathlib

from openai import AsyncOpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

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
#  Each agent has a focused persona — passed as the system message each call
# ══════════════════════════════════════════════════════════════════════════════

RESEARCHER_INSTRUCTIONS = """\
You are an expert Research Analyst specialising in comprehensive topic research.
Your job is to gather key facts, current trends, challenges, and opportunities
for any given topic. Always structure findings clearly with headers and bullets.
Be factual, specific, and cite numbers/data where possible."""

STRATEGIST_INSTRUCTIONS = """\
You are a Senior Content Strategist with expertise in audience analysis and
narrative planning. You transform raw research into actionable content strategies.
Always specify target audience, core message, tone, and a 5-section outline.
Your plans are specific, grounded in the research provided, and immediately usable."""

WRITER_INSTRUCTIONS = """\
You are an expert Content Writer who crafts compelling, well-structured articles.
You translate research and strategy into engaging, readable content that educates
and inspires readers. Use markdown (# headings, **bold**, bullet points).
Your writing is clear, precise, and exactly matches the tone specified in the strategy."""

REVIEWER_INSTRUCTIONS = """\
You are a Senior Editorial Reviewer specialising in content quality assessment.
You score content across five dimensions, highlight the top three improvements,
and deliver a final publication-ready version with those improvements applied.
Your reviews are objective, constructive, and always raise the quality bar."""


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED HELPER
# ══════════════════════════════════════════════════════════════════════════════

async def call_agent(
    system_prompt: str,
    messages: list[dict],
    label: str,
    panel_style: str,
) -> str:
    """
    Call the OpenAI chat API with a system prompt + accumulated message history.
    Prints a rich panel with the response and returns the assistant text.
    """
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + messages,
        temperature=0.7,
    )
    text = response.choices[0].message.content
    console.print(Panel(text, title=f"[{panel_style}]{label}[/{panel_style}]",
                        border_style=panel_style))
    return text


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 1 — Researcher
#  Input : str           (topic)
#  Output: list[dict]    (OpenAI message history with research appended)
# ══════════════════════════════════════════════════════════════════════════════

async def stage_researcher(topic: str) -> list[dict]:
    """Stage 1 — extracts key facts, trends, challenges, and opportunities."""
    console.print(Rule("🔍  Stage 1 — Researcher", style="bold blue"))

    user_msg = (
        f"Research this topic thoroughly: **{topic}**\n\n"
        "Provide:\n"
        "1. **Key Facts** — 5-7 facts with data/statistics where possible\n"
        "2. **Current Trends** — what is happening right now in this space\n"
        "3. **Key Challenges** — main problems and pain points\n"
        "4. **Opportunities** — key applications and growth areas\n"
        "5. **Expert Consensus** — widely accepted viewpoints from the field\n\n"
        "Use clear markdown headers and bullet points."
    )
    messages = [{"role": "user", "content": user_msg}]
    result = await call_agent(RESEARCHER_INSTRUCTIONS, messages, "Research Findings", "blue")

    # Append the assistant reply so the next stage has full context
    messages.append({"role": "assistant", "content": result})
    return messages


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 2 — Content Strategist
#  Input : list[dict]    (research history)
#  Output: list[dict]    (strategy appended to history)
# ══════════════════════════════════════════════════════════════════════════════

async def stage_strategist(messages: list[dict]) -> list[dict]:
    """Stage 2 — builds a content strategy from the research."""
    console.print(Rule("📋  Stage 2 — Content Strategist", style="bold yellow"))

    user_msg = (
        "Based on the research above, create a detailed content strategy:\n\n"
        "1. **Target Audience** — profile, needs, knowledge level\n"
        "2. **Core Message** — the single most important takeaway (1-2 sentences)\n"
        "3. **Content Outline** — 5 sections, each with 2-3 sub-points\n"
        "4. **Tone & Style** — pick one (Technical / Accessible / Inspirational) and explain why\n"
        "5. **Opening Hooks** — 3 compelling ways to start (question, stat, story)\n"
        "6. **Call-to-Action** — what should readers do after reading?\n\n"
        "Be specific and ground every decision in the research findings."
    )
    messages.append({"role": "user", "content": user_msg})
    result = await call_agent(STRATEGIST_INSTRUCTIONS, messages, "Content Strategy", "yellow")
    messages.append({"role": "assistant", "content": result})
    return messages


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 3 — Content Writer
#  Input : list[dict]    (research + strategy history)
#  Output: list[dict]    (draft article appended to history)
# ══════════════════════════════════════════════════════════════════════════════

async def stage_writer(messages: list[dict]) -> list[dict]:
    """Stage 3 — writes a full polished article using research + strategy."""
    console.print(Rule("✍️   Stage 3 — Content Writer", style="bold green"))

    user_msg = (
        "Using the research and strategy above, write a complete article (700-900 words).\n\n"
        "Requirements:\n"
        "- Start with the strongest hook from the strategy\n"
        "- Follow the outlined 5-section structure exactly\n"
        "- Weave in key facts and statistics naturally (do not list them raw)\n"
        "- Match the recommended tone and style precisely\n"
        "- Close with the suggested call-to-action\n"
        "- Format using markdown: # H1, ## H2, **bold**, and bullet points\n\n"
        "Write the full article now:"
    )
    messages.append({"role": "user", "content": user_msg})
    result = await call_agent(WRITER_INSTRUCTIONS, messages, "Draft Article", "green")
    messages.append({"role": "assistant", "content": result})
    return messages


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE 4 — Quality Reviewer  (terminal stage)
#  Input : list[dict]    (full pipeline history)
#  Output: str           (final reviewed article)
# ══════════════════════════════════════════════════════════════════════════════

async def stage_reviewer(messages: list[dict]) -> str:
    """
    Stage 4 — scores quality across 5 dimensions, applies top 3 improvements,
    and returns the final publication-ready article.
    """
    console.print(Rule("✅  Stage 4 — Quality Reviewer", style="bold magenta"))

    user_msg = (
        "Review the article above comprehensively and provide:\n\n"
        "## 📊 Quality Scorecard\n"
        "Rate each dimension 1-10 with a one-line reason:\n"
        "- **Accuracy**      — do the facts match the research?\n"
        "- **Clarity**       — is it easy to understand?\n"
        "- **Structure**     — does it flow logically?\n"
        "- **Engagement**    — will it hold the reader's attention?\n"
        "- **Actionability** — does the CTA inspire action?\n"
        "- **Overall Score** — /10\n\n"
        "## 🔧 Top 3 Improvements Applied\n"
        "List the three most impactful changes you made.\n\n"
        "## 📄 Final Polished Article\n"
        "Provide the complete, publication-ready version with every improvement applied."
    )
    messages.append({"role": "user", "content": user_msg})
    return await call_agent(REVIEWER_INSTRUCTIONS, messages, "Final Reviewed Output", "magenta")


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE RUNNER
# ══════════════════════════════════════════════════════════════════════════════

async def run_content_pipeline(topic: str) -> None:
    """
    Executes the 4-stage sequential pipeline:
        Researcher ──► Strategist ──► Writer ──► Reviewer
    """
    console.print(
        Panel.fit(
            f"[bold cyan]Content Intelligence Pipeline[/bold cyan]\n"
            f"[dim]Sequential Agent Pattern — OpenAI SDK[/dim]\n\n"
            f"Topic: [bold white]{topic}[/bold white]\n"
            f"Model: [dim]{MODEL}[/dim]",
            border_style="cyan",
        )
    )

    # ── Stage 1: Research ────────────────────────────────────────────────────
    messages = await stage_researcher(topic)

    # ── Stage 2: Strategy (receives full research context) ───────────────────
    messages = await stage_strategist(messages)

    # ── Stage 3: Writing (receives research + strategy context) ─────────────
    messages = await stage_writer(messages)

    # ── Stage 4: Review (receives full pipeline context) ────────────────────
    final_output = await stage_reviewer(messages)

    # ── Save output ──────────────────────────────────────────────────────────
    console.print(Rule("📄  FINAL OUTPUT", style="bold white"))
    console.print(Markdown(final_output))
    _save_output(topic, final_output)


def _save_output(topic: str, content: str) -> None:
    """Persist the final pipeline output to a markdown file."""
    output_file = "pipeline_output.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Content Intelligence Pipeline — Output\n\n")
        f.write(f"**Topic**: {topic}\n\n")
        f.write("---\n\n")
        f.write(content)
    console.print(f"\n[dim]💾  Saved to [bold]{output_file}[/bold][/dim]")


# ══════════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

SAMPLE_TOPICS = {
    "1": "The impact of AI agents on software development in 2025",
    "2": "Building resilient microservices with event-driven architecture",
    "3": "The rise of multimodal AI and its practical applications",
    "4": "DevSecOps best practices for cloud-native applications",
    "5": "How vector databases are transforming enterprise search",
}


async def main() -> None:
    console.print(
        "\n[bold]🚀  Content Intelligence Pipeline[/bold]\n"
        "[dim]Sequential Agent Pattern | Microsoft Agent Framework[/dim]\n"
    )

    console.print("[bold]Sample Topics:[/bold]")
    for key, t in SAMPLE_TOPICS.items():
        console.print(f"  [cyan]{key}[/cyan].  {t}")

    console.print("\n[dim]Or type a custom topic and press Enter.[/dim]\n")
    choice = input("Select (1-5) or enter custom topic: ").strip()

    topic = SAMPLE_TOPICS.get(choice, choice or SAMPLE_TOPICS["1"])
    await run_content_pipeline(topic)


if __name__ == "__main__":
    asyncio.run(main())
