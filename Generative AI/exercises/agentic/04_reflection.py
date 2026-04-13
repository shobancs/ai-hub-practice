"""
Exercise: Reflection — Self-Improving Email Writer
====================================================
Pattern: REFLECTION (Chapter 4)

GOAL:
  Build an agent that drafts a professional email, critiques it,
  and iteratively improves it until it meets quality standards.

YOUR TASKS:
  1. Implement the critique() function      (TODO 1)
  2. Implement the reflection loop          (TODO 2)
  3. (Bonus) Add rubric-based scoring       (TODO 3)

SETUP:
  pip install openai python-dotenv

RUN:
  python 04_reflection.py
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
#  GENERATOR (PROVIDED)
# ═══════════════════════════════════════════════════════════

def generate_email(context: str, feedback: str = "") -> str:
    """Generate (or revise) a professional email."""
    prompt = f"Write a professional email for this situation:\n{context}"
    if feedback:
        prompt += f"\n\nIMPROVEMENT FEEDBACK from reviewer:\n{feedback}"
        prompt += "\n\nRevise the email addressing ALL the feedback above."

    return call_llm(
        "You are a professional email writer. Write clear, concise, "
        "and well-structured emails. Include subject line, greeting, "
        "body, and sign-off.",
        prompt,
    )


# ═══════════════════════════════════════════════════════════
#  CRITIC
# ═══════════════════════════════════════════════════════════

def critique(email: str, context: str) -> dict:
    """
    TODO 1: Critique the email and return structured feedback.

    Call call_llm() with a system prompt that asks the model to:
    - Evaluate: tone, clarity, completeness, professionalism, length
    - Score each criterion out of 10
    - Provide an overall score (average)
    - List specific issues
    - List specific suggestions for improvement

    IMPORTANT: Ask the model to respond in this exact JSON format:
    {
        "overall_score": 7,
        "criteria": {
            "tone": 8,
            "clarity": 7,
            "completeness": 6,
            "professionalism": 8,
            "length": 7
        },
        "issues": ["issue 1", "issue 2"],
        "suggestions": ["suggestion 1", "suggestion 2"]
    }

    Parse the JSON and return it as a dict.
    If JSON parsing fails, return a default dict with score 5.
    """
    # YOUR CODE HERE
    pass


# ═══════════════════════════════════════════════════════════
#  REFLECTION LOOP
# ═══════════════════════════════════════════════════════════

def reflect_and_improve(context: str, max_rounds: int = 3, threshold: int = 8) -> str:
    """
    TODO 2: Implement the reflection loop.

    Loop up to max_rounds times:
      1. Generate (or revise) the email
      2. Critique it
      3. If overall_score >= threshold → return the email (good enough!)
      4. Otherwise, build a feedback string from the critique and loop again

    Print progress for each round:
      - Round number
      - Score
      - Issues found

    Return the final email.
    """
    # YOUR CODE HERE
    pass


# ═══════════════════════════════════════════════════════════
#  BONUS: RUBRIC-BASED SCORING
# ═══════════════════════════════════════════════════════════

RUBRIC = {
    "tone": "Should be warm but professional. Not too formal, not too casual.",
    "clarity": "Each paragraph should have one main point. No jargon.",
    "completeness": "Must address ALL points from the context.",
    "professionalism": "Proper grammar, no typos, appropriate sign-off.",
    "length": "Between 100-200 words for the body. Not too long.",
}

def critique_with_rubric(email: str, context: str) -> dict:
    """
    TODO 3 (BONUS): Use the RUBRIC above to guide the critique.
    
    Pass the rubric criteria into the system prompt so the critic
    evaluates against specific standards rather than being vague.
    """
    # YOUR CODE HERE
    pass


# ═══════════════════════════════════════════════════════════
#  SAMPLE SCENARIOS
# ═══════════════════════════════════════════════════════════

SCENARIOS = [
    {
        "name": "Project Delay Notification",
        "context": "You need to inform your client (Sarah, CEO of TechCorp) that "
                   "the project delivery will be delayed by 2 weeks due to unexpected "
                   "API integration issues. Offer a revised timeline and propose a "
                   "brief call to discuss mitigation steps.",
    },
    {
        "name": "Job Offer Negotiation",
        "context": "You received a job offer for $120K but you were hoping for $140K. "
                   "Write an email to the hiring manager (David) expressing enthusiasm "
                   "for the role while negotiating the salary. Mention your 8 years of "
                   "experience and a competing offer.",
    },
    {
        "name": "Partnership Proposal",
        "context": "You want to propose a partnership between your AI startup and "
                   "a university's CS department. Offer to provide API access for "
                   "research projects in exchange for case studies and co-authored papers.",
    },
]


def main():
    print("=" * 60)
    print("🔄 Reflection: Self-Improving Email Writer")
    print("=" * 60)

    scenario = SCENARIOS[0]  # Change index to try different scenarios
    print(f"\n📋 Scenario: {scenario['name']}")
    print(f"   {scenario['context'][:80]}...\n")

    result = reflect_and_improve(scenario["context"])

    if result:
        print("\n" + "=" * 60)
        print("📧 FINAL EMAIL")
        print("=" * 60)
        print(result)
    else:
        print("\n❌ TODO 2 not implemented yet!")


if __name__ == "__main__":
    main()
