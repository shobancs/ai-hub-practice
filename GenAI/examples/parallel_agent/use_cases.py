"""
Parallel Agent Pattern — Use Case Blueprints
============================================
PATTERN : PARALLEL  (Fan-Out → Fan-In)
SDK     : OpenAI Python SDK (async)

Five production-ready blueprints showing the parallel pattern across
different industries. Each blueprint shares the same structure:

  1. N independent worker agents analyse the same input from different angles
  2. asyncio.gather() launches all workers at the same instant
  3. A single aggregator agent synthesises all worker reports into a final verdict

USE CASES:
  1. Code Security Audit         — DevSec / Engineering
  2. Job Candidate Screening     — HR / Talent Acquisition
  3. Academic Paper Review       — Research / Publishing
  4. Product Review Intelligence — E-commerce / Consumer
  5. Crisis Communication Triage — PR / Communications

RUN:
  python use_cases.py
"""

import asyncio
import os
import pathlib
import time

from openai import AsyncOpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

# ─── Load .env from the GenAI parent directory ────────────────────────────────
_env_path = pathlib.Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)

console = Console()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL          = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client         = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED UTILITY
# ══════════════════════════════════════════════════════════════════════════════

async def _call(system: str, user: str) -> str:
    """Thin async wrapper around the OpenAI chat endpoint."""
    r = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.6,
    )
    return r.choices[0].message.content


def _timed_panel(label: str, style: str, text: str, elapsed: float) -> None:
    """Print a rich panel with elapsed time in the subtitle."""
    console.print(Panel(
        text,
        title=f"[{style}]{label}[/{style}]",
        subtitle=f"[dim]{elapsed:.1f}s[/dim]",
        border_style=style,
        padding=(0, 1),
    ))


async def _run_parallel(topic: str, workers: list, aggregator_fn) -> str:
    """
    Generic parallel runner:
      1. Fan-out  — launch all worker coroutines concurrently
      2. Timing   — print a wall-clock vs sequential comparison table
      3. Fan-in   — pass all reports to the aggregator
    Returns the aggregator's final output string.
    """
    t_wall = time.perf_counter()
    reports: list[dict] = await asyncio.gather(*[w(topic) for w in workers])
    wall_time = time.perf_counter() - t_wall

    # Timing table
    table = Table(show_header=True, header_style="bold cyan",
                  border_style="dim", title="⏱  Timing")
    table.add_column("Worker");  table.add_column("Time", justify="right")
    for r in reports:
        table.add_row(r["label"], f"{r['elapsed']:.1f}s")
    seq_total = sum(r["elapsed"] for r in reports)
    table.add_row("[bold green]Wall-clock (parallel)[/bold green]",
                  f"[bold green]{wall_time:.1f}s[/bold green]")
    table.add_row("[dim red]Sequential would take ≈[/dim red]",
                  f"[dim red]{seq_total:.1f}s[/dim red]")
    table.add_row("[bold]Speedup[/bold]",
                  f"[bold yellow]{seq_total / wall_time:.1f}×[/bold yellow]")
    console.print(table)

    return await aggregator_fn(topic, reports)


# ══════════════════════════════════════════════════════════════════════════════
#
#  USE CASE 1 — Code Security Audit
#  ─────────────────────────────────
#  PROBLEM : Reviewing a code snippet / PR for multiple quality dimensions
#            sequentially is slow and subjective. Running specialist reviewers
#            in parallel gives a faster, more comprehensive audit.
#
#  WORKERS : Security | Performance | Code Quality | Dependencies | Test Coverage
#  FAN-IN  : Lead Architect — produces a prioritised fix list + verdict
#
#  RECOMMENDED WHEN:
#    ✅ Code reviews blocking CI/CD pipelines
#    ✅ Security audits before production deploys
#    ✅ Onboarding PRs from contractors / new hires
#    ✅ Automated pre-merge gates in GitHub Actions
#
# ══════════════════════════════════════════════════════════════════════════════

async def _code_security_worker(system: str, label: str, style: str, code: str) -> dict:
    t = time.perf_counter()
    result = await _call(system, f"Review this code:\n\n```\n{code}\n```")
    elapsed = time.perf_counter() - t
    _timed_panel(label, style, result, elapsed)
    return {"label": label, "content": result, "elapsed": elapsed}


