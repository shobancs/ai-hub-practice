"""
Exercise 9: Parallel Agents — Product Comparison Engine
========================================================
Difficulty: ⭐⭐ Intermediate
Time: 60-90 minutes
Pattern: PARALLEL

GOAL:
  Build a system that analyzes multiple products IN PARALLEL, then merges
  results into a comparison report.

  Flow:
    1. User provides 2-3 products to compare
    2. One agent analyzes each product (running concurrently)
    3. An aggregator merges all analyses into a comparison table + recommendation

YOUR TASKS:
  1. Implement the async agent runner (TODO #1)
  2. Complete the aggregator prompt (TODO #2)
  3. Implement the parallel comparison engine (TODO #3)
  4. Add timing to compare parallel vs sequential speed

CONCEPTS:
  - asyncio for concurrent API calls
  - Gathering parallel results
  - Result aggregation / synthesis

SETUP:
  pip install openai python-dotenv

RUN:
  python 09_parallel_agents.py
"""

import asyncio
import json
import os
import time
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv

load_dotenv()
async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sync_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ╔══════════════════════════════════════════════════════════════╗
# ║  PRODUCT ANALYST PROMPT — Each product gets this agent       ║
# ╚══════════════════════════════════════════════════════════════╝

PRODUCT_ANALYST_PROMPT = """You are a detailed Product Analyst.

Analyze the given product thoroughly and provide:

1. **Overview** (2-3 sentences)
2. **Key Features** (bullet list, 5 items)
3. **Strengths** (3 items with brief explanation)
4. **Weaknesses** (3 items with brief explanation)
5. **Best For** (who should buy this, 2-3 use cases)
6. **Value Rating** (1-10 with justification)

Be objective, specific, and data-driven. Avoid marketing language.
Keep total response under 300 words."""


# ╔══════════════════════════════════════════════════════════════╗
# ║  AGGREGATOR PROMPT — Merges parallel results                 ║
# ╚══════════════════════════════════════════════════════════════╝

# TODO #2: Complete the aggregator prompt
AGGREGATOR_PROMPT = """You are a Product Comparison Expert.

You receive individual analyses of multiple products from specialist analysts.
Synthesize them into a comprehensive comparison report with:

1. **Comparison Table** — Markdown table with key attributes side-by-side
   (price, key feature, rating, best for)
2. **Head-to-Head** — Direct comparison on: features, value, usability, ecosystem
3. **Winner by Category** — Which product wins in each category and why
4. **Overall Recommendation** — Clear recommendation with reasoning
   (consider different user types)
5. **Quick Verdict** — One-sentence summary

Be fair and balanced. Acknowledge that different products suit different needs.
"""


# ╔══════════════════════════════════════════════════════════════╗
# ║  ASYNC AGENT RUNNER                                          ║
# ╚══════════════════════════════════════════════════════════════╝

async def analyze_product_async(product_name: str, product_info: str) -> dict:
    """
    Analyze a single product asynchronously.

    TODO #1: Implement this function:
    1. Print f"  🔍 Analyzing {product_name}..."
    2. Record the start time
    3. Call async_client.chat.completions.create() with:
       - model="gpt-4o-mini"
       - messages: system=PRODUCT_ANALYST_PROMPT, user=product details
    4. Get the response content
    5. Calculate elapsed time
    6. Print f"  ✅ {product_name} done ({elapsed:.1f}s)"
    7. Return dict: {"product": product_name, "analysis": response_content, "time": elapsed}

    Hint: Use `await` before the API call since it's async.
    """
    pass


async def run_parallel_analysis(products: dict) -> list[dict]:
    """
    Run all product analyses in parallel using asyncio.gather().

    TODO #3: Implement this function:
    1. Create a list of tasks using analyze_product_async()
    2. Use asyncio.gather(*tasks) to run them all concurrently
    3. Return the list of results
    """
    pass


# ╔══════════════════════════════════════════════════════════════╗
# ║  SEQUENTIAL RUNNER (for timing comparison)                   ║
# ╚══════════════════════════════════════════════════════════════╝

def analyze_product_sync(product_name: str, product_info: str) -> dict:
    """Analyze a single product synchronously (for comparison)."""
    print(f"  🔍 Analyzing {product_name}...")
    start = time.time()

    response = sync_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PRODUCT_ANALYST_PROMPT},
            {"role": "user", "content": f"Analyze this product:\n\n{product_name}:\n{product_info}"}
        ]
    )

    elapsed = time.time() - start
    print(f"  ✅ {product_name} done ({elapsed:.1f}s)")
    return {
        "product": product_name,
        "analysis": response.choices[0].message.content,
        "time": elapsed
    }


