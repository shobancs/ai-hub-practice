"""
Sequential Agent Pattern — 5 Recommended Use-Case Blueprints
=============================================================
Each blueprint shows the pipeline stages, the typed handoff between stages,
and a complete WorkflowBuilder wiring — ready for you to flesh out with your
own prompts and business logic.

USE CASES COVERED
  1. Code Review Pipeline          — PR code → Analyser → Reviewer → Fixer → Doc Writer
  2. Customer Support Pipeline     — Ticket → Classifier → KB Lookup → Responder → QA Checker
  3. Data Analysis Pipeline        — Raw CSV/JSON → Cleaner → Analyser → Insight Generator → Report Writer
  4. Legal Document Pipeline       — Contract text → Parser → Risk Identifier → Summariser → Compliance Checker
  5. Product Launch Pipeline       — Feature spec → Market Analyst → Prioritiser → Launch Planner → Checklist Generator

HOW TO USE THESE BLUEPRINTS
  1. Copy the pipeline you want.
  2. Fill in the AGENT_INSTRUCTIONS strings with your domain-specific prompts.
  3. Customise the @handler user message to match your input format.
  4. Wire it into your main() as shown in main.py.

NOTE  Pin the agent-framework version while it is in preview:
      pip install agent-framework-azure-ai==1.0.0b260107
      pip install agent-framework-core==1.0.0b260107
"""

import asyncio
import os
from typing_extensions import Never

from agent_framework import (
    ChatAgent,
    ChatMessage,
    Executor,
    ExecutorFailedEvent,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowFailedEvent,
    WorkflowOutputEvent,
    WorkflowRunState,
    WorkflowStatusEvent,
    handler,
)
from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "")
MODEL    = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")


# ══════════════════════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████████████████████
#  USE CASE 1 — CODE REVIEW PIPELINE
#  Input : pull-request diff / code snippet (str)
#  Stages: Analyser → Security Reviewer → Fix Suggester → Doc Writer
#  Output: Structured review report with suggested fixes and updated docs
#
#  WHEN TO BUILD THIS:
#    • Automated PR reviews in CI/CD pipelines
#    • Static-analysis augmentation with LLM reasoning
#    • Security-focused code audit workflows
#    • Generating JSDoc / docstrings automatically alongside review feedback
# ██████████████████████████████████████████████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════

CODE_ANALYSER_INSTRUCTIONS = """\
You are a senior software engineer who analyses code for quality, structure,
complexity, and adherence to best practices. Identify design issues, code smells,
and areas where the logic could be simplified. Return a structured analysis."""

CODE_SECURITY_INSTRUCTIONS = """\
You are an application security expert. Review code for OWASP Top-10 vulnerabilities,
secrets in code, insecure dependencies, injection risks, and authentication flaws.
Rate each finding by severity (Critical / High / Medium / Low)."""

FIX_SUGGESTER_INSTRUCTIONS = """\
You are a staff-level engineer who provides concrete, copy-paste-ready code fixes
for every issue found in a code analysis and security review. For each issue,
output: the problem, the original snippet, and the corrected snippet."""

DOC_WRITER_INSTRUCTIONS = """\
You are a technical writer who produces clear, accurate API documentation and
inline code comments. Given a code snippet and its review, write JSDoc/docstrings
for all public functions and a brief module-level overview."""


class CodeAnalyserExecutor(Executor):
    """Stage 1 — Analyses code quality and structure."""

    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="code-analyser")

    @handler
    async def analyse(self, code: str, ctx: WorkflowContext[list[ChatMessage]]) -> None:
        messages: list[ChatMessage] = [
            ChatMessage(
                role=Role.USER,
                text=(
                    "Analyse the following code for quality, complexity, "
                    "design patterns, and best-practice adherence:\n\n"
                    f"```\n{code}\n```\n\n"
                    "Return:\n"
                    "1. **Complexity Score** (1-10)\n"
                    "2. **Code Smells** (list with line references if possible)\n"
                    "3. **Design Issues** (architecture / pattern violations)\n"
                    "4. **Positive Highlights** (what is done well)\n"
                    "5. **Priority Issues** (top 3 to fix first)"
                ),
            )
        ]
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)


