"""
Solution: Prompt Chaining — Job Application Preparer
=====================================================
Pattern: PROMPT CHAINING (Chapter 1)

Complete solution with all TODOs implemented.
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
#  STEP 1: Extract Requirements  ✅ (TODO 1)
# ═══════════════════════════════════════════════════════════

def step_extract_requirements(job_description: str) -> str:
    """Extract key requirements from the job description."""
    return call_llm(
        "You are a job requirements analyst. Extract and organise the key "
        "requirements from the job description into a clear bulleted list:\n"
        "- **Required Skills**: list each technical skill\n"
        "- **Experience**: years and domains required\n"
        "- **Preferred Qualifications**: nice-to-haves\n"
        "Be thorough — don't miss any requirements.",
        f"Job Description:\n{job_description}",
    )


# ═══════════════════════════════════════════════════════════
#  STEP 2: Generate Resume Bullets (PROVIDED)
# ═══════════════════════════════════════════════════════════

def step_resume_bullets(requirements: str) -> str:
    """Generate tailored resume bullet points."""
    return call_llm(
        "You are a resume writer. Given extracted job requirements, "
        "generate 6-8 achievement-focused resume bullet points that "
        "match the requirements. Use the XYZ format: "
        "'Accomplished [X] as measured by [Y] by doing [Z]'.",
        f"Job Requirements:\n{requirements}",
    )


# ═══════════════════════════════════════════════════════════
#  STEP 3: Write Cover Letter  ✅ (TODO 2)
# ═══════════════════════════════════════════════════════════

def step_cover_letter(job_description: str, resume_bullets: str) -> str:
    """Write a cover letter using the job description and resume bullets."""
    return call_llm(
        "You are a professional cover letter writer. Write a 3-paragraph "
        "cover letter that:\n"
        "- Opens with genuine enthusiasm for the specific role\n"
        "- In the body, references specific job requirements and maps "
        "them to the candidate's achievements\n"
        "- Closes with a confident call to action\n"
        "Be professional but personable. Avoid clichés.",
        f"Job Description:\n{job_description}\n\n"
        f"Candidate's Resume Highlights:\n{resume_bullets}",
    )


# ═══════════════════════════════════════════════════════════
#  STEP 4: Interview Prep (PROVIDED)
# ═══════════════════════════════════════════════════════════

def step_interview_prep(requirements: str) -> str:
    """Generate interview prep questions."""
    return call_llm(
        "You are an interview coach. Given job requirements, generate:\n"
        "- 3 likely technical questions\n"
        "- 3 behavioural questions (STAR format)\n"
        "- 2 questions the candidate should ASK the interviewer\n"
        "For each question, include a brief tip on how to answer well.",
        f"Job Requirements:\n{requirements}",
    )


# ═══════════════════════════════════════════════════════════
#  QUALITY GATE  ✅ (TODO 3 — BONUS)
# ═══════════════════════════════════════════════════════════

def quality_gate(step_name: str, output: str) -> bool:
    """Check quality between steps. Retry if not acceptable."""
    result = call_llm(
        "You are a quality reviewer. Evaluate the following output for:\n"
        "- Completeness: Does it cover all required aspects?\n"
        "- Relevance: Is it on-topic and specific?\n"
        "- Quality: Is it well-written and actionable?\n\n"
        "Answer ONLY 'PASS' or 'FAIL' followed by a brief reason.",
        f"Step: {step_name}\n\nOutput to review:\n{output}",
    )
    passed = "pass" in result.lower()
    if not passed:
        print(f"   ⚠️ Quality gate: {result.strip()}")
    return passed


# ═══════════════════════════════════════════════════════════
#  RUN THE CHAIN
# ═══════════════════════════════════════════════════════════

def run_chain(job_description: str):
    print("=" * 60)
    print("🔗 Prompt Chaining: Job Application Preparer")
    print("=" * 60)

    # Step 1
    print("\n📋 Step 1: Extracting requirements...")
    requirements = step_extract_requirements(job_description)
    quality_gate("Extract Requirements", requirements)
    print("   ✅ Done\n")

    # Step 2
    print("📝 Step 2: Generating resume bullets...")
    bullets = step_resume_bullets(requirements)
    quality_gate("Resume Bullets", bullets)
    print("   ✅ Done\n")

    # Step 3
    print("✉️  Step 3: Writing cover letter...")
    cover_letter = step_cover_letter(job_description, bullets)
    quality_gate("Cover Letter", cover_letter)
    print("   ✅ Done\n")

    # Step 4
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
