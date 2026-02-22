"""
core/config.py - Centralized configuration management

Handles all app settings, model options, and cost constants.
Reusable pattern: import AppConfig into any project for consistent settings.
"""
import os
import logging
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Model cost table (USD per 1000 tokens) ────────────────────────────────────
MODEL_COSTS: dict[str, dict[str, float]] = {
    # ── GPT-5 series (latest) ─────────────────────────────────────────────────
    "gpt-5.2": {"input": 0.015, "output": 0.060},           # Latest — Dec 2025
    "gpt-5.2-chat-latest": {"input": 0.015, "output": 0.060},
    "gpt-5.1": {"input": 0.012, "output": 0.048},           # Nov 2025
    "gpt-5": {"input": 0.010, "output": 0.040},             # Aug 2025
    "gpt-5-mini": {"input": 0.001, "output": 0.004},        # Efficient GPT-5
    # ── GPT-4 series ──────────────────────────────────────────────────────────
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4.1": {"input": 0.002, "output": 0.008},           # Apr 2025
    "gpt-4.1-mini": {"input": 0.0004, "output": 0.0016},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    # ── Reasoning models ──────────────────────────────────────────────────────
    "o3": {"input": 0.010, "output": 0.040},
    "o3-mini": {"input": 0.0011, "output": 0.0044},
    "o1": {"input": 0.015, "output": 0.060},
    # ── Legacy ────────────────────────────────────────────────────────────────
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}

DEFAULT_MODEL = "gpt-5.2"   # Latest available model (Dec 2025)


@dataclass
class AppConfig:
    """
    Central configuration object for the Text Processor app.

    Usage:
        config = AppConfig()                     # defaults
        config = AppConfig(model="gpt-4o")       # override model
        config = AppConfig(budget_limit_usd=1.0) # set spending cap
    """

    # API
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # Model
    model: str = DEFAULT_MODEL
    temperature: float = 0.3
    max_tokens: int = 1024

    # Budget guardrail (USD). Set to 0.0 to disable.
    budget_limit_usd: float = 5.0

    # Storage
    db_path: str = "text_processor.db"
    cache_enabled: bool = True

    # Text handling
    max_input_chars: int = 15_000   # ~3750 tokens — safe for most models
    chunk_size: int = 3_000         # chars per chunk when splitting long text

    def validate(self) -> None:
        """Raise ValueError if the config is invalid."""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Add it to your .env file or export it as an environment variable."
            )
        if self.model not in MODEL_COSTS:
            raise ValueError(
                f"Unknown model '{self.model}'. "
                f"Choose from: {list(MODEL_COSTS.keys())}"
            )
        logger.info("Config validated. Model: %s | Budget cap: $%.2f", self.model, self.budget_limit_usd)
        logger.info("Latest model active: %s", self.model)

    def cost_per_1k(self, token_type: str = "input") -> float:
        """Return cost per 1000 tokens for the configured model."""
        return MODEL_COSTS.get(self.model, {}).get(token_type, 0.0)

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate total USD cost for a single API call."""
        input_cost  = (input_tokens  / 1000) * self.cost_per_1k("input")
        output_cost = (output_tokens / 1000) * self.cost_per_1k("output")
        return round(input_cost + output_cost, 6)

    @property
    def available_models(self) -> list[str]:
        return list(MODEL_COSTS.keys())