class SecurityReviewerExecutor(Executor):
    """Stage 2 — Scans for security vulnerabilities."""

    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="security-reviewer")

    @handler
    async def review_security(
        self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]
    ) -> None:
        messages.append(
            ChatMessage(
                role=Role.USER,
                text=(
                    "Now perform a security review of the same code:\n\n"
                    "Check for:\n"
                    "- SQL/Command injection\n"
                    "- Hard-coded secrets or credentials\n"
                    "- Insecure deserialization\n"
                    "- Missing input validation\n"
                    "- Authentication / authorisation bypass\n"
                    "- Dependency vulnerabilities (note package names)\n\n"
                    "For each finding: state Severity, Location, and Risk."
                ),
            )
        )
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)


class FixSuggesterExecutor(Executor):
    """Stage 3 — Generates concrete, copy-paste-ready code fixes."""

    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="fix-suggester")

    @handler
    async def suggest_fixes(
        self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]
    ) -> None:
        messages.append(
            ChatMessage(
                role=Role.USER,
                text=(
                    "For every issue identified in the analysis and security review above, "
                    "provide a concrete fix.\n\n"
                    "For each fix use this format:\n"
                    "### Issue: [short title]\n"
                    "**Problem**: [one sentence]\n"
                    "**Before**:\n```\n[original code]\n```\n"
                    "**After**:\n```\n[corrected code]\n```\n"
                    "**Explanation**: [why this fix resolves the issue]"
                ),
            )
        )
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)


class DocWriterExecutor(Executor):
    """Stage 4 — Writes documentation and docstrings (terminal stage)."""

    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="doc-writer")

    @handler
    async def write_docs(
        self, messages: list[ChatMessage], ctx: WorkflowContext[Never, str]
    ) -> None:
        messages.append(
            ChatMessage(
                role=Role.USER,
                text=(
                    "Using the original code and all review feedback above:\n\n"
                    "1. Write complete JSDoc/docstrings for every public function\n"
                    "2. Add a module-level docstring / file header\n"
                    "3. Produce a final **Review Summary** with:\n"
                    "   - Overall quality grade (A/B/C/D/F)\n"
                    "   - Total issues found (Critical / High / Medium / Low)\n"
                    "   - Recommended merge decision (Approve / Request Changes / Reject)"
                ),
            )
        )
        response = await self.agent.run(messages)
        await ctx.yield_output(response.messages[-1].contents[-1].text)


async def run_code_review_pipeline(code_snippet: str) -> None:
    """Execute the Code Review sequential pipeline."""
    async with DefaultAzureCredential() as credential:
        client = AzureAIClient(
            project_endpoint=ENDPOINT, model_deployment_name=MODEL, credential=credential
        )
        async with (
            client.create_agent(name="CodeAnalyserAgent",    instructions=CODE_ANALYSER_INSTRUCTIONS)  as analyser,
            client.create_agent(name="SecurityReviewerAgent", instructions=CODE_SECURITY_INSTRUCTIONS) as security,
            client.create_agent(name="FixSuggesterAgent",    instructions=FIX_SUGGESTER_INSTRUCTIONS)  as fixer,
            client.create_agent(name="DocWriterAgent",       instructions=DOC_WRITER_INSTRUCTIONS)     as doc_writer,
        ):
            workflow = (
                WorkflowBuilder()
                .register_executor(lambda: CodeAnalyserExecutor(analyser),       name="CodeAnalyser")
                .register_executor(lambda: SecurityReviewerExecutor(security),   name="SecurityReviewer")
                .register_executor(lambda: FixSuggesterExecutor(fixer),          name="FixSuggester")
                .register_executor(lambda: DocWriterExecutor(doc_writer),        name="DocWriter")
                .add_edge("CodeAnalyser",    "SecurityReviewer")
                .add_edge("SecurityReviewer", "FixSuggester")
                .add_edge("FixSuggester",    "DocWriter")
                .set_start_executor("CodeAnalyser")
                .build()
            )
            async for event in workflow.run_stream(code_snippet):
                if isinstance(event, WorkflowOutputEvent):
                    print("\n=== CODE REVIEW REPORT ===\n")
                    print(event.data)


