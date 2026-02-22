"""
core/prompts.py - Reusable prompt templates

Each method returns a (system_message, user_message) tuple that you can pass
directly to LLMClient.chat().  Centralising prompts here means:
  - Easy A/B testing: swap one string, all callers pick it up
  - Version control: track prompt changes in git
  - Reuse across interfaces (CLI, web, API all use the same prompts)
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PromptPair:
    system: str
    user: str


class PromptTemplates:
    """
    Library of production-quality prompt templates.

    Usage:
        pt = PromptTemplates()
        pair = pt.summarize(text, style="bullet_points", length="medium")
        response = client.chat(pair.user, system_message=pair.system)
    """

    # ── Summarization ──────────────────────────────────────────────────────────

    _SUMMARY_STYLES = {
        "bullet_points": "as clear bullet points highlighting the main ideas",
        "paragraph":     "as a single cohesive paragraph",
        "key_takeaways": "as numbered key takeaways the reader should remember",
        "tldr":          "as a one-sentence TL;DR followed by 3 supporting bullets",
    }

    _SUMMARY_LENGTHS = {
        "short":  "in roughly 50 words",
        "medium": "in roughly 150 words",
        "long":   "in roughly 300 words",
    }

    def summarize(
        self,
        text: str,
        style: str = "bullet_points",
        length: str = "medium",
        audience: str = "general",
    ) -> PromptPair:
        """Generate a summarization prompt pair."""
        style_instruction  = self._SUMMARY_STYLES.get(style,  self._SUMMARY_STYLES["bullet_points"])
        length_instruction = self._SUMMARY_LENGTHS.get(length, self._SUMMARY_LENGTHS["medium"])

        system = (
            f"You are an expert at distilling information clearly for a {audience} audience. "
            "Produce accurate, concise summaries that preserve the original meaning."
        )
        user = (
            f"Summarize the following text {length_instruction} {style_instruction}.\n\n"
            f"Text:\n{text}\n\n"
            "Summary:"
        )
        return PromptPair(system=system, user=user)

    # ── Sentiment & Tone Analysis ──────────────────────────────────────────────

    def analyze_sentiment(self, text: str) -> PromptPair:
        """Return a structured sentiment analysis prompt."""
        system = (
            "You are a sentiment analysis expert. Always respond with valid JSON only — "
            "no markdown fences, no extra text."
        )
        user = (
            "Analyse the sentiment of the following text and return a JSON object with keys:\n"
            "  sentiment   (one of: positive / negative / neutral / mixed)\n"
            "  confidence  (float 0-1)\n"
            "  tone        (e.g. formal, casual, urgent, optimistic …)\n"
            "  emotions    (array of detected emotions)\n"
            "  explanation (one sentence)\n\n"
            f"Text:\n{text}\n\nJSON:"
        )
        return PromptPair(system=system, user=user)

    # ── Action Item Extraction ─────────────────────────────────────────────────

    def extract_action_items(self, text: str) -> PromptPair:
        """Extract tasks, deadlines, and owners from meeting notes or emails."""
        system = (
            "You are an executive assistant who extracts actionable tasks from unstructured text. "
            "Always respond with valid JSON only."
        )
        user = (
            "Extract all action items from the text below. "
            "Return a JSON object with a single key 'action_items' containing an array. "
            "Each item should have:\n"
            "  task    (string — what needs to be done)\n"
            "  owner   (string — person responsible, or 'unassigned')\n"
            "  due     (string — deadline if mentioned, else 'not specified')\n"
            "  priority (one of: high / medium / low)\n\n"
            f"Text:\n{text}\n\nJSON:"
        )
        return PromptPair(system=system, user=user)

    # ── Classification ─────────────────────────────────────────────────────────

    def classify(self, text: str, categories: list[str]) -> PromptPair:
        """Zero-shot text classification."""
        cats = ", ".join(f'"{c}"' for c in categories)
        system = (
            "You are a precise text classifier. Always respond with valid JSON only."
        )
        user = (
            f"Classify the following text into exactly one of these categories: [{cats}].\n"
            "Return a JSON object with keys:\n"
            "  category    (the chosen category)\n"
            "  confidence  (float 0-1)\n"
            "  reasoning   (one sentence)\n\n"
            f"Text:\n{text}\n\nJSON:"
        )
        return PromptPair(system=system, user=user)

    # ── Question & Answer ──────────────────────────────────────────────────────

    def answer_from_context(self, question: str, context: str) -> PromptPair:
        """Answer a question strictly from the provided context (grounded QA)."""
        system = (
            "You are a precise question-answering assistant. "
            "Answer only from the provided context. "
            "If the answer is not in the context, say exactly: 'I don't know based on the provided text.'"
        )
        user = (
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )
        return PromptPair(system=system, user=user)

    # ── Translation ────────────────────────────────────────────────────────────

    def translate(self, text: str, target_language: str) -> PromptPair:
        system = (
            f"You are a professional translator. Translate text into {target_language} "
            "preserving meaning, tone, and formatting."
        )
        user = f"Translate the following text into {target_language}:\n\n{text}\n\nTranslation:"
        return PromptPair(system=system, user=user)

    # ── Content Improvement ────────────────────────────────────────────────────

    def improve_writing(self, text: str, goal: str = "clarity") -> PromptPair:
        """
        Improve writing for a given goal.

        goal options: clarity | conciseness | formal | casual | persuasive
        """
        goal_instructions = {
            "clarity":     "Improve clarity and readability. Fix awkward phrasing.",
            "conciseness": "Make it shorter and more direct without losing meaning.",
            "formal":      "Rewrite in a professional, formal tone suitable for business.",
            "casual":      "Rewrite in a friendly, conversational tone.",
            "persuasive":  "Rewrite to be more compelling and persuasive.",
        }
        instruction = goal_instructions.get(goal, goal_instructions["clarity"])
        system = "You are an expert editor and writing coach."
        user = (
            f"{instruction}\n\n"
            "Return ONLY the improved text — no explanations, no labels.\n\n"
            f"Original:\n{text}\n\nImproved:"
        )
        return PromptPair(system=system, user=user)

    # ── Available operations (used by CLI / UI menus) ─────────────────────────

    @staticmethod
    def available_operations() -> dict[str, str]:
        return {
            "summarize":       "Summarize text (bullet points, paragraph, key takeaways, TL;DR)",
            "sentiment":       "Analyse sentiment and tone",
            "action_items":    "Extract action items, owners, and deadlines",
            "classify":        "Classify text into custom categories",
            "qa":              "Answer a question from the provided text",
            "translate":       "Translate to a target language",
            "improve_writing": "Improve writing quality",
        }
