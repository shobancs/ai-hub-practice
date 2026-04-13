"""
Exercise: Multi-Agent — Product Launch Team
=============================================
Pattern: MULTI-AGENT (Chapter 7)

GOAL:
  Simulate a product launch team with 4 specialised agents:
    - Market Researcher
    - Copywriter
    - Designer (describes visuals)
    - Launch Strategist
  A Coordinator orchestrates their work.

YOUR TASKS:
  1. Create the copywriter agent           (TODO 1)
  2. Create the launch_strategist agent    (TODO 2)
  3. Implement the coordinator             (TODO 3)

SETUP:
  pip install openai python-dotenv

RUN:
  python 07_multi_agent.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ═══════════════════════════════════════════════════════════
#  AGENT CLASS (PROVIDED)
# ═══════════════════════════════════════════════════════════

class Agent:
    """A simple agent with a name and specialised system prompt."""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def run(self, task: str) -> str:
        print(f"  🤖 {self.name} working...")
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": task},
            ],
        )
        result = r.choices[0].message.content
        print(f"  ✅ {self.name} done.\n")
        return result


# ═══════════════════════════════════════════════════════════
#  DEFINE AGENTS
# ═══════════════════════════════════════════════════════════

market_researcher = Agent(
    "Market Researcher",
    "You are a market research specialist. Given a product, provide:\n"
    "- Target audience (demographics, psychographics)\n"
    "- Market size estimate\n"
    "- Top 3 competitors and their weaknesses\n"
    "- Key differentiators for this product\n"
    "- Recommended positioning statement\n"
    "Be data-driven and specific.",
)

designer = Agent(
    "Visual Designer",
    "You are a creative director. Given a product and its target audience, describe:\n"
    "- Brand colour palette (3-4 colours with hex codes)\n"
    "- Logo concept (describe in detail)\n"
    "- Key visual style (modern/playful/luxury/minimal)\n"
    "- Hero image concept for the landing page\n"
    "- Social media visual themes\n"
    "Be vivid and specific in your descriptions.",
)

# ─────────────────────────────────────────────────────
# TODO 1: Create a 'copywriter' Agent
#
# Name: "Copywriter"
# System prompt should instruct the agent to:
# - Write a compelling product tagline
# - Write a hero section headline + subheadline
# - Write 3 feature descriptions (with benefit-focused language)
# - Write a call-to-action (CTA) button text + supporting line
# - The tone should match the target audience
# ─────────────────────────────────────────────────────

copywriter = None  # Replace with Agent(...)


# ─────────────────────────────────────────────────────
# TODO 2: Create a 'launch_strategist' Agent
#
# Name: "Launch Strategist"
# System prompt should instruct the agent to:
# - Create a 4-week launch timeline
# - Define 3 launch phases (teaser, launch, sustain)
# - Recommend marketing channels (social, email, PR, paid)
# - Set KPIs for each phase
# - Include a launch day hour-by-hour schedule
# ─────────────────────────────────────────────────────

launch_strategist = None  # Replace with Agent(...)


# ═══════════════════════════════════════════════════════════
#  COORDINATOR
# ═══════════════════════════════════════════════════════════

def coordinate_launch(product: str) -> str:
    """
    TODO 3: Orchestrate the multi-agent product launch.

    Steps:
    1. Market Researcher analyses the product first
    2. Pass research to the Designer (for visual direction)
    3. Pass research to the Copywriter (for messaging)
    4. Pass ALL outputs to the Launch Strategist (for timeline)
    5. Compile a final launch brief combining all outputs

    Use a final LLM call to compile everything into a structured
    "Product Launch Brief" document.

    Return the final brief.
    """
    print(f"🚀 Launching: {product}\n")

    # Step 1: Research
    research = market_researcher.run(f"Analyse this product for launch: {product}")

    # Step 2: Design (uses research)
    visuals = designer.run(
        f"Product: {product}\n\nMarket Research:\n{research}\n\n"
        f"Design the visual identity for this product launch."
    )

    # Steps 3-5: YOUR CODE HERE
    pass


# ═══════════════════════════════════════════════════════════
#  SAMPLE PRODUCTS
# ═══════════════════════════════════════════════════════════

PRODUCTS = [
    "FocusFlow — an AI-powered productivity app that learns your work patterns "
    "and creates optimised daily schedules. Features: smart task prioritisation, "
    "Pomodoro timer with AI break suggestions, integration with Calendar & Slack. "
    "Price: $9.99/month. Target: remote workers and freelancers.",

    "PetPal — a smart pet collar with GPS tracking, health monitoring, and an "
    "AI vet chat. Features: real-time location, activity tracking, heart rate "
    "monitoring, bark pattern analysis. Price: $79 + $4.99/month. Target: dog owners.",

    "LearnLingo — an AI language tutor that creates personalised lessons from "
    "your Netflix shows and YouTube videos. Features: subtitle analysis, "
    "spaced repetition, pronunciation scoring. Price: $14.99/month. Target: Gen-Z.",
]


def main():
    print("=" * 60)
    print("🚀 Product Launch Team (Multi-Agent Pattern)")
    print("=" * 60)

    product = PRODUCTS[0]  # Change index to try different products
    print(f"\n📦 Product: {product[:80]}...\n")

    result = coordinate_launch(product)

    if result:
        print("\n" + "=" * 60)
        print("📋 PRODUCT LAUNCH BRIEF")
        print("=" * 60)
        print(result)
    else:
        print("\n❌ TODOs not implemented yet!")


if __name__ == "__main__":
    main()