# ══════════════════════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████████████████████
#  USE CASE 2 — CUSTOMER SUPPORT PIPELINE
#  Input : raw support ticket text (str)
#  Stages: Classifier → KB Researcher → Responder → Tone / QA Checker
#  Output: Polished, empathetic, accurate support response ready to send
#
#  WHEN TO BUILD THIS:
#    • Automated Tier-1 support triage and response drafting
#    • Helpdesk augmentation that surfaces KB articles and drafts replies
#    • SLA-sensitive pipelines where each step is timed and auditable
#    • Multi-language support workflows (add a Translator stage)
# ██████████████████████████████████████████████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════

TICKET_CLASSIFIER_INSTRUCTIONS = """\
You are a customer-support triage specialist. Classify incoming tickets by:
Category (Billing / Technical / Account / Feature Request / Other),
Priority (P1-Critical / P2-High / P3-Medium / P4-Low),
Sentiment (Frustrated / Neutral / Satisfied),
and extract the core issue in one sentence."""

KB_RESEARCHER_INSTRUCTIONS = """\
You are a knowledge-base specialist. Given a classified support ticket,
identify the most relevant KB articles, FAQs, or troubleshooting steps
that would resolve it. Summarise the top 3 solutions clearly and concisely."""

SUPPORT_RESPONDER_INSTRUCTIONS = """\
You are an expert customer support agent. Using the ticket classification
and KB solutions provided, write a complete, helpful, and personalised
support response. Always acknowledge the customer's frustration if present,
provide step-by-step guidance, and offer escalation if needed."""

TONE_QA_INSTRUCTIONS = """\
You are a quality assurance reviewer for customer support. Review draft
responses for tone, accuracy, completeness, and professionalism.
Fix any issues and deliver the final, send-ready response."""


class TicketClassifierExecutor(Executor):
    """Stage 1 — Classifies the support ticket."""
    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="ticket-classifier")

    @handler
    async def classify(self, ticket: str, ctx: WorkflowContext[list[ChatMessage]]) -> None:
        messages: list[ChatMessage] = [
            ChatMessage(
                role=Role.USER,
                text=(
                    f"Classify this support ticket:\n\n{ticket}\n\n"
                    "Return: Category, Priority, Sentiment, and Core Issue (1 sentence)."
                ),
            )
        ]
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)


class KBResearcherExecutor(Executor):
    """Stage 2 — Finds relevant KB solutions."""
    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="kb-researcher")

    @handler
    async def research_kb(
        self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]
    ) -> None:
        messages.append(
            ChatMessage(
                role=Role.USER,
                text=(
                    "Based on the ticket classification above, "
                    "identify the top 3 solutions or KB articles that address this issue. "
                    "For each solution: Title, Summary (2-3 sentences), Steps to resolve."
                ),
            )
        )
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)


class SupportResponderExecutor(Executor):
    """Stage 3 — Drafts the customer response."""
    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="support-responder")

    @handler
    async def respond(
        self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]
    ) -> None:
        messages.append(
            ChatMessage(
                role=Role.USER,
                text=(
                    "Write a complete customer support response using the classification "
                    "and KB solutions above. Be empathetic, clear, and include step-by-step guidance."
                ),
            )
        )
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        await ctx.send_message(messages)


class ToneQAExecutor(Executor):
    """Stage 4 — QA reviews tone and accuracy (terminal stage)."""
    agent: ChatAgent

    def __init__(self, agent: ChatAgent):
        self.agent = agent
        super().__init__(id="tone-qa")

    @handler
    async def qa_review(
        self, messages: list[ChatMessage], ctx: WorkflowContext[Never, str]
    ) -> None:
        messages.append(
            ChatMessage(
                role=Role.USER,
                text=(
                    "Review the draft response above for tone, accuracy, and completeness. "
                    "Fix any issues and return the final, send-ready response."
                ),
            )
        )
        response = await self.agent.run(messages)
        await ctx.yield_output(response.messages[-1].contents[-1].text)


