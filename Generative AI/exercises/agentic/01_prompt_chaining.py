"""
Exercise: Prompt Chaining — Job Application Preparer
=====================================================
Pattern: PROMPT CHAINING (Chapter 1)

GOAL:
  Build a 4-step chain that takes a job description and produces:
    Step 1: Extract key requirements from the job description
    Step 2: Generate tailored resume bullet points
    Step 3: Write a cover letter draft
    Step 4: Create interview prep questions

YOUR TASKS:
  1. Implement step_extract_requirements()  (TODO 1)
  2. Implement step_cover_letter()          (TODO 2)
  3. Add a quality gate between steps       (TODO 3)

SETUP:
  pip install openai python-dotenv

RUN:
  python 01_prompt_chaining.py
"""

import os
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
#  STEP 1: Extract Requirements
# ═══════════════════════════════════════════════════════════

def step_extract_requirements(job_description: str) -> str:
    """
    TODO 1: Extract key requirements from the job description.
    
    Call call_llm() with a system prompt that instructs the LLM to:
    - List required skills
    - List required experience (years, domains)
    - List preferred qualifications
    - Output as a structured bulleted list
    """
    # YOUR CODE HERE
    pass


# ═══════════════════════════════════════════════════════════
#  STEP 2: Generate Resume Bullets (PROVIDED)
# ═══════════════════════════════════════════════════════════

def step_resume_bullets(requirements: str) -> str:
    """Generate tailored resume bullet points. (DONE — use as reference)"""
    return call_llm(
        "You are a resume writer. Given extracted job requirements, "
        "generate 6-8 achievement-focused resume bullet points that "
        "match the requirements. Use the XYZ format: "
        "'Accomplished [X] as measured by [Y] by doing [Z]'.",
        f"Job Requirements:\n{requirements}",
    )


# ═══════════════════════════════════════════════════════════
#  STEP 3: Write Cover Letter
# ═══════════════════════════════════════════════════════════

def step_cover_letter(job_description: str, resume_bullets: str) -> str:
    """
    TODO 2: Write a cover letter using the job description and resume bullets.

    Call call_llm() with a system prompt that instructs the LLM to:
    - Write a 3-paragraph cover letter
    - Reference specific requirements from the job
    - Incorporate the resume bullet achievements
    - Be professional but personable
    """
    # YOUR CODE HERE
    pass


# ═══════════════════════════════════════════════════════════
#  STEP 4: Interview Prep (PROVIDED)
# ═══════════════════════════════════════════════════════════

def step_interview_prep(requirements: str) -> str:
    """Generate interview prep questions. (DONE)"""
    return call_llm(
        "You are an interview coach. Given job requirements, generate:\n"
        "- 3 likely technical questions\n"
        "- 3 behavioural questions (STAR format)\n"
        "- 2 questions the candidate should ASK the interviewer\n"
        "For each question, include a brief tip on how to answer well.",
        f"Job Requirements:\n{requirements}",
    )


# ═══════════════════════════════════════════════════════════
#  QUALITY GATE (OPTIONAL CHALLENGE)
# ═══════════════════════════════════════════════════════════

def quality_gate(step_name: str, output: str) -> bool:
    """
    TODO 3 (BONUS): Add a quality check between steps.
    
    Call call_llm() to evaluate whether the output is:
    - Complete (covers all required aspects)
    - Relevant (matches the job context)
    
    Return True if quality is acceptable, False to retry.
    """
    # YOUR CODE HERE
    return True  # Default: always pass


# ═══════════════════════════════════════════════════════════
#  RUN THE CHAIN
# ═══════════════════════════════════════════════════════════

def run_chain(job_description: str):
    print("=" * 60)
    print("🔗 Prompt Chaining: Job Application Preparer")
    print("=" * 60)

    print("\n📋 Step 1: Extracting requirements...")
    requirements = step_extract_requirements(job_description)
    if requirements is None:
        print("   ❌ TODO 1 not implemented yet!")
        return
    print("   ✅ Done\n")

    print("📝 Step 2: Generating resume bullets...")
    bullets = step_resume_bullets(requirements)
    print("   ✅ Done\n")

    print("✉️  Step 3: Writing cover letter...")
    cover_letter = step_cover_letter(job_description, bullets)
    if cover_letter is None:
        print("   ❌ TODO 2 not implemented yet!")
        return
    print("   ✅ Done\n")

    print("🎤 Step 4: Preparing interview questions...")
    interview = step_interview_prep(requirements)
    print("   ✅ Done\n")

    # Print results
    print("=" * 60)
    print("📋 REQUIREMENTS")
    print("=" * 60)
    print(requirements)

    print("\n" + "=" * 60)
    print("📝 RESUME BULLETS")
    print("=" * 60)
    print(bullets)

    print("\n" + "=" * 60)
    print("✉️  COVER LETTER")
    print("=" * 60)
    print(cover_letter)

    print("\n" + "=" * 60)
    print("🎤 INTERVIEW PREP")
    print("=" * 60)
    print(interview)


# ═══════════════════════════════════════════════════════════
#  SAMPLE JOB DESCRIPTION
# ═══════════════════════════════════════════════════════════

SAMPLE_JOB = """
Senior Python Developer — AI Platform Team

We're looking for a Senior Python Developer to join our AI Platform team.

Requirements:
- 5+ years of Python development experience
- Strong understanding of async programming (asyncio)
- Experience with LLM APIs (OpenAI, Anthropic, or similar)
- Familiarity with FastAPI or Flask for building REST APIs
- Experience with Docker and Kubernetes
- Strong testing practices (pytest, CI/CD)

Preferred:
- Experience with agent frameworks (LangChain, AutoGen, CrewAI)
- Knowledge of vector databases (Pinecone, Weaviate, Chroma)
- Contributions to open-source projects
- Experience mentoring junior developers

We offer competitive salary, remote work, and a team passionate about AI.
"""

if __name__ == "__main__":
    run_chain(SAMPLE_JOB)
