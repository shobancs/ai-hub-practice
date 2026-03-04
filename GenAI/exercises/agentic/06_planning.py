"""
Exercise: Planning — Trip Planner Agent
=========================================
Pattern: PLANNING (Chapter 6)

GOAL:
  Build an agent that takes a travel request, creates a plan,
  executes each step, and re-plans if something changes.

YOUR TASKS:
  1. Implement create_plan()     (TODO 1)
  2. Implement execute_step()    (TODO 2)
  3. Wire up the plan-execute loop (TODO 3)

SETUP:
  pip install openai python-dotenv

RUN:
  python 06_planning.py
"""

import os, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(system: str, user: str) -> str:
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return r.choices[0].message.content


# ═══════════════════════════════════════════════════════════
#  STEP 1: CREATE PLAN
# ═══════════════════════════════════════════════════════════

def create_plan(goal: str, context: str = "") -> list[str]:
    """
    TODO 1: Ask the LLM to create a step-by-step plan.

    System prompt should instruct the LLM to:
    - Break the goal into 4-6 concrete steps
    - Each step should be a single clear action
    - Output as a numbered list (1. xxx, 2. xxx, etc.)
    - If context is provided (from previous steps), account for it

    Parse the response into a list of strings (one per step).
    Hint: Split by newlines, strip whitespace, filter empty lines.
    """
    import re

    prompt = f"Travel request: {goal}"
    if context:
        prompt += f"\n\nContext from previous research:\n{context}"

    result = call_llm(
        "You are a travel planning expert. Break the travel request into "
        "4-6 concrete research steps. Each step should be a single clear "
        "action like 'Research flights from X to Y' or 'Find hotels in Z'.\n\n"
        "Output as a numbered list:\n"
        "1. First step\n"
        "2. Second step\n"
        "...\n\n"
        "ONLY output the numbered list, nothing else.",
        prompt,
    )

    # Parse numbered steps — remove "1.", "2)", "- ", etc.
    steps = []
    for line in result.strip().split("\n"):
        line = line.strip()
        cleaned = re.sub(r"^\d+[\.)\-]\s*", "", line)
        cleaned = re.sub(r"^[-•]\s*", "", cleaned)
        if cleaned:
            steps.append(cleaned)

    return steps


# ═══════════════════════════════════════════════════════════
#  STEP 2: EXECUTE A STEP
# ═══════════════════════════════════════════════════════════

def execute_step(step: str, context: str) -> str:
    """
    TODO 2: Execute one step of the plan.

    Call call_llm() with:
    - System prompt: "You are a travel planning assistant executing 
      one step of a plan. Be specific and detailed. Include real 
      suggestions (hotels, restaurants, activities, prices)."
    - User prompt: The step to execute + context from previous steps

    Return the result.
    """
    return call_llm(
        "You are a travel planning assistant executing one step of a plan. "
        "Be specific and detailed. Include real suggestions:\n"
        "- Specific hotel names with approximate prices\n"
        "- Restaurant names with cuisine types\n"
        "- Activity suggestions with durations and costs\n"
        "- Transportation options and tips\n"
        "Keep your response focused on just this one step.",
        f"Step to execute: {step}\n\n"
        f"Context from previous steps:\n{context if context else 'This is the first step.'}",
    )


# ═══════════════════════════════════════════════════════════
#  STEP 3: CHECK IF RE-PLAN NEEDED (PROVIDED)
# ═══════════════════════════════════════════════════════════

def should_replan(step_result: str, remaining_steps: list[str]) -> bool:
    """Check if the remaining plan still makes sense."""
    if not remaining_steps:
        return False
    result = call_llm(
        "You evaluate travel plans. Given the latest research result, "
        "determine if the remaining steps still make sense. "
        "Answer ONLY 'yes' (replan needed) or 'no' (plan is fine).",
        f"Latest result:\n{step_result}\n\n"
        f"Remaining steps:\n" + "\n".join(remaining_steps),
    )
    return "yes" in result.lower()


# ═══════════════════════════════════════════════════════════
#  SYNTHESISER (PROVIDED)
# ═══════════════════════════════════════════════════════════

def synthesise(goal: str, all_results: str) -> str:
    """Combine all step results into a final travel plan."""
    return call_llm(
        "You are a travel agent. Combine all the research into a "
        "beautiful, well-organised final travel itinerary. Include:\n"
        "- Day-by-day schedule\n"
        "- Accommodation recommendations\n"
        "- Restaurant suggestions\n"
        "- Estimated budget breakdown\n"
        "- Packing tips",
        f"Trip request: {goal}\n\nResearch:\n{all_results}",
    )


# ═══════════════════════════════════════════════════════════
#  PLAN-AND-EXECUTE LOOP
# ═══════════════════════════════════════════════════════════

def plan_and_execute(goal: str) -> str:
    """
    TODO 3: Wire up the planning loop.

    Steps:
    1. Call create_plan(goal) to get the initial list of steps
    2. Print the plan
    3. Loop through each step:
       a. Call execute_step(step, context)
       b. Append the result to the running context
       c. Check should_replan() for remaining steps
       d. If replan needed, call create_plan() with the updated context
    4. Call synthesise() to produce the final itinerary
    5. Return the final itinerary

    Print progress as you go (step number, step name, ✅ done).
    """
    # 1️⃣  Create the initial plan
    print("📋 Creating plan...")
    steps = create_plan(goal)

    if not steps:
        return "Failed to create a plan."

    print(f"\n📋 Plan ({len(steps)} steps):")
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    print()

    # 2️⃣  Execute each step, accumulating context
    context = ""
    all_results = ""
    step_num = 0

    while steps:
        step = steps.pop(0)
        step_num += 1

        print(f"▶️  Step {step_num}: {step}")
        result = execute_step(step, context)
        print(f"   ✅ Done\n")

        # Build running context for downstream steps
        context += f"\n\n--- Step {step_num}: {step} ---\n{result}"
        all_results += f"\n\n## Step {step_num}: {step}\n{result}"

        # 3️⃣  Re-plan if remaining steps no longer make sense
        if steps and should_replan(result, steps):
            print("🔄 Re-planning remaining steps...")
            steps = create_plan(goal, context)
            print(f"   📋 New plan ({len(steps)} steps):")
            for i, s in enumerate(steps, 1):
                print(f"      {i}. {s}")
            print()

    # 4️⃣  Synthesise everything into a final itinerary
    print("📝 Synthesising final itinerary...")
    itinerary = synthesise(goal, all_results)

    return itinerary


# ═══════════════════════════════════════════════════════════
#  SAMPLE TRAVEL REQUESTS
# ═══════════════════════════════════════════════════════════

TRIPS = [
    "Plan a 5-day trip to Tokyo for a couple who loves food and anime, "
    "budget $3000, visiting in April during cherry blossom season.",

    "Plan a 3-day weekend getaway to Barcelona for a solo traveller "
    "interested in architecture and nightlife, budget $1500.",

    "Plan a 7-day family vacation (2 adults, 2 kids ages 8 and 12) "
    "to Orlando, Florida. Budget $5000. Must include theme parks.",
]


def main():
    print("=" * 60)
    print("🗺️  Trip Planner (Planning Pattern)")
    print("=" * 60)

    trip = TRIPS[0]  # Change index to try different trips
    print(f"\n📋 Request: {trip}\n")

    result = plan_and_execute(trip)

    if result:
        print("\n" + "=" * 60)
        print("🗺️  FINAL ITINERARY")
        print("=" * 60)
        print(result)
    else:
        print("\n❌ TODOs not implemented yet!")


if __name__ == "__main__":
    main()