async def code_security_reviewer(code: str) -> dict:
    console.print("[dim red]  ⚡ Security Reviewer started[/dim red]")
    return await _code_security_worker(
        "You are an application security expert (OWASP Top 10). "
        "Identify injection risks, auth flaws, sensitive data exposure, "
        "insecure deserialization, and any other CVEs. Rate severity (Critical/High/Medium/Low).",
        "🔒 Security Review", "red", code,
    )


async def code_performance_reviewer(code: str) -> dict:
    console.print("[dim yellow]  ⚡ Performance Reviewer started[/dim yellow]")
    return await _code_security_worker(
        "You are a performance engineer. Identify O(n²) loops, N+1 queries, "
        "memory leaks, blocking I/O, and missing caching opportunities. "
        "Suggest specific fixes with estimated impact.",
        "⚡ Performance Review", "yellow", code,
    )


async def code_quality_reviewer(code: str) -> dict:
    console.print("[dim cyan]  ⚡ Code Quality Reviewer started[/dim cyan]")
    return await _code_security_worker(
        "You are a senior software engineer focused on code quality. "
        "Evaluate: readability, naming conventions, SOLID principles, "
        "DRY violations, complexity (cyclomatic), and documentation. "
        "Score overall quality 1-10.",
        "✨ Code Quality Review", "cyan", code,
    )


async def code_dependency_reviewer(code: str) -> dict:
    console.print("[dim magenta]  ⚡ Dependency Reviewer started[/dim magenta]")
    return await _code_security_worker(
        "You are a DevOps engineer specialising in supply-chain security. "
        "Identify outdated, deprecated, or vulnerable dependencies. "
        "Flag any licence incompatibilities. Recommend upgrades or alternatives.",
        "📦 Dependency Review", "magenta", code,
    )


async def code_test_reviewer(code: str) -> dict:
    console.print("[dim green]  ⚡ Test Coverage Reviewer started[/dim green]")
    return await _code_security_worker(
        "You are a QA engineer. Evaluate test coverage: are edge cases covered? "
        "Are mocks / stubs appropriate? Identify untested paths. "
        "Suggest the 3 highest-value test cases to add.",
        "🧪 Test Coverage Review", "green", code,
    )


async def _code_audit_aggregator(code: str, reports: list[dict]) -> str:
    console.print(Rule("🏗️  Lead Architect — Audit Summary", style="bold white"))
    combined = "\n\n".join(f"### {r['label']}\n{r['content']}" for r in reports)
    result = await _call(
        "You are a Lead Architect producing a final code audit report. "
        "Summarise all findings into: (1) Critical issues to fix NOW, "
        "(2) High-priority improvements, (3) Nice-to-haves. "
        "Assign an overall code health score (A/B/C/D/F) with a brief rationale. "
        "Keep it under 300 words.",
        f"Code snippet reviews:\n\n{combined}",
    )
    console.print(Panel(result, title="[bold white]📋 Audit Report[/bold white]",
                        border_style="white", padding=(0, 1)))
    return result


async def run_code_audit(code_snippet: str) -> None:
    """
    Use Case 1: Code Security Audit
    Fan-out → 5 specialist code reviewers (security, perf, quality, deps, tests)
    Fan-in  → Lead Architect audit summary
    """
    console.print(Panel.fit(
        "[bold red]Code Security Audit[/bold red]\n"
        "[dim]5 specialist reviewers running in parallel[/dim]",
        border_style="red",
    ))
    console.print(Rule("⚡  Fan-Out — 5 Code Reviewers", style="bold red"))

    workers = [
        code_security_reviewer,
        code_performance_reviewer,
        code_quality_reviewer,
        code_dependency_reviewer,
        code_test_reviewer,
    ]
    await _run_parallel(code_snippet, workers, _code_audit_aggregator)


