"""
Solution: Exercise 10 — Hierarchical Agents Startup Pitch Advisor
==================================================================
Pattern: HIERARCHICAL (Manager + Workers)
"""

import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ── Helper ────────────────────────────────────────────────────

def call_llm(system: str, user: str, model: str = "gpt-4o-mini", json_mode: bool = False) -> str:
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        **kwargs
    )
    return response.choices[0].message.content


# ── Workers (COMPLETE PROMPTS) ────────────────────────────────

WORKERS = {
    "market_researcher": {
        "name": "Market Research Specialist",
        "prompt": """You are a Market Research Specialist for startups.

Given a startup idea, provide a thorough market analysis:
1. **Market Size** — TAM, SAM, SOM with estimated dollar figures
2. **Target Customer** — Detailed persona (demographics, behaviors, pain points)
3. **Competitor Landscape** — Top 3-5 competitors with strengths/weaknesses
4. **Market Trends** — 3 trends supporting this market
5. **Entry Barriers** — What makes it hard for others to compete

Be specific with numbers (even estimates). Use data-driven language.
Keep response under 400 words."""
    },

    "product_strategist": {
        "name": "Product Strategy Specialist",
        "prompt": """You are a Product Strategy Specialist for startups.

Given a startup idea, provide a clear product strategy:
1. **Value Proposition** — One compelling sentence that captures the unique value
2. **Core Features** — MVP scope: exactly 5 must-have features with brief descriptions
3. **Technical Architecture** — High-level: frontend, backend, key infrastructure, APIs
4. **Product Roadmap**:
   - Phase 1 (Months 1-3): MVP — what ships first
   - Phase 2 (Months 4-8): Growth — key feature additions
   - Phase 3 (Months 9-12): Scale — platform maturity features
5. **Differentiation** — 3 things that make this product unique vs competitors

Be specific and technical where appropriate.
Keep response under 400 words."""
    },

    "financial_modeler": {
        "name": "Financial Modeling Specialist",
        "prompt": """You are a Financial Modeling Specialist for startups.

Given a startup idea and any market/product context, build a financial model:
1. **Revenue Model** — How will you make money? Pricing tiers, freemium strategy
2. **Cost Structure**:
   - Fixed costs (team, infrastructure, office)
   - Variable costs (per-user costs, API calls, support)
3. **Unit Economics**:
   - Customer Acquisition Cost (CAC) — estimated with channel breakdown
   - Lifetime Value (LTV) — with calculation assumptions
   - LTV:CAC ratio and payback period
4. **3-Year Projection** (table format):
   | Metric | Year 1 | Year 2 | Year 3 |
   - Monthly Active Users
   - Revenue
   - Costs
   - Net Profit/Loss
5. **Funding Needs** — How much to raise, what it covers, expected runway

Use realistic estimates. Show your assumptions.
Keep response under 400 words."""
    },

    "go_to_market_planner": {
        "name": "Go-to-Market Strategy Specialist",
        "prompt": """You are a Go-to-Market Strategy Specialist.

Given a startup idea and any context provided, create a GTM plan:
1. **Launch Strategy** — How to launch (beta → public, or big bang?)
2. **Marketing Channels** — Top 5 channels ranked by expected ROI
3. **Sales Approach** — Self-serve, sales-led, or hybrid?
4. **Partnership Opportunities** — 3 strategic partnerships to pursue
5. **First 90 Days Plan** — Week-by-week action items for launch

Be tactical and specific. Include estimated costs where possible.
Keep response under 400 words."""
    },
}


# ── Manager Prompts ───────────────────────────────────────────

MANAGER_PLAN_PROMPT = """You are a Senior Startup Strategy Advisor managing a team of specialists.

Given a startup idea, create a delegation plan as JSON:
{
  "startup_summary": "Brief 1-sentence summary of the startup idea",
  "subtasks": [
    {
      "worker": "worker_id",
      "instruction": "Specific instruction for this worker including any relevant context",
      "priority": "high/medium/low"
    }
  ],
  "key_questions": ["list of 3 critical questions this pitch must answer"]
}

Available workers (use these exact IDs):
- market_researcher: Market analysis, competitors, trends
- product_strategist: Product features, architecture, roadmap
- financial_modeler: Revenue model, costs, projections
- go_to_market_planner: Launch strategy, marketing, sales

Order workers logically. Financial modeler should come after market researcher.
Include startup-specific instructions for each worker."""


