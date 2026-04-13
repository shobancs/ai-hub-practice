"""
Research Assistant Agent — Entry Point

An AI-powered research assistant that uses the ReAct pattern
(Reasoning + Acting) to systematically research any topic.

The agent autonomously:
  • Searches the web for relevant information
  • Reads webpages for detailed content
  • Takes structured notes with tags
  • Performs calculations when needed
  • Compiles findings into a research brief

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                  RESEARCH ASSISTANT AGENT                    │
    │                                                              │
    │  research_agent/                                             │
    │  ├── main.py              ← You are here (entry point)      │
    │  ├── requirements.txt     ← Dependencies                    │
    │  ├── core/                                                   │
    │  │   ├── config.py        ← Configuration (@dataclass)      │
    │  │   ├── models.py        ← Data models (Note, Session)     │
    │  │   ├── tools.py         ← Tool implementations (simulated)│
    │  │   └── agent.py         ← ReAct loop orchestrator         │
    │  └── interfaces/                                             │
    │      └── cli.py           ← Rich terminal UI                │
    │                                                              │
    │  Flow:                                                       │
    │  User ──► CLI ──► Agent.research() ──► ReAct Loop            │
    │                        │                   │                  │
    │                  ResearchSession       LLM + Tools            │
    │                  (notes, state)      (search, read,           │
    │                                      note, calc)             │
    └─────────────────────────────────────────────────────────────┘

Agentic Patterns Demonstrated:
  ✅ ReAct (Reasoning + Acting)
  ✅ Tool Use (function calling)
  ✅ Memory (session-scoped note-taking)
  ✅ Planning (systematic research approach via system prompt)

Usage:
    python main.py                          # Interactive menu
    python main.py --research "agentic AI"  # Direct research mode
    python main.py --help                   # Show help

Prerequisites:
    export OPENAI_API_KEY="sk-..."
    pip install -r requirements.txt
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure parent is on path for package imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research_agent.core.config import config
from research_agent.interfaces.cli import run_interactive, run_direct_research


# ─────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s  [%(levelname)-8s]  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# CLI argument parsing
# ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="🔬 AI Research Assistant Agent — powered by ReAct pattern",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                            Interactive menu
  python main.py --research "agentic AI"    Research a topic directly
  python main.py --research "climate change" --verbose
        """,
    )
    parser.add_argument(
        "--research", "-r",
        type=str,
        help="Research a topic directly (skips interactive menu)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

async def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate API key
    if not config.openai_api_key:
        print("❌ OPENAI_API_KEY is not set.")
        print("   Set it in your environment or in GenAI/.env")
        sys.exit(1)

    if args.research:
        await run_direct_research(args.research)
    else:
        await run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
