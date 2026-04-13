# Agent Patterns: Single, Sequential, Parallel & Hierarchical

## Overview

Agent patterns define **how agents are organized and coordinated** to accomplish tasks. Choosing the right pattern depends on the complexity, latency requirements, and nature of the task.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Pattern Spectrum                       │
│                                                                  │
│  Simple ◄──────────────────────────────────────────► Complex     │
│                                                                  │
│  Single        Sequential        Parallel        Hierarchical    │
│  Agent          Pipeline          Agents           (Manager +    │
│                                                     Workers)     │
└─────────────────────────────────────────────────────────────────┘
```

| Pattern | When to Use | Latency | Complexity |
|---------|-------------|---------|------------|
| **Single** | One-purpose tasks, tool use | Low | Low |
| **Sequential** | Multi-step pipelines where order matters | Medium | Medium |
| **Parallel** | Independent subtasks, speed matters | Low | Medium |
| **Hierarchical** | Complex tasks needing delegation & synthesis | High | High |

---

## Pattern 1: Single Agent

### Concept

A **single agent** has one LLM brain, a system prompt, and a set of tools. It runs a **think → act → observe** loop until the task is done.

```
┌──────────────────────────────────┐
│           USER QUERY             │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│         SINGLE AGENT             │
│  ┌────────────────────────────┐  │
│  │  System Prompt + LLM       │  │
│  └──────────┬─────────────────┘  │
│             │                    │
│  ┌──────────▼─────────────────┐  │
│  │  Tools:                    │  │
│  │  🔧 search_kb()            │  │
│  │  🔧 check_order()          │  │
│  │  🔧 process_refund()       │  │
│  │  🔧 send_email()           │  │
│  └────────────────────────────┘  │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│         FINAL RESPONSE           │
└──────────────────────────────────┘
```

### How It Works

```
Loop:
  1. LLM receives user input + conversation history
  2. LLM decides: respond directly OR call a tool
  3. If tool call → execute tool → feed result back to LLM
  4. Repeat until LLM generates final answer
```

### Key Characteristics
- ✅ **Simple** — one LLM, one set of tools
- ✅ **Good for**: customer support, data lookup, calculations
- ⚠️ **Limitation**: struggles with complex multi-domain tasks

### Code Example

```python
import json
from openai import OpenAI

client = OpenAI()

# ── Tool Definitions ──────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search the product catalog by keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check if a product is in stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"}
                },
                "required": ["product_id"]
            }
        }
    }
]

# ── Tool Implementations ──────────────────────────────────────
CATALOG = {
    "laptop-01": {"name": "ProBook Laptop", "price": 999, "stock": 5},
    "phone-02":  {"name": "SmartPhone X",   "price": 699, "stock": 0},
    "tablet-03": {"name": "TabPro 11",      "price": 449, "stock": 12},
}

def search_products(query: str) -> str:
    results = [
        {"id": pid, **info}
        for pid, info in CATALOG.items()
        if query.lower() in info["name"].lower()
    ]
    return json.dumps(results) if results else "No products found."

def check_inventory(product_id: str) -> str:
    product = CATALOG.get(product_id)
    if not product:
        return f"Product {product_id} not found."
    status = "In Stock" if product["stock"] > 0 else "Out of Stock"
    return f"{product['name']}: {status} ({product['stock']} units)"

TOOL_MAP = {
    "search_products": search_products,
    "check_inventory": check_inventory,
}