async def run_support_pipeline(ticket: str) -> None:
    """Execute the Customer Support sequential pipeline."""
    async with DefaultAzureCredential() as credential:
        client = AzureAIClient(
            project_endpoint=ENDPOINT, model_deployment_name=MODEL, credential=credential
        )
        async with (
            client.create_agent(name="TicketClassifierAgent", instructions=TICKET_CLASSIFIER_INSTRUCTIONS) as classifier,
            client.create_agent(name="KBResearcherAgent",     instructions=KB_RESEARCHER_INSTRUCTIONS)     as kb,
            client.create_agent(name="SupportResponderAgent", instructions=SUPPORT_RESPONDER_INSTRUCTIONS) as responder,
            client.create_agent(name="ToneQAAgent",           instructions=TONE_QA_INSTRUCTIONS)           as qa,
        ):
            workflow = (
                WorkflowBuilder()
                .register_executor(lambda: TicketClassifierExecutor(classifier), name="Classifier")
                .register_executor(lambda: KBResearcherExecutor(kb),             name="KBResearcher")
                .register_executor(lambda: SupportResponderExecutor(responder),  name="Responder")
                .register_executor(lambda: ToneQAExecutor(qa),                   name="ToneQA")
                .add_edge("Classifier",  "KBResearcher")
                .add_edge("KBResearcher","Responder")
                .add_edge("Responder",   "ToneQA")
                .set_start_executor("Classifier")
                .build()
            )
            async for event in workflow.run_stream(ticket):
                if isinstance(event, WorkflowOutputEvent):
                    print("\n=== FINAL SUPPORT RESPONSE ===\n")
                    print(event.data)


# ══════════════════════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████████████████████
#  USE CASE 3 — DATA ANALYSIS PIPELINE
#  Input : raw data description or CSV text (str)
#  Stages: Data Cleaner → Statistical Analyser → Insight Generator → Report Writer
#  Output: Executive-ready data analysis report with key insights
#
#  WHEN TO BUILD THIS:
#    • Automated analysis of uploaded datasets in web apps
#    • Weekly/monthly KPI report generation
#    • Business intelligence dashboards that narrate their numbers
#    • Research data pipelines where cleaning + analysis must be auditable
# ██████████════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════

DATA_CLEANER_INSTRUCTIONS = """\
You are a data quality expert. Given raw data (description or CSV sample),
identify quality issues: missing values, outliers, inconsistent formats,
duplicate entries, and encoding problems. Suggest cleaning steps and
produce a cleaned data summary."""

STAT_ANALYSER_INSTRUCTIONS = """\
You are a quantitative analyst. Given cleaned data, compute or estimate:
descriptive statistics, distributions, correlations, and trends.
Identify the top 5 statistically significant patterns."""

INSIGHT_GENERATOR_INSTRUCTIONS = """\
You are a business intelligence analyst. Given the statistical analysis,
translate numbers into plain-English business insights. For each insight:
state What you found, Why it matters, and What action it implies."""

REPORT_WRITER_INSTRUCTIONS = """\
You are an executive report writer. Produce a concise, well-structured
data analysis report with: an Executive Summary (3-4 sentences),
Key Findings (numbered list), Recommendations (actionable bullets),
and a Next Steps section. Use clear, non-technical language."""


async def run_data_analysis_pipeline(data_description: str) -> None:
    """
    Execute the Data Analysis sequential pipeline.

    Stage flow:
      DataCleaner → StatAnalyser → InsightGenerator → ReportWriter
    """
    async with DefaultAzureCredential() as credential:
        client = AzureAIClient(
            project_endpoint=ENDPOINT, model_deployment_name=MODEL, credential=credential
        )
        async with (
            client.create_agent(name="DataCleanerAgent",    instructions=DATA_CLEANER_INSTRUCTIONS)  as cleaner,
            client.create_agent(name="StatAnalyserAgent",   instructions=STAT_ANALYSER_INSTRUCTIONS) as analyser,
            client.create_agent(name="InsightGeneratorAgent", instructions=INSIGHT_GENERATOR_INSTRUCTIONS) as insight_gen,
            client.create_agent(name="ReportWriterAgent",   instructions=REPORT_WRITER_INSTRUCTIONS) as report_writer,
        ):
            # Each executor follows the same pattern as main.py — just the prompts differ
            # Implementation left as an exercise; see main.py ResearcherExecutor for reference

            # Pipeline graph: DataCleaner → StatAnalyser → InsightGenerator → ReportWriter
            print("Data Analysis Pipeline — implement executors following main.py patterns")
            print(f"Agents created: {cleaner}, {analyser}, {insight_gen}, {report_writer}")