# ══════════════════════════════════════════════════════════════════════════════
#
#  USE CASE 2 — Job Candidate Screening
#  ──────────────────────────────────────
#  PROBLEM : HR teams spend hours manually reviewing CVs across multiple
#            dimensions. Parallel specialist agents screen simultaneously,
#            surfacing the best candidates faster and more consistently.
#
#  WORKERS : Skills Match | Experience Depth | Culture Fit |
#            Red Flags | Growth Potential
#  FAN-IN  : Hiring Manager — GO / HOLD / PASS recommendation
#
#  RECOMMENDED WHEN:
#    ✅ High-volume recruitment (>20 applicants per role)
#    ✅ Technical roles requiring multi-dimensional screening
#    ✅ Reducing unconscious bias via structured evaluation
#    ✅ Async pre-screening before live interviews
#
# ══════════════════════════════════════════════════════════════════════════════

async def _cv_worker(system: str, label: str, style: str, cv: str) -> dict:
    t = time.perf_counter()
    result = await _call(system, f"Candidate CV:\n\n{cv}")
    elapsed = time.perf_counter() - t
    _timed_panel(label, style, result, elapsed)
    return {"label": label, "content": result, "elapsed": elapsed}


async def screen_skills(cv: str) -> dict:
    console.print("[dim cyan]  ⚡ Skills Matcher started[/dim cyan]")
    return await _cv_worker(
        "You are a Technical Skills Evaluator. Score the candidate's skills "
        "against a senior software engineer role: Python, distributed systems, "
        "cloud (AWS/GCP/Azure), API design, and system design. "
        "Give each skill a rating (Expert/Proficient/Familiar/Gap) and an overall match score /10.",
        "🛠️  Skills Match", "cyan", cv,
    )


async def screen_experience(cv: str) -> dict:
    console.print("[dim green]  ⚡ Experience Analyst started[/dim green]")
    return await _cv_worker(
        "You are an Experience Analyst. Evaluate: total YoE, seniority trajectory, "
        "company quality/relevance, project scope (team size, impact), "
        "and domain expertise breadth. Score depth of experience /10.",
        "📈 Experience Depth", "green", cv,
    )


async def screen_culture(cv: str) -> dict:
    console.print("[dim yellow]  ⚡ Culture Evaluator started[/dim yellow]")
    return await _cv_worker(
        "You are a Culture Fit Analyst for a fast-moving, collaborative startup. "
        "Look for: open-source contributions, side projects, leadership signals, "
        "cross-functional collaboration, communication clarity in the CV itself. "
        "Rate culture fit /10 with key evidence.",
        "🤝 Culture Fit", "yellow", cv,
    )


async def screen_red_flags(cv: str) -> dict:
    console.print("[dim red]  ⚡ Red Flag Detector started[/dim red]")
    return await _cv_worker(
        "You are a careful recruiter looking for warning signs. Flag: "
        "unexplained employment gaps (>6 months), very short tenures (<6 months) "
        "at multiple companies, vague/inflated descriptions, missing education details, "
        "or inconsistencies. Rate overall concern level: None / Minor / Moderate / Major.",
        "🚩 Red Flag Check", "red", cv,
    )


async def screen_potential(cv: str) -> dict:
    console.print("[dim magenta]  ⚡ Growth Potential Assessor started[/dim magenta]")
    return await _cv_worker(
        "You are a talent development specialist. Assess growth trajectory: "
        "promotions, increasing scope, learning agility (new tech adopted), "
        "initiative taken, and long-term ceiling. Score potential /10 and "
        "give one paragraph on why this candidate could be exceptional in 3 years.",
        "🚀 Growth Potential", "magenta", cv,
    )


async def _hiring_aggregator(cv: str, reports: list[dict]) -> str:
    console.print(Rule("👔  Hiring Manager — Final Recommendation", style="bold white"))
    combined = "\n\n".join(f"### {r['label']}\n{r['content']}" for r in reports)
    result = await _call(
        "You are a Hiring Manager making a final screening decision. "
        "Based on all specialist evaluations, provide: "
        "(1) Decision: ADVANCE TO INTERVIEW / HOLD / PASS "
        "(2) Top 3 reasons for this decision "
        "(3) 3 questions to ask if advancing to interview "
        "(4) Overall candidate score /10.",
        f"Specialist evaluations:\n\n{combined}",
    )
    console.print(Panel(result, title="[bold white]📋 Hiring Decision[/bold white]",
                        border_style="white", padding=(0, 1)))
    return result


