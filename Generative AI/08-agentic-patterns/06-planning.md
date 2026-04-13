# Chapter 6: Planning

> Break a complex goal into steps, execute them, and re-plan if needed.

## 🧠 Concept

A **planning agent** first creates a step-by-step plan, then executes each step. If a step fails or conditions change, it **re-plans** dynamically. This is the difference between "winging it" and having a strategy — and it's what separates truly capable AI agents from simple prompt-response systems.

Planning sits in the **Reasoning** layer of the AI Agent architecture. While the orchestration layer (frameworks like LangGraph, Google ADK) provides structure, and the data/tools layer (MCP servers, APIs) provides capabilities, it's the **reasoning layer** — powered by language models (LRMs, LLMs, SLMs) — that makes planning possible.

```
┌────────────────────────────────────────────────────────────────┐
│                       PLANNING LOOP                            │
│                                                                │
│  Goal ──▶ [PLANNER LLM] ──▶ Plan (steps 1-N)                  │
│                                  │                             │
│                                  ▼                             │
│                          ┌──────────────┐                      │
│                          │ Execute Step │──▶ Tools / APIs      │
│                          └──────┬───────┘                      │
│                                 │                              │
│                          ┌──────┴──────┐                       │
│                          │  Evaluate   │                       │
│                          │  Result     │                       │
│                          └──────┬──────┘                       │
│                            Y/   │   \N                         │
│                           /     │     \                        │
│                    Next step    │   Re-plan                    │
│                                 │   (new steps)                │
│                          ┌──────┴──────┐                       │
│                          │  All done?  │                       │
│                          └──────┬──────┘                       │
│                                 │                              │
│                          ┌──────┴──────┐                       │
│                          │ Synthesise  │                       │
│                          └──────┬──────┘                       │
│                                 │                              │
│                              Output                            │
└────────────────────────────────────────────────────────────────┘
```

## Where Planning Fits in the AI Agent Stack

Based on the layered architecture of modern AI agents:

```
┌──────────────────────────────────────────────────────────────┐
│  INPUT/OUTPUT          Chat UI (text, image, audio, video)   │
├──────────────────────────────────────────────────────────────┤
│  ORCHESTRATION         Frameworks & SDKs (LangGraph, ADK)    │
│                        Guardrails · Tracing · Evaluation     │
├──────────────────────────────────────────────────────────────┤
│  REASONING  ★          Language Models (LRMs / LLMs / SLMs)  │  ◀── Planning
│                        ↕ MCP Protocol                        │      lives here
├──────────────────────────────────────────────────────────────┤
│  DATA & TOOLS          MCP Server → Vector DB, APIs, etc.    │
├──────────────────────────────────────────────────────────────┤
│  AGENT INTEROP         A2A Protocol → Multi-agent workflows  │
└──────────────────────────────────────────────────────────────┘
```

The **reasoning layer** separates agents from monolithic automations. Planning gives the LLM the ability to:

1. **Decompose** — Break a complex goal into manageable steps
2. **Sequence** — Order steps based on dependencies
3. **Execute** — Carry out each step (possibly using tools via MCP)
4. **Evaluate** — Assess whether results change the remaining plan
5. **Re-plan** — Adapt when new information invalidates the original plan

## When to Use Planning

| ✅ Good Fit | ❌ Not Needed |
|------------|--------------|
| Multi-step research tasks | Simple Q&A |
| Trip/event planning | Single-step lookups |
| Project management agents | Direct tool calls |
| Complex workflows with dependencies | Stateless transformations |
| Goals requiring sequential reasoning | Classification tasks |

## Key Planning Strategies

### 1. Plan-and-Execute (used in this chapter)

The simplest approach: plan all steps upfront, then execute one-by-one.

```python
steps = create_plan(goal)           # LLM generates steps
for step in steps:
    result = execute_step(step)     # LLM executes each step
    if should_replan(result):       # LLM evaluates
        steps = create_plan(...)    # LLM re-plans
```

### 2. ReAct (Reason + Act)

Interleave reasoning and action at every turn:

```
Thought: I need to find flights to Tokyo
Action: search_flights("SFO", "NRT", "2026-04-01")
Observation: Found 12 flights, cheapest $650
Thought: Good, now I need hotels near Shibuya...
```

### 3. Tree of Thoughts

Explore multiple plan branches and pick the best:

```
Goal: Plan a weekend trip
├── Branch A: Beach getaway → score: 7/10
├── Branch B: Mountain hiking → score: 8/10  ★
└── Branch C: City exploration → score: 6/10
```

### 4. Reflexion

Execute, self-critique, then retry with lessons learned:

```
Attempt 1 → Result → Self-critique → Improved Attempt 2
```

## Code Example — Research Planner

