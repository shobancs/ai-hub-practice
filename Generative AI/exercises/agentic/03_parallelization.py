"""
Exercise: Parallelization — Startup Idea Validator
====================================================
Pattern: PARALLELIZATION (Chapter 3)

GOAL:
  Given a startup idea, run 4 independent analyses in parallel:
    - Market analysis
    - Technical feasibility
    - Financial viability
    - Competitive landscape
  Then aggregate into a final Go / No-Go verdict.

YOUR TASKS:
  1. Implement analyse_financial()       (TODO 1)
  2. Implement analyse_competition()     (TODO 2)
  3. Implement the parallel runner       (TODO 3)

SETUP:
  pip install openai python-dotenv

RUN:
  python 03_parallelization.py
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


async def analyse_financial(idea: str) -> dict:
    """
    TODO 1: Financial viability worker.

    Create an async function that calls call_llm() to evaluate:
    - Revenue model options
    - Estimated startup costs
    - Time to breakeven
    - Funding requirements
    Give a viability score out of 10.

    Return: {"aspect": "Financial Viability", "analysis": result}
    """
    # YOUR CODE HERE
    pass


async def analyse_competition(idea: str) -> dict:
    """
    TODO 2: Competitive landscape worker.

    Create an async function that calls call_llm() to evaluate:
    - Existing competitors (name 3-5)
    - Differentiation potential
    - Barriers to entry
    - Competitive moats available
    Give a competitive advantage score out of 10.

    Return: {"aspect": "Competitive Landscape", "analysis": result}
    """
    # YOUR CODE HERE
    pass


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
#  PARALLEL RUNNER
# ═══════════════════════════════════════════════════════════

async def validate_startup(idea: str) -> str:
    """
    TODO 3: Run all 4 analyses in parallel using asyncio.gather().

    Steps:
    1. Record start time
    2. Use asyncio.gather() to run all 4 analyse_* functions concurrently
    3. Filter out None results (from unimplemented TODOs)
    4. Print time taken
    5. Call aggregate() with the results
    6. Return the final verdict

    Hint: analyses = await asyncio.gather(func1(idea), func2(idea), ...)
    """
    print(f"🚀 Validating: {idea}\n")

    # YOUR CODE HERE
    pass


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

    idea = IDEAS[0]  # Change index to try different ideas
    result = asyncio.run(validate_startup(idea))

    if result:
        print("\n" + "=" * 60)
        print("📊 FINAL VERDICT")
        print("=" * 60)
        print(result)
    else:
        print("\n❌ TODO 3 not implemented yet!")


if __name__ == "__main__":
    main()
