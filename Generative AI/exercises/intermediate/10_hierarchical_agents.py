"""
Exercise 10: Hierarchical Agents — Startup Pitch Advisor
==========================================================
Difficulty: ⭐⭐⭐ Advanced
Time: 90-120 minutes
Pattern: HIERARCHICAL (Manager + Workers)

GOAL:
  Build a hierarchical agent system where a Manager (Strategy Advisor)
  delegates to specialist Workers, reviews their outputs, and synthesizes
  a complete startup pitch document.

  Flow:
    1. User describes a startup idea
    2. Manager creates a delegation plan
    3. Manager assigns tasks to specialist workers
    4. Workers produce their analyses
    5. Manager reviews (can request revisions!)
    6. Manager synthesizes final pitch document

YOUR TASKS:
  1. Complete the worker prompts (TODO #1)
  2. Implement the manager's planning logic (TODO #2)
  3. Implement the manager's review logic (TODO #3)
  4. Complete the hierarchical runner (TODO #4)
  5. Test with sample startup ideas

CONCEPTS:
  - Manager agent with planning ability
  - Specialist worker agents
  - Review/feedback loop
  - Multi-step synthesis

SETUP:
  pip install openai python-dotenv

RUN:
  python 10_hierarchical_agents.py
"""

import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ╔══════════════════════════════════════════════════════════════╗
# ║  HELPER                                                      ║
# ╚══════════════════════════════════════════════════════════════╝

def call_llm(system: str, user: str, model: str = "gpt-4o-mini", json_mode: bool = False) -> str:
    """Call the LLM with a system prompt and user message."""
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