def run_sequential_analysis(products: dict) -> list[dict]:
    """Run all analyses sequentially (for timing comparison)."""
    results = []
    for name, info in products.items():
        results.append(analyze_product_sync(name, info))
    return results


# ╔══════════════════════════════════════════════════════════════╗
# ║  AGGREGATION — Merge results into comparison                 ║
# ╚══════════════════════════════════════════════════════════════╝

def aggregate_results(results: list[dict]) -> str:
    """
    Send all product analyses to the aggregator agent.

    This one is implemented for you as a reference!
    """
    combined = "\n\n---\n\n".join(
        f"### {r['product']}\n{r['analysis']}" for r in results
    )

    response = sync_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AGGREGATOR_PROMPT},
            {"role": "user", "content": f"Compare these products:\n\n{combined}"}
        ]
    )
    return response.choices[0].message.content


# ╔══════════════════════════════════════════════════════════════╗
# ║  SAMPLE PRODUCTS — Test comparisons                          ║
# ╚══════════════════════════════════════════════════════════════╝

COMPARISONS = {
    "laptops": {
        "MacBook Pro 16 M4": "Apple laptop. M4 Pro chip, 18GB RAM, 512GB SSD, 16-inch Liquid Retina XDR, 22-hour battery. $2,499. macOS. Great for creative professionals.",
        "Dell XPS 15": "Windows laptop. Intel Core Ultra 7, 16GB RAM, 512GB SSD, 15.6-inch OLED, 13-hour battery. $1,799. Best Windows ultrabook for productivity.",
        "ThinkPad X1 Carbon": "Lenovo business laptop. Intel Core Ultra 5, 16GB RAM, 256GB SSD, 14-inch 2.8K OLED, 15-hour battery. $1,449. Best keyboard, MIL-STD tested.",
    },
    "cloud_providers": {
        "AWS": "Amazon Web Services. Largest cloud provider, 200+ services. Strengths: breadth of services, global reach, mature ecosystem. Weaknesses: complex pricing, steep learning curve.",
        "Azure": "Microsoft Azure. Second largest. Strengths: enterprise integration, hybrid cloud, AI services. Weaknesses: portal UX, inconsistent naming.",
        "GCP": "Google Cloud Platform. Third largest. Strengths: data analytics, ML/AI, Kubernetes. Weaknesses: smaller market share, fewer enterprise features.",
    },
    "ai_coding_tools": {
        "GitHub Copilot": "AI coding assistant by GitHub/Microsoft. IDE integration (VS Code, JetBrains). $10/month individual. Strengths: deep IDE integration, chat, pull request summaries.",
        "Cursor": "AI-first code editor. Fork of VS Code with built-in AI. $20/month pro. Strengths: AI-native UX, composer mode, multi-file editing.",
        "Cody by Sourcegraph": "AI coding assistant with code graph context. Free tier available, $9/month pro. Strengths: codebase-aware context, self-hosted option.",
    },
}


# ╔══════════════════════════════════════════════════════════════╗
# ║  CLI RUNNER                                                   ║
# ╚══════════════════════════════════════════════════════════════╝

def main():
    print("=" * 60)
    print("⚡ Parallel Product Comparison Engine")
    print("=" * 60)

    print("\nAvailable comparisons:")
    for key in COMPARISONS:
        products = list(COMPARISONS[key].keys())
        print(f"  • {key}: {' vs '.join(products)}")

    choice = input("\nChoose a comparison: ").strip().lower()
    if choice not in COMPARISONS:
        print(f"Unknown choice. Using 'laptops'.")
        choice = "laptops"

    products = COMPARISONS[choice]

    # --- Parallel Execution ---
    print(f"\n🚀 PARALLEL Analysis ({len(products)} products simultaneously)...")
    start = time.time()
    parallel_results = asyncio.run(run_parallel_analysis(products))
    parallel_time = time.time() - start
    print(f"⏱️  Parallel total: {parallel_time:.1f}s")

    # --- Sequential Execution (for comparison) ---
    print(f"\n🐢 SEQUENTIAL Analysis ({len(products)} products one by one)...")
    start = time.time()
    sequential_results = run_sequential_analysis(products)
    sequential_time = time.time() - start
    print(f"⏱️  Sequential total: {sequential_time:.1f}s")

    # --- Speed comparison ---
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"\n⚡ Speedup: {speedup:.1f}x faster with parallel execution!")

    # --- Aggregate ---
    print("\n📊 Aggregating comparison report...")
    report = aggregate_results(parallel_results)

    print("\n" + "=" * 60)
    print("📋 COMPARISON REPORT")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()
