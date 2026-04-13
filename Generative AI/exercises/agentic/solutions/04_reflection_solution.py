"""
Solution: Reflection — Self-Improving Email Writer
====================================================
Pattern: REFLECTION (Chapter 4)

Complete solution with all TODOs implemented.
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
#  ✅ TODO 1: CRITIC
# ═══════════════════════════════════════════════════════════

def critique(email: str, context: str) -> dict:
    """Critique the email and return structured feedback."""
    result = call_llm(
        "You are a professional communication coach who critiques emails.\n\n"
        "Evaluate the email on these criteria (score each out of 10):\n"
        "- tone: Is it appropriately professional yet personable?\n"
        "- clarity: Is each paragraph clear with one main point?\n"
        "- completeness: Does it address ALL points from the context?\n"
        "- professionalism: Proper grammar, no typos, appropriate sign-off?\n"
        "- length: Is it concise (100-200 words for the body)?\n\n"
        "Respond ONLY in this JSON format, nothing else:\n"
        "{\n"
        '  "overall_score": 7,\n'
        '  "criteria": {"tone": 8, "clarity": 7, "completeness": 6, "professionalism": 8, "length": 7},\n'
        '  "issues": ["issue 1", "issue 2"],\n'
        '  "suggestions": ["suggestion 1", "suggestion 2"]\n'
        "}",
        f"Original context: {context}\n\nEmail to critique:\n{email}",
    )

    try:
        return json.loads(result.strip())
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        start = result.find("{")
        end = result.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(result[start:end])
            except json.JSONDecodeError:
                pass
        # Default fallback
        return {
            "overall_score": 5,
            "criteria": {"tone": 5, "clarity": 5, "completeness": 5, "professionalism": 5, "length": 5},
            "issues": ["Could not parse structured feedback"],
            "suggestions": ["Re-evaluate manually"],
        }


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 2: REFLECTION LOOP
# ═══════════════════════════════════════════════════════════

def reflect_and_improve(context: str, max_rounds: int = 3, threshold: int = 8) -> str:
    """Implement the reflection loop."""
    feedback = ""

    for round_num in range(1, max_rounds + 1):
        print(f"\n🔄 Round {round_num}/{max_rounds}")
        print("─" * 40)

        # Generate or revise the email
        email = generate_email(context, feedback)
        print(f"   📝 Email generated ({len(email.split())} words)")

        # Critique it
        review = critique(email, context)
        score = review.get("overall_score", 0)
        issues = review.get("issues", [])
        suggestions = review.get("suggestions", [])

        print(f"   📊 Score: {score}/10")
        print(f"   📋 Criteria: {review.get('criteria', {})}")
        for issue in issues:
            print(f"   ⚠️  Issue: {issue}")

        # Good enough?
        if score >= threshold:
            print(f"\n   ✅ Score {score} meets threshold {threshold} — done!")
            return email

        # Build feedback for next round
        feedback_parts = []
        if issues:
            feedback_parts.append("Issues to fix:\n" + "\n".join(f"- {i}" for i in issues))
        if suggestions:
            feedback_parts.append("Suggestions:\n" + "\n".join(f"- {s}" for s in suggestions))
        feedback = "\n\n".join(feedback_parts)

        print(f"   🔁 Below threshold ({score} < {threshold}), improving...")

    print(f"\n   ⏹️ Max rounds reached. Returning best effort.")
    return email


# ═══════════════════════════════════════════════════════════
#  ✅ TODO 3 BONUS: RUBRIC-BASED SCORING
# ═══════════════════════════════════════════════════════════

RUBRIC = {
    "tone": "Should be warm but professional. Not too formal, not too casual.",
    "clarity": "Each paragraph should have one main point. No jargon.",
    "completeness": "Must address ALL points from the context.",
    "professionalism": "Proper grammar, no typos, appropriate sign-off.",
    "length": "Between 100-200 words for the body. Not too long.",
}


def critique_with_rubric(email: str, context: str) -> dict:
    """Use the RUBRIC to guide the critique."""
    rubric_text = "\n".join(f"- {k}: {v}" for k, v in RUBRIC.items())

    result = call_llm(
        "You are a professional communication coach. Critique the email "
        "using the following specific rubric:\n\n"
        f"{rubric_text}\n\n"
        "Score each criterion out of 10 based on how well the email meets "
        "the specific standard described.\n\n"
        "Respond ONLY in this JSON format:\n"
        "{\n"
        '  "overall_score": 7,\n'
        '  "criteria": {"tone": 8, "clarity": 7, "completeness": 6, "professionalism": 8, "length": 7},\n'
        '  "issues": ["issue 1", "issue 2"],\n'
        '  "suggestions": ["suggestion 1", "suggestion 2"]\n'
        "}",
        f"Original context: {context}\n\nEmail to critique:\n{email}",
    )

    try:
        return json.loads(result.strip())
    except json.JSONDecodeError:
        start = result.find("{")
        end = result.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(result[start:end])
            except json.JSONDecodeError:
                pass
        return {
            "overall_score": 5,
            "criteria": {k: 5 for k in RUBRIC},
            "issues": ["Could not parse structured feedback"],
            "suggestions": ["Re-evaluate manually"],
        }


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

    scenario = SCENARIOS[0]
    print(f"\n📋 Scenario: {scenario['name']}")
    print(f"   {scenario['context'][:80]}...\n")

    result = reflect_and_improve(scenario["context"])

    if result:
        print("\n" + "=" * 60)
        print("📧 FINAL EMAIL")
        print("=" * 60)
        print(result)


if __name__ == "__main__":
    main()