MANAGER_REVIEW_PROMPT = """You are a Senior Startup Strategy Advisor reviewing a specialist's work.

Review the worker's output for:
1. **Completeness** — Did they cover all required areas?
2. **Specificity** — Are there concrete numbers, names, and details (not vague)?
3. **Consistency** — Does it align with the startup idea and other analyses?
4. **Actionability** — Can a founder actually use this advice?

Respond in JSON:
{
  "approved": true,
  "quality_score": 8,
  "feedback": "specific feedback if not approved, or brief praise if approved",
  "revision_instruction": null
}

Set approved=false and provide revision_instruction only if there are significant issues.
Minor imperfections are OK — approve with constructive feedback."""


MANAGER_SYNTHESIS_PROMPT = """You are a Senior Startup Strategy Advisor.

You delegated tasks to your specialist team. Now synthesize their findings into a
**complete investor pitch document**. Structure it as:

# [Startup Name] — Investor Pitch

## 1. Executive Summary (150 words)
## 2. Problem & Opportunity
## 3. Solution & Product
## 4. Market Analysis
## 5. Business Model & Financials
## 6. Go-to-Market Strategy
## 7. Competitive Advantage
## 8. Team Needs (what roles to hire)
## 9. The Ask (funding amount + use of funds)
## 10. Vision (where will this be in 5 years?)

Make it compelling, professional, and investor-ready.
Weave insights from all specialists into a cohesive narrative.
Use data and specifics from the analyses — don't make up new numbers."""


# ── Hierarchical Engine (SOLUTION) ────────────────────────────

def manager_create_plan(startup_idea: str) -> dict:
    """Manager creates a delegation plan."""
    print("🧠 Manager: Creating delegation plan...")
    plan_json = call_llm(MANAGER_PLAN_PROMPT, startup_idea, json_mode=True)
    plan = json.loads(plan_json)
    print(f"   📋 Summary: {plan['startup_summary']}")
    print(f"   📋 Subtasks: {len(plan['subtasks'])}")
    print(f"   ❓ Key Questions:")
    for q in plan.get("key_questions", []):
        print(f"      - {q}")
    return plan


def manager_review_work(worker_name: str, worker_output: str, startup_idea: str) -> dict:
    """Manager reviews a worker's output."""
    review_request = (
        f"Startup idea: {startup_idea}\n\n"
        f"Worker: {worker_name}\n\n"
        f"Worker's output:\n{worker_output}"
    )
    review_json = call_llm(MANAGER_REVIEW_PROMPT, review_request, json_mode=True)
    review = json.loads(review_json)
    return review


def execute_worker(worker_id: str, instruction: str, context: str = "") -> str:
    """Execute a worker agent."""
    worker = WORKERS[worker_id]
    user_input = instruction
    if context:
        user_input += f"\n\nContext from previous analyses:\n{context}"
    print(f"  👷 {worker['name']} working...")
    result = call_llm(worker["prompt"], user_input)
    print(f"     ✅ Complete!")
    return result


