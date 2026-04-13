# Agent Pattern Use Cases & Practice Projects

## Overview

This guide provides **12 real-world use cases** organized by agent pattern. Each use case includes a problem statement, architecture diagram, suggested tools, and implementation hints so you can build and run them for learning.

---

## 🟢 Single Agent Use Cases

### Use Case 1: Personal Finance Advisor

**Problem**: Build an agent that helps users manage their finances — checking budgets, categorizing expenses, and giving advice.

**Tools to Implement**:
```python
tools = [
    "get_account_balance(account_id) → balance info",
    "get_transactions(account_id, days=30) → recent transactions",
    "categorize_expense(description) → category + subcategory",
    "get_budget(category) → budget limit + current spending",
    "set_budget_alert(category, threshold) → confirmation"
]
```

**Architecture**:
```
User: "How much did I spend on food this month?"
  │
  ▼
Finance Agent
  ├── get_transactions("checking", 30)
  ├── categorize_expense() for each
  ├── get_budget("food")
  └── Generate summary + advice
```

**Sample Interactions**:
```
User: "Am I over budget on dining out?"
User: "What are my top 3 spending categories?"
User: "Help me create a savings plan for $500/month"
```

**Implementation Tips**:
- Use a dictionary as a mock database for accounts/transactions
- The categorization tool can be another LLM call or rule-based
- Add memory so the agent remembers user preferences across queries

---

### Use Case 2: DevOps Incident Responder

**Problem**: Build an agent that helps diagnose and respond to production incidents.

**Tools to Implement**:
```python
tools = [
    "check_service_health(service_name) → UP/DOWN + metrics",
    "get_recent_logs(service_name, lines=50) → log entries",
    "get_deployment_history(service_name) → recent deploys",
    "rollback_deployment(service_name) → rollback result",
    "create_incident_report(title, severity, details) → report_id",
    "notify_team(channel, message) → sent confirmation"
]
```

**Sample Interactions**:
```
User: "The checkout service is returning 500 errors"
User: "Was there a recent deployment to payments?"
User: "Rollback the auth service to the previous version"
```

---

### Use Case 3: Smart Study Assistant

**Problem**: Build an agent that helps students study — creating flashcards, quizzes, and explanations.

**Tools to Implement**:
```python
tools = [
    "create_flashcards(topic, count=10) → flashcard set",
    "generate_quiz(topic, difficulty, num_questions) → quiz",
    "explain_concept(concept, level='beginner') → explanation",
    "search_notes(query) → matching notes",
    "track_progress(topic) → mastery score + weak areas"
]
```

**Sample Interactions**:
```
User: "Create 10 flashcards on Python decorators"
User: "Give me a medium quiz on machine learning basics"
User: "Explain transformers like I'm a beginner"
```

---

## 🔵 Sequential Pipeline Use Cases

### Use Case 4: Job Application Pipeline

**Problem**: Given a job posting URL and a resume, create a tailored application package.

