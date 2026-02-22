"""
tests/test_core.py - Unit tests for core modules (no API key needed)

Run:
    cd GenAI/examples/text_processor
    python -m pytest tests/ -v
"""
import json
import sys
import tempfile
import os
from pathlib import Path
import pytest

# Make sure the package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from text_processor.core.config import AppConfig, MODEL_COSTS
from text_processor.core.prompts import PromptTemplates
from text_processor.core.document_processor import DocumentProcessor, Document
from text_processor.storage.database import Database


# ── AppConfig tests ────────────────────────────────────────────────────────────

class TestAppConfig:
    def test_default_model_is_valid(self):
        config = AppConfig()
        assert config.model in MODEL_COSTS

    def test_validate_raises_without_api_key(self):
        config = AppConfig(openai_api_key="")
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            config.validate()

    def test_validate_raises_for_unknown_model(self):
        config = AppConfig(openai_api_key="sk-test", model="gpt-999")
        with pytest.raises(ValueError, match="Unknown model"):
            config.validate()

    def test_estimate_cost_is_non_negative(self):
        config = AppConfig()
        cost = config.estimate_cost(100, 200)
        assert cost >= 0.0

    def test_available_models_matches_cost_table(self):
        config = AppConfig()
        assert set(config.available_models) == set(MODEL_COSTS.keys())

    def test_cost_per_1k_returns_float(self):
        config = AppConfig()
        assert isinstance(config.cost_per_1k("input"), float)
        assert isinstance(config.cost_per_1k("output"), float)


# ── PromptTemplates tests ─────────────────────────────────────────────────────

class TestPromptTemplates:
    pt = PromptTemplates()
    SAMPLE = "The quick brown fox jumps over the lazy dog."

    def test_summarize_returns_prompt_pair(self):
        pair = self.pt.summarize(self.SAMPLE)
        assert pair.system and pair.user
        assert self.SAMPLE in pair.user

    def test_summarize_all_styles(self):
        for style in ["bullet_points", "paragraph", "key_takeaways", "tldr"]:
            pair = self.pt.summarize(self.SAMPLE, style=style)
            assert pair.user  # not empty

    def test_summarize_all_lengths(self):
        for length in ["short", "medium", "long"]:
            pair = self.pt.summarize(self.SAMPLE, length=length)
            assert pair.user

    def test_analyze_sentiment_instructs_json(self):
        pair = self.pt.analyze_sentiment(self.SAMPLE)
        assert "JSON" in pair.system or "JSON" in pair.user

    def test_extract_action_items_contains_text(self):
        pair = self.pt.extract_action_items("Alice will finish the report by Friday.")
        assert "Alice" in pair.user

    def test_classify_includes_all_categories(self):
        cats = ["sports", "politics", "tech"]
        pair = self.pt.classify(self.SAMPLE, categories=cats)
        for cat in cats:
            assert cat in pair.user

    def test_answer_from_context_includes_question(self):
        pair = self.pt.answer_from_context("What colour is the fox?", self.SAMPLE)
        assert "What colour" in pair.user
        assert self.SAMPLE in pair.user

    def test_translate_includes_target_language(self):
        pair = self.pt.translate(self.SAMPLE, "Spanish")
        assert "Spanish" in pair.system or "Spanish" in pair.user

    def test_improve_writing_unknown_goal_falls_back(self):
        pair = self.pt.improve_writing(self.SAMPLE, goal="unknown_goal")
        assert pair.user  # should not raise, should fall back

    def test_available_operations_is_dict(self):
        ops = PromptTemplates.available_operations()
        assert isinstance(ops, dict)
        assert len(ops) >= 5


# ── DocumentProcessor tests ───────────────────────────────────────────────────

