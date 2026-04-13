# 🧠 AI Text Processor

A **production-ready, modular AI application** built on OpenAI.  
Use it as a learning project, a reusable template, or a daily productivity tool.

---

## Features

| Operation | Description |
|-----------|-------------|
| **Summarize** | Bullet points, paragraph, key takeaways, TL;DR — any length |
| **Sentiment** | Sentiment, confidence, tone, and detected emotions (JSON) |
| **Action Items** | Extract tasks, owners, and deadlines from meeting notes |
| **Improve Writing** | Rewrite for clarity, conciseness, formal, casual, or persuasive tone |
| **Classify** | Zero-shot classification into custom categories |
| **Q&A** | Answer questions strictly from provided context |
| **Translate** | Translate to any language |

All results are **saved to SQLite** with full cost and token tracking.

---

## Project Structure

```
text_processor/
├── core/
│   ├── config.py            # Centralized settings, model costs, budget cap
│   ├── llm_client.py        # OpenAI wrapper — retries, token tracking, cost
│   ├── prompts.py           # Reusable prompt templates (the "brain")
│   └── document_processor.py# Text / file / URL ingestion layer
├── storage/
│   └── database.py          # SQLite: history, caching, stats
├── interfaces/
│   ├── cli.py               # argparse command-line interface
│   ├── web_ui.py            # Gradio browser UI
│   └── api.py               # FastAPI REST endpoints
├── tests/
│   └── test_core.py         # Unit tests (no API key needed)
├── main.py                  # Single entry point
├── requirements.txt
└── .env.example
```

> **Reusable pattern**: `core/` has zero UI dependencies.  
> Swap `cli.py`, `web_ui.py`, or `api.py` independently.

---

## Quick Start

### 1. Install dependencies
```bash
cd GenAI/examples/text_processor
pip install -r requirements.txt
```

### 2. Set up your API key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run
```bash
# Interactive menu
python main.py

# Direct CLI commands
python main.py summarize --text "Paste your text here"
python main.py summarize --file notes.md --style key_takeaways
python main.py summarize --url https://en.wikipedia.org/wiki/Python_(programming_language)
python main.py sentiment --text "I love this product but shipping was slow."
python main.py action-items --file meeting_notes.txt
python main.py history
python main.py stats

# Web UI (browser)
python main.py --web        # opens http://localhost:7860

# REST API
python main.py --api        # opens http://localhost:8000/docs
```

---

## CLI Reference

```
python main.py summarize --text "..." [--style bullet_points] [--length medium] [--audience general] [--model gpt-4o-mini]
python main.py summarize --file path/to/file.md
python main.py summarize --url https://...
python main.py sentiment  --text "..."
python main.py action-items --text "..." | --file ...
python main.py history [--limit 20]
python main.py stats
```

### Available models
| Model | Speed | Cost | Best for |
|-------|-------|------|----------|
| `gpt-4o-mini` | Fast | Lowest | Learning, dev, most tasks |
| `gpt-4o` | Fast | Medium | Higher accuracy |
| `gpt-3.5-turbo` | Fast | Low | Simple tasks |
| `gpt-4-turbo` | Slower | High | Complex reasoning |

---

## REST API

Start the API:
```bash
python main.py --api
# Swagger docs: http://localhost:8000/docs
```

Example requests:
```bash
# Summarize
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here...", "style": "bullet_points", "length": "medium"}'

# Sentiment
curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "The product is amazing but expensive."}'

# Stats
curl http://localhost:8000/stats
```

---

## Cost Awareness

The app tracks every API call:

```
tokens: 245in + 87out  |  cost: $0.0001  |  latency: 842ms
```

View cumulative spend:
```bash
python main.py stats
```

Default budget cap is **$5.00** — configurable in `AppConfig`.

---

## How to Extend

### Add a new operation
1. Add a new `PromptPair` method in `core/prompts.py`
2. Add a CLI sub-command in `interfaces/cli.py`
3. Add a Gradio tab in `interfaces/web_ui.py`
4. Add a FastAPI endpoint in `interfaces/api.py`

### Add a new input source (e.g. PDF)
Edit `core/document_processor.py` and add a `from_pdf()` method.  
All interfaces pick it up automatically.

### Switch models
```python
config = AppConfig(model="gpt-4o")
```

---

## Learning Checkpoints

After building this app, you should be able to explain:

- [ ] Why we separate `core/` from `interfaces/`
- [ ] How the retry logic in `llm_client.py` handles rate limits
- [ ] Why prompt templates are centralized in `prompts.py`
- [ ] How `database.py` enables caching and cost tracking
- [ ] How the same core powers CLI, web UI, and REST API

---

## Next Steps

- [ ] Add PDF/DOCX support in `document_processor.py`
- [ ] Add streaming responses (word-by-word output)
- [ ] Add a `/translate` endpoint
- [ ] Add authentication to the REST API
- [ ] Deploy to Azure Container Apps or Fly.io
- [ ] Add evaluation: compare GPT-4o-mini vs GPT-4o quality

---

*Part of the [AI Hub Practice](../../README.md) training curriculum — Module 4: Hands-On Development.*
