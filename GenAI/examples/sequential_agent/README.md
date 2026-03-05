# Sequential Agent Pattern

> **Framework**: Microsoft Agent Framework (`agent-framework-azure-ai==1.0.0b260107`)
> **Language**: Python 3.10+
> **Level**: Intermediate → Advanced

---

## What Is the Sequential Pattern?

The **Sequential Pattern** routes a task through a fixed chain of specialised agents,
where each agent's output becomes enriched input for the next. It is the simplest
multi-agent topology and the foundation for understanding all other agentic patterns.

```
INPUT → [Agent 1] → [Agent 2] → [Agent 3] → … → [Agent N] → OUTPUT
          Stage 1     Stage 2     Stage 3           Terminal
```

**Key properties:**
- Stages run **strictly one at a time** — no parallelism
- Every stage receives the **full accumulated context** of all prior stages
- The **final stage** yields the workflow output using `ctx.yield_output()`
- Context travels as `list[ChatMessage]` — the conversation grows richer at each hop

---

## When to Use the Sequential Pattern ✅

| Scenario | Example |
|---|---|
| Multi-step transformation | Research → Draft → Edit → Publish |
| Quality-refinement pipelines | Write → Proofread → Review → Approve |
| Data enrichment chains | Extract → Clean → Classify → Validate |
| Decision-support pipelines | Gather → Analyse → Recommend → Explain |
| Document processing | Parse → Summarise → Translate → Archive |
| Code automation | Analyse → Review → Fix → Document |
| Customer support triage | Classify → KB Lookup → Respond → QA |

---

## When NOT to Use Sequential ❌

| Situation | Better Pattern |
|---|---|
| Stages are independent (no shared context needed) | **Parallelization** |
| Flow depends on conditions (if/else routing) | **Routing** |
| Iterative self-correction loop | **Reflection** |
| Dynamic agent collaboration without fixed order | **Multi-Agent** |
| Simple single-turn task | **Single Agent** |

---

## Architecture: Context Flow

```
topic: str
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│  ResearcherExecutor                                              │
│  handler: research(topic: str, ctx: WorkflowContext[list[ChatMessage]])
│  → appends research findings to messages                         │
│  → ctx.send_message(messages)                                    │
└──────────────────────┬───────────────────────────────────────────┘
                       │  list[ChatMessage]  (research)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  StrategistExecutor                                              │
│  handler: strategize(messages, ctx: WorkflowContext[list[ChatMessage]])
│  → appends content strategy to messages                          │
│  → ctx.send_message(messages)                                    │
└──────────────────────┬───────────────────────────────────────────┘
                       │  list[ChatMessage]  (research + strategy)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  WriterExecutor                                                  │
│  handler: write(messages, ctx: WorkflowContext[list[ChatMessage]])
│  → appends draft article to messages                             │
│  → ctx.send_message(messages)                                    │
└──────────────────────┬───────────────────────────────────────────┘
                       │  list[ChatMessage]  (research + strategy + draft)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  ReviewerExecutor  (TERMINAL — yields output)                    │
│  handler: review(messages, ctx: WorkflowContext[Never, str])     │
│  → produces quality scorecard + final polished article           │
│  → ctx.yield_output(final_output)                                │
└──────────────────────────────────────────────────────────────────┘
                       │  str  (workflow output)
                       ▼
                  WorkflowOutputEvent
```

---

## Project Structure

```
sequential_agent/
├── main.py          ← Primary demo: Content Intelligence Pipeline (4 stages)
├── use_cases.py     ← 5 additional pipeline blueprints (see below)
├── requirements.txt ← Pinned dependencies
├── .env.example     ← Environment variable template
└── README.md        ← This file
```

---

## Primary Demo: Content Intelligence Pipeline

**File**: `main.py`

A 4-stage pipeline that turns a topic into a publication-ready article:

| Stage | Agent | Input | Output |
|---|---|---|---|
| 1 | `ResearcherAgent` | `str` (topic) | `list[ChatMessage]` (research) |
| 2 | `StrategistAgent` | `list[ChatMessage]` | `list[ChatMessage]` (+ strategy) |
| 3 | `WriterAgent` | `list[ChatMessage]` | `list[ChatMessage]` (+ draft) |
| 4 | `ReviewerAgent` ⭐ | `list[ChatMessage]` | `str` (final output) |

⭐ = terminal stage — uses `WorkflowContext[Never, str]` and calls `ctx.yield_output()`

---

## Recommended Use Cases to Implement

### Use Case 1 — Code Review Pipeline
**File**: `use_cases.py` → `run_code_review_pipeline()`

```
code snippet (str)
    │
    ├─► CodeAnalyser      → quality + complexity analysis
    ├─► SecurityReviewer  → OWASP vulnerability scan
    ├─► FixSuggester      → copy-paste-ready code fixes
    └─► DocWriter ⭐       → docstrings + review summary
```

**Build this when:**
- You want automated PR reviews in your CI/CD pipeline
- Security audits need LLM-level reasoning beyond static analysis
- You want to auto-generate JSDoc/docstrings alongside review feedback

---

### Use Case 2 — Customer Support Pipeline
**File**: `use_cases.py` → `run_support_pipeline()`

```
support ticket (str)
    │
    ├─► TicketClassifier  → category, priority, sentiment
    ├─► KBResearcher      → top 3 KB solutions
    ├─► SupportResponder  → empathetic draft response
    └─► ToneQA ⭐          → final, send-ready reply
```

**Build this when:**
- You want to automate Tier-1 support triage and response drafting
- Response quality must be consistently reviewed before sending
- You need an auditable pipeline for SLA reporting

---

