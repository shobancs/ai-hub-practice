# Chapter 2: Routing

> Classify the user's intent and route to the most appropriate specialised handler.

## 🧠 Concept

A **router** acts as a dispatcher. It inspects the input, determines which category it belongs to, and forwards it to a specialist — either a dedicated prompt, a tool, or another agent entirely.

```
                          ┌──────────────┐
                          │   ROUTER     │
                          │  (Classify)  │
                          └──────┬───────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                 ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │  Handler A   │ │  Handler B   │ │  Handler C   │
        │  (Billing)   │ │  (Technical) │ │  (General)   │
        └──────────────┘ └──────────────┘ └──────────────┘
```

## Why Routing?

| Benefit | Explanation |
|---------|-------------|
| **Specialisation** | Each handler has a focused system prompt |
| **Accuracy** | Narrow context → better responses |
| **Scalability** | Add new routes without changing existing handlers |
| **Cost control** | Route simple queries to cheaper models |

## When to Use

- Customer support with multiple departments
- Multi-lingual systems (route by language)
- Complexity-based routing (simple → GPT-4o-mini, hard → GPT-4o)
- Content moderation pipelines

## Architecture

```
┌───────────────────────────────────────────────────┐
│                 ROUTING PATTERN                     │
│                                                     │
│  Input ──▶ [Classifier LLM] ──▶ category           │
│                                     │               │
│              ┌──────────────────────┤               │
│              ▼           ▼          ▼               │
│          Handler A   Handler B   Handler C          │
│              │           │          │               │
│              └──────────┬┘──────────┘               │
│                         ▼                           │
│                      Output                         │
└───────────────────────────────────────────────────┘
```

## Code Example — Customer Support Router

```python
import json, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(system: str, user: str) -> str:
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return r.choices[0].message.content


# ── Step 1: Classify ─────────────────────────────────────

def classify(query: str) -> str:
    """Route the query to the right department."""
    result = call_llm(
        "Classify the customer query into exactly ONE category.\n"
        "Categories: billing, technical, general, complaint\n"
        "Respond with ONLY the category name, nothing else.",
        query,
    )
    return result.strip().lower()


# ── Step 2: Specialised Handlers ─────────────────────────

HANDLERS = {
    "billing": (
        "You are a billing specialist. Help with invoices, payments, "
        "refunds, and subscription changes. Be precise with amounts."
    ),
    "technical": (
        "You are a technical support engineer. Help diagnose issues, "
        "suggest fixes, and walk users through step-by-step solutions."
    ),
    "general": (
        "You are a general customer service rep. Be friendly and helpful. "
        "Answer questions about products, policies, and company info."
    ),
    "complaint": (
        "You are a customer relations specialist handling complaints. "
        "Be empathetic, acknowledge the issue, and offer resolution."
    ),
}

def handle(category: str, query: str) -> str:
    system_prompt = HANDLERS.get(category, HANDLERS["general"])
    return call_llm(system_prompt, query)


# ── Run ──────────────────────────────────────────────────

def route_and_respond(query: str) -> str:
    category = classify(query)
    print(f"  🏷️  Routed to: {category.upper()}")
    response = handle(category, query)
    return response


if __name__ == "__main__":
    queries = [
        "I was charged twice for my subscription",
        "My app keeps crashing when I open settings",
        "What are your store hours?",
        "This is the worst service I've ever experienced!",
    ]

    for q in queries:
        print(f"\n{'='*50}")
        print(f"📩 Query: {q}")
        answer = route_and_respond(q)
        print(f"💬 Response: {answer}\n")
```

## Key Design Decisions

1. **LLM classifier vs. rule-based** — Use LLM when categories are fuzzy; use regex/keywords when they're clear-cut.
2. **Confidence threshold** — If the classifier isn't confident, fall back to a general handler or ask a clarifying question.
3. **Model routing** — Route to different *models* (cheap vs. expensive) based on complexity, not just different prompts.

## Pattern Variants

| Variant | Description |
|---------|-------------|
| **Intent routing** | Route by user intent (buy, cancel, ask) |
| **Model routing** | Easy → mini model, Hard → large model |
| **Language routing** | Detect language → route to translated handler |
| **Cascading routing** | Route → sub-route → handler (hierarchical) |

## 🏋️ Practice

→ [Exercise: Routing](../exercises/agentic/02_routing.py)
