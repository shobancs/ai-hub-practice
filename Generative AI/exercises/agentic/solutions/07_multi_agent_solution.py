"""
Solution: Multi-Agent — Product Launch Team
=============================================
Pattern: MULTI-AGENT (Chapter 7)

Complete solution with all TODOs implemented.
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

# ═══════════════════════════════════════════════════════════
#  ✅ TODO 1: Copywriter Agent
# ═══════════════════════════════════════════════════════════

copywriter = Agent(
    "Copywriter",
    "You are a senior copywriter specialising in product launches. "
    "Given a product and its market research, write:\n"
    "- A compelling product tagline (5-8 words)\n"
    "- Hero section headline + subheadline for the landing page\n"
    "- 3 feature descriptions with benefit-focused language\n"
    "- A call-to-action (CTA) button text + supporting line\n"
    "- 3 social media post captions\n"
    "Match the tone to the target audience. Be persuasive and concise.",
)

# ═══════════════════════════════════════════════════════════
#  ✅ TODO 2: Launch Strategist Agent
# ═══════════════════════════════════════════════════════════

launch_strategist = Agent(
    "Launch Strategist",
    "You are a product launch strategist. Given a product, its market research, "
    "visual identity, and copy, create:\n"
    "- A 4-week launch timeline with key milestones\n"
    "- 3 launch phases: Teaser (build hype), Launch Day (big reveal), "
    "Sustain (maintain momentum)\n"
    "- Recommended marketing channels (social media, email, PR, paid ads) "
    "with budget allocation percentages\n"
    "- KPIs for each phase (e.g., sign-ups, engagement rate, conversion rate)\n"
    "- Launch day hour-by-hour schedule (8am to 8pm)\n"
    "Be actionable and specific with dates and numbers.",
)


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 3: COORDINATOR
# ═══════════════════════════════════════════════════════════

def coordinate_launch(product: str) -> str:
    """Orchestrate the multi-agent product launch."""
    print(f"🚀 Launching: {product}\n")

    # Step 1: Market Research (foundation for everything else)
    research = market_researcher.run(
        f"Analyse this product for launch: {product}"
    )

    # Step 2: Visual Design (informed by research)
    visuals = designer.run(
        f"Product: {product}\n\n"
        f"Market Research:\n{research}\n\n"
        f"Design the visual identity for this product launch."
    )

    # Step 3: Copywriting (informed by research)
    copy = copywriter.run(
        f"Product: {product}\n\n"
        f"Market Research:\n{research}\n\n"
        f"Write all the launch copy for this product."
    )

    # Step 4: Launch Strategy (informed by all previous outputs)
    strategy = launch_strategist.run(
        f"Product: {product}\n\n"
        f"Market Research:\n{research}\n\n"
        f"Visual Identity:\n{visuals}\n\n"
        f"Copy & Messaging:\n{copy}\n\n"
        f"Create the complete launch strategy."
    )

    # Step 5: Compile final brief
    print("  📋 Compiling final launch brief...\n")
    brief = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a project manager. Compile all the team outputs "
                    "into a structured Product Launch Brief document with these sections:\n"
                    "1. Executive Summary\n"
                    "2. Market Research Highlights\n"
                    "3. Visual Identity\n"
                    "4. Messaging & Copy\n"
                    "5. Launch Strategy & Timeline\n"
                    "6. Success Metrics\n\n"
                    "Be well-organised and use clear headings."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Product: {product}\n\n"
                    f"--- Market Research ---\n{research}\n\n"
                    f"--- Visual Identity ---\n{visuals}\n\n"
                    f"--- Copy & Messaging ---\n{copy}\n\n"
                    f"--- Launch Strategy ---\n{strategy}"
                ),
            },
        ],
    ).choices[0].message.content

    return brief


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

    product = PRODUCTS[0]
    print(f"\n📦 Product: {product[:80]}...\n")

    result = coordinate_launch(product)

    if result:
        print("\n" + "=" * 60)
        print("📋 PRODUCT LAUNCH BRIEF")
        print("=" * 60)
        print(result)


if __name__ == "__main__":
    main()