### Use Case 3 — Data Analysis Pipeline
**File**: `use_cases.py` → `run_data_analysis_pipeline()`

```
raw data / CSV description (str)
    │
    ├─► DataCleaner        → quality issues + cleaning plan
    ├─► StatAnalyser       → descriptive stats + patterns
    ├─► InsightGenerator   → business insights in plain English
    └─► ReportWriter ⭐     → executive-ready analysis report
```

**Build this when:**
- Business users upload datasets and need instant narrative analysis
- Weekly KPI reports need automated generation from data dumps
- You want a BI tool that narrates its own numbers

---

### Use Case 4 — Legal Document Pipeline
**File**: `use_cases.py` → `run_legal_document_pipeline()`

```
contract text (str)
    │
    ├─► LegalParser        → parties, obligations, key clauses
    ├─► RiskIdentifier     → high-risk clauses + risk rating
    ├─► PlainLanguageSummariser → non-lawyer-friendly summary
    └─► ComplianceChecker ⭐ → GDPR/CCPA compliance report
```

**Build this when:**
- You want to automate NDA / vendor contract review
- Legal due-diligence volume is too high for manual review
- Non-legal staff need to understand contracts quickly

---

### Use Case 5 — Product Launch Planning Pipeline
**File**: `use_cases.py` → `run_product_launch_pipeline()`

```
product feature spec (str)
    │
    ├─► MarketAnalyst      → market size, competitors, GTM channels
    ├─► FeaturePrioritiser → MoSCoW + ICE scored backlog
    ├─► LaunchPlanner      → 90-day week-by-week launch plan
    └─► ChecklistGenerator ⭐ → launch readiness checklist
```

**Build this when:**
- Product managers need a structured GTM framework quickly
- Startups are validating product-market fit before a launch
- You need a consistent, repeatable process for every feature release

---

## Setup

### Prerequisites
- Python 3.10 or higher
- An Azure AI Foundry project ([create one here](https://ai.azure.com))
- Azure CLI installed (`brew install azure-cli` on macOS)

### 1. Create a virtual environment
```bash
cd examples/sequential_agent
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **Pin the version** while Agent Framework is in preview:
> `pip install agent-framework-azure-ai==1.0.0b260107`

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT_NAME
```

### 4. Authenticate with Azure
```bash
az login
```

### 5. Run the primary demo
```bash
python main.py
```

### 6. Run a use-case blueprint
```bash
python use_cases.py
```

---

## Key Concepts

### WorkflowContext typing

```python
# Middle stage — sends messages downstream
async def handle(self, messages: list[ChatMessage],
                 ctx: WorkflowContext[list[ChatMessage]]) -> None:
    ...
    await ctx.send_message(enriched_messages)

# Terminal stage — yields the final output
async def handle(self, messages: list[ChatMessage],
                 ctx: WorkflowContext[Never, str]) -> None:
    ...
    await ctx.yield_output(final_result)
```

| `WorkflowContext[T_Out, T_W_Out]` | Meaning |
|---|---|
| `WorkflowContext[list[ChatMessage]]` | Sends `list[ChatMessage]` downstream |
| `WorkflowContext[Never, str]` | Terminal: yields `str` as workflow output |
| `WorkflowContext[Never, Never]` | No downstream message, no workflow output |

### Factory-based executor registration (recommended)

```python
# ✅  Use lambdas — creates fresh executor per workflow run
workflow = (
    WorkflowBuilder()
    .register_executor(lambda: ResearcherExecutor(researcher), name="Researcher")
    .register_executor(lambda: StrategistExecutor(strategist), name="Strategist")
    ...
    .add_edge("Researcher", "Strategist")
    .set_start_executor("Researcher")
    .build()
)
```

### Handling streaming events

```python
async for event in workflow.run_stream(input):
    if isinstance(event, WorkflowOutputEvent):
        print(event.data)        # Final output from terminal stage
    elif isinstance(event, WorkflowStatusEvent):
        print(event.state)       # IDLE, IN_PROGRESS, etc.
    elif isinstance(event, ExecutorFailedEvent):
        print(event.executor_id) # Which stage failed
    elif isinstance(event, WorkflowFailedEvent):
        print(event.details.message)
```

---

## Extending a Blueprint

To flesh out a blueprint from `use_cases.py` into a full working pipeline:

1. **Copy the executor class structure** from `main.py` (e.g., `ResearcherExecutor`)
2. **Replace the agent, handler name, and user message** for your use case
3. **Wire it into the WorkflowBuilder** using `.add_edge()` and `.set_start_executor()`
4. **Test with sample inputs** from the `PIPELINES` dict in `use_cases.py`

---

## Next Steps

| What | How |
|---|---|
| **Add Reflection** | Loop the Reviewer's feedback back to the Writer for iterative improvement |
| **Add Routing** | Insert a Classifier stage that routes to different pipelines based on topic type |
| **Add Parallelization** | Run the Researcher across multiple sources concurrently with Fan-out/Fan-in |
| **Add Tracing** | Use `aitk-get_tracing_code_gen_best_practices` in GitHub Copilot |
| **Add Evaluation** | Use `aitk-evaluation_planner` to measure output quality |
| **Deploy to Foundry** | Wrap as HTTP server and use the Foundry deploy command |

---

## Pattern Comparison

| Pattern | Structure | Use When |
|---|---|---|
| **Sequential** ← *this* | A → B → C → D | Steps depend on each other |
| **Parallel** | A → [B, C, D] → E | Steps are independent |
| **Routing** | A → if/else → B or C | Output drives which path to take |
| **Reflection** | A ⇄ B (loop) | Iterative self-improvement needed |
| **Multi-Agent** | A ↔ B ↔ C (dynamic) | Complex collaboration, emergent order |