```python
import json, os, re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(system: str, user: str) -> str:
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return r.choices[0].message.content


# ── Step 1: Create Plan ──────────────────────────────────

def create_plan(goal: str, context: str = "") -> list[str]:
    """Ask LLM to decompose the goal into concrete steps."""
    prompt = f"Goal: {goal}"
    if context:
        prompt += f"\n\nProgress so far:\n{context}"

    result = call_llm(
        "You are a planning expert. Given a goal, create a numbered "
        "step-by-step plan (3-6 steps). Each step should be a single, "
        "clear action. Return ONLY the numbered list.",
        prompt,
    )

    # Parse: remove "1.", "2)", "- ", "•" prefixes
    steps = []
    for line in result.strip().split("\n"):
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", line.strip())
        cleaned = re.sub(r"^[-•]\s*", "", cleaned)
        if cleaned:
            steps.append(cleaned)
    return steps


# ── Step 2: Execute a Step ───────────────────────────────

def execute_step(step: str, context: str) -> str:
    """Execute one step using context from all previous steps."""
    return call_llm(
        "You are a research assistant executing one step of a plan. "
        "Use the context from previous steps. Be thorough but concise.",
        f"Step to execute: {step}\n\nContext so far:\n{context}",
    )


# ── Step 3: Re-plan if needed ───────────────────────────

def should_replan(step_result: str, remaining_steps: list[str]) -> bool:
    """Let the LLM decide if the remaining plan is still valid."""
    result = call_llm(
        "You evaluate whether a plan needs adjustment. "
        "Answer ONLY 'yes' or 'no'.",
        f"Latest result:\n{step_result}\n\n"
        f"Remaining steps:\n{chr(10).join(remaining_steps)}\n\n"
        f"Do the remaining steps still make sense given this result?",
    )
    return "no" in result.lower()


# ── Run: Plan → Execute → Re-plan → Synthesise ──────────

def plan_and_execute(goal: str, allow_replan: bool = True) -> str:
    print(f"🎯 Goal: {goal}\n")

    steps = create_plan(goal)
    print("📋 Plan:")
    for s in steps:
        print(f"   {s}")
    print()

    context = ""
    i = 0
    while i < len(steps):
        step = steps[i]
        print(f"▶️  Executing: {step}")
        result = execute_step(step, context)
        context += f"\n\n--- {step} ---\n{result}"
        print(f"   ✅ Done\n")

        # Check if the remaining plan is still valid
        remaining = steps[i + 1:]
        if allow_replan and remaining and should_replan(result, remaining):
            print("🔄 Re-planning remaining steps...")
            new_steps = create_plan(
                f"Original goal: {goal}\nCompleted so far:\n{context}\n"
                f"Create remaining steps to finish the goal."
            )
            steps = steps[:i + 1] + new_steps
            print("📋 Updated plan:")
            for s in steps[i + 1:]:
                print(f"   {s}")
            print()

        i += 1

    # Final synthesis
    summary = call_llm(
        "Synthesise the research into a final comprehensive answer.",
        f"Goal: {goal}\n\nResearch:\n{context}",
    )
    return summary


if __name__ == "__main__":
    result = plan_and_execute(
        "Compare the pros and cons of Python vs Rust for building CLI tools"
    )
    print("\n" + "=" * 50)
    print(result)
```

## Plan Representations

| Format | Pros | Cons |
|--------|------|------|
| **Numbered list** | Simple, easy to parse | No dependencies |
| **JSON with deps** | Captures parallelism | More complex prompt |
| **DAG (directed graph)** | Full dependency model | Hardest to implement |

### Example: JSON Plan with Dependencies

```json
{
  "steps": [
    {"id": 1, "action": "Research flights", "depends_on": []},
    {"id": 2, "action": "Research hotels",  "depends_on": []},
    {"id": 3, "action": "Plan activities",  "depends_on": [1, 2]},
    {"id": 4, "action": "Create itinerary", "depends_on": [1, 2, 3]}
  ]
}
```

Steps 1 and 2 can run in **parallel** (no dependencies), while steps 3 and 4 must wait.

## Planning + Other Agentic Patterns

Planning often combines with other patterns from this course:

| Combination | How It Works |
|-------------|-------------|
| **Planning + Tool Use** (Ch 5) | Each step can call tools (search, APIs) via MCP protocol |
| **Planning + Reflection** (Ch 4) | After execution, self-critique and improve the plan |
| **Planning + Parallelization** (Ch 3) | Execute independent steps simultaneously |
| **Planning + Routing** (Ch 2) | Route different step types to specialist sub-agents |
| **Planning + Multi-Agent** (Ch 7) | Planner agent delegates steps to specialist agents |
| **Planning + Guardrails** (Ch 8) | Validate each step's output before proceeding |

## Common Pitfalls

| Pitfall | Mitigation |
|---------|-----------|
| **Plan too vague** | Instruct LLM: "each step must be a single concrete action" |
| **Infinite re-planning** | Cap re-plan attempts (e.g., max 2 re-plans) |
| **Context overflow** | Summarise context periodically instead of appending everything |
| **No error handling** | Wrap step execution in try/catch; skip or retry failed steps |
| **Over-planning** | For simple goals, skip planning; use direct prompting instead |

## Real-World Applications

- **Travel Agents** — Research → Book → Organise itinerary (exercise below)
- **Software Development** — Analyse requirements → Design → Implement → Test
- **Research Assistants** — Form hypothesis → Gather data → Analyse → Report
- **Customer Support** — Diagnose issue → Try fixes → Escalate if needed
- **Data Pipelines** — Ingest → Clean → Transform → Validate → Load

## 🏋️ Practice

→ [Exercise: Planning — Trip Planner Agent](../exercises/agentic/06_planning.py)

Build a trip planner that:
1. Takes a travel request (destination, budget, preferences)
2. Creates a research plan (flights, hotels, activities, restaurants)
3. Executes each research step with detailed recommendations
4. Re-plans if new information changes the approach
5. Synthesises everything into a polished day-by-day itinerary