async def run_candidate_screening(cv_text: str) -> None:
    """
    Use Case 2: Job Candidate Screening
    Fan-out → 5 HR specialist agents (skills, experience, culture, red flags, potential)
    Fan-in  → Hiring Manager recommendation
    """
    console.print(Panel.fit(
        "[bold cyan]Job Candidate Screening[/bold cyan]\n"
        "[dim]5 specialist HR agents running in parallel[/dim]",
        border_style="cyan",
    ))
    console.print(Rule("⚡  Fan-Out — 5 Screening Agents", style="bold cyan"))

    workers = [screen_skills, screen_experience, screen_culture,
               screen_red_flags, screen_potential]
    await _run_parallel(cv_text, workers, _hiring_aggregator)


# ══════════════════════════════════════════════════════════════════════════════
#
#  USE CASE 3 — Academic Paper Peer Review
#  ────────────────────────────────────────
#  PROBLEM : Traditional peer review is slow (weeks to months) because
#            reviewers evaluate sequentially. Parallel specialist agents
#            review different quality dimensions simultaneously.
#
#  WORKERS : Methodology | Data Quality | Novelty | Reproducibility | Clarity
#  FAN-IN  : Editor-in-Chief — Accept / Minor Revision / Major Revision / Reject
#
#  RECOMMENDED WHEN:
#    ✅ Journal / conference automated pre-screening
#    ✅ Internal research quality gates before external submission
#    ✅ Grant proposal review panels
#    ✅ Speeding up literature review for systematic reviews
#
# ══════════════════════════════════════════════════════════════════════════════

async def _paper_worker(system: str, label: str, style: str, abstract: str) -> dict:
    t = time.perf_counter()
    result = await _call(system, f"Paper abstract / excerpt:\n\n{abstract}")
    elapsed = time.perf_counter() - t
    _timed_panel(label, style, result, elapsed)
    return {"label": label, "content": result, "elapsed": elapsed}


async def review_methodology(abstract: str) -> dict:
    console.print("[dim blue]  ⚡ Methodology Reviewer started[/dim blue]")
    return await _paper_worker(
        "You are an expert in research methodology. Evaluate: study design, "
        "sample size justification, control groups, statistical tests used, "
        "confounding variables addressed, and internal validity. "
        "Score methodology rigour 1-10.",
        "🔬 Methodology Review", "blue", abstract,
    )


async def review_data_quality(abstract: str) -> dict:
    console.print("[dim green]  ⚡ Data Quality Reviewer started[/dim green]")
    return await _paper_worker(
        "You are a data quality expert. Evaluate: data sources and credibility, "
        "dataset size and representativeness, preprocessing steps, handling of "
        "missing data, and potential biases in the dataset. Score 1-10.",
        "📊 Data Quality Review", "green", abstract,
    )


async def review_novelty(abstract: str) -> dict:
    console.print("[dim magenta]  ⚡ Novelty Assessor started[/dim magenta]")
    return await _paper_worker(
        "You are a domain expert assessing originality. Compare against known prior art: "
        "What is truly new here? Is the contribution incremental or transformative? "
        "Does it open new research directions? Score novelty 1-10.",
        "💡 Novelty Assessment", "magenta", abstract,
    )


async def review_reproducibility(abstract: str) -> dict:
    console.print("[dim yellow]  ⚡ Reproducibility Checker started[/dim yellow]")
    return await _paper_worker(
        "You are a reproducibility specialist. Assess: are methods described in "
        "enough detail to replicate? Is code/data promised or available? "
        "Are hyperparameters and environments specified? Score reproducibility 1-10.",
        "🔁 Reproducibility Check", "yellow", abstract,
    )


async def review_clarity(abstract: str) -> dict:
    console.print("[dim cyan]  ⚡ Writing Clarity Reviewer started[/dim cyan]")
    return await _paper_worker(
        "You are a scientific writing expert. Evaluate: clarity of the abstract, "
        "structure of the argument, appropriate use of jargon, figure/table "
        "quality (inferred from descriptions), and overall readability. "
        "Score writing clarity 1-10.",
        "📝 Clarity & Writing", "cyan", abstract,
    )


