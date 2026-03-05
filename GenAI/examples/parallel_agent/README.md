# Parallel Agent Pattern — Business Intelligence Platform

> **Pattern**: Parallel (Fan-Out → Fan-In)
> **Level**: Intermediate → Advanced
> **SDK**: OpenAI Python SDK (async)

---

## Pattern Overview

```
         INPUT (topic/document/query)
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼      ← Fan-Out (concurrent)
 [Agent A]  [Agent B]  [Agent C]  [Agent D]  [Agent E]
    │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┘
                          │
                   [Aggregator]                        ← Fan-In (sequential)
                          │
                    FINAL OUTPUT
```

All worker agents launch **simultaneously** via `asyncio.gather()`.
The aggregator runs only **after all workers complete**, with full context
from every worker report.

---

## Best Uses ✅

| Scenario | Why Parallel Wins |
|---|---|
| Multi-perspective analysis | Market + Financial + Tech + Risk simultaneously |
| Speed-critical pipelines | Wall-clock time ≈ slowest single agent (not sum) |
| Ensemble / voting | Same task N times → pick majority or highest quality |
| Document chunking | Split large doc → summarise chunks in parallel → merge |
| Multi-criteria evaluation | Audits, scorecards, due diligence, code review |

## Avoid When ❌

- **Stages depend on each other** → use Sequential pattern
- **Dynamic routing on intermediate results** → use Routing pattern
- **Agents need to debate / revise each other** → use Multi-Agent / Reflection
- **API rate limits are very tight** → parallel = N simultaneous calls

---

## Project Structure

```
parallel_agent/
├── main.py          ← Main demo: Business Intelligence Platform (5 analysts + CIO)
├── use_cases.py     ← 5 production-ready blueprints (code audit, CV screening, etc.)
├── requirements.txt ← openai, python-dotenv, rich
├── .env.example     ← env var reference (actual .env lives in GenAI/)
└── README.md        ← This file
```

---

## Quick Start

```bash
cd GenAI/examples/parallel_agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run main demo (Business Intelligence Platform)
python main.py

# Run use-case blueprints (5 patterns across industries)
python use_cases.py
```

> **Auth**: Reads `OPENAI_API_KEY` from `GenAI/.env` automatically.
> No Azure CLI or extra configuration required.

---

## Main Demo — Business Intelligence Platform

Analyse any business idea through **5 specialist lenses simultaneously**,
then synthesise into an executive GO / NO-GO brief.

```
topic (str)
  ├──► [📊 Market Analyst]        → TAM/SAM/SOM, trends, entry barriers
  ├──► [💰 Financial Analyst]     → Revenue model, costs, path to profit
  ├──► [🔧 Technology Analyst]    → Feasibility, stack, build timeline
  ├──► [🏆 Competitive Intel]     → Competitors, moats, white space
  └──► [⚠️  Risk Analyst]         → Risk matrix (likelihood × impact)
                    │
            [🧠 CIO Aggregator]   → Executive Intelligence Brief
                    │
          GO / NO-GO / CONDITIONAL GO
```

**Sample output includes:**
- Individual analyst report for each of the 5 dimensions
- Parallel timing table (wall-clock vs estimated sequential)
- Speedup multiplier (typically 3–5× faster)
- GO/NO-GO recommendation with top 3 strengths + concerns
- 5-step priority action plan
- 2×2 Opportunity Matrix
- Overall confidence score (0–100%)
- Saved to `intelligence_brief.md`

---

## Use Case Blueprints

### 1. 🔒 Code Security Audit — `DevSec / Engineering`

**Workers**: Security (OWASP) | Performance | Code Quality | Dependencies | Test Coverage

**Aggregator**: Lead Architect → Critical issues / High-priority / Nice-to-haves + Code Health Grade (A–F)

**Recommended when**:
- Code reviews blocking CI/CD pipelines
- Security audits before production deploys
- Automated pre-merge gates in GitHub Actions
- Onboarding PRs from contractors / new hires

---

### 2. 👔 Job Candidate Screening — `HR / Talent Acquisition`

**Workers**: Skills Match | Experience Depth | Culture Fit | Red Flags | Growth Potential

**Aggregator**: Hiring Manager → ADVANCE / HOLD / PASS + interview questions

**Recommended when**:
- High-volume recruitment (>20 applicants per role)
- Technical roles requiring multi-dimensional evaluation
- Reducing unconscious bias via structured scoring
- Async pre-screening before live interviews

---

### 3. 📚 Academic Paper Peer Review — `Research / Publishing`

**Workers**: Methodology | Data Quality | Novelty | Reproducibility | Writing Clarity

**Aggregator**: Editor-in-Chief → ACCEPT / MINOR REVISION / MAJOR REVISION / REJECT

**Recommended when**:
- Journal / conference automated pre-screening
- Internal research quality gates before external submission
- Grant proposal review panels
- Systematic literature review triage

---

### 4. 🛒 Product Review Intelligence — `E-commerce / Consumer`

**Workers**: Feature Analysis | Price & Value | Reliability & UX | User Sentiment | Competitive Position

**Aggregator**: Consumer Advisor → BUY NOW / WAIT / SKIP / BETTER ALTERNATIVES

**Recommended when**:
- Product recommendation engines
- Procurement / purchasing decision support
- Competitive product benchmarking reports
- Consumer journalism / editorial review sites

---

### 5. 🚨 Crisis Communication Triage — `PR / Communications`

**Workers**: Media Sentiment | Stakeholder Impact | Legal Exposure | Reputation Damage | Response Quality

**Aggregator**: Crisis Manager → 48-Hour Response Playbook

**Recommended when**:
- Breaking news about the brand (data breach, product recall)
- Executive misconduct response planning
- Regulatory investigation communications
- Any incident where minutes matter

---

## How Parallel Differs from Sequential

| Dimension | Sequential | Parallel |
|---|---|---|
| **Execution** | Stage N runs after Stage N-1 finishes | All workers run at the same instant |
| **Context** | Each stage sees all prior stages' output | Each worker sees only the shared input |
| **Latency** | Sum of all stage latencies | Max of all worker latencies |
| **Best for** | Dependent transformations (research → write → review) | Independent analysis of the same input |
| **Token cost** | Same total tokens, spread over time | Same total tokens, consumed simultaneously |

---

## Key Implementation Pattern

```python
import asyncio

# Fan-Out: all workers start at the same instant
reports = await asyncio.gather(
    worker_market(topic),
    worker_financial(topic),
    worker_tech(topic),
    worker_competitive(topic),
    worker_risk(topic),
)

# Fan-In: aggregator sees all 5 reports
final_brief = await aggregator(topic, reports)
```

**That's the entire pattern.** Everything else is just the content of each worker.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ Yes | — | Your OpenAI API key |
| `OPENAI_MODEL` | Optional | `gpt-4o-mini` | Override the model |

The `.env` file is read from `GenAI/.env` (two directories above this folder).

---

## Related Patterns

| Pattern | Use when… |
|---|---|
| [Sequential](../sequential_agent/) | Stages build on each other's output |
| **Parallel** ← you are here | Stages are independent analyses of the same input |
| Routing | Input determines which agent to use |
| Reflection | Agent reviews and improves its own output |
| Multi-Agent | Agents collaborate, debate, or divide complex tasks |