**Pipeline Stages**:
```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ JOB PARSER   │──►│ RESUME       │──►│ COVER LETTER │──►│ INTERVIEW    │
│              │   │ TAILOR       │   │ WRITER       │   │ PREP         │
│ Extract:     │   │              │   │              │   │              │
│ - Title      │   │ Rewrite      │   │ Write        │   │ Generate:    │
│ - Skills     │   │ resume to    │   │ personalized │   │ - 10 likely  │
│ - Reqs       │   │ match job    │   │ cover letter │   │   questions  │
│ - Culture    │   │ requirements │   │              │   │ - STAR       │
│              │   │              │   │              │   │   answers    │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

**Implementation**:
```python
stages = [
    {"name": "Job Parser",     "prompt": "Extract key requirements, skills, and culture values..."},
    {"name": "Resume Tailor",  "prompt": "Rewrite this resume to emphasize matching skills..."},
    {"name": "Cover Letter",   "prompt": "Write a compelling cover letter using these details..."},
    {"name": "Interview Prep", "prompt": "Generate likely interview questions with STAR answers..."}
]
```

---

### Use Case 5: Code Documentation Pipeline

**Problem**: Take raw source code and produce complete documentation.

**Pipeline Stages**:
```
Code Input → Analyzer → Docstring Writer → README Generator → API Docs Formatter
```

| Stage | Input | Output |
|-------|-------|--------|
| **Analyzer** | Raw source code | List of functions, classes, params, relationships |
| **Docstring Writer** | Analysis + code | Code with docstrings added |
| **README Generator** | Analysis | Installation, usage, examples README |
| **API Docs Formatter** | Docstrings + analysis | Formatted API reference (Markdown) |

---

### Use Case 6: Customer Feedback Pipeline

**Problem**: Process raw customer reviews into actionable insights.

**Pipeline Stages**:
```
Raw Reviews → Sentiment Classifier → Theme Extractor → Priority Ranker → Action Report
```

**Implementation Sketch**:
```python
def feedback_pipeline(reviews: list[str]) -> str:
    # Stage 1: Classify each review
    classified = run_agent(CLASSIFIER, format_reviews(reviews))
    # → [{"text": "...", "sentiment": "negative", "score": 0.2}, ...]

    # Stage 2: Extract common themes
    themes = run_agent(THEME_EXTRACTOR, classified)
    # → ["shipping delays", "product quality", "customer service"]

    # Stage 3: Rank by urgency/frequency
    ranked = run_agent(PRIORITY_RANKER, themes + classified)
    # → [{"theme": "shipping", "priority": "HIGH", "count": 45}, ...]

    # Stage 4: Generate action report
    report = run_agent(ACTION_REPORTER, ranked)
    # → Formatted report with recommendations

    return report
```

---

## 🟡 Parallel Agent Use Cases

### Use Case 7: Multi-Source News Analyzer

**Problem**: Given a news topic, analyze it from multiple perspectives simultaneously.

**Parallel Agents**:
```
Topic: "AI Regulation in Europe"
  │
  ├── 🔴 Political Analyst   → Policy implications
  ├── 🔵 Tech Analyst        → Impact on AI companies
  ├── 🟢 Economic Analyst    → Market effects
  └── 🟡 Ethics Analyst      → Human rights perspective
  │
  ▼
Synthesis Agent → Balanced multi-perspective report
```

**Why Parallel?** Each perspective is independent — no agent needs another's output.

---

### Use Case 8: Multi-Language Content Localizer

**Problem**: Translate and culturally adapt marketing content for multiple regions at once.

**Parallel Agents**:
```
English Marketing Copy
  │
  ├── 🇪🇸 Spanish Localizer  (Spain + LatAm variants)
  ├── 🇫🇷 French Localizer   (France + Canada variants)
  ├── 🇯🇵 Japanese Localizer  (formal business tone)
  └── 🇧🇷 Portuguese Localizer (Brazil)
  │
  ▼
Quality Checker → Verify consistency across all versions
```

**Implementation Tips**:
- Each localizer is the same agent with different system prompts
- The quality checker ensures brand voice consistency
- Use `asyncio.gather()` for true parallel execution

---

### Use Case 9: Competitive Product Analyzer

**Problem**: Compare 3-4 products in detail, analyzing each independently, then merging.

**Parallel Agents**:
```
"Compare iPhone 16 vs Galaxy S25 vs Pixel 9"
  │
  ├── Agent 1: Deep dive iPhone 16   (specs, reviews, pros/cons)
  ├── Agent 2: Deep dive Galaxy S25  (specs, reviews, pros/cons)
  └── Agent 3: Deep dive Pixel 9     (specs, reviews, pros/cons)
  │
  ▼
Comparison Agent → Side-by-side table + recommendation
```

---

## 🔴 Hierarchical Agent Use Cases

### Use Case 10: Startup Business Plan Generator

**Problem**: Generate a complete business plan by delegating to domain experts.

**Architecture**:
```
User: "Create a business plan for an AI tutoring startup"
  │
  ▼