class TestDocumentProcessor:
    config = AppConfig(openai_api_key="sk-test")
    dp = DocumentProcessor(config)
    SAMPLE = "Hello world. This is a test."

    def test_from_text_returns_document(self):
        doc = self.dp.from_text(self.SAMPLE)
        assert isinstance(doc, Document)
        assert doc.content == self.SAMPLE
        assert doc.source_type == "text"

    def test_from_text_sets_word_count(self):
        doc = self.dp.from_text(self.SAMPLE)
        assert doc.word_count > 0

    def test_from_text_truncates_large_input(self):
        big = "x " * 100_000
        doc = self.dp.from_text(big)
        assert doc.was_truncated
        assert doc.char_count <= self.config.max_input_chars + 10

    def test_from_file_raises_for_missing_file(self):
        with pytest.raises(FileNotFoundError):
            self.dp.from_file("/nonexistent/path/file.txt")

    def test_from_file_raises_for_unsupported_type(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"fake pdf")
            tmp_path = f.name
        try:
            with pytest.raises(ValueError, match="Unsupported"):
                self.dp.from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_from_file_loads_txt(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
            f.write("Hello from file!")
            tmp_path = f.name
        try:
            doc = self.dp.from_file(tmp_path)
            assert "Hello from file!" in doc.content
            assert doc.source_type == "file"
        finally:
            os.unlink(tmp_path)

    def test_chunk_splits_large_document(self):
        long_text = " ".join(["word"] * 5000)
        doc = self.dp.from_text(long_text)
        chunks = self.dp.chunk(doc)
        assert len(chunks) > 1
        for c in chunks:
            assert isinstance(c, Document)

    def test_chunk_small_document_returns_one(self):
        doc = self.dp.from_text("Short text.")
        chunks = self.dp.chunk(doc)
        assert len(chunks) == 1

    def test_clean_normalises_whitespace(self):
        messy = "  Hello   world\n\n\n\nFoo  "
        doc = self.dp.from_text(messy)
        assert "   " not in doc.content
        assert doc.content.startswith("Hello")


# ── Database tests ─────────────────────────────────────────────────────────────

class TestDatabase:
    def setup_method(self):
        """Use an in-memory-like temp DB for each test."""
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = Database(self.tmp.name)

    def teardown_method(self):
        self.db.close()
        os.unlink(self.tmp.name)

    def test_save_and_retrieve_result(self):
        row_id = self.db.save_result("summarize", "test.txt", "Summary text",
                                     input_text="original", model="gpt-4o-mini",
                                     input_tokens=100, output_tokens=50, cost_usd=0.001)
        assert row_id > 0
        history = self.db.get_history(limit=1)
        assert len(history) == 1
        assert history[0]["operation"] == "summarize"
        assert history[0]["result"] == "Summary text"

    def test_cache_hit_and_miss(self):
        self.db.cache_result("my input", "summarize", "Cached result")
        hit = self.db.get_cached("my input", "summarize")
        assert hit == "Cached result"

        miss = self.db.get_cached("other input", "summarize")
        assert miss is None

    def test_cache_miss_different_operation(self):
        self.db.cache_result("my input", "summarize", "Result A")
        miss = self.db.get_cached("my input", "sentiment")
        assert miss is None

    def test_get_stats_returns_expected_keys(self):
        stats = self.db.get_stats()
        assert "total_operations" in stats
        assert "total_cost_usd" in stats
        assert "total_tokens" in stats

    def test_get_total_cost_starts_at_zero(self):
        cost = self.db.get_total_cost()
        assert cost == 0.0

    def test_get_total_cost_accumulates(self):
        self.db.save_result("summarize", "src", "res", cost_usd=0.005)
        self.db.save_result("sentiment", "src", "res", cost_usd=0.002)
        cost = self.db.get_total_cost()
        assert abs(cost - 0.007) < 1e-6

    def test_get_history_filter_by_operation(self):
        self.db.save_result("summarize", "src", "res1")
        self.db.save_result("sentiment", "src", "res2")
        rows = self.db.get_history(operation="summarize")
        assert all(r["operation"] == "summarize" for r in rows)

    def test_cache_replace_updates_result(self):
        self.db.cache_result("input", "summarize", "old result")
        self.db.cache_result("input", "summarize", "new result")
        result = self.db.get_cached("input", "summarize")
        assert result == "new result"
