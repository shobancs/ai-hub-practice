"""
interfaces/cli.py - Interactive command-line interface

Demonstrates: argparse, rich terminal output, interactive menus.
Reusable pattern: the CLI is just a thin shell over the core modules —
  swap it out for any other interface without changing business logic.

Run:
    python -m text_processor.interfaces.cli --help
    python -m text_processor.interfaces.cli summarize --text "Your text here"
    python -m text_processor.interfaces.cli summarize --file notes.md
    python -m text_processor.interfaces.cli summarize --url https://example.com
    python -m text_processor.interfaces.cli sentiment --text "I love this product!"
    python -m text_processor.interfaces.cli history
    python -m text_processor.interfaces.cli stats
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

# ─ local imports ──────────────────────────────────────────────────────────────
# Support both `python cli.py` and `python -m text_processor.interfaces.cli`
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from text_processor.core import AppConfig, LLMClient, PromptTemplates, DocumentProcessor
    from text_processor.storage import Database
else:
    from ..core import AppConfig, LLMClient, PromptTemplates, DocumentProcessor
    from ..storage import Database


# ── Helpers ────────────────────────────────────────────────────────────────────

def _divider(char: str = "─", width: int = 60) -> str:
    return char * width


def _print_result(label: str, content: str, meta: dict | None = None) -> None:
    print(f"\n{_divider()}")
    print(f"  {label}")
    print(_divider())
    print(textwrap.fill(content, width=70) if "\n" not in content else content)
    if meta:
        print(_divider("·"))
        for k, v in meta.items():
            print(f"  {k:20s}: {v}")
    print(_divider())


def _load_input(args) -> tuple[str, str, str]:
    """
    Resolve text / file / url from args.
    Returns (text, source_label, source_type).
    """
    config = AppConfig()
    dp = DocumentProcessor(config)

    if hasattr(args, "text") and args.text:
        doc = dp.from_text(args.text)
    elif hasattr(args, "file") and args.file:
        doc = dp.from_file(args.file)
    elif hasattr(args, "url") and args.url:
        doc = dp.from_url(args.url)
    else:
        print("Error: provide --text, --file, or --url")
        sys.exit(1)

    if doc.was_truncated:
        print(f"⚠  Input truncated to {config.max_input_chars:,} characters.")
    return doc.content, doc.source, doc.source_type


# ── Sub-commands ───────────────────────────────────────────────────────────────

def cmd_summarize(args) -> None:
    text, source, source_type = _load_input(args)

    config = AppConfig(
        model=args.model,
        budget_limit_usd=args.budget,
    )
    config.validate()

    client    = LLMClient(config)
    db        = Database(config.db_path)
    templates = PromptTemplates()

    pair = templates.summarize(
        text,
        style=args.style,
        length=args.length,
        audience=args.audience,
    )

    # Check cache first
    if config.cache_enabled:
        cached = db.get_cached(text, f"summarize:{args.style}:{args.length}")
        if cached:
            _print_result("SUMMARY (cached)", cached, {"source": source})
            return

    response = client.chat(pair.user, system_message=pair.system)
    result   = response.content

    # Persist
    db.save_result(
        "summarize", source, result,
        source_type=source_type,
        input_text=text,
        model=response.model,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
        latency_ms=response.latency_ms,
    )
    if config.cache_enabled:
        db.cache_result(text, f"summarize:{args.style}:{args.length}", result)

    _print_result(
        "SUMMARY",
        result,
        {
            "source":  source,
            "model":   response.model,
            "tokens":  f"{response.input_tokens}in + {response.output_tokens}out",
            "cost":    f"${response.cost_usd:.4f}",
            "latency": f"{response.latency_ms:.0f} ms",
        },
    )


def cmd_sentiment(args) -> None:
    text, source, source_type = _load_input(args)

    config = AppConfig(model=args.model)
    config.validate()
    client    = LLMClient(config)
    db        = Database(config.db_path)
    templates = PromptTemplates()

    pair     = templates.analyze_sentiment(text)
    response = client.chat(pair.user, system_message=pair.system, temperature=0.0)

    # Pretty-print JSON
    try:
        parsed = json.loads(response.content)
        result_str = json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        result_str = response.content

    db.save_result(
        "sentiment", source, result_str,
        source_type=source_type,
        input_text=text,
        model=response.model,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
        latency_ms=response.latency_ms,
    )
    _print_result("SENTIMENT ANALYSIS", result_str, {"source": source, "cost": f"${response.cost_usd:.4f}"})


def cmd_action_items(args) -> None:
    text, source, source_type = _load_input(args)

    config = AppConfig(model=args.model)
    config.validate()
    client    = LLMClient(config)
    db        = Database(config.db_path)
    templates = PromptTemplates()

    pair     = templates.extract_action_items(text)
    response = client.chat(pair.user, system_message=pair.system, temperature=0.0)

    try:
        parsed     = json.loads(response.content)
        result_str = json.dumps(parsed, indent=2)
        items      = parsed.get("action_items", [])
        print(f"\n  Found {len(items)} action item(s):\n")
        for i, item in enumerate(items, 1):
            print(f"  {i}. [{item.get('priority','?').upper()}] {item.get('task','')}")
            print(f"     Owner: {item.get('owner','?')} | Due: {item.get('due','?')}\n")
    except json.JSONDecodeError:
        result_str = response.content
        _print_result("ACTION ITEMS", result_str)

    db.save_result("action_items", source, result_str, input_text=text, model=response.model,
                   input_tokens=response.input_tokens, output_tokens=response.output_tokens,
                   cost_usd=response.cost_usd, latency_ms=response.latency_ms)


def cmd_history(args) -> None:
    config = AppConfig()
    db     = Database(config.db_path)
    rows   = db.get_history(limit=args.limit)
    if not rows:
        print("No history yet.")
        return
    print(f"\n{'ID':>4}  {'Created':19}  {'Operation':15}  {'Source':30}  {'Cost':>8}")
    print(_divider("─", 85))
    for r in rows:
        print(f"{r['id']:>4}  {r['created_at'][:19]}  {r['operation']:15}  "
              f"{str(r['source'])[:30]:30}  ${r['cost_usd']:>7.4f}")


def cmd_stats(args) -> None:
    config = AppConfig()
    db     = Database(config.db_path)
    stats  = db.get_stats()
    print("\n── Session Stats ───────────────────────────────────")
    for k, v in stats.items():
        if k == "operations_breakdown":
            print("  Operations:")
            for op, cnt in v.items():
                print(f"    {op:20s}: {cnt}")
        else:
            print(f"  {k:30s}: {v}")


# ── Argument parser ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="text-processor",
        description="AI-powered text processing tool — summarize, analyse, extract and more.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python -m text_processor.interfaces.cli summarize --text "Paste your text here"
          python -m text_processor.interfaces.cli summarize --file meeting_notes.md --style key_takeaways
          python -m text_processor.interfaces.cli summarize --url https://en.wikipedia.org/wiki/Python_(programming_language)
          python -m text_processor.interfaces.cli sentiment --text "The product is amazing but shipping was slow."
          python -m text_processor.interfaces.cli action-items --file meeting_notes.txt
          python -m text_processor.interfaces.cli history --limit 5
          python -m text_processor.interfaces.cli stats
        """),
    )

    # ── Global options
    parser.add_argument(
        "--model", default="gpt-5.2",
        choices=["gpt-5.2", "gpt-5.2-chat-latest", "gpt-5.1", "gpt-5", "gpt-5-mini",
                 "gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-4o-mini",
                 "o3", "o3-mini", "o1", "gpt-3.5-turbo"],
        help="LLM to use (default: gpt-5.2)",
    )
    parser.add_argument("--budget", type=float, default=5.0, help="Max spend in USD (default: 5.0)")

    subs = parser.add_subparsers(dest="command", required=True)

    # ── summarize
    p_sum = subs.add_parser("summarize", help="Summarize text")
    _add_input_args(p_sum)
    p_sum.add_argument("--style",    default="bullet_points",
                       choices=["bullet_points", "paragraph", "key_takeaways", "tldr"])
    p_sum.add_argument("--length",   default="medium",   choices=["short", "medium", "long"])
    p_sum.add_argument("--audience", default="general",  help="Target audience (e.g. 'expert', 'student')")
    p_sum.set_defaults(func=cmd_summarize)

    # ── sentiment
    p_sen = subs.add_parser("sentiment", help="Analyse sentiment and tone")
    _add_input_args(p_sen)
    p_sen.set_defaults(func=cmd_sentiment)

    # ── action-items
    p_act = subs.add_parser("action-items", help="Extract action items and owners")
    _add_input_args(p_act)
    p_act.set_defaults(func=cmd_action_items)

    # ── history
    p_hist = subs.add_parser("history", help="Show operation history")
    p_hist.add_argument("--limit", type=int, default=20, help="Number of rows to show")
    p_hist.set_defaults(func=cmd_history)

    # ── stats
    p_stats = subs.add_parser("stats", help="Show usage statistics and costs")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def _add_input_args(p: argparse.ArgumentParser) -> None:
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Raw text string")
    group.add_argument("--file", help="Path to a .txt or .md file")
    group.add_argument("--url",  help="Web URL to fetch and process")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as exc:
        print(f"\nError: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
