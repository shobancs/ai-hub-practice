"""
interfaces/api.py - FastAPI REST interface

Demonstrates: how a clean core layer enables building a production HTTP API
with no changes to the business logic modules.

Run:
    uvicorn text_processor.interfaces.api:app --reload --port 8000
    # then open http://localhost:8000/docs  (Swagger UI)

Endpoints:
    POST /summarize
    POST /sentiment
    POST /action-items
    POST /improve
    GET  /history
    GET  /stats
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

# ── resolve imports ────────────────────────────────────────────────────────────
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from text_processor.core import AppConfig, LLMClient, PromptTemplates, DocumentProcessor
    from text_processor.storage import Database
else:
    from ..core import AppConfig, LLMClient, PromptTemplates, DocumentProcessor
    from ..storage import Database

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError:
    print("FastAPI is not installed. Run:  pip install fastapi uvicorn")
    sys.exit(1)


# ── App singleton ──────────────────────────────────────────────────────────────

app       = FastAPI(
    title="AI Text Processor API",
    description="Summarize, analyse sentiment, extract actions, and improve writing via REST.",
    version="1.0.0",
)
_config    = AppConfig()
_templates = PromptTemplates()
_dp        = DocumentProcessor(_config)
_db        = Database(_config.db_path)


def _client(model: str = "gpt-4o-mini") -> LLMClient:
    cfg = AppConfig(model=model)
    cfg.validate()
    return LLMClient(cfg)


# ── Request / Response schemas ────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str           = Field(..., description="Text to process")
    url:  Optional[str] = Field(None, description="URL to fetch instead of text")
    model: str          = Field("gpt-5.2", description="OpenAI model to use")


class SummarizeRequest(TextInput):
    style:    str = Field("bullet_points", description="bullet_points | paragraph | key_takeaways | tldr")
    length:   str = Field("medium",        description="short | medium | long")
    audience: str = Field("general",       description="Target audience")


class ImproveRequest(TextInput):
    goal: str = Field("clarity", description="clarity | conciseness | formal | casual | persuasive")


class ClassifyRequest(TextInput):
    categories: list[str] = Field(..., description="List of category labels")


class QARequest(BaseModel):
    question: str  = Field(..., description="Question to answer")
    context:  str  = Field(..., description="Source text to answer from")
    model:    str  = Field("gpt-4o-mini")


class OperationResponse(BaseModel):
    result:        str
    model:         str
    input_tokens:  int
    output_tokens: int
    cost_usd:      float
    latency_ms:    float


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/summarize", response_model=OperationResponse, tags=["Operations"])
def summarize(req: SummarizeRequest):
    """Summarize text or a web URL."""
    try:
        doc = _dp.from_url(req.url) if req.url else _dp.from_text(req.text)
        pair = _templates.summarize(doc.content, style=req.style, length=req.length, audience=req.audience)
        resp = _client(req.model).chat(pair.user, system_message=pair.system)
        _db.save_result("summarize", doc.source, resp.content, input_text=doc.content,
                        model=resp.model, input_tokens=resp.input_tokens,
                        output_tokens=resp.output_tokens, cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
        return OperationResponse(result=resp.content, model=resp.model,
                                 input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                                 cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/sentiment", response_model=OperationResponse, tags=["Operations"])
def sentiment(req: TextInput):
    """Analyse sentiment and tone from text."""
    try:
        doc  = _dp.from_text(req.text)
        pair = _templates.analyze_sentiment(doc.content)
        resp = _client(req.model).chat(pair.user, system_message=pair.system, temperature=0.0)
        _db.save_result("sentiment", "api", resp.content, input_text=doc.content, model=resp.model,
                        input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                        cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
        return OperationResponse(result=resp.content, model=resp.model,
                                 input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                                 cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/action-items", response_model=OperationResponse, tags=["Operations"])
def action_items(req: TextInput):
    """Extract action items, owners, and deadlines from meeting notes."""
    try:
        doc  = _dp.from_text(req.text)
        pair = _templates.extract_action_items(doc.content)
        resp = _client(req.model).chat(pair.user, system_message=pair.system, temperature=0.0)
        _db.save_result("action_items", "api", resp.content, input_text=doc.content, model=resp.model,
                        input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                        cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
        return OperationResponse(result=resp.content, model=resp.model,
                                 input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                                 cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/improve", response_model=OperationResponse, tags=["Operations"])
def improve_writing(req: ImproveRequest):
    """Improve writing for clarity, formality, brevity etc."""
    try:
        doc  = _dp.from_text(req.text)
        pair = _templates.improve_writing(doc.content, goal=req.goal)
        resp = _client(req.model).chat(pair.user, system_message=pair.system)
        _db.save_result("improve_writing", "api", resp.content, input_text=doc.content, model=resp.model,
                        input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                        cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
        return OperationResponse(result=resp.content, model=resp.model,
                                 input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                                 cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/classify", response_model=OperationResponse, tags=["Operations"])
def classify(req: ClassifyRequest):
    """Zero-shot classify text into one of the provided categories."""
    try:
        doc  = _dp.from_text(req.text)
        pair = _templates.classify(doc.content, categories=req.categories)
        resp = _client(req.model).chat(pair.user, system_message=pair.system, temperature=0.0)
        _db.save_result("classify", "api", resp.content, input_text=doc.content, model=resp.model,
                        input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                        cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
        return OperationResponse(result=resp.content, model=resp.model,
                                 input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                                 cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/qa", response_model=OperationResponse, tags=["Operations"])
def question_answer(req: QARequest):
    """Answer a question strictly from the provided context."""
    try:
        pair = _templates.answer_from_context(req.question, req.context)
        resp = _client(req.model).chat(pair.user, system_message=pair.system)
        _db.save_result("qa", "api", resp.content, input_text=req.context, model=resp.model,
                        input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                        cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
        return OperationResponse(result=resp.content, model=resp.model,
                                 input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                                 cost_usd=resp.cost_usd, latency_ms=resp.latency_ms)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/history", tags=["Monitoring"])
def history(limit: int = 20):
    """Return the most recent operation history."""
    return _db.get_history(limit=limit)


@app.get("/stats", tags=["Monitoring"])
def stats():
    """Return cumulative usage statistics."""
    return _db.get_stats()


@app.get("/health", tags=["Monitoring"])
def health():
    return {"status": "ok", "model": _config.model}
