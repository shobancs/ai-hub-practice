"""
Solution: Exercise 8 — Sequential Pipeline Email Campaign Generator
====================================================================
Pattern: SEQUENTIAL (Pipeline)
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ── Helper ────────────────────────────────────────────────────

def call_agent(system_prompt: str, user_input: str, model: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


# ── Stage Prompts (SOLUTIONS) ────────────────────────────────

AUDIENCE_ANALYZER_PROMPT = """You are an expert Marketing Audience Analyst.

Given a product description, identify exactly 3 target audience segments.

For EACH segment, provide:
1. Segment Name (e.g., "Tech-Savvy Professionals")
2. Demographics (age range, income, occupation)
3. Pain Points (what problems they have that this product solves)
4. Messaging Angle (how to appeal to this segment)

Format your response as a numbered list with clear headers for each segment.
Be specific and actionable — avoid generic descriptions."""


SUBJECT_LINE_WRITER_PROMPT = """You are an Email Subject Line Specialist with 15 years of experience.

Given audience segments and a product description, generate email subject lines.

For EACH of the 3 audience segments, create exactly 5 subject lines that:
- Are under 60 characters
- Create curiosity or urgency
- Are personalized to the segment's pain points
- Include at least one emoji option and one without

Also mark your TOP PICK for each segment with ⭐.

Format:
## Segment 1: [Name]
1. [subject line]
2. [subject line]
...
⭐ Top Pick: #[number]

Repeat for all 3 segments."""


EMAIL_BODY_WRITER_PROMPT = """You are an Email Copywriter who specializes in high-converting marketing emails.

Given audience segments, the best subject lines, and a product description,
write 3 email versions (one per audience segment).

Each email MUST include:
1. **Opening Hook** (first 2 sentences — grab attention, reference their pain point)
2. **Value Proposition** (what the product does for THEM specifically)
3. **Social Proof** (a stat, testimonial, or credibility marker)
4. **Feature Highlights** (3 bullet points most relevant to this segment)
5. **Call to Action** (clear, specific, one primary CTA button text)
6. **P.S. Line** (urgency or bonus offer)

Each email should be 150-200 words. Write in a conversational but professional tone.
Personalize heavily for each segment — these should NOT feel like the same email."""


AB_TEST_PLANNER_PROMPT = """You are an Email Marketing Optimization Specialist.

Given the email campaign components (audiences, subject lines, email bodies),
create a comprehensive A/B testing plan:

1. **Test Matrix** — What to test:
   - Subject line variants (which 2 per segment to test)
   - Send time variants (suggest 2 time slots based on segment behavior)
   - CTA button text variants (2 options per email)
   - Preview text variants

2. **Test Parameters**:
   - Recommended sample size per variant (with reasoning)
   - Test duration (how long to run before picking winner)
   - Statistical significance threshold (suggest 95%)
   - Primary metric (open rate for subject, click rate for CTA)

3. **Implementation Timeline**:
   - Week 1: [actions]
   - Week 2: [actions]
   - Week 3: [actions]

4. **Success Criteria**:
   - What open rate = good? (benchmark by industry)
   - What click rate = good?
   - When to scale the winner