# ══════════════════════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████████████████████
#  USE CASE 4 — LEGAL DOCUMENT PIPELINE
#  Input : contract or legal document text (str)
#  Stages: Parser → Risk Identifier → Plain-Language Summariser → Compliance Checker
#  Output: Risk assessment, plain-English summary, and compliance report
#
#  WHEN TO BUILD THIS:
#    • Contract review automation (NDA, SaaS agreements, vendor contracts)
#    • Regulatory compliance monitoring (GDPR, HIPAA, SOC2)
#    • Legal due-diligence pipelines for M&A or partnerships
#    • Employee handbook or policy document review workflows
# ██████████████████████████████████████████████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════

LEGAL_PARSER_INSTRUCTIONS = """\
You are a legal document specialist. Parse the provided legal text and extract:
Parties involved, Key obligations for each party, Important dates and deadlines,
Penalty and termination clauses, and Defined terms (glossary)."""

RISK_IDENTIFIER_INSTRUCTIONS = """\
You are a legal risk analyst. Given a parsed legal document, identify:
High-risk clauses (unfair obligations, unlimited liability, broad indemnification),
Missing standard protections (IP ownership, data protection, dispute resolution),
and Ambiguous language that could be interpreted against your interests.
Rate overall contract risk: Low / Medium / High."""

PLAIN_LANGUAGE_SUMMARISER_INSTRUCTIONS = """\
You are a plain-language writer specialising in making legal documents accessible.
Summarise the contract in simple, jargon-free language that a non-lawyer can understand.
Cover: what is being agreed, what each side must do, key risks, and when it expires."""

COMPLIANCE_CHECKER_INSTRUCTIONS = """\
You are a regulatory compliance specialist. Check the document for compliance with:
GDPR (data processing, consent, data subject rights),
CCPA (California consumer rights),
and general commercial best practices.
Flag any missing clauses and recommend additions."""


async def run_legal_document_pipeline(contract_text: str) -> None:
    """
    Execute the Legal Document sequential pipeline.

    Stage flow:
      Parser → RiskIdentifier → PlainLanguageSummariser → ComplianceChecker
    """
    async with DefaultAzureCredential() as credential:
        client = AzureAIClient(
            project_endpoint=ENDPOINT, model_deployment_name=MODEL, credential=credential
        )
        async with (
            client.create_agent(name="LegalParserAgent",      instructions=LEGAL_PARSER_INSTRUCTIONS)           as parser,
            client.create_agent(name="RiskIdentifierAgent",   instructions=RISK_IDENTIFIER_INSTRUCTIONS)        as risk_id,
            client.create_agent(name="PlainLanguageAgent",    instructions=PLAIN_LANGUAGE_SUMMARISER_INSTRUCTIONS) as summariser,
            client.create_agent(name="ComplianceCheckerAgent",instructions=COMPLIANCE_CHECKER_INSTRUCTIONS)     as compliance,
        ):
            # Pipeline graph: Parser → RiskIdentifier → PlainLanguageSummariser → ComplianceChecker
            print("Legal Document Pipeline — implement executors following main.py patterns")
            print(f"Agents created: {parser}, {risk_id}, {summariser}, {compliance}")


# ══════════════════════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████████████████████
#  USE CASE 5 — PRODUCT LAUNCH PLANNING PIPELINE
#  Input : product feature specification (str)
#  Stages: Market Analyst → Feature Prioritiser → Launch Planner → Checklist Generator
#  Output: GTM strategy, prioritised roadmap, launch plan, and readiness checklist
#
#  WHEN TO BUILD THIS:
#    • Product managers who need a structured GTM framework quickly
#    • Startups validating product-market fit before a launch
#    • Feature release planning inside an existing product
#    • New market entry analysis for B2B / B2C products
# ██████████████████████████████████████████████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════