async def _editor_aggregator(abstract: str, reports: list[dict]) -> str:
    console.print(Rule("📚  Editor-in-Chief — Final Decision", style="bold white"))
    combined = "\n\n".join(f"### {r['label']}\n{r['content']}" for r in reports)
    result = await _call(
        "You are an Editor-in-Chief for a top-tier conference. "
        "Based on all reviewer reports, give: "
        "(1) Decision: ACCEPT / MINOR REVISION / MAJOR REVISION / REJECT "
        "(2) The 2-3 strongest points of the paper "
        "(3) The 2-3 most critical issues that must be addressed "
        "(4) Overall paper score (1-10).",
        f"Reviewer reports:\n\n{combined}",
    )
    console.print(Panel(result, title="[bold white]📋 Editorial Decision[/bold white]",
                        border_style="white", padding=(0, 1)))
    return result


async def run_paper_review(abstract_text: str) -> None:
    """
    Use Case 3: Academic Paper Peer Review
    Fan-out → 5 specialist reviewers (methodology, data, novelty, reproducibility, clarity)
    Fan-in  → Editor-in-Chief decision
    """
    console.print(Panel.fit(
        "[bold blue]Academic Paper Peer Review[/bold blue]\n"
        "[dim]5 specialist reviewers running in parallel[/dim]",
        border_style="blue",
    ))
    console.print(Rule("⚡  Fan-Out — 5 Peer Reviewers", style="bold blue"))

    workers = [review_methodology, review_data_quality, review_novelty,
               review_reproducibility, review_clarity]
    await _run_parallel(abstract_text, workers, _editor_aggregator)


# ══════════════════════════════════════════════════════════════════════════════
#
#  USE CASE 4 — Product Review Intelligence
#  ─────────────────────────────────────────
#  PROBLEM : E-commerce buyers drown in thousands of reviews. Parallel agents
#            analyse different aspects simultaneously and surface a concise,
#            structured buying recommendation.
#
#  WORKERS : Feature Analysis | Pricing/Value | UX & Reliability |
#            Sentiment Mining | Competitor Comparison
#  FAN-IN  : Consumer Advisor — Buy / Wait / Skip recommendation
#
#  RECOMMENDED WHEN:
#    ✅ Product recommendation engines
#    ✅ Procurement / purchasing decision support
#    ✅ Competitive product benchmarking
#    ✅ Consumer journalism / review sites
#
# ══════════════════════════════════════════════════════════════════════════════

async def _product_worker(system: str, label: str, style: str, product: str) -> dict:
    t = time.perf_counter()
    result = await _call(system, f"Product: {product}")
    elapsed = time.perf_counter() - t
    _timed_panel(label, style, result, elapsed)
    return {"label": label, "content": result, "elapsed": elapsed}


async def analyse_features(product: str) -> dict:
    console.print("[dim cyan]  ⚡ Feature Analyst started[/dim cyan]")
    return await _product_worker(
        "You are a product features specialist. Evaluate the top 5 features, "
        "what works well and what is missing compared to user expectations. "
        "Rate feature completeness /10.",
        "🔍 Feature Analysis", "cyan", product,
    )


async def analyse_value(product: str) -> dict:
    console.print("[dim green]  ⚡ Value Analyst started[/dim green]")
    return await _product_worker(
        "You are a pricing and value-for-money analyst. Assess: price point, "
        "what you get for the price, comparable alternatives at lower/higher cost, "
        "and hidden costs (subscription, accessories, repairs). Rate value /10.",
        "💲 Price & Value", "green", product,
    )


async def analyse_reliability(product: str) -> dict:
    console.print("[dim yellow]  ⚡ Reliability Analyst started[/dim yellow]")
    return await _product_worker(
        "You are a product durability and UX specialist. Evaluate: "
        "build quality, common failure modes reported by users, "
        "ease of use, learning curve, and customer support quality. "
        "Rate reliability & UX /10.",
        "🛡️  Reliability & UX", "yellow", product,
    )