Be specific with numbers and timelines."""


# ── Pipeline Runner (SOLUTION) ────────────────────────────────

def validate_output(stage_name: str, output: str, min_length: int = 100) -> bool:
    if not output or len(output.strip()) < min_length:
        print(f"  ⚠️  {stage_name} output too short ({len(output)} chars). Retrying...")
        return False
    return True


def run_stage(stage_name: str, prompt: str, user_input: str, max_retries: int = 2) -> str:
    """Run a single pipeline stage with retry logic."""
    print(f"\n{'─' * 40}")
    print(f"🔄 Stage: {stage_name}")
    print(f"{'─' * 40}")

    for attempt in range(max_retries + 1):
        output = call_agent(prompt, user_input)

        if validate_output(stage_name, output):
            print(f"  ✅ {stage_name} complete! ({len(output)} chars)")
            return output

        if attempt < max_retries:
            print(f"  🔁 Retry {attempt + 1}/{max_retries}...")

    print(f"  ⚠️  {stage_name} returned short output after retries. Proceeding anyway.")
    return output


def email_campaign_pipeline(product_description: str) -> dict:
    """Run the full sequential email campaign pipeline."""
    results = {}
    print(f"\n🚀 Starting Email Campaign Pipeline\n")

    # Stage 1: Audience Analysis
    results["audiences"] = run_stage(
        "Audience Analyzer",
        AUDIENCE_ANALYZER_PROMPT,
        f"Analyze audiences for this product:\n\n{product_description}"
    )

    # Stage 2: Subject Lines (uses Stage 1 output)
    results["subject_lines"] = run_stage(
        "Subject Line Writer",
        SUBJECT_LINE_WRITER_PROMPT,
        (
            f"Product:\n{product_description}\n\n"
            f"Target Audiences:\n{results['audiences']}"
        )
    )

    # Stage 3: Email Bodies (uses Stage 1 + 2 outputs)
    results["email_bodies"] = run_stage(
        "Email Body Writer",
        EMAIL_BODY_WRITER_PROMPT,
        (
            f"Product:\n{product_description}\n\n"
            f"Target Audiences:\n{results['audiences']}\n\n"
            f"Subject Lines:\n{results['subject_lines']}"
        )
    )

    # Stage 4: A/B Test Plan (uses all previous outputs)
    results["ab_test_plan"] = run_stage(
        "A/B Test Planner",
        AB_TEST_PLANNER_PROMPT,
        (
            f"Product:\n{product_description}\n\n"
            f"Audiences:\n{results['audiences']}\n\n"
            f"Subject Lines:\n{results['subject_lines']}\n\n"
            f"Email Bodies:\n{results['email_bodies']}"
        )
    )

    return results


# ── Sample Products ───────────────────────────────────────────

SAMPLE_PRODUCTS = {
    "saas_tool": """
        ProductivAI — AI-powered project management tool.
        Features: auto task prioritization, meeting summarizer, deadline predictor.
        Price: $15/user/month. Target: remote teams and startups.
        Launched 2025, 5000+ teams, 4.8/5 rating.
    """,
    "fitness_app": """
        FitGenius — Personalized AI fitness coach app.
        Features: custom workout plans, nutrition tracking, form analysis via camera.
        Price: $9.99/month or $79.99/year.
        Target: fitness beginners who want gym-quality guidance at home.
    """,
    "dev_tool": """
        CodeShield — AI-powered code security scanner.
        Features: real-time vulnerability detection, auto-fix suggestions,
        compliance reporting (SOC2, HIPAA), CI/CD integration.
        Price: Free for open source, $29/dev/month for teams.
        Target: development teams who care about security.
    """,
}


# ── CLI ───────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("📧 Email Campaign Generator (Solution)")
    print("=" * 60)

    print("\nAvailable sample products:")
    for key, desc in SAMPLE_PRODUCTS.items():
        print(f"  • {key}: {desc.strip().split(chr(10))[0].strip()}")

    choice = input("\nChoose a product (or 'custom'): ").strip().lower()

    if choice == "custom":
        print("Enter your product description (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        product_desc = "\n".join(lines)
    elif choice in SAMPLE_PRODUCTS:
        product_desc = SAMPLE_PRODUCTS[choice]
    else:
        product_desc = SAMPLE_PRODUCTS["saas_tool"]

    results = email_campaign_pipeline(product_desc)

    print("\n" + "=" * 60)
    print("📊 PIPELINE RESULTS")
    print("=" * 60)

    for stage_name, output in results.items():
        print(f"\n{'─' * 40}")
        print(f"📌 {stage_name.upper().replace('_', ' ')}")
        print(f"{'─' * 40}")
        print(output)

    output_file = "email_campaign_output.md"
    with open(output_file, "w") as f:
        f.write("# Email Campaign — Generated Output\n\n")
        for stage_name, output in results.items():
            f.write(f"## {stage_name.replace('_', ' ').title()}\n\n{output}\n\n---\n\n")
    print(f"\n💾 Saved to {output_file}")


if __name__ == "__main__":
    main()
