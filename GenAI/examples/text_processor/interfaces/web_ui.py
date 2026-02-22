"""
interfaces/web_ui.py - Gradio browser-based interface

Demonstrates: how the same core logic powers a completely different
interface without any changes to prompts.py, llm_client.py, etc.

Run:
    python -m text_processor.interfaces.web_ui
    # then open http://localhost:7860
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ── resolve imports for both direct and module run ────────────────────────────
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from text_processor.core import AppConfig, LLMClient, PromptTemplates, DocumentProcessor
    from text_processor.storage import Database
else:
    from ..core import AppConfig, LLMClient, PromptTemplates, DocumentProcessor
    from ..storage import Database


def _get_deps():
    """Lazy-import Gradio so the rest of the app still works without it."""
    try:
        import gradio as gr
        return gr
    except ImportError:
        print("Gradio is not installed. Run:  pip install gradio")
        sys.exit(1)


# ── Shared app singletons (created once at startup) ───────────────────────────
_config    = AppConfig()
_templates = PromptTemplates()
_dp        = DocumentProcessor(_config)
_db        = Database(_config.db_path)


def _make_client(model: str) -> LLMClient:
    cfg = AppConfig(model=model)
    cfg.validate()
    return LLMClient(cfg)


# ── Operation handlers ─────────────────────────────────────────────────────────

def handle_summarize(text: str, url: str, style: str, length: str, audience: str, model: str):
    try:
        doc = _dp.from_url(url.strip()) if url.strip() else _dp.from_text(text)
    except Exception as exc:
        return f"Input error: {exc}", ""

    client   = _make_client(model)
    pair     = _templates.summarize(doc.content, style=style, length=length, audience=audience)
    response = client.chat(pair.user, system_message=pair.system)

    _db.save_result("summarize", doc.source, response.content, input_text=doc.content,
                    model=response.model, input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens, cost_usd=response.cost_usd,
                    latency_ms=response.latency_ms)

    meta = (f"Model: {response.model} | "
            f"Tokens: {response.input_tokens}+{response.output_tokens} | "
            f"Cost: ${response.cost_usd:.4f} | Latency: {response.latency_ms:.0f}ms")
    return response.content, meta


def handle_sentiment(text: str, model: str):
    if not text.strip():
        return "Please enter some text.", ""
    client   = _make_client(model)
    pair     = _templates.analyze_sentiment(text)
    response = client.chat(pair.user, system_message=pair.system, temperature=0.0)
    _db.save_result("sentiment", "web-input", response.content, input_text=text,
                    model=response.model, input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens, cost_usd=response.cost_usd)
    try:
        parsed = json.loads(response.content)
        result = json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        result = response.content
    meta = f"Cost: ${response.cost_usd:.4f}"
    return result, meta


def handle_action_items(text: str, model: str):
    if not text.strip():
        return "Please enter meeting notes or an email.", ""
    client   = _make_client(model)
    pair     = _templates.extract_action_items(text)
    response = client.chat(pair.user, system_message=pair.system, temperature=0.0)
    _db.save_result("action_items", "web-input", response.content, input_text=text,
                    model=response.model, input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens, cost_usd=response.cost_usd)
    try:
        parsed = json.loads(response.content)
        result = json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        result = response.content
    meta = f"Cost: ${response.cost_usd:.4f}"
    return result, meta


def handle_improve(text: str, goal: str, model: str):
    if not text.strip():
        return "Please enter text to improve.", ""
    client   = _make_client(model)
    pair     = _templates.improve_writing(text, goal=goal)
    response = client.chat(pair.user, system_message=pair.system)
    _db.save_result("improve_writing", "web-input", response.content, input_text=text,
                    model=response.model, input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens, cost_usd=response.cost_usd)
    meta = f"Cost: ${response.cost_usd:.4f}"
    return response.content, meta


def get_history_table():
    rows = _db.get_history(limit=15)
    return [[r["id"], r["created_at"][:19], r["operation"], str(r["source"])[:40],
             f"${r['cost_usd']:.4f}"] for r in rows]


def get_stats_text():
    s = _db.get_stats()
    lines = [
        f"Total Operations : {s['total_operations']}",
        f"Total Cost (USD) : ${s['total_cost_usd']:.4f}",
        f"Total Tokens     : {s['total_tokens']:,}",
        f"Avg Latency      : {s['avg_latency_ms']:.0f} ms",
        "",
        "── Operations Breakdown ──",
    ]
    for op, cnt in s.get("operations_breakdown", {}).items():
        lines.append(f"  {op:20s}: {cnt}")
    return "\n".join(lines)


# ── Build the Gradio UI ────────────────────────────────────────────────────────

def build_ui():
    gr = _get_deps()

    MODEL_CHOICES = ["gpt-5.2", "gpt-5.2-chat-latest", "gpt-5.1", "gpt-5", "gpt-5-mini",
                     "gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-4o-mini",
                     "o3", "o3-mini", "o1", "gpt-3.5-turbo"]

    with gr.Blocks(title="AI Text Processor") as demo:
        gr.Markdown("# 🧠 AI Text Processor\nPowered by OpenAI · Modular · Reusable")

        with gr.Tabs():

            # ── Summarize ──────────────────────────────────────────────────────
            with gr.Tab("📄 Summarize"):
                gr.Markdown("Summarize text or any web article.")
                with gr.Row():
                    with gr.Column():
                        sum_text  = gr.Textbox(label="Paste text here", lines=8, placeholder="Or leave empty and use URL below…")
                        sum_url   = gr.Textbox(label="Or enter a URL", placeholder="https://en.wikipedia.org/wiki/…")
                        sum_style = gr.Radio(["bullet_points", "paragraph", "key_takeaways", "tldr"],
                                             value="bullet_points", label="Style")
                        sum_len   = gr.Radio(["short", "medium", "long"], value="medium", label="Length")
                        sum_aud   = gr.Textbox(label="Audience", value="general", placeholder="e.g. expert, student, executive")
                        sum_model = gr.Dropdown(MODEL_CHOICES, value="gpt-4o-mini", label="Model")
                        sum_btn   = gr.Button("Summarize", variant="primary")
                    with gr.Column():
                        sum_out  = gr.Textbox(label="Summary", lines=12)
                        sum_meta = gr.Textbox(label="Usage info", interactive=False)
                sum_btn.click(handle_summarize,
                              inputs=[sum_text, sum_url, sum_style, sum_len, sum_aud, sum_model],
                              outputs=[sum_out, sum_meta])

            # ── Sentiment ──────────────────────────────────────────────────────
            with gr.Tab("😊 Sentiment"):
                gr.Markdown("Detect sentiment, tone, and emotions from text.")
                with gr.Row():
                    with gr.Column():
                        sen_text  = gr.Textbox(label="Text", lines=6)
                        sen_model = gr.Dropdown(MODEL_CHOICES, value="gpt-4o-mini", label="Model")
                        sen_btn   = gr.Button("Analyse", variant="primary")
                    with gr.Column():
                        sen_out  = gr.Code(label="Result (JSON)", language="json", lines=12)
                        sen_meta = gr.Textbox(label="Usage info", interactive=False)
                sen_btn.click(handle_sentiment, inputs=[sen_text, sen_model], outputs=[sen_out, sen_meta])

            # ── Action Items ───────────────────────────────────────────────────
            with gr.Tab("✅ Action Items"):
                gr.Markdown("Extract action items, owners, and deadlines from meeting notes or emails.")
                with gr.Row():
                    with gr.Column():
                        act_text  = gr.Textbox(label="Meeting notes / email", lines=8)
                        act_model = gr.Dropdown(MODEL_CHOICES, value="gpt-4o-mini", label="Model")
                        act_btn   = gr.Button("Extract", variant="primary")
                    with gr.Column():
                        act_out  = gr.Code(label="Action Items (JSON)", language="json", lines=12)
                        act_meta = gr.Textbox(label="Usage info", interactive=False)
                act_btn.click(handle_action_items, inputs=[act_text, act_model], outputs=[act_out, act_meta])

            # ── Improve Writing ────────────────────────────────────────────────
            with gr.Tab("✏️ Improve Writing"):
                gr.Markdown("Rewrite text for a specific goal.")
                with gr.Row():
                    with gr.Column():
                        imp_text  = gr.Textbox(label="Original text", lines=8)
                        imp_goal  = gr.Radio(["clarity", "conciseness", "formal", "casual", "persuasive"],
                                             value="clarity", label="Goal")
                        imp_model = gr.Dropdown(MODEL_CHOICES, value="gpt-4o-mini", label="Model")
                        imp_btn   = gr.Button("Improve", variant="primary")
                    with gr.Column():
                        imp_out  = gr.Textbox(label="Improved text", lines=10)
                        imp_meta = gr.Textbox(label="Usage info", interactive=False)
                imp_btn.click(handle_improve, inputs=[imp_text, imp_goal, imp_model], outputs=[imp_out, imp_meta])

            # ── History & Stats ────────────────────────────────────────────────
            with gr.Tab("📊 History & Stats"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Recent Operations")
                        hist_table = gr.Dataframe(
                            headers=["ID", "Time", "Operation", "Source", "Cost"],
                            value=get_history_table,
                            interactive=False,
                            every=30,
                        )
                        gr.Button("🔄 Refresh").click(get_history_table, outputs=hist_table)
                    with gr.Column():
                        gr.Markdown("### Cumulative Stats")
                        stats_out = gr.Textbox(label="Stats", lines=12, value=get_stats_text, every=30)

    return demo


def main():
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()