async def analyse_sentiment(product: str) -> dict:
    console.print("[dim magenta]  ⚡ Sentiment Analyst started[/dim magenta]")
    return await _product_worker(
        "You are a sentiment analysis expert. Summarise: "
        "top 3 things users love, top 3 complaints, "
        "sentiment trend (improving / declining over recent reviews), "
        "and the most commonly mentioned deal-breaker. Rate sentiment /10.",
        "💬 User Sentiment", "magenta", product,
    )


async def analyse_competitors(product: str) -> dict:
    console.print("[dim red]  ⚡ Competitor Analyst started[/dim red]")
    return await _product_worker(
        "You are a competitive analysis specialist. Name 2-3 direct alternatives, "
        "how they compare on key specs, and which type of buyer should choose each. "
        "Is this product best in class, mid-tier, or value play?",
        "🏆 Competitive Position", "red", product,
    )


async def _consumer_aggregator(product: str, reports: list[dict]) -> str:
    console.print(Rule("🛒  Consumer Advisor — Final Verdict", style="bold white"))
    combined = "\n\n".join(f"### {r['label']}\n{r['content']}" for r in reports)
    result = await _call(
        "You are a trusted consumer advisor. Synthesise all specialist reviews into: "
        "(1) Verdict: BUY NOW / WAIT FOR NEXT VERSION / SKIP / BETTER ALTERNATIVES EXIST "
        "(2) Best suited for: [type of buyer] "
        "(3) Not for: [type of buyer to avoid it] "
        "(4) Top 3 pros and top 3 cons "
        "(5) Overall product score /10.",
        f"Product: {product}\n\nSpecialist reviews:\n\n{combined}",
    )
    console.print(Panel(result, title="[bold white]📋 Consumer Verdict[/bold white]",
                        border_style="white", padding=(0, 1)))
    return result


async def run_product_review(product_name: str) -> None:
    """
    Use Case 4: Product Review Intelligence
    Fan-out → 5 specialist analysts (features, value, reliability, sentiment, competitors)
    Fan-in  → Consumer advisor final verdict
    """
    console.print(Panel.fit(
        "[bold green]Product Review Intelligence[/bold green]\n"
        "[dim]5 specialist analysts running in parallel[/dim]",
        border_style="green",
    ))
    console.print(Rule("⚡  Fan-Out — 5 Product Analysts", style="bold green"))

    workers = [analyse_features, analyse_value, analyse_reliability,
               analyse_sentiment, analyse_competitors]
    await _run_parallel(product_name, workers, _consumer_aggregator)


# ══════════════════════════════════════════════════════════════════════════════
#
#  USE CASE 5 — Crisis Communication Triage
#  ─────────────────────────────────────────
#  PROBLEM : When a PR crisis hits, response teams scramble across media,
#            legal, and stakeholder concerns simultaneously. Parallel agents
#            assess every dimension at once and produce a coordinated response
#            plan before the news cycle moves on.
#
#  WORKERS : Media Sentiment | Stakeholder Impact | Legal Exposure |
#            Reputation Damage | Response Quality Assessment
#  FAN-IN  : Crisis Manager — 48-hour response playbook
#
#  RECOMMENDED WHEN:
#    ✅ Monitoring breaking news about the brand
#    ✅ Product recall communications
#    ✅ Data breach disclosures
#    ✅ Executive misconduct response planning
#
# ══════════════════════════════════════════════════════════════════════════════

async def _crisis_worker(system: str, label: str, style: str, incident: str) -> dict:
    t = time.perf_counter()
    result = await _call(system, f"Crisis incident:\n\n{incident}")
    elapsed = time.perf_counter() - t
    _timed_panel(label, style, result, elapsed)
    return {"label": label, "content": result, "elapsed": elapsed}


async def assess_media_sentiment(incident: str) -> dict:
    console.print("[dim cyan]  ⚡ Media Sentiment Analyst started[/dim cyan]")
    return await _crisis_worker(
        "You are a media intelligence analyst. Assess: current media sentiment "
        "(positive/neutral/negative ratio), likely headline framing by journalists, "
        "key media outlets most likely to amplify, and social media virality risk. "
        "Rate media threat level 1-10.",
        "📰 Media Sentiment", "cyan", incident,
    )


