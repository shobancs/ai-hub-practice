"""
Configuration for the Research Assistant Agent.

Values are loaded from environment variables first, then fall back to
sensible defaults.  Copy ../../.env or set vars in your shell.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the GenAI root (two parents up)
_dotenv_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_dotenv_path)


@dataclass
class ResearchAgentConfig:
    """Central configuration for the research assistant agent."""

    # ------------------------------------------------------------------ #
    # OpenAI
    # ------------------------------------------------------------------ #
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )

    # ------------------------------------------------------------------ #
    # Agent behaviour
    # ------------------------------------------------------------------ #
    max_iterations: int = 10           # Max ReAct loops before forced stop
    temperature: float = 0.3           # Low temp for factual research
    max_notes: int = 50                # Max notes the agent can store

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )


# Singleton config
config = ResearchAgentConfig()