MARKET_ANALYST_INSTRUCTIONS = """\
You are a product market analyst. Given a product spec, analyse:
Target market size and segments, Top 3 competitors and their positioning,
Unique differentiators, Customer pain points this product solves,
and Go-to-market channel recommendations (direct, partner, PLG)."""

FEATURE_PRIORITISER_INSTRUCTIONS = """\
You are a product manager expert in prioritisation frameworks.
Using MoSCoW (Must / Should / Could / Won't) and ICE scoring (Impact × Confidence / Effort),
prioritise the features described. Produce a ranked feature backlog with scores."""

LAUNCH_PLANNER_INSTRUCTIONS = """\
You are a go-to-market strategist. Create a 90-day product launch plan with:
Week-by-week milestones, Owner roles for each milestone,
Marketing and sales enablement activities, Success KPIs for Day 30 / 60 / 90,
and Risk mitigation strategies."""

CHECKLIST_GENERATOR_INSTRUCTIONS = """\
You are a product launch readiness expert. Generate a comprehensive
launch readiness checklist covering: Technical (infrastructure, security, monitoring),
Marketing (messaging, assets, channels), Sales (training, collateral, CRM),
Legal (terms of service, privacy policy, compliance), and Support (documentation, runbooks)."""


async def run_product_launch_pipeline(product_spec: str) -> None:
    """
    Execute the Product Launch Planning sequential pipeline.

    Stage flow:
      MarketAnalyst → FeaturePrioritiser → LaunchPlanner → ChecklistGenerator
    """
    async with DefaultAzureCredential() as credential:
        client = AzureAIClient(
            project_endpoint=ENDPOINT, model_deployment_name=MODEL, credential=credential
        )
        async with (
            client.create_agent(name="MarketAnalystAgent",      instructions=MARKET_ANALYST_INSTRUCTIONS)      as market,
            client.create_agent(name="FeaturePrioritiserAgent", instructions=FEATURE_PRIORITISER_INSTRUCTIONS) as prioritiser,
            client.create_agent(name="LaunchPlannerAgent",      instructions=LAUNCH_PLANNER_INSTRUCTIONS)      as planner,
            client.create_agent(name="ChecklistGeneratorAgent", instructions=CHECKLIST_GENERATOR_INSTRUCTIONS) as checklist,
        ):
            # Pipeline graph: MarketAnalyst → FeaturePrioritiser → LaunchPlanner → ChecklistGenerator
            print("Product Launch Pipeline — implement executors following main.py patterns")
            print(f"Agents created: {market}, {prioritiser}, {planner}, {checklist}")


# ══════════════════════════════════════════════════════════════════════════════
#  DEMO RUNNER — run any pipeline from the command line
# ══════════════════════════════════════════════════════════════════════════════

PIPELINES = {
    "1": ("Code Review",         run_code_review_pipeline,    "def add(a, b):\n    return a + b"),
    "2": ("Customer Support",    run_support_pipeline,        "I can't log in to my account. It says 'Invalid credentials' even though I just reset my password."),
    "3": ("Data Analysis",       run_data_analysis_pipeline,  "Monthly sales: Jan=120, Feb=98, Mar=145, Apr=132 (units sold, target=110)"),
    "4": ("Legal Document",      run_legal_document_pipeline, "CONFIDENTIALITY AGREEMENT: Party A agrees not to disclose any information shared by Party B for an unlimited period with no exceptions."),
    "5": ("Product Launch",      run_product_launch_pipeline, "AI-powered meeting notes app that auto-summarises, assigns action items, and integrates with Slack and Jira. $12/user/month."),
}


async def main() -> None:
    print("\n🚀  Sequential Agent Use-Case Demos\n")
    for key, (name, _, _) in PIPELINES.items():
        print(f"  {key}. {name} Pipeline")
    print()
    choice = input("Select a pipeline (1-5): ").strip()
    if choice not in PIPELINES:
        print(f"Invalid choice. Using 1.")
        choice = "1"
    name, runner, sample_input = PIPELINES[choice]
    print(f"\n▶  Running: {name} Pipeline")
    print(f"   Input: {sample_input[:80]}...\n")
    await runner(sample_input)


if __name__ == "__main__":
    asyncio.run(main())
