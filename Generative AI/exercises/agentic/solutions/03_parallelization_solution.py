"""
Solution: Parallelization — Startup Idea Validator
====================================================
Pattern: PARALLELIZATION (Chapter 3)

Complete solution with all TODOs implemented.
"""

import asyncio, os, time
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def call_llm(system: str, user: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return r.choices[0].message.content


# ═══════════════════════════════════════════════════════════
#  PARALLEL WORKERS
# ═══════════════════════════════════════════════════════════

async def analyse_market(idea: str) -> dict:
    """Market analysis worker. (PROVIDED)"""
    result = await call_llm(
        "You are a market research analyst. Evaluate the startup idea for:\n"
        "- Target market size (TAM, SAM, SOM)\n"
        "- Customer segments\n"
        "- Market trends and timing\n"
        "Give a market score out of 10.",
        f"Startup idea: {idea}",
    )
    return {"aspect": "Market Analysis", "analysis": result}


async def analyse_technical(idea: str) -> dict:
    """Technical feasibility worker. (PROVIDED)"""
    result = await call_llm(
        "You are a CTO evaluating a startup idea. Assess:\n"
        "- Technical complexity (1=simple, 10=moon-shot)\n"
        "- Key technologies needed\n"
        "- Time to MVP estimate\n"
        "- Major technical risks\n"
        "Give a feasibility score out of 10.",
        f"Startup idea: {idea}",
    )
    return {"aspect": "Technical Feasibility", "analysis": result}


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 1: Financial Viability Worker
# ═══════════════════════════════════════════════════════════

async def analyse_financial(idea: str) -> dict:
    """Financial viability worker."""
    result = await call_llm(
        "You are a startup financial analyst. Evaluate the idea for:\n"
        "- Revenue model options (subscription, freemium, marketplace, etc.)\n"
        "- Estimated startup costs (development, marketing, ops)\n"
        "- Time to breakeven estimate\n"
        "- Funding requirements (bootstrappable vs needs VC)\n"
        "- Unit economics potential\n"
        "Give a financial viability score out of 10.",
        f"Startup idea: {idea}",
    )
    return {"aspect": "Financial Viability", "analysis": result}


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 2: Competitive Landscape Worker
# ═══════════════════════════════════════════════════════════

async def analyse_competition(idea: str) -> dict:
    """Competitive landscape worker."""
    result = await call_llm(
        "You are a competitive intelligence analyst. Evaluate the idea for:\n"
        "- Existing competitors (name 3-5 real or plausible ones)\n"
        "- Differentiation potential\n"
        "- Barriers to entry (technical, regulatory, network effects)\n"
        "- Competitive moats available (data, brand, patents, switching costs)\n"
        "- Risk of incumbents copying the idea\n"
        "Give a competitive advantage score out of 10.",
        f"Startup idea: {idea}",
    )
    return {"aspect": "Competitive Landscape", "analysis": result}


# ═══════════════════════════════════════════════════════════
#  AGGREGATOR (PROVIDED)
# ═══════════════════════════════════════════════════════════

async def aggregate(idea: str, analyses: list[dict]) -> str:
    """Combine all analyses into a Go / No-Go verdict."""
    combined = "\n\n".join(
        f"### {a['aspect']}\n{a['analysis']}" for a in analyses if a
    )
    return await call_llm(
        "You are a startup advisor. Given analyses from 4 specialists, "
        "write a final verdict:\n"
        "1. Summary of strengths and weaknesses\n"
        "2. Overall score (average of specialist scores)\n"
        "3. Clear GO / NO-GO / PIVOT recommendation\n"
        "4. Top 3 action items if GO\n"
        "Be concise (200 words max).",
        f"Startup Idea: {idea}\n\nAnalyses:\n{combined}",
    )


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 3: PARALLEL RUNNER
# ═══════════════════════════════════════════════════════════

async def validate_startup(idea: str) -> str:
    """Run all 4 analyses in parallel using asyncio.gather()."""
    print(f"🚀 Validating: {idea}\n")

    start = time.time()

    # Run all 4 workers concurrently
    analyses = await asyncio.gather(
        analyse_market(idea),
        analyse_technical(idea),
        analyse_financial(idea),
        analyse_competition(idea),
    )

    # Filter out any None results
    analyses = [a for a in analyses if a is not None]

    elapsed = time.time() - start
    print(f"⏱️  All {len(analyses)} analyses completed in {elapsed:.1f}s (parallel!)\n")

    # Print individual results
    for a in analyses:
        print(f"{'─' * 50}")
        print(f"📊 {a['aspect']}")
        print(f"{'─' * 50}")
        print(a["analysis"])
        print()

    # Aggregate into final verdict
    verdict = await aggregate(idea, analyses)
    return verdict


# ═══════════════════════════════════════════════════════════
#  SAMPLE STARTUP IDEAS
# ═══════════════════════════════════════════════════════════

IDEAS = [
    "An AI-powered personal finance advisor that connects to your bank accounts "
    "and gives real-time spending advice via WhatsApp",

    "A marketplace for freelance AI prompt engineers to help businesses "
    "optimize their LLM workflows",

    "An AR glasses app that translates restaurant menus in real-time "
    "and shows calorie/allergen info",
]


def main():
    print("=" * 60)
    print("🚀 Startup Idea Validator (Parallel Pattern)")
    print("=" * 60)

    idea = IDEAS[0]
    result = asyncio.run(validate_startup(idea))

    if result:
        print("\n" + "=" * 60)
        print("📊 FINAL VERDICT")
        print("=" * 60)
        print(result)


if __name__ == "__main__":
    main()