def run_hierarchical(startup_idea: str, allow_revisions: bool = True, max_revisions: int = 1) -> str:
    """Run the full hierarchical agent system."""
    print(f"\n{'=' * 60}")
    print(f"🚀 Startup Pitch Advisor — Hierarchical System")
    print(f"{'=' * 60}")

    # Step 1: Manager creates plan
    plan = manager_create_plan(startup_idea)

    # Step 2: Execute workers in order
    worker_results = {}

    for i, subtask in enumerate(plan["subtasks"], 1):
        worker_id = subtask["worker"]
        instruction = subtask["instruction"]

        if worker_id not in WORKERS:
            print(f"  ⚠️  Unknown worker: {worker_id}, skipping.")
            continue

        print(f"\n--- Worker {i}/{len(plan['subtasks'])}: {WORKERS[worker_id]['name']} ---")

        # Build context from previous workers
        context = ""
        if worker_results:
            context = "\n---\n".join(
                f"[{WORKERS[wid]['name']}]:\n{result[:500]}..."
                for wid, result in worker_results.items()
            )

        # Execute worker
        result = execute_worker(worker_id, instruction, context)

        # Manager review
        if allow_revisions:
            print(f"  🧠 Manager reviewing {WORKERS[worker_id]['name']}'s work...")
            review = manager_review_work(
                WORKERS[worker_id]["name"],
                result,
                startup_idea
            )

            score = review.get("quality_score", "?")
            approved = review.get("approved", True)
            print(f"     Score: {score}/10 | Approved: {'✅' if approved else '❌'}")
            print(f"     Feedback: {review.get('feedback', 'N/A')[:100]}")

            # Revision if needed
            if not approved and max_revisions > 0:
                revision_instruction = review.get("revision_instruction", "Please improve your analysis.")
                print(f"  🔄 Requesting revision: {revision_instruction[:80]}...")
                result = execute_worker(
                    worker_id,
                    f"{instruction}\n\nMANAGER FEEDBACK — Please address: {revision_instruction}",
                    context
                )
                print(f"  🧠 Revision accepted.")

        worker_results[worker_id] = result

    # Step 3: Manager synthesizes final pitch
    print(f"\n{'─' * 40}")
    print("🧠 Manager: Synthesizing final pitch document...")
    all_results = "\n\n---\n\n".join(
        f"## {WORKERS[wid]['name']} Report:\n{result}"
        for wid, result in worker_results.items()
    )

    final_pitch = call_llm(
        MANAGER_SYNTHESIS_PROMPT,
        f"Original startup idea: {startup_idea}\n\nSpecialist Reports:\n{all_results}"
    )

    print("✅ Final pitch document ready!")
    return final_pitch


# ── Sample Ideas ──────────────────────────────────────────────

STARTUP_IDEAS = {
    "ai_tutor": """
        EduMind AI — An AI-powered personalized tutoring platform that adapts
        to each student's learning style, pace, and knowledge gaps. Uses
        conversational AI to teach K-12 subjects with interactive exercises,
        real-time feedback, and parent dashboards. Targets underserved students
        who can't afford private tutors.
    """,
    "green_delivery": """
        EcoFleet — A last-mile delivery platform using electric cargo bikes
        and AI route optimization for urban areas. Partners with local
        businesses for same-day delivery. Carbon-negative model where
        every delivery plants a tree. Targets eco-conscious consumers
        and sustainable businesses in cities with 500K+ population.
    """,
    "health_ai": """
        MedScribe AI — An AI medical documentation assistant that listens
        to doctor-patient conversations and automatically generates
        structured clinical notes, billing codes (ICD-10), and follow-up
        recommendations. HIPAA compliant. Saves doctors 2+ hours/day.
        Targets independent clinics and small hospital systems.
    """,
    "creator_economy": """
        CreatorOS — An all-in-one platform for content creators to manage
        their business: AI-powered content calendar, sponsor matchmaking,
        revenue tracking across platforms (YouTube, TikTok, Instagram),
        tax preparation, and audience analytics. Targets mid-tier creators
        (10K-500K followers) who are turning their hobby into a business.
    """,
}


# ── CLI ───────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🚀 Startup Pitch Advisor (Solution)")
    print("=" * 60)

    print("\nAvailable ideas:")
    for key, desc in STARTUP_IDEAS.items():
        print(f"  • {key}: {desc.strip().split(chr(10))[0].strip()}")

    choice = input("\nChoose an idea (or 'custom'): ").strip().lower()

    if choice == "custom":
        print("Describe your startup idea (Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        startup_idea = "\n".join(lines)
    elif choice in STARTUP_IDEAS:
        startup_idea = STARTUP_IDEAS[choice]
    else:
        startup_idea = STARTUP_IDEAS["ai_tutor"]

    pitch = run_hierarchical(startup_idea)

    print("\n" + "=" * 60)
    print("📄 FINAL INVESTOR PITCH")
    print("=" * 60)
    print(pitch)

    output_file = "startup_pitch_output.md"
    with open(output_file, "w") as f:
        f.write(pitch)
    print(f"\n💾 Saved to {output_file}")


if __name__ == "__main__":
    main()
