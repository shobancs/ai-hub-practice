# Chapter 1: Prompt Chaining

> Decompose a complex task into a sequence of simpler LLM calls, where each step's output feeds the next.

## 🧠 Concept

Instead of asking one huge prompt to do everything, you **chain** multiple focused prompts together. Each link in the chain does one thing well.

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Step 1   │────▶│  Step 2   │────▶│  Step 3   │────▶│  Step 4   │
│ Extract   │     │ Analyse   │     │ Generate  │     │ Format   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
  Raw Input      Structured       Insight /         Final Output
                   Data           Draft
```

## Why Prompt Chaining?

| Benefit | Explanation |
|---------|-------------|
| **Better accuracy** | Each step has a narrow, clear goal |
| **Easier debugging** | You can inspect intermediate outputs |
| **Reusability** | Steps can be reused across different chains |
| **Token efficiency** | Smaller prompts = less waste |

## When to Use

- Multi-step content creation (research → outline → draft → edit)
- Data pipelines (extract → transform → validate → load)
- Any task that can be broken into sequential stages

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PROMPT CHAIN                           │
│                                                          │
│  Input ──▶ [Prompt A] ──▶ [Gate?] ──▶ [Prompt B] ──▶   │
│                              │                           │
│                         (optional                        │
│                          validation)                     │
│                                                          │
│            ──▶ [Prompt C] ──▶ Output                     │
└─────────────────────────────────────────────────────────┘
```

**Gate / Checkpoint**: Between steps you can add validation — if the output of step N isn't good enough, retry or abort.

## Code Example — Blog Post Generator

```python
from openai import OpenAI
from dotenv import load_dotenv
import os, json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(system: str, user: str) -> str:
    """Helper: single LLM call."""
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return r.choices[0].message.content


# ── Step 1: Research ──────────────────────────────────────

def step_research(topic: str) -> str:
    return call_llm(
        "You are a research assistant. Given a topic, list 5 key points "
        "with one-sentence explanations. Output as a numbered list.",
        f"Topic: {topic}",
    )


# ── Step 2: Outline ──────────────────────────────────────

def step_outline(research: str) -> str:
    return call_llm(
        "You are a content strategist. Given research notes, create a "
        "blog post outline with: Title, Hook, 3-4 sections, conclusion. "
        "Format as Markdown headers.",
        f"Research:\n{research}",
    )


# ── Step 3: Draft ────────────────────────────────────────

def step_draft(outline: str) -> str:
    return call_llm(
        "You are a blog writer. Expand the outline into a full blog "
        "post (~500 words). Make it engaging and informative.",
        f"Outline:\n{outline}",
    )


# ── Step 4: Polish ───────────────────────────────────────

def step_polish(draft: str) -> str:
    return call_llm(
        "You are an editor. Improve this blog post for clarity, grammar, "
        "and flow. Add a catchy opening and strong closing. "
        "Return the final polished post.",
        f"Draft:\n{draft}",
    )


# ── Run the Chain ────────────────────────────────────────

def run_chain(topic: str) -> str:
    print(f"📝 Step 1: Researching '{topic}'...")
    research = step_research(topic)
    print(f"✅ Research done.\n")

    print("📋 Step 2: Creating outline...")
    outline = step_outline(research)
    print(f"✅ Outline ready.\n")

    print("✍️  Step 3: Writing draft...")
    draft = step_draft(outline)
    print(f"✅ Draft written.\n")

    print("🔍 Step 4: Polishing...")
    final = step_polish(draft)
    print(f"✅ Final post ready!\n")

    return final


if __name__ == "__main__":
    post = run_chain("Why Agentic AI is the next big thing in 2026")
    print("=" * 60)
    print(post)
```

## Key Design Decisions

1. **Fixed vs. Dynamic chains** — The example above is fixed (always 4 steps). Dynamic chains decide the next step based on intermediate results.
2. **Error handling** — If Step 2 fails, do you retry it or restart from Step 1? Good chains have retry logic per step.
3. **State passing** — Each step receives only what it needs. Avoid dumping the full history into every prompt.

## Pattern Variants

| Variant | Description |
|---------|-------------|
| **Linear chain** | A → B → C → D (fixed order) |
| **Gated chain** | A → [check] → B or retry A |
| **Branching chain** | A → if X then B, else C |
| **Looping chain** | A → B → [quality check] → repeat B if poor |

## 🏋️ Practice

→ [Exercise: Prompt Chaining](../exercises/agentic/01_prompt_chaining.py)
