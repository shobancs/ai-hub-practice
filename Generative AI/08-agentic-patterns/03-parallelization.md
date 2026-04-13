# Chapter 3: Parallelization

> Run independent sub-tasks concurrently, then merge the results.

## 🧠 Concept

When a task has parts that **don't depend on each other**, run them all at once instead of one-by-one. This slashes latency and is the agent equivalent of multi-threading.

```
                    ┌────────────────┐
                    │  SPLIT INPUT   │
                    └────────┬───────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │  Agent A   │ │  Agent B   │ │  Agent C   │
       │ (Analyse)  │ │ (Research) │ │ (Generate) │
       └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌────────────────┐
                    │   AGGREGATE    │
                    └────────────────┘
```

## Two Sub-Patterns

### 1. Sectioning (Split by sub-task)
Each worker does a **different** job on the **same** input.

```
"Review this product" ──▶  Worker A: Analyse features
                           Worker B: Check pricing
                           Worker C: Read user reviews
                    ──▶ Merge all into final review
```

### 2. Voting (Same task, multiple attempts)
Multiple workers do the **same** job; you pick the best or majority answer.

```
"Translate this text" ──▶  Worker A: Translation v1
                           Worker B: Translation v2
                           Worker C: Translation v3
                    ──▶ Pick best / majority vote
```

## When to Use

- Comparing multiple products, articles, or datasets
- Multi-perspective analysis (legal, financial, technical)
- Speed-critical tasks with independent components
- Ensemble answers for higher reliability

## Code Example — Parallel Product Analyser

```python
import asyncio, os, json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def call_llm(system: str, user: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return r.choices[0].message.content


# ── Parallel Workers ─────────────────────────────────────

async def analyse_features(product: str) -> dict:
    result = await call_llm(
        "You are a product features analyst. List the top 5 features "
        "and rate each out of 10.",
        f"Product: {product}",
    )
    return {"aspect": "features", "analysis": result}


async def analyse_pricing(product: str) -> dict:
    result = await call_llm(
        "You are a pricing analyst. Evaluate the pricing strategy, "
        "compare to competitors, and rate value-for-money out of 10.",
        f"Product: {product}",
    )
    return {"aspect": "pricing", "analysis": result}


async def analyse_reviews(product: str) -> dict:
    result = await call_llm(
        "You are a sentiment analyst. Summarise common user complaints "
        "and praises. Give an overall sentiment score (1-10).",
        f"Product: {product}",
    )
    return {"aspect": "user_sentiment", "analysis": result}


# ── Aggregator ───────────────────────────────────────────

async def aggregate(product: str, analyses: list[dict]) -> str:
    combined = "\n\n".join(
        f"### {a['aspect'].upper()}\n{a['analysis']}" for a in analyses
    )
    return await call_llm(
        "You are a senior product reviewer. Given analyses from multiple "
        "specialists, write a concise final verdict (200 words). "
        "Include an overall score out of 10.",
        f"Product: {product}\n\nAnalyses:\n{combined}",
    )


# ── Run ──────────────────────────────────────────────────

async def parallel_review(product: str):
    print(f"🔍 Analysing '{product}' in parallel...\n")

    analyses = await asyncio.gather(
        analyse_features(product),
        analyse_pricing(product),
        analyse_reviews(product),
    )

    for a in analyses:
        print(f"  ✅ {a['aspect']} done")

    print("\n📝 Aggregating...")
    verdict = await aggregate(product, analyses)
    return verdict


if __name__ == "__main__":
    result = asyncio.run(parallel_review("iPhone 16 Pro Max"))
    print("\n" + "=" * 50)
    print(result)
```

## Parallel vs. Sequential — When Each Wins

| Scenario | Better Pattern |
|----------|---------------|
| Steps depend on each other | Sequential (chaining) |
| Steps are independent | **Parallel** |
| Need majority vote / ensemble | **Parallel (voting)** |
| Output of step N is input to step N+1 | Sequential |
| Latency is critical | **Parallel** |

## Key Design Decisions

1. **Error handling** — If one worker fails, do you: retry, skip it, or abort all?
2. **Timeout** — Set a max wait time. Don't let one slow worker block everything.
3. **Aggregation strategy** — Concatenate, vote, score-and-rank, or LLM-summarise?

## 🏋️ Practice

→ [Exercise: Parallelization](../exercises/agentic/03_parallelization.py)
