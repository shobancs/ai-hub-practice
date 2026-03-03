"""
Exercise 8: Sequential Pipeline — Email Campaign Generator
============================================================
Difficulty: ⭐⭐ Intermediate
Time: 60-90 minutes
Pattern: SEQUENTIAL (Pipeline)

GOAL:
  Build a 4-stage pipeline that takes a product description and generates
  a complete email marketing campaign:
    Stage 1: Audience Analyzer  → Identify target segments
    Stage 2: Subject Line Writer → Generate 5 subject lines per segment
    Stage 3: Email Body Writer   → Write email body for best subject line
    Stage 4: A/B Test Planner    → Create A/B testing plan

YOUR TASKS:
  1. Complete the stage prompts (marked with TODO)
  2. Implement the pipeline runner
  3. Add validation between stages
  4. Test with sample products

CONCEPTS:
  - Sequential agent handoff
  - Output validation between stages
  - Context passing through a pipeline

SETUP:
  pip install openai python-dotenv

RUN:
  python 08_sequential_agents.py
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ╔══════════════════════════════════════════════════════════════╗
# ║  HELPER: Call an LLM agent with a specific role              ║
# ╚══════════════════════════════════════════════════════════════╝

def call_agent(system_prompt: str, user_input: str, model: str = "gpt-4o-mini") -> str:
    """Call the LLM with a system prompt and user input."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


# ╔══════════════════════════════════════════════════════════════╗
# ║  STAGE 1: Audience Analyzer                                  ║
# ╚══════════════════════════════════════════════════════════════╝

AUDIENCE_ANALYZER_PROMPT = """You are an expert Marketing Audience Analyst.

Given a product description, identify exactly 3 target audience segments.

For EACH segment, provide:
1. Segment Name (e.g., "Tech-Savvy Professionals")
2. Demographics (age range, income, occupation)
3. Pain Points (what problems they have that this product solves)
4. Messaging Angle (how to appeal to this segment)

Format your response as a numbered list with clear headers for each segment.
Be specific and actionable — avoid generic descriptions."""


# TODO: Complete Stage 2 prompt
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

# TODO: Write the prompt for Stage 3
# It should:
# - Take the best subject line + audience segment info
# - Write a compelling email body (150-200 words)
# - Include: hook, value proposition, social proof, CTA
# - Write 3 different email versions (one per segment)
EMAIL_BODY_WRITER_PROMPT = """
TODO: Write your Stage 3 prompt here.
"""


# TODO: Write the prompt for Stage 4
# It should:
# - Create an A/B testing plan for the email campaign
# - Define what to test (subject lines, send times, CTAs)
# - Specify success metrics (open rate, click rate, conversion)
# - Recommend sample sizes and test duration
AB_TEST_PLANNER_PROMPT = """
TODO: Write your Stage 4 prompt here.
"""


# ╔══════════════════════════════════════════════════════════════╗
# ║  PIPELINE STAGES                                             ║
# ╚══════════════════════════════════════════════════════════════╝

def validate_output(stage_name: str, output: str, min_length: int = 100) -> bool:
    """Basic validation: ensure output is not empty and meets minimum length."""
    if not output or len(output.strip()) < min_length:
        print(f"  ⚠️  {stage_name} output too short ({len(output)} chars). Retrying...")
        return False
    return True


def run_stage(stage_name: str, prompt: str, user_input: str, max_retries: int = 2) -> str:
    """
    Run a single pipeline stage with retry logic.

    TODO: Implement this function:
    1. Print stage start message
    2. Call call_agent() with the prompt and user_input
    3. Validate the output using validate_output()
    4. If invalid, retry up to max_retries times
    5. Print stage completion message
    6. Return the output
    """
    pass


# ╔══════════════════════════════════════════════════════════════╗
# ║  MAIN PIPELINE                                               ║
# ╚══════════════════════════════════════════════════════════════╝

def email_campaign_pipeline(product_description: str) -> dict:
    """
    Run the full email campaign pipeline.

    TODO: Implement the sequential pipeline:
    1. Run Stage 1 (Audience Analyzer) with the product description
    2. Run Stage 2 (Subject Lines) with product_description + Stage 1 output
    3. Run Stage 3 (Email Body) with product_description + Stage 1 + Stage 2 output
    4. Run Stage 4 (A/B Testing) with all previous outputs
    5. Return a dict with all stage results

    Hint: Each stage's input should include relevant outputs from previous stages.
    Format the input clearly so each agent knows what it's working with.
    """
    results = {}

    # Stage 1: Audience Analysis
    # results["audiences"] = run_stage(...)

    # Stage 2: Subject Lines
    # results["subject_lines"] = run_stage(...)

    # Stage 3: Email Bodies
    # results["email_bodies"] = run_stage(...)

    # Stage 4: A/B Testing Plan
    # results["ab_test_plan"] = run_stage(...)

    return results


# ╔══════════════════════════════════════════════════════════════╗
# ║  SAMPLE PRODUCTS — Test your pipeline with these             ║
# ╚══════════════════════════════════════════════════════════════╝

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


# ╔══════════════════════════════════════════════════════════════╗
# ║  CLI RUNNER                                                   ║
# ╚══════════════════════════════════════════════════════════════╝

def main():
    print("=" * 60)
    print("📧 Email Campaign Generator Pipeline")
    print("=" * 60)

    print("\nAvailable sample products:")
    for key, desc in SAMPLE_PRODUCTS.items():
        print(f"  • {key}: {desc.strip().split(chr(10))[0].strip()}")

    print(f"\nOr type 'custom' to enter your own product description.")
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
        print(f"Unknown choice: {choice}. Using 'saas_tool'.")
        product_desc = SAMPLE_PRODUCTS["saas_tool"]

    print(f"\n🚀 Starting pipeline for: {product_desc.strip()[:80]}...\n")

    results = email_campaign_pipeline(product_desc)

    # Print results
    print("\n" + "=" * 60)
    print("📊 PIPELINE RESULTS")
    print("=" * 60)

    for stage_name, output in results.items():
        print(f"\n{'─' * 40}")
        print(f"📌 {stage_name.upper().replace('_', ' ')}")
        print(f"{'─' * 40}")
        print(output)

    # Save to file
    output_file = "email_campaign_output.md"
    with open(output_file, "w") as f:
        f.write(f"# Email Campaign — Generated {os.popen('date').read().strip()}\n\n")
        for stage_name, output in results.items():
            f.write(f"## {stage_name.replace('_', ' ').title()}\n\n{output}\n\n---\n\n")
    print(f"\n💾 Saved to {output_file}")


if __name__ == "__main__":
    main()
