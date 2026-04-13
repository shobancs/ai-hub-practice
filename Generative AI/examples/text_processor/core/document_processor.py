"""
core/document_processor.py - Universal text ingestion layer

Supports: raw text strings, local .txt / .md files, and web URLs.
Reusable pattern: separate IO concerns from AI logic so you can plug in
new sources (PDF, DOCX, email …) without touching the rest of the app.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from dataclasses import dataclass

import requests

from .config import AppConfig

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Normalised representation of any ingested document."""
    content: str           # Clean UTF-8 text
    source: str            # Human-readable origin label
    source_type: str       # "text" | "file" | "url"
    char_count: int = 0
    word_count: int = 0
    was_truncated: bool = False

    def __post_init__(self):
        self.char_count = len(self.content)
        self.word_count = len(self.content.split())


class DocumentProcessor:
    """
    Loads text from various sources and returns clean Document objects.

    Usage:
        dp = DocumentProcessor(config)
        doc = dp.from_text("Some text …")
        doc = dp.from_file("/path/to/notes.md")
        doc = dp.from_url("https://en.wikipedia.org/wiki/Python_(programming_language)")
    """

    # Browser-like user agent to avoid 403s on simple sites
    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    # ── Public loaders ─────────────────────────────────────────────────────────

    def from_text(self, text: str, label: str = "raw text") -> Document:
        """Accept a plain string and return a Document."""
        clean = self._clean(text)
        truncated, clean = self._maybe_truncate(clean)
        logger.info("Loaded %s | %d chars", label, len(clean))
        return Document(content=clean, source=label, source_type="text", was_truncated=truncated)

    def from_file(self, path: str | Path) -> Document:
        """Load a .txt or .md file from disk."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        if p.suffix.lower() not in {".txt", ".md", ".text"}:
            raise ValueError(f"Unsupported file type '{p.suffix}'. Use .txt or .md files.")

        raw = p.read_text(encoding="utf-8", errors="replace")
        clean = self._clean(raw)
        truncated, clean = self._maybe_truncate(clean)
        logger.info("Loaded file '%s' | %d chars", p.name, len(clean))
        return Document(content=clean, source=str(p), source_type="file", was_truncated=truncated)

    def from_url(self, url: str) -> Document:
        """
        Fetch a web page and extract readable text.
        Falls back gracefully if BeautifulSoup is not installed.
        """
        logger.info("Fetching URL: %s", url)
        try:
            resp = requests.get(url, headers=self._HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch URL: {exc}") from exc

        text = self._extract_text_from_html(resp.text)
        clean = self._clean(text)
        truncated, clean = self._maybe_truncate(clean)
        logger.info("Loaded URL '%s' | %d chars", url, len(clean))
        return Document(content=clean, source=url, source_type="url", was_truncated=truncated)

    def chunk(self, doc: Document) -> list[Document]:
        """
        Split a large Document into smaller chunks for models with token limits.
        Returns a list of Documents with updated source labels.
        """
        if doc.char_count <= self.config.chunk_size:
            return [doc]

        words  = doc.content.split()
        size   = self.config.chunk_size // 5   # rough word estimate
        chunks = []
        for i, start in enumerate(range(0, len(words), size)):
            piece = " ".join(words[start : start + size])
            chunks.append(
                Document(
                    content=piece,
                    source=f"{doc.source} [chunk {i + 1}]",
                    source_type=doc.source_type,
                )
            )
        logger.info("Split '%s' into %d chunks", doc.source, len(chunks))
        return chunks

    # ── Internal helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _clean(text: str) -> str:
        """Normalise whitespace and strip control characters."""
        text = re.sub(r"[\r\n]+", "\n", text)          # normalise newlines
        text = re.sub(r"[ \t]+", " ", text)             # collapse spaces/tabs
        text = re.sub(r"\n{3,}", "\n\n", text)          # max two consecutive newlines
        return text.strip()

    def _maybe_truncate(self, text: str) -> tuple[bool, str]:
        """Truncate text to config.max_input_chars and return (was_truncated, text)."""
        if len(text) > self.config.max_input_chars:
            logger.warning(
                "Text truncated from %d to %d chars.", len(text), self.config.max_input_chars
            )
            return True, text[: self.config.max_input_chars]
        return False, text

    @staticmethod
    def _extract_text_from_html(html: str) -> str:
        """Extract readable text from HTML — uses BeautifulSoup if available."""
        try:
            from bs4 import BeautifulSoup  # optional dependency
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()
            return soup.get_text(separator=" ")
        except ImportError:
            logger.warning("beautifulsoup4 not installed — stripping HTML with regex fallback.")
            return re.sub(r"<[^>]+>", " ", html)