Manager Agent (CEO/Strategist)
  │
  ├── Market Research Worker
  │     → Market size, target audience, competitors
  │
  ├── Product Strategy Worker
  │     → Features, tech stack, MVP scope, roadmap
  │
  ├── Financial Modeling Worker
  │     → Revenue projections, costs, funding needs
  │
  ├── Marketing Strategy Worker
  │     → Go-to-market plan, channels, CAC/LTV
  │
  └── Manager synthesizes into complete business plan
```

**Manager's Planning Prompt**:
```python
MANAGER = """You are a startup advisor managing specialist consultants.
Given a startup idea, create a plan with these phases:
1. Identify which specialists to consult
2. Craft specific questions for each
3. Review their outputs for consistency
4. Synthesize into a cohesive business plan

If a specialist's output is insufficient, you may request a revision."""
```

---

### Use Case 11: Full-Stack Feature Builder

**Problem**: A manager agent coordinates the full lifecycle of building a software feature.

**Architecture**:
```
User: "Build a user authentication feature"
  │
  ▼
Tech Lead (Manager)
  │
  ├── UX Designer Worker → Wireframes, user flow
  │     ↓ (reviewed by manager)
  ├── Backend Developer Worker → API design, DB schema
  │     ↓ (reviewed by manager)
  ├── Frontend Developer Worker → UI components (using UX output)
  │     ↓ (reviewed by manager)
  ├── QA Engineer Worker → Test cases, edge cases
  │     ↓ (reviewed by manager)
  └── Tech Lead synthesizes → Implementation plan + timeline
```

**Key Feature**: The manager **reviews each worker's output** and can request revisions before proceeding.

---

### Use Case 12: Travel Itinerary Planner

**Problem**: Plan a detailed multi-day travel itinerary.

**Architecture**:
```
User: "Plan a 5-day trip to Japan for 2 people, budget $5000"
  │
  ▼
Travel Manager Agent
  │
  ├── Flight Worker → Find best flight options + booking tips
  ├── Hotel Worker → Accommodation options by area + budget
  ├── Activities Worker → Day-by-day activities + tickets
  ├── Food Worker → Restaurant recommendations + food tours
  ├── Budget Worker → Complete budget breakdown + tips
  │
  └── Manager → Day-by-day itinerary with times, costs, logistics
```

---

## Practice Roadmap

### Week 1: Single Agent (Beginner)
Pick **one** from Use Cases 1-3. Build it with:
- [ ] 3+ tools
- [ ] Proper agent loop with max iterations
- [ ] Error handling for tool failures
- [ ] Interactive CLI

### Week 2: Sequential Pipeline (Intermediate)
Pick **one** from Use Cases 4-6. Build it with:
- [ ] 3+ pipeline stages
- [ ] Output validation between stages
- [ ] Ability to retry a failed stage
- [ ] Save intermediate results to files

### Week 3: Parallel Agents (Intermediate)
Pick **one** from Use Cases 7-9. Build it with:
- [ ] `asyncio` for true parallel execution
- [ ] 3+ parallel agents
- [ ] Aggregation/synthesis step
- [ ] Timing comparison (parallel vs sequential)

### Week 4: Hierarchical (Advanced)
Pick **one** from Use Cases 10-12. Build it with:
- [ ] Manager with planning ability
- [ ] 3+ specialized workers
- [ ] Manager reviews worker outputs
- [ ] Re-delegation on insufficient results
- [ ] Final synthesis

---

## Tips for All Exercises

1. **Start with mocks** — Use dictionaries and fake data before calling real APIs
2. **Add logging** — Print each step so you can see the agent's reasoning
3. **Set token limits** — Track costs with `response.usage.total_tokens`
4. **Test edge cases** — What happens when a tool fails? When input is ambiguous?
5. **Compare models** — Try `gpt-4o-mini` vs `gpt-4o` — notice the quality difference

---

**Previous**: [Agent Patterns Tutorial](./04-agent-patterns.md)  
**Exercises**: [Start practicing →](../exercises/intermediate/)