async def assess_stakeholder_impact(incident: str) -> dict:
    console.print("[dim yellow]  ⚡ Stakeholder Analyst started[/dim yellow]")
    return await _crisis_worker(
        "You are a stakeholder relations expert. Map the impact on: customers, "
        "employees, investors, regulators, and partners. For each group: "
        "what are they worried about? What do they need to hear? "
        "Rate overall stakeholder alarm level 1-10.",
        "👥 Stakeholder Impact", "yellow", incident,
    )


async def assess_legal_exposure(incident: str) -> dict:
    console.print("[dim red]  ⚡ Legal Exposure Analyst started[/dim red]")
    return await _crisis_worker(
        "You are a corporate legal counsel. Identify: potential regulatory violations, "
        "class action litigation risk, contractual breach exposure, and "
        "what statements must NOT be made publicly. Rate legal exposure 1-10.",
        "⚖️  Legal Exposure", "red", incident,
    )


async def assess_reputation_damage(incident: str) -> dict:
    console.print("[dim magenta]  ⚡ Reputation Analyst started[/dim magenta]")
    return await _crisis_worker(
        "You are a brand reputation specialist. Assess: immediate brand equity "
        "damage (1-10), likely long-term trust erosion, comparison to similar "
        "past crises, and what recovery typically looks like in terms of "
        "timeline and actions required.",
        "💔 Reputation Damage", "magenta", incident,
    )


async def assess_response_quality(incident: str) -> dict:
    console.print("[dim green]  ⚡ Response Quality Analyst started[/dim green]")
    return await _crisis_worker(
        "You are a crisis communications specialist. Evaluate the company's "
        "initial public response (or likely default response if none given): "
        "Was it fast enough? Empathetic? Transparent? Action-oriented? "
        "Identify the 3 most critical gaps in the current response. Rate /10.",
        "📢 Response Quality", "green", incident,
    )


async def _crisis_manager_aggregator(incident: str, reports: list[dict]) -> str:
    console.print(Rule("🚨  Crisis Manager — 48-Hour Playbook", style="bold white"))
    combined = "\n\n".join(f"### {r['label']}\n{r['content']}" for r in reports)
    result = await _call(
        "You are a Crisis Management Director. Produce a 48-hour response playbook: "
        "(1) Threat Level: LOW / MEDIUM / HIGH / CRITICAL "
        "(2) Immediate actions in the next 2 hours "
        "(3) Key messages for each stakeholder group "
        "(4) What to say publicly AND what not to say "
        "(5) 48-hour milestone plan (Hour 2 / Hour 8 / Hour 24 / Hour 48) "
        "(6) Recovery success metrics.",
        f"Crisis incident:\n\n{incident}\n\nSpecialist assessments:\n\n{combined}",
    )
    console.print(Panel(result, title="[bold white]🚨 Crisis Response Playbook[/bold white]",
                        border_style="white", padding=(0, 1)))
    return result


async def run_crisis_triage(incident_description: str) -> None:
    """
    Use Case 5: Crisis Communication Triage
    Fan-out → 5 specialist analysts (media, stakeholders, legal, reputation, response)
    Fan-in  → Crisis Manager 48-hour playbook
    """
    console.print(Panel.fit(
        "[bold red]Crisis Communication Triage[/bold red]\n"
        "[dim]5 specialist crisis analysts running in parallel[/dim]",
        border_style="red",
    ))
    console.print(Rule("⚡  Fan-Out — 5 Crisis Analysts", style="bold red"))

    workers = [assess_media_sentiment, assess_stakeholder_impact, assess_legal_exposure,
               assess_reputation_damage, assess_response_quality]
    await _run_parallel(incident_description, workers, _crisis_manager_aggregator)


# ══════════════════════════════════════════════════════════════════════════════
#  SAMPLE INPUTS FOR EACH USE CASE
# ══════════════════════════════════════════════════════════════════════════════

SAMPLE_CODE = """\
import sqlite3

def get_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    users = cursor.fetchall()
    for user in users:
        for i in range(len(users)):
            print(users[i])
    return users
"""