# ── Agent Loop ────────────────────────────────────────────────
def run_single_agent(user_input: str, max_turns: int = 5) -> str:
    messages = [
        {"role": "system", "content": (
            "You are a helpful shopping assistant. "
            "Use tools to search products and check inventory. "
            "Always check stock before recommending a product."
        )},
        {"role": "user", "content": user_input}
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump())

        # No tool calls → final answer
        if not msg.tool_calls:
            return msg.content

        # Execute each tool call
        for tc in msg.tool_calls:
            fn = TOOL_MAP[tc.function.name]
            result = fn(**json.loads(tc.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return "Max turns reached."

# ── Run ───────────────────────────────────────────────────────
answer = run_single_agent("Do you have any laptops in stock?")
print(answer)
```

### Use Cases for Practice

| # | Use Case | Tools Needed |
|---|----------|-------------|
| 1 | **Shopping Assistant** | `search_products`, `check_inventory`, `get_price` |
| 2 | **IT Help Desk** | `search_docs`, `check_system_status`, `create_ticket` |
| 3 | **Travel Planner** | `search_flights`, `search_hotels`, `get_weather` |
| 4 | **Recipe Finder** | `search_recipes`, `check_pantry`, `get_nutrition` |

---

## Pattern 2: Sequential (Pipeline) Agent

### Concept

Multiple agents run **one after another**, each passing its output as input to the next. Like an assembly line — each station does one job.

```
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│ Agent 1   │───►│ Agent 2   │───►│ Agent 3   │───►│ Agent 4  │
│ RESEARCH  │    │ OUTLINE   │    │ WRITE     │    │ REVIEW   │
│           │    │           │    │           │    │          │
│ "Find     │    │ "Create   │    │ "Write    │    │ "Edit &  │
│  sources" │    │  outline" │    │  article" │    │  polish" │
└──────────┘    └───────────┘    └───────────┘    └──────────┘
     │               │                │                │
     ▼               ▼                ▼                ▼
  Sources         Outline          Draft           Final Article
```

### How It Works

```
Pipeline:
  1. Agent 1 receives user input → produces Output 1
  2. Agent 2 receives Output 1 → produces Output 2
  3. Agent 3 receives Output 2 → produces Output 3
  ...
  N. Final output returned to user
```

### Key Characteristics
- ✅ **Modular** — each agent has a focused role
- ✅ **Good for**: content pipelines, data processing, review workflows
- ⚠️ **Limitation**: slow (sequential), one failure blocks the chain

### Code Example

```python
from openai import OpenAI

client = OpenAI()

def run_agent(system_prompt: str, user_input: str, model: str = "gpt-4o-mini") -> str:
    """Run a single agent with a specific role."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# ── Define Pipeline Stages ────────────────────────────────────

RESEARCHER = """You are a Research Agent.
Given a topic, produce 5 key facts with brief explanations.
Format: numbered list with fact + 1-sentence explanation."""

OUTLINER = """You are an Outline Agent.
Given research notes, create a structured blog post outline with:
- Title
- Introduction hook
- 3-4 main sections with bullet points
- Conclusion"""

WRITER = """You are a Writing Agent.
Given an outline, write a complete blog post (400-500 words).
Use engaging tone, clear paragraphs, and smooth transitions."""

EDITOR = """You are an Editing Agent.
Review and improve the article:
- Fix grammar and clarity
- Improve flow and transitions
- Add a compelling opening line
- Ensure consistent tone
Return the polished final version."""

# ── Run Sequential Pipeline ───────────────────────────────────

def content_pipeline(topic: str) -> dict:
    """Run the full content creation pipeline."""
    print(f"📝 Topic: {topic}\n")

    # Stage 1: Research
    print("🔍 Stage 1: Researching...")
    research = run_agent(RESEARCHER, f"Research this topic: {topic}")
    print(f"   Found key facts ✓\n")

    # Stage 2: Outline
    print("📋 Stage 2: Creating outline...")
    outline = run_agent(OUTLINER, f"Create outline from:\n{research}")
    print(f"   Outline ready ✓\n")

    # Stage 3: Write
    print("✍️  Stage 3: Writing article...")
    draft = run_agent(WRITER, f"Write article from outline:\n{outline}")
    print(f"   Draft complete ✓\n")

    # Stage 4: Edit
    print("🔧 Stage 4: Editing & polishing...")
    final = run_agent(EDITOR, f"Edit and polish:\n{draft}")
    print(f"   Final version ready ✓\n")

    return {
        "research": research,
        "outline": outline,
        "draft": draft,
        "final_article": final
    }

# ── Run ───────────────────────────────────────────────────────
result = content_pipeline("The Future of AI Agents in 2026")
print("=" * 60)
print(result["final_article"])
```

### Use Cases for Practice

| # | Use Case | Pipeline Stages |
|---|----------|----------------|
| 1 | **Blog Post Generator** | Research → Outline → Write → Edit |
| 2 | **Email Drafter** | Analyze context → Draft → Tone check → Personalize |
| 3 | **Bug Report Processor** | Parse → Classify severity → Suggest fix → Format report |
| 4 | **Resume Optimizer** | Parse resume → Analyze job description → Rewrite → Format |

---

## Pattern 3: Parallel Agents

### Concept

Multiple agents run **simultaneously** on different subtasks. Results are **collected and merged** at the end. Best when subtasks are independent.

```
                    ┌──────────────┐
                    │  USER QUERY  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  DISPATCHER  │
                    │  (split task)│
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Agent A  │ │ Agent B  │ │ Agent C  │
        │ Tech     │ │ Market   │ │ Finance  │
        │ Analysis │ │ Research │ │ Analysis │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Result A │ │ Result B │ │ Result C │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          │
                   ┌──────▼───────┐
                   │  AGGREGATOR  │
                   │  (merge all) │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ FINAL REPORT │
                   └──────────────┘
```

### How It Works

```
Parallel Execution:
  1. Dispatcher splits the task into N independent subtasks
  2. N agents run concurrently (asyncio / threading)
  3. All results collected
  4. Aggregator merges results into final output
```

### Key Characteristics
- ✅ **Fast** — runs in parallel, total time ≈ slowest agent
- ✅ **Good for**: multi-source research, multi-perspective analysis
- ⚠️ **Limitation**: subtasks must be independent; merging can be tricky

### Code Example

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def run_agent_async(name: str, system_prompt: str, user_input: str) -> dict:
    """Run a single agent asynchronously."""
    print(f"  🚀 {name} started...")
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    result = response.choices[0].message.content
    print(f"  ✅ {name} finished!")
    return {"agent": name, "result": result}

# ── Define Parallel Agents ────────────────────────────────────

AGENTS = {
    "Tech Analyst": (
        "You are a Technology Analyst. "
        "Analyze the given company/product from a TECHNOLOGY perspective. "
        "Cover: tech stack, innovation, patents, R&D. Keep it to 150 words."
    ),
    "Market Analyst": (
        "You are a Market Analyst. "
        "Analyze the given company/product from a MARKET perspective. "
        "Cover: market share, competitors, growth trends. Keep it to 150 words."
    ),
    "Financial Analyst": (
        "You are a Financial Analyst. "
        "Analyze the given company/product from a FINANCIAL perspective. "
        "Cover: revenue, profitability, valuation, risks. Keep it to 150 words."
    ),
    "Sentiment Analyst": (
        "You are a Public Sentiment Analyst. "
        "Analyze public perception of the given company/product. "
        "Cover: social media trends, customer reviews, brand reputation. Keep it to 150 words."
    ),
}

AGGREGATOR = """You are a Senior Analyst. You receive analyses from multiple specialists.
Synthesize them into one cohesive executive summary (300 words max).
Include: key strengths, risks, and an overall recommendation."""

# ── Run Parallel Pipeline ─────────────────────────────────────

async def parallel_analysis(topic: str) -> str:
    print(f"\n📊 Parallel Analysis: {topic}\n")

    # Step 1: Run all agents in parallel
    tasks = [
        run_agent_async(name, prompt, f"Analyze: {topic}")
        for name, prompt in AGENTS.items()
    ]
    results = await asyncio.gather(*tasks)

    # Step 2: Aggregate results
    print("\n📋 Aggregating results...")
    combined = "\n\n".join(
        f"### {r['agent']}\n{r['result']}" for r in results
    )

    aggregation = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AGGREGATOR},
            {"role": "user", "content": f"Synthesize these analyses:\n\n{combined}"}
        ]
    )

    return aggregation.choices[0].message.content

# ── Run ───────────────────────────────────────────────────────
final_report = asyncio.run(parallel_analysis("Tesla's AI and Robotics Strategy"))
print("\n" + "=" * 60)
print(final_report)
```

### Use Cases for Practice

| # | Use Case | Parallel Agents |
|---|----------|----------------|
| 1 | **Company Research** | Tech + Market + Finance + Sentiment analysts |
| 2 | **Multi-language Translator** | English→Spanish, English→French, English→German |
| 3 | **Code Review** | Security reviewer + Performance reviewer + Style reviewer |
| 4 | **Product Comparison** | One agent per product → Comparison aggregator |

---

## Pattern 4: Hierarchical (Manager-Workers)

### Concept

A **Manager Agent** receives the task, creates a plan, and **delegates subtasks** to specialized **Worker Agents**. The manager coordinates, monitors progress, and synthesizes the final result.

```
                    ┌──────────────────┐
                    │    USER TASK     │
                    │ "Plan a company  │
                    │  offsite event"  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  MANAGER AGENT   │
                    │                  │
                    │ 1. Understand    │
                    │ 2. Plan          │
                    │ 3. Delegate      │
                    │ 4. Synthesize    │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  VENUE       │ │  CATERING    │ │  ACTIVITIES  │
    │  WORKER      │ │  WORKER      │ │  WORKER      │
    │              │ │              │ │              │
    │ Find venues  │ │ Plan menu    │ │ Plan team    │
    │ Compare      │ │ Budget       │ │ activities   │
    │ Recommend    │ │ Dietary needs│ │ Schedule     │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼
      Venue Report     Menu Plan      Activity Plan
           │                │                │
           └────────────────┼────────────────┘
                            │
                   ┌────────▼─────────┐
                   │  MANAGER AGENT   │
                   │  Reviews &       │
                   │  Synthesizes     │
                   │  Final Plan      │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  COMPLETE EVENT  │
                   │  PLAN + BUDGET   │
                   └──────────────────┘
```

### How It Works

```
Hierarchical Flow:
  1. Manager receives the full task
  2. Manager creates a plan + identifies subtasks
  3. Manager delegates each subtask to a specialist Worker
  4. Workers execute and return results
  5. Manager reviews, may request revisions
  6. Manager synthesizes final output
```

### Key Characteristics
- ✅ **Powerful** — handles complex, multi-domain tasks
- ✅ **Adaptive** — manager can re-plan based on worker results
- ✅ **Good for**: project planning, complex research, multi-step workflows
- ⚠️ **Limitation**: higher cost (many LLM calls), more complex to build

### Code Example

```python
import json
from openai import OpenAI

client = OpenAI()

def call_llm(system: str, user: str, model: str = "gpt-4o-mini", json_mode: bool = False) -> str:
    """Helper to call the LLM."""
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        **kwargs
    )
    return response.choices[0].message.content

# ── Worker Agents ─────────────────────────────────────────────

WORKERS = {
    "venue_finder": {
        "prompt": (
            "You are a Venue Research Specialist. "
            "Given event requirements, suggest 3 venue options with:\n"
            "- Name & type\n- Capacity\n- Estimated cost\n- Pros & cons\n"
            "Be specific and realistic."
        )
    },
    "catering_planner": {
        "prompt": (
            "You are a Catering Specialist. "
            "Given event details, create a catering plan with:\n"
            "- Menu options (dietary-inclusive)\n"
            "- Per-person cost estimate\n- Beverage options\n"
            "- Special accommodations"
        )
    },
    "activity_designer": {
        "prompt": (
            "You are a Team Activities Designer. "
            "Given the event context, propose:\n"
            "- 3 team-building activities\n"
            "- Detailed schedule\n- Required materials\n"
            "- Ice-breaker suggestions"
        )
    },
    "budget_analyst": {
        "prompt": (
            "You are a Budget Analyst. "
            "Given venue, catering, and activity plans, create:\n"
            "- Itemized budget breakdown\n"
            "- Total estimated cost\n- Cost-saving tips\n"
            "- Contingency recommendations (10-15%)"
        )
    }
}

# ── Manager Agent ─────────────────────────────────────────────

MANAGER_PLAN = """You are an Event Planning Manager.
Given a task, create a delegation plan as JSON:
{
  "understanding": "brief summary of what's needed",
  "subtasks": [
    {"worker": "worker_name", "instruction": "specific instruction for this worker"}
  ]
}

Available workers: venue_finder, catering_planner, activity_designer, budget_analyst
Order subtasks logically (budget_analyst should come last, as it needs other results)."""

MANAGER_SYNTHESIZE = """You are an Event Planning Manager.
You delegated subtasks to specialists. Now synthesize their results into
a complete, well-organized event plan. Include:
- Executive Summary
- Venue Recommendation (pick the best option)
- Catering Plan
- Activity Schedule
- Budget Overview
- Next Steps

Make it professional and actionable."""

# ── Hierarchical Execution ────────────────────────────────────

def run_hierarchical(task: str) -> str:
    print(f"📋 Task: {task}\n")

    # Step 1: Manager creates plan
    print("🧠 Manager: Creating delegation plan...")
    plan_json = call_llm(MANAGER_PLAN, task, json_mode=True)
    plan = json.loads(plan_json)
    print(f"   Understanding: {plan['understanding']}")
    print(f"   Subtasks: {len(plan['subtasks'])}\n")

    # Step 2: Execute each worker
    worker_results = {}
    for subtask in plan["subtasks"]:
        worker_name = subtask["worker"]
        instruction = subtask["instruction"]
        worker_prompt = WORKERS[worker_name]["prompt"]

        # Include previous results for context
        context = ""
        if worker_results:
            context = "\n\nPrevious results for reference:\n" + "\n---\n".join(
                f"[{k}]: {v[:300]}..." for k, v in worker_results.items()
            )

        print(f"  👷 Delegating to {worker_name}...")
        result = call_llm(
            worker_prompt,
            f"{instruction}{context}"
        )
        worker_results[worker_name] = result
        print(f"     ✅ {worker_name} complete!")

    # Step 3: Manager synthesizes
    print("\n🧠 Manager: Synthesizing final plan...")
    all_results = "\n\n---\n\n".join(
        f"## {name} Report:\n{result}"
        for name, result in worker_results.items()
    )
    final = call_llm(
        MANAGER_SYNTHESIZE,
        f"Original task: {task}\n\nWorker results:\n{all_results}"
    )

    return final

# ── Run ───────────────────────────────────────────────────────
plan = run_hierarchical(
    "Plan a 2-day company offsite for 50 engineers. "
    "Budget: $15,000. Location: San Francisco Bay Area. "
    "Goals: team building, strategic planning, and fun."
)
print("\n" + "=" * 60)
print(plan)
```

### Use Cases for Practice

| # | Use Case | Manager + Workers |
|---|----------|-------------------|
| 1 | **Event Planner** | Manager → Venue + Catering + Activities + Budget workers |
| 2 | **Startup Advisor** | Manager → Market research + Tech feasibility + Financial model workers |
| 3 | **Course Creator** | Manager → Curriculum designer + Content writer + Quiz maker workers |
| 4 | **App Feature Planner** | Manager → UX researcher + Developer + QA workers |

---

## Choosing the Right Pattern

### Decision Flowchart

```
START: What is your task?
  │
  ├── Simple, one-domain task?
  │     └── ✅ Single Agent
  │
  ├── Multi-step where each step depends on the previous?
  │     └── ✅ Sequential Pipeline
  │
  ├── Multiple independent subtasks that can run at once?
  │     └── ✅ Parallel Agents
  │
  └── Complex task needing planning, delegation & synthesis?
        └── ✅ Hierarchical (Manager-Workers)
```

### Combining Patterns

Real-world systems often **combine** patterns:

```
┌────────────────────────────────────────────────┐
│  HIERARCHICAL + PARALLEL + SEQUENTIAL          │
│                                                │
│  Manager creates plan                          │
│    │                                           │
│    ├── Worker Group A (parallel)               │
│    │     ├── Research Agent 1                  │
│    │     └── Research Agent 2                  │
│    │           │                               │
│    │           ▼                               │
│    │     Merged Research                       │
│    │           │                               │
│    ├── Worker B (sequential pipeline)          │
│    │     Draft → Review → Polish               │
│    │           │                               │
│    └── Manager synthesizes all                 │
└────────────────────────────────────────────────┘
```

---

## Summary Comparison

| Feature | Single | Sequential | Parallel | Hierarchical |
|---------|--------|------------|----------|-------------|
| **Agents** | 1 | N (chain) | N (concurrent) | 1 manager + N workers |
| **Speed** | Fast | Slow (sum of all) | Fast (max of all) | Medium |
| **Complexity** | Low | Medium | Medium | High |
| **LLM Calls** | 1-5 | N | N+1 | N+2 or more |
| **Best For** | Tool use | Pipelines | Independent tasks | Complex planning |
| **Error Impact** | Contained | Blocks chain | Partial failure OK | Manager can re-plan |

---

## Exercises

Ready to practice? Head to the exercises:

1. [Exercise 7: Single Agent — IT Help Desk](../exercises/intermediate/07_single_agent.py)
2. [Exercise 8: Sequential Pipeline — Email Campaign](../exercises/intermediate/08_sequential_agents.py)
3. [Exercise 9: Parallel Agents — Product Comparison](../exercises/intermediate/09_parallel_agents.py)
4. [Exercise 10: Hierarchical — Startup Pitch Advisor](../exercises/intermediate/10_hierarchical_agents.py)

---

**Next**: [Agent Use Cases & Practice Projects](./05-agent-use-cases.md)