# ╔══════════════════════════════════════════════════════════════╗
# ║  WORKER DEFINITIONS                                          ║
# ╚══════════════════════════════════════════════════════════════╝

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
        # TODO #1a: Write the product strategist prompt
        # It should ask the agent to provide:
        # - Value Proposition (one clear sentence)
        # - Core Features (MVP scope — 5 key features)
        # - Technical Architecture (high-level: frontend, backend, infrastructure)
        # - Product Roadmap (3 phases: MVP, Growth, Scale)
        # - Differentiation (what makes this unique vs competitors)
        "prompt": """
TODO: Write the product strategist prompt here.
"""
    },

    "financial_modeler": {
        "name": "Financial Modeling Specialist",
        # TODO #1b: Write the financial modeler prompt
        # It should ask the agent to provide:
        # - Revenue Model (how will you make money — pricing strategy)
        # - Cost Structure (fixed + variable costs breakdown)
        # - Unit Economics (CAC, LTV, payback period)
        # - 3-Year Projection (Year 1, 2, 3 revenue + users)
        # - Funding Needs (how much to raise, what it's for)
        "prompt": """
TODO: Write the financial modeler prompt here.
"""
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


# ╔══════════════════════════════════════════════════════════════╗
# ║  MANAGER AGENT — Plans, Delegates, Reviews, Synthesizes      ║
# ╚══════════════════════════════════════════════════════════════╝

MANAGER_PLAN_PROMPT = """You are a Senior Startup Strategy Advisor managing a team of specialists.

Given a startup idea, create a delegation plan as JSON:
{{
  "startup_summary": "Brief 1-sentence summary of the startup idea",
  "subtasks": [
    {{
      "worker": "worker_id",
      "instruction": "Specific instruction for this worker including any relevant context",
      "priority": "high/medium/low"
    }}
  ],
  "key_questions": ["list of 3 critical questions this pitch must answer"]
}}

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
{{
  "approved": true/false,
  "quality_score": 1-10,
  "feedback": "specific feedback if not approved, or brief praise if approved",
  "revision_instruction": "if not approved, what to fix (null if approved)"
}}

Only reject (approved=false) if there are significant issues. Minor imperfections are OK."""


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


# ╔══════════════════════════════════════════════════════════════╗
# ║  HIERARCHICAL ENGINE                                         ║
# ╚══════════════════════════════════════════════════════════════╝

def manager_create_plan(startup_idea: str) -> dict:
    """
    Manager creates a delegation plan.

    TODO #2: Implement this function:
    1. Call call_llm() with MANAGER_PLAN_PROMPT and the startup_idea
       (use json_mode=True)
    2. Parse the JSON response
    3. Print the plan summary
    4. Return the parsed plan dict
    """
    pass


def manager_review_work(worker_name: str, worker_output: str, startup_idea: str) -> dict:
    """
    Manager reviews a worker's output.

    TODO #3: Implement this function:
    1. Create a review request combining:
       - The startup idea (for context)
       - The worker's name
       - The worker's output
    2. Call call_llm() with MANAGER_REVIEW_PROMPT (json_mode=True)
    3. Parse and return the review JSON

    The review JSON looks like:
    {
      "approved": true/false,
      "quality_score": 8,
      "feedback": "...",
      "revision_instruction": null or "..."
    }
    """
    pass


def execute_worker(worker_id: str, instruction: str, context: str = "") -> str:
    """Execute a worker agent with the given instruction."""
    worker = WORKERS[worker_id]
    user_input = instruction
    if context:
        user_input += f"\n\nContext from previous analyses:\n{context}"

    print(f"  👷 {worker['name']} working...")
    result = call_llm(worker["prompt"], user_input)
    print(f"     ✅ Complete!")
    return result


def run_hierarchical(startup_idea: str, allow_revisions: bool = True, max_revisions: int = 1) -> str:
    """
    Run the full hierarchical agent system.

    TODO #4: Implement this function:

    Step 1: Manager creates plan
      - Call manager_create_plan(startup_idea)
      - Print the plan

    Step 2: Execute workers in order
      - Loop through plan["subtasks"]
      - For each subtask:
        a. Execute the worker using execute_worker()
        b. If allow_revisions: have manager review using manager_review_work()
        c. If not approved and max_revisions > 0: re-run worker with feedback
        d. Store the result in a dict (worker_results)
      - Pass previous worker results as context to later workers

    Step 3: Manager synthesizes
      - Combine all worker results
      - Call call_llm() with MANAGER_SYNTHESIS_PROMPT
      - Return the final pitch document

    Hint: Build a context string from previous results to pass to each worker.
    """
    pass


# ╔══════════════════════════════════════════════════════════════╗
# ║  SAMPLE STARTUP IDEAS                                        ║
# ╚══════════════════════════════════════════════════════════════╝

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


# ╔══════════════════════════════════════════════════════════════╗
# ║  CLI RUNNER                                                   ║
# ╚══════════════════════════════════════════════════════════════╝

def main():
    print("=" * 60)
    print("🚀 Startup Pitch Advisor — Hierarchical Agent System")
    print("=" * 60)

    print("\nAvailable startup ideas:")
    for key, desc in STARTUP_IDEAS.items():
        first_line = desc.strip().split("\n")[0].strip()
        print(f"  • {key}: {first_line}")

    print(f"\nOr type 'custom' to describe your own startup idea.")
    choice = input("\nChoose an idea (or 'custom'): ").strip().lower()

    if choice == "custom":
        print("Describe your startup idea (press Enter twice to finish):")
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
        print(f"Unknown choice. Using 'ai_tutor'.")
        startup_idea = STARTUP_IDEAS["ai_tutor"]

    print(f"\n📋 Startup Idea: {startup_idea.strip()[:100]}...\n")

    # Run the hierarchical system
    pitch = run_hierarchical(startup_idea)

    if pitch:
        print("\n" + "=" * 60)
        print("📄 FINAL INVESTOR PITCH")
        print("=" * 60)
        print(pitch)

        # Save to file
        output_file = "startup_pitch_output.md"
        with open(output_file, "w") as f:
            f.write(pitch)
        print(f"\n💾 Saved to {output_file}")
    else:
        print("❌ Pipeline failed. Check the TODOs!")


if __name__ == "__main__":
    main()