SAMPLE_CV = """\
Jane Smith | jane@email.com | github.com/janesmith

EXPERIENCE
2022–Present  Senior Software Engineer, TechCorp (Series B, 200 engineers)
  - Led migration of monolith to microservices (Python/Go), reduced p99 latency 60%
  - Managed a team of 4 engineers, mentored 2 junior devs to promotion
  - Designed event-driven architecture handling 2M events/day on AWS

2019–2022     Software Engineer, StartupXYZ (acquired 2022)
  - Built ML feature pipeline from scratch (Spark + Airflow), saving $200k/yr
  - Contributed to open-source: 3 merged PRs to Apache Airflow

2017–2019     Junior Developer, AgencyABC
  - Built REST APIs in Django for 3 client projects

EDUCATION  BSc Computer Science, State University, 2017 (GPA 3.8)
SKILLS     Python, Go, AWS, Kubernetes, PostgreSQL, Spark, Kafka
SIDE PROJECTS  github.com/janesmith — 2 projects with 400+ stars total
"""

SAMPLE_ABSTRACT = """\
Title: RAG-Bench: A Standardised Evaluation Framework for Retrieval-Augmented
Generation Systems Across Domain-Specific Knowledge Bases

Abstract: Retrieval-Augmented Generation (RAG) systems have emerged as a
leading architecture for grounding large language models in factual knowledge,
yet no standardised benchmark exists for comparing RAG pipelines across domains.
We introduce RAG-Bench, a curated evaluation suite of 12,000 question-answer
pairs spanning 6 domains (legal, medical, finance, scientific, technical support,
and general knowledge). We evaluate 8 state-of-the-art RAG configurations
including BM25, dense retrieval (DPR, ColBERT), and hybrid approaches across
three LLM backends (GPT-4o, Claude 3.5, Llama 3.1-70B). Our results reveal
that hybrid retrieval improves answer faithfulness by 23% in domain-specific
settings while reducing hallucination rate from 18.4% to 6.1%. All datasets,
evaluation scripts, and model outputs are released under CC-BY-4.0.
"""

SAMPLE_PRODUCT = "Apple MacBook Pro 14-inch M4 Pro (2024)"

SAMPLE_CRISIS = """\
A major food delivery platform (500k daily active users) has experienced a
data breach affecting 2.3 million customer records including names, addresses,
partial payment card data (last 4 digits), and order history. The breach occurred
through an unpatched API vulnerability that was reportedly known for 3 months.
A hacker group has published a sample of 10,000 records on a public forum as proof.
The story broke on TechCrunch 45 minutes ago and is spreading on X (Twitter).
The company's initial statement was: 'We are aware of reports and are investigating.'
"""


# ══════════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

USE_CASES = {
    "1": ("Code Security Audit",         run_code_audit,          SAMPLE_CODE),
    "2": ("Job Candidate Screening",      run_candidate_screening, SAMPLE_CV),
    "3": ("Academic Paper Review",        run_paper_review,        SAMPLE_ABSTRACT),
    "4": ("Product Review Intelligence",  run_product_review,      SAMPLE_PRODUCT),
    "5": ("Crisis Communication Triage",  run_crisis_triage,       SAMPLE_CRISIS),
}


async def main() -> None:
    console.print(
        "\n[bold]🚀  Parallel Agent Use Cases[/bold]\n"
        "[dim]5 production-ready blueprints using the Parallel pattern[/dim]\n"
    )
    console.print("[bold]Available Use Cases:[/bold]")
    for key, (name, _, _) in USE_CASES.items():
        console.print(f"  [cyan]{key}[/cyan].  {name}")

    console.print("\n[dim]Select a use case to run with its built-in sample input.[/dim]\n")
    choice = input("Select (1-5): ").strip()

    if choice not in USE_CASES:
        console.print("[red]Invalid choice. Running Use Case 1.[/red]")
        choice = "1"

    name, fn, sample_input = USE_CASES[choice]
    console.print(f"\n[bold]Running:[/bold] {name}\n")
    await fn(sample_input)


if __name__ == "__main__":
    asyncio.run(main())
