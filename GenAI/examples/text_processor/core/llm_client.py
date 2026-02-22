"""
core/llm_client.py - Singleton OpenAI client with retry logic & cost tracking

Reusable pattern: wrap the raw SDK in a class that adds:
  - Retry with exponential back-off on transient errors
  - Automatic token counting and cost estimation
  - Budget guardrail (raises BudgetExceededError)
  - Structured response dataclass for easy downstream use
"""
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI, RateLimitError, APIError, APIConnectionError

from .config import AppConfig

logger = logging.getLogger(__name__)


# ── Custom exceptions ─────────────────────────────────────────────────────────

class BudgetExceededError(RuntimeError):
    """Raised when cumulative spend would exceed AppConfig.budget_limit_usd."""


class LLMError(RuntimeError):
    """Raised when the API call fails after all retries."""


# ── Response dataclass ────────────────────────────────────────────────────────

@dataclass
class LLMResponse:
    """Structured result returned by LLMClient.chat()."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    cached: bool = False
    metadata: dict = field(default_factory=dict)


# ── Client ────────────────────────────────────────────────────────────────────

class LLMClient:
    """
    Thin, reusable wrapper around the OpenAI Chat Completions API.

    Usage:
        config = AppConfig()
        config.validate()
        client = LLMClient(config)
        response = client.chat("Summarize this text: ...")
        print(response.content)
        print(f"Cost: ${response.cost_usd:.4f}")
    """

    MAX_RETRIES = 3
    RETRY_DELAYS = [2, 4, 8]   # seconds (exponential back-off)

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._client = OpenAI(api_key=config.openai_api_key)
        self._total_cost_usd: float = 0.0
        self._total_tokens: int = 0
        logger.info("LLMClient initialised. Model: %s", config.model)

    # ── Public API ─────────────────────────────────────────────────────────────

    def chat(
        self,
        user_message: str,
        system_message: str = "You are a helpful AI assistant.",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Send a chat request and return a structured LLMResponse.

        Args:
            user_message:   The user turn content.
            system_message: Persona / instructions for the model.
            temperature:    Override config temperature for this call.
            max_tokens:     Override config max_tokens for this call.

        Returns:
            LLMResponse dataclass with content, usage, and cost info.

        Raises:
            BudgetExceededError: if the cumulative spend would exceed the cap.
            LLMError:            if the API call fails after all retries.
        """
        temp   = temperature if temperature is not None else self.config.temperature
        tokens = max_tokens  if max_tokens  is not None else self.config.max_tokens

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user",   "content": user_message},
        ]

        last_error: Optional[Exception] = None

        # GPT-5.x, o1, and o3 models require max_completion_tokens instead of max_tokens
        _COMPLETION_TOKENS_PREFIXES = ("gpt-5", "o1", "o3")
        use_completion_tokens = any(
            self.config.model.startswith(p) for p in _COMPLETION_TOKENS_PREFIXES
        )

        for attempt in range(self.MAX_RETRIES):
            try:
                start = time.monotonic()

                call_kwargs: dict = {
                    "model":       self.config.model,
                    "messages":    messages,
                    "temperature": temp,
                }
                if use_completion_tokens:
                    call_kwargs["max_completion_tokens"] = tokens
                else:
                    call_kwargs["max_tokens"] = tokens

                raw = self._client.chat.completions.create(**call_kwargs)

                latency_ms = (time.monotonic() - start) * 1000
                response   = self._build_response(raw, latency_ms)

                # Budget check
                projected = self._total_cost_usd + response.cost_usd
                if (
                    self.config.budget_limit_usd > 0
                    and projected > self.config.budget_limit_usd
                ):
                    raise BudgetExceededError(
                        f"Spending cap ${self.config.budget_limit_usd:.2f} would be exceeded. "
                        f"Cumulative spend so far: ${self._total_cost_usd:.4f}"
                    )

                self._total_cost_usd += response.cost_usd
                self._total_tokens   += response.input_tokens + response.output_tokens

                logger.info(
                    "API call OK | tokens=%d+%d | cost=$%.4f | latency=%.0fms",
                    response.input_tokens, response.output_tokens,
                    response.cost_usd, response.latency_ms,
                )
                return response

            except BudgetExceededError:
                raise   # never retry budget errors

            except RateLimitError as exc:
                last_error = exc
                wait = self.RETRY_DELAYS[min(attempt, len(self.RETRY_DELAYS) - 1)]
                logger.warning("Rate limit hit (attempt %d/%d). Waiting %ds…", attempt + 1, self.MAX_RETRIES, wait)
                time.sleep(wait)

            except (APIConnectionError, APIError) as exc:
                last_error = exc
                wait = self.RETRY_DELAYS[min(attempt, len(self.RETRY_DELAYS) - 1)]
                logger.warning("API error (attempt %d/%d): %s. Retrying in %ds…", attempt + 1, self.MAX_RETRIES, exc, wait)
                time.sleep(wait)

        raise LLMError(f"API call failed after {self.MAX_RETRIES} attempts. Last error: {last_error}")

    # ── Stats ──────────────────────────────────────────────────────────────────

    @property
    def total_cost_usd(self) -> float:
        """Cumulative cost of all calls made by this client instance."""
        return round(self._total_cost_usd, 6)

    @property
    def total_tokens(self) -> int:
        return self._total_tokens

    def session_summary(self) -> dict:
        return {
            "total_cost_usd": self.total_cost_usd,
            "total_tokens": self.total_tokens,
            "model": self.config.model,
        }

    # ── Internal ───────────────────────────────────────────────────────────────

    def _build_response(self, raw, latency_ms: float) -> LLMResponse:
        usage        = raw.usage
        input_tokens = usage.prompt_tokens
        output_tokens= usage.completion_tokens
        cost         = self.config.estimate_cost(input_tokens, output_tokens)

        return LLMResponse(
            content=raw.choices[0].message.content.strip(),
            model=raw.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=round(latency_ms, 1),
        )
