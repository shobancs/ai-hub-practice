# Agentic AI — A Comprehensive Tutorial

> From foundational concepts to building production-ready autonomous AI systems

---

## 📖 Table of Contents

1. [What is Agentic AI?](#what-is-agentic-ai)
2. [AI Agents vs. Agentic AI — What's the Difference?](#ai-agents-vs-agentic-ai--whats-the-difference)
3. [Agents vs. Traditional LLMs](#agents-vs-traditional-llms)
4. [Core Components of an Agent](#core-components-of-an-agent)
5. [The Agent Loop — ReAct Pattern](#the-agent-loop--react-pattern)
6. [Agentic Design Patterns](#agentic-design-patterns)
7. [Building Your First Agent](#building-your-first-agent)
8. [Tool Use — Giving Agents Superpowers](#tool-use--giving-agents-superpowers)
9. [Memory and State Management](#memory-and-state-management)
10. [Planning and Reasoning](#planning-and-reasoning)
11. [Multi-Agent Systems](#multi-agent-systems)
12. [Guardrails and Safety](#guardrails-and-safety)
13. [Evaluation and Observability](#evaluation-and-observability)
14. [Agentic AI Frameworks](#agentic-ai-frameworks)
15. [Production Considerations](#production-considerations)
16. [Hands-On Exercises](#hands-on-exercises)

---

## What is Agentic AI?

**Agentic AI** refers to AI systems that can **autonomously perceive, reason, plan, and act** to achieve goals — going far beyond simple question-answering.

```
┌──────────────────────────────────────────────────────────┐
│                    AGENTIC AI SPECTRUM                     │
│                                                           │
│  Chatbot ◄─────────────────────────────────► Full Agent   │
│                                                           │
│  "Answer        "Answer with      "Plan, act,    "Fully   │
│   questions"     tool access"      observe,       autonomous│
│                                    repeat"        system"  │
│                                                           │
│  GPT chat       Function calling   ReAct loop    Multi-   │
│  interface      + single step      + memory       agent   │
│                                                  swarms"  │
└──────────────────────────────────────────────────────────┘
```

### Key Definition

> An **AI Agent** is an LLM-powered system that operates in a loop — reasoning about what to do, taking actions (calling tools, APIs, or other models), observing the results, and repeating until the task is complete.

### The Five Pillars of Agentic AI

| Pillar | Description | Example |
|--------|-------------|---------|
| **Autonomy** | Acts independently without step-by-step human guidance | Agent decides which API to call |
| **Reasoning** | Thinks through problems logically before acting | "I need weather data first, then I can plan the trip" |
| **Tool Use** | Interacts with external systems and APIs | Calling a database, web search, or calculator |
| **Memory** | Maintains context across interactions and sessions | Remembers user preferences, past actions |
| **Planning** | Breaks complex goals into executable steps | Decomposes "plan a vacation" into 8 sub-tasks |

---

## AI Agents vs. Agentic AI — What's the Difference?

These two terms are often used interchangeably, but they refer to **different levels of abstraction**:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│   AI AGENT                           AGENTIC AI                  │
│   ────────                           ──────────                  │
│                                                                  │
│   A specific software entity         A design philosophy /       │
│   that acts autonomously             architectural approach      │
│                                                                  │
│   "The thing you build"              "How you build it"          │
│                                                                  │
│   Has a system prompt, tools,        Any system that exhibits    │
│   memory, and a reasoning loop       autonomous, goal-directed   │
│                                      behavior — may involve one  │
│   One agent = one instance           or many agents              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Definitions

| Term | Definition |
|------|------------|
| **AI Agent** | A concrete, self-contained software entity powered by an LLM that can perceive its environment, reason about tasks, use tools, and take actions autonomously to achieve a specific goal. |
| **Agentic AI** | A broader design paradigm where AI systems exhibit **agent-like qualities** — autonomy, reasoning, tool use, planning — regardless of whether the system is a single agent, a multi-agent team, or an agentic workflow. |

### Key Differences

| Aspect | AI Agent | Agentic AI |
|--------|----------|------------|
| **What is it?** | A specific runtime entity | A design philosophy / system property |
| **Scope** | Single unit with defined tools & persona | Any system exhibiting autonomous behavior |
| **Granularity** | One agent = one LLM + tools + memory | Can be 1 agent, 10 agents, or a pipeline |
| **Focus** | Implementation — *how to build one agent* | Architecture — *how to design autonomous systems* |
| **Examples** | "Customer support agent", "code review agent" | "Agentic RAG", "agentic workflow", "agentic IDE" |
| **Analogy** | A single employee | A company's operating model |

### The Spectrum

```
                NOT AGENTIC                              FULLY AGENTIC
                ◄─────────────────────────────────────────────────────►

    Static         Agentic          Single           Multi-Agent      Autonomous
    Prompt         Workflow         Agent            System           System
    ──────         ────────         ──────           ────────         ──────────
    Fixed          LLM calls        Autonomous       Multiple         Self-improving
    input/output   chained with     loop with        agents           agents that
    no tools       routing &        tools,           collaborating    learn, adapt,
                   branching        memory,          & delegating     and evolve
                                    planning

    "Chatbot"      "Smart           "Travel          "Dev team:       "Research
                    pipeline"        assistant"       PM + Dev +       lab that
                                                      QA agents"       runs itself"

    NOT an agent   Uses agentic     IS an agent      IS agentic AI    IS agentic AI
                   patterns                          (multi-agent)    (advanced)
```

### Practical Examples

**AI Agent** (a concrete thing you deploy):
```python
# This IS an AI Agent — it has tools, a loop, and autonomy
agent = Agent(
    name="billing-support",
    system_prompt="You handle billing questions and refunds.",
    tools=[lookup_invoice, process_refund, send_email],
    model="gpt-4o-mini"
)
result = await agent.run("I was charged twice for my subscription")
```

**Agentic AI** (a system property / design choice):
```python
# This IS an Agentic AI system — multiple agents + orchestration
research_agent = Agent(name="researcher", tools=[web_search, arxiv_search])
analysis_agent = Agent(name="analyst", tools=[data_analysis, chart_gen])
writer_agent   = Agent(name="writer", tools=[document_gen, format_md])

# Agentic orchestration — agents collaborate autonomously
pipeline = AgenticWorkflow(
    agents=[research_agent, analysis_agent, writer_agent],
    strategy="hierarchical",  # manager delegates to specialists
    goal="Produce a market analysis report on AI chips"
)
report = await pipeline.execute()
```

**Agentic Workflow** (agentic without being a full agent):
```python
# This is AGENTIC (uses agentic patterns) but has NO single "agent"
# It's a pipeline with routing, parallelization, and reflection
result = await prompt_chain(
    extract_entities,     # Step 1: Extract
    classify_sentiment,   # Step 2: Classify
    generate_response,    # Step 3: Generate
    reflect_and_improve,  # Step 4: Self-critique
)
```

### When to Use Which Term

| Say **"AI Agent"** when... | Say **"Agentic AI"** when... |
|---------------------------|-----------------------------|
| Referring to a specific, named agent you built | Describing a system's overall architecture |
| Talking about capabilities of one entity | Talking about a design approach or philosophy |
| "Our billing agent handles refunds" | "We're building an agentic customer service platform" |
| Deploying a single autonomous unit | Designing a system of collaborating components |
| The agent has a clear persona and tool set | The system exhibits autonomy as an emergent property |

### TL;DR

> **AI Agent** = the actor (noun) — a specific thing you build and deploy.
>
> **Agentic AI** = the quality (adjective) — a property of systems that act autonomously.
>
> All AI Agents are examples of Agentic AI, but not all Agentic AI involves a single identifiable "agent."

---

## Agents vs. Traditional LLMs

### Traditional LLM (Stateless, Single-Turn)

```
User → [Prompt] → LLM → [Response] → Done
```

- No access to external data
- No ability to take actions
- No memory between calls
- Single input → single output

### AI Agent (Stateful, Multi-Turn Loop)

```
User → [Goal] → Agent:
  ├── Think: "What do I need?"
  ├── Act:   Call weather API
  ├── Observe: "72°F, sunny"
  ├── Think: "Now I can suggest outdoor activities"
  ├── Act:   Search events database
  ├── Observe: "3 events found"
  └── Respond: "Here are outdoor activities for today..."
```

### Side-by-Side Comparison

| Aspect | Traditional LLM | AI Agent |
|--------|-----------------|----------|
| **Interaction** | Single turn | Multi-turn loop |
| **External access** | None | Tools, APIs, databases |
| **State** | Stateless | Maintains memory |
| **Decision-making** | None | Autonomous reasoning |
| **Error handling** | None | Retry, fallback, escalate |
| **Output** | Text only | Text + actions + side effects |
| **Complexity** | Low | Medium to High |

---

## Core Components of an Agent

Every AI agent is built from these foundational components:

```
┌─────────────────────────────────────────────────────────┐
│                      AI AGENT                            │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  🧠 LLM Brain                    │    │
│  │  (Reasoning engine — GPT-4, Claude, etc.)       │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────┬───────────┼───────────┬──────────────┐    │
│  │          │           │           │              │    │
│  ▼          ▼           ▼           ▼              ▼    │
│ 📋         🔧          💾         🎯            🛡️    │
│ System     Tools       Memory     Planning      Guard-  │
│ Prompt     & APIs      Store      Engine        rails   │
│            │                                            │
│            ├── Web Search                               │
│            ├── Database                                  │
│            ├── Calculator                                │
│            ├── Code Executor                             │
│            └── File System                               │
└─────────────────────────────────────────────────────────┘
```

### 1. System Prompt (Persona & Instructions)

The system prompt defines **who** the agent is and **how** it should behave:

```python
SYSTEM_PROMPT = """You are a DevOps assistant agent.

Your capabilities:
- Check service health and metrics
- Analyze logs for errors
- Suggest and execute rollbacks
- Create incident reports

Rules:
- Always check service health before suggesting fixes
- Never execute destructive operations without confirmation
- Escalate to humans for severity-1 incidents
"""
```

### 2. Tools (Actions the Agent Can Take)

Tools are **functions** the agent can call to interact with the real world:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
]
```

### 3. Memory (Short-Term and Long-Term)

```
┌─────────────────────────────────────────┐
│              MEMORY LAYERS               │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Working Memory (Conversation)     │  │
│  │  Current messages and tool results │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Short-Term Memory (Session)       │  │
│  │  Summaries, entity tracking        │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Long-Term Memory (Persistent)     │  │
│  │  Vector DB, knowledge base         │  │
│  └────────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### 4. Planning Engine

The planning component breaks goals into actionable steps:

```
Goal: "Analyze our Q3 sales performance"

Plan:
  Step 1: Retrieve Q3 sales data from database
  Step 2: Calculate key metrics (revenue, growth, trends)
  Step 3: Compare with Q2 and last year's Q3
  Step 4: Identify top/bottom performing products
  Step 5: Generate executive summary with charts
```

### 5. Guardrails (Safety Boundaries)

```python
# Input guardrails — validate before processing
if contains_pii(user_input):
    return "I cannot process personal information"

# Output guardrails — validate before responding
if is_harmful(agent_response):
    return "I cannot provide that information"

# Action guardrails — validate before executing
if action.is_destructive and not user_confirmed:
    return "This action requires explicit confirmation"
```

---

## The Agent Loop — ReAct Pattern

The **ReAct** (Reasoning + Acting) pattern is the foundation of most modern agents:

```
┌─────────────────────────────────────────────────────┐
│                   ReAct LOOP                         │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │                 User Goal                     │   │
│  └──────────────────────┬───────────────────────┘   │
│                         │                            │
│                         ▼                            │
│  ┌──────────────────────────────────────────────┐   │
│  │  REASON: "What should I do next?"             │◄─┐│
│  │  Think about the goal, context, and tools     │  ││
│  └──────────────────────┬───────────────────────┘  ││
│                         │                           ││
│              ┌──────────┴──────────┐                ││
│              │                     │                ││
│              ▼                     ▼                ││
│     ┌──────────────┐    ┌──────────────────┐       ││
│     │ Final Answer  │    │ ACT: Call a tool  │       ││
│     │ (Done!)       │    │ or take action    │       ││
│     └──────────────┘    └────────┬─────────┘       ││
│                                  │                  ││
│                                  ▼                  ││
│                        ┌──────────────────┐         ││
│                        │ OBSERVE: Get      │─────────┘│
│                        │ tool result       │          │
│                        └──────────────────┘          │
└─────────────────────────────────────────────────────┘
```

### ReAct in Code

```python
import json
from openai import AsyncOpenAI

async def agent_loop(client, messages, tools, tool_functions):
    """Core ReAct loop — reason, act, observe, repeat."""
    
    while True:
        # REASON: Ask the LLM what to do next
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        # Check: Is the agent done?
        if message.tool_calls is None:
            return message.content  # Final answer
        
        # ACT + OBSERVE: Execute each tool call
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            # Execute the tool
            result = await tool_functions[func_name](**func_args)
            
            # Feed observation back
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
```

---

## Agentic Design Patterns

There are **8 foundational patterns** for building agentic systems:

### Pattern Overview

```
┌───────────────────────────────────────────────────────────┐
│              AGENTIC DESIGN PATTERNS                       │
│                                                            │
│  ORCHESTRATION          INTELLIGENCE        RESILIENCE     │
│  ─────────────          ────────────        ──────────     │
│  1. Prompt Chaining     4. Reflection       7. Guardrails  │
│  2. Routing             5. Tool Use         8. Human-in-   │
│  3. Parallelization     6. Planning            the-Loop    │
│                                                            │
│  COORDINATION                                              │
│  ────────────                                              │
│  Multi-Agent Systems (combines multiple patterns)          │
└───────────────────────────────────────────────────────────┘
```

### 1. Prompt Chaining
Break a complex task into a sequence of simpler LLM calls:
```
[Extract] → [Analyze] → [Generate] → [Format]
```
**Use when**: Tasks have clear sequential stages (content pipelines, data ETL).

### 2. Routing
Classify input and route to specialized handlers:
```
Input → [Classifier] → Route A (technical)
                      → Route B (billing)
                      → Route C (general)
```
**Use when**: Different input types need different processing strategies.

### 3. Parallelization
Run independent sub-tasks concurrently and merge results:
```
         ┌─ [Task A] ─┐
Input ───┼─ [Task B] ──┼─── [Merge] → Output
         └─ [Task C] ─┘
```
**Use when**: Sub-tasks are independent and speed matters.

### 4. Reflection
The agent critiques its own output and iterates:
```
[Generate] → [Critique] → [Improve] → [Critique] → [Final]
```
**Use when**: Quality matters more than speed (writing, code review).

### 5. Tool Use
Agent decides which external tools to call:
```
Agent → Decide tool → Execute → Observe → Decide next
```
**Use when**: Agent needs real-world data or side effects.

### 6. Planning
Break a goal into steps, execute, and re-plan:
```
Goal → [Plan] → [Execute Step 1] → [Re-evaluate] → [Execute Step 2] → ...
```
**Use when**: Complex, open-ended tasks with uncertain paths.

### 7. Multi-Agent
Multiple specialized agents collaborate:
```
[Manager Agent] → delegates to → [Research Agent]
                                → [Analysis Agent]
                                → [Writing Agent]
```
**Use when**: Task requires diverse expertise or separation of concerns.

### 8. Guardrails
Validate inputs, outputs, and actions at every stage:
```
Input → [Validate] → Agent → [Validate Output] → Response
                        ↓
                   [Validate Actions]
```
**Use when**: Always! Safety and reliability are non-negotiable.

---

## Building Your First Agent

### Step-by-Step: Weather + Activity Recommendation Agent

```python
import asyncio
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI()

# --- Define Tools ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. 'San Francisco'"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_activities",
            "description": "Search for activities in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "activity_type": {
                        "type": "string",
                        "enum": ["outdoor", "indoor", "both"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# --- Tool Implementations (Mock) ---
async def get_weather(location: str) -> str:
    """Simulate weather API call."""
    weather_data = {
        "San Francisco": {"temp": 65, "condition": "Foggy", "wind": "12mph"},
        "New York": {"temp": 78, "condition": "Sunny", "wind": "5mph"},
        "London": {"temp": 58, "condition": "Rainy", "wind": "15mph"},
    }
    data = weather_data.get(location, {"temp": 70, "condition": "Clear", "wind": "8mph"})
    return json.dumps({"location": location, **data})

async def search_activities(location: str, activity_type: str = "both") -> str:
    """Simulate activity search."""
    return json.dumps({
        "location": location,
        "activities": [
            {"name": "City Walking Tour", "type": "outdoor", "rating": 4.5},
            {"name": "Museum Visit", "type": "indoor", "rating": 4.8},
            {"name": "Food Tour", "type": "outdoor", "rating": 4.7},
        ]
    })

TOOL_MAP = {
    "get_weather": get_weather,
    "search_activities": search_activities,
}

# --- Agent Loop ---
async def run_agent(user_message: str):
    """Run the agent with the ReAct loop."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful travel assistant. "
                "Use the available tools to get weather and activity info, "
                "then give personalized recommendations."
            )
        },
        {"role": "user", "content": user_message}
    ]
    
    while True:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        
        msg = response.choices[0].message
        messages.append(msg)
        
        # No tool calls → agent is done
        if not msg.tool_calls:
            print(f"\n🤖 Agent: {msg.content}")
            return msg.content
        
        # Execute tool calls
        for tc in msg.tool_calls:
            func = TOOL_MAP[tc.function.name]
            args = json.loads(tc.function.arguments)
            print(f"  🔧 Calling {tc.function.name}({args})")
            
            result = await func(**args)
            print(f"  📊 Result: {result}")
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

# --- Run ---
if __name__ == "__main__":
    asyncio.run(run_agent("What should I do in San Francisco today?"))
```

---

## Tool Use — Giving Agents Superpowers

### Tool Definition Best Practices

| Practice | Why |
|----------|-----|
| **Clear descriptions** | The LLM reads descriptions to decide when to use a tool |
| **Typed parameters** | Helps the LLM generate correct arguments |
| **Required vs optional** | Mark required params to avoid missing data |
| **Error responses** | Return structured errors so the agent can retry |
| **Idempotent tools** | Safe to retry without side effects |

### Common Tool Categories

```
📊 DATA RETRIEVAL          🔧 ACTIONS                 🧮 COMPUTATION
─────────────────          ──────────                 ────────────
- Database queries         - Send email              - Calculator
- API calls                - Create ticket           - Code executor
- File reading             - Update record           - Data analysis
- Web search               - Deploy service          - Chart generation
- Knowledge base           - Webhook trigger         - ML inference
```

### Structured Error Handling in Tools

```python
async def get_stock_price(symbol: str) -> str:
    """Get stock price with proper error handling."""
    try:
        # Validate input
        if not symbol.isalpha() or len(symbol) > 5:
            return json.dumps({
                "error": True,
                "message": f"Invalid stock symbol: {symbol}",
                "suggestion": "Use a valid ticker like AAPL, GOOGL, MSFT"
            })
        
        # Call API (mock)
        price = {"AAPL": 175.50, "GOOGL": 140.25}.get(symbol)
        if price is None:
            return json.dumps({
                "error": True,
                "message": f"Symbol {symbol} not found"
            })
        
        return json.dumps({
            "symbol": symbol,
            "price": price,
            "currency": "USD"
        })
    
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Failed to fetch price: {str(e)}"
        })
```

---

## Memory and State Management

### Memory Architecture for Agents

```
┌──────────────────────────────────────────────────────────┐
│                    MEMORY SYSTEM                          │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  WORKING MEMORY                                    │  │
│  │  • Current conversation messages                   │  │
│  │  • Tool call results                               │  │
│  │  • In-context (limited by context window)          │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  SHORT-TERM MEMORY                                 │  │
│  │  • Conversation summaries                          │  │
│  │  • Entity extraction (names, dates, preferences)   │  │
│  │  • Session-scoped key-value store                  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  LONG-TERM MEMORY                                  │  │
│  │  • Vector database (ChromaDB, Pinecone)            │  │
│  │  • Semantic search over past interactions          │  │
│  │  • User profile / preference store                 │  │
│  │  • Persistent across sessions                      │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Implementing Conversation Memory

```python
class ConversationMemory:
    """Manages agent memory with automatic summarization."""
    
    def __init__(self, max_messages: int = 20):
        self.messages = []
        self.max_messages = max_messages
        self.summaries = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self._summarize_and_trim()
    
    async def _summarize_and_trim(self):
        """Summarize older messages to stay within context limits."""
        old_messages = self.messages[:10]
        summary = await self._generate_summary(old_messages)
        self.summaries.append(summary)
        self.messages = self.messages[10:]
    
    def get_context(self) -> list:
        """Get messages with summary prefix."""
        context = []
        if self.summaries:
            context.append({
                "role": "system",
                "content": f"Previous conversation summary: {' '.join(self.summaries)}"
            })
        context.extend(self.messages)
        return context
```

---

## Planning and Reasoning

### Planning Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| **Linear Planning** | Fixed sequence of steps | Simple pipelines |
| **Dynamic Re-planning** | Adjust plan after each step | Uncertain tasks |
| **Hierarchical Planning** | Break into sub-goals, then sub-steps | Complex tasks |
| **ReAct** | Interleave reasoning and acting | General purpose |

### Dynamic Planning Example

```python
PLANNING_PROMPT = """Given this goal: {goal}

Create a step-by-step plan. For each step, specify:
1. What to do
2. Which tool to use (if any)
3. What information is needed
4. What the expected output is

Current context:
{context}

Previously completed steps:
{completed_steps}

Respond with a JSON plan:
{{
    "steps": [
        {{
            "id": 1,
            "action": "description",
            "tool": "tool_name or null",
            "depends_on": [],
            "status": "pending"
        }}
    ]
}}
"""
```

### Reasoning Techniques

```
┌─────────────────────────────────────────────────────────┐
│               REASONING TECHNIQUES                       │
│                                                          │
│  Chain-of-Thought (CoT)                                  │
│  ─────────────────────                                   │
│  "Let me think step by step..."                          │
│  → Linear reasoning through a problem                    │
│                                                          │
│  Tree-of-Thought (ToT)                                   │
│  ─────────────────────                                   │
│  Explore multiple reasoning paths, evaluate, backtrack   │
│  → Better for problems with many possible approaches     │
│                                                          │
│  ReAct                                                   │
│  ─────                                                   │
│  Interleave reasoning with tool use                      │
│  → Standard for tool-using agents                        │
│                                                          │
│  Self-Consistency                                        │
│  ────────────────                                        │
│  Generate multiple solutions, take majority vote         │
│  → Higher accuracy for factual/mathematical tasks        │
│                                                          │
│  Reflexion                                               │
│  ─────────                                               │
│  Reflect on failures, build episodic memory              │
│  → Learning from mistakes across attempts                │
└─────────────────────────────────────────────────────────┘
```

---

## Multi-Agent Systems

### Coordination Patterns

```
PATTERN 1: MANAGER + WORKERS (Hierarchical)
─────────────────────────────────────────
                ┌──────────────┐
                │   Manager    │
                │   Agent      │
                └──────┬───────┘
           ┌───────────┼───────────┐
           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Research  │ │ Analysis │ │ Writing  │
    │ Agent     │ │ Agent    │ │ Agent    │
    └──────────┘ └──────────┘ └──────────┘


PATTERN 2: PIPELINE (Sequential)
────────────────────────────────
    ┌────────┐   ┌────────┐   ┌────────┐
    │Agent A │──▶│Agent B │──▶│Agent C │
    │Collect │   │Analyze │   │Report  │
    └────────┘   └────────┘   └────────┘


PATTERN 3: DEBATE (Adversarial)
───────────────────────────────
    ┌────────┐       ┌────────┐
    │Agent A │◄─────▶│Agent B │
    │ (Pro)  │       │ (Con)  │
    └────┬───┘       └────┬───┘
         └───────┬────────┘
                 ▼
          ┌──────────┐
          │  Judge   │
          │  Agent   │
          └──────────┘


PATTERN 4: SWARM (Emergent)
───────────────────────────
    ┌──────┐  ┌──────┐  ┌──────┐
    │  A   │──│  B   │──│  C   │
    └──┬───┘  └──┬───┘  └──┬───┘
       │         │         │
    ┌──┴───┐  ┌──┴───┐  ┌──┴───┐
    │  D   │──│  E   │──│  F   │
    └──────┘  └──────┘  └──────┘
    (Agents hand off tasks dynamically)
```

### Multi-Agent Code Example

```python
async def run_multi_agent_research(topic: str):
    """Hierarchical multi-agent system."""
    
    # Agent 1: Research Agent
    research = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a research specialist. Gather key facts and data."},
            {"role": "user", "content": f"Research this topic thoroughly: {topic}"}
        ]
    )
    research_data = research.choices[0].message.content
    
    # Agent 2: Analysis Agent
    analysis = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an analytical expert. Find patterns and insights."},
            {"role": "user", "content": f"Analyze this research:\n{research_data}"}
        ]
    )
    analysis_data = analysis.choices[0].message.content
    
    # Agent 3: Writer Agent
    report = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional writer. Create clear, engaging reports."},
            {"role": "user", "content": (
                f"Write an executive report based on:\n"
                f"Research: {research_data}\n"
                f"Analysis: {analysis_data}"
            )}
        ]
    )
    
    return report.choices[0].message.content
```

---

## Guardrails and Safety

### The Guardrails Framework

```
┌─────────────────────────────────────────────────────────┐
│                  GUARDRAILS LAYERS                        │
│                                                          │
│  Layer 1: INPUT VALIDATION                               │
│  ─────────────────────────                               │
│  • PII detection and redaction                           │
│  • Prompt injection detection                            │
│  • Topic classification (on/off topic)                   │
│  • Rate limiting and abuse prevention                    │
│                                                          │
│  Layer 2: PROCESSING GUARDRAILS                          │
│  ──────────────────────────────                          │
│  • Tool call validation (authorized tools only)          │
│  • Parameter bounds checking                             │
│  • Budget/token limits                                   │
│  • Timeout enforcement                                   │
│                                                          │
│  Layer 3: OUTPUT VALIDATION                              │
│  ──────────────────────────                              │
│  • Content safety filtering                              │
│  • Factuality checks                                     │
│  • Format compliance                                     │
│  • Sensitive data leakage prevention                     │
│                                                          │
│  Layer 4: ACTION GUARDRAILS                              │
│  ──────────────────────────                              │
│  • Destructive action confirmation                       │
│  • Scope limitation (what agent CAN'T do)               │
│  • Audit logging                                         │
│  • Human approval gates                                  │
└─────────────────────────────────────────────────────────┘
```

### Practical Guardrails

```python
class AgentGuardrails:
    """Safety wrapper for agent operations."""
    
    MAX_ITERATIONS = 15
    MAX_TOKENS_PER_RUN = 50000
    BLOCKED_TOPICS = ["illegal", "harmful", "personal_data"]
    
    @staticmethod
    def check_input(user_input: str) -> tuple[bool, str]:
        """Validate user input before processing."""
        # Check for prompt injection patterns
        injection_patterns = [
            "ignore previous instructions",
            "you are now",
            "forget your system prompt",
        ]
        for pattern in injection_patterns:
            if pattern.lower() in user_input.lower():
                return False, "Potential prompt injection detected"
        
        return True, "Input valid"
    
    @staticmethod
    def check_tool_call(tool_name: str, args: dict) -> tuple[bool, str]:
        """Validate tool calls before execution."""
        # Example: prevent unauthorized operations
        dangerous_tools = ["delete_database", "execute_sql_raw"]
        if tool_name in dangerous_tools:
            return False, f"Tool '{tool_name}' requires admin approval"
        
        return True, "Tool call authorized"
```

---

## Evaluation and Observability

### What to Measure

| Metric | Description | How to Measure |
|--------|-------------|----------------|
| **Task completion rate** | % of tasks completed successfully | Track success/failure per run |
| **Tool accuracy** | Correct tool selected for the task | Compare tool choice vs. ideal |
| **Reasoning quality** | Logic soundness of agent thinking | LLM-as-judge scoring |
| **Latency** | Time from request to final response | Timestamp tracking |
| **Token efficiency** | Tokens used per successful task | Token counting per run |
| **Error recovery** | How well agent handles failures | Inject failures, measure recovery |
| **Safety compliance** | Guardrail trigger rate | Count blocked/modified outputs |

### Observability Stack

```
┌─────────────────────────────────────────────┐
│              AGENT OBSERVABILITY              │
│                                               │
│  TRACING                                      │
│  ────────                                     │
│  • Every LLM call with input/output           │
│  • Tool calls with arguments and results      │
│  • Decision points and reasoning              │
│  • Timing for each step                       │
│                                               │
│  LOGGING                                      │
│  ───────                                      │
│  • Structured JSON logs                       │
│  • Correlation IDs across agent steps          │
│  • Error and exception tracking               │
│                                               │
│  METRICS                                      │
│  ───────                                      │
│  • Token usage per run                        │
│  • Latency percentiles (p50, p95, p99)        │
│  • Success/failure rates                      │
│  • Tool call frequency                        │
│                                               │
│  TOOLS: OpenTelemetry, LangSmith, Arize,      │
│         Weights & Biases, custom dashboards    │
└─────────────────────────────────────────────┘
```

---

## Agentic AI Frameworks

### Framework Comparison

| Framework | Language | Best For | Key Feature |
|-----------|----------|----------|-------------|
| **OpenAI Agents SDK** | Python | Production agents | Native tool calling, handoffs |
| **LangChain / LangGraph** | Python, JS | Complex workflows | Graph-based orchestration |
| **CrewAI** | Python | Multi-agent teams | Role-based agents |
| **AutoGen** | Python | Research, conversations | Multi-agent conversations |
| **Semantic Kernel** | C#, Python | Enterprise | Microsoft ecosystem integration |
| **Haystack** | Python | RAG + agents | Pipeline-based |
| **Phidata** | Python | Quick prototyping | Minimal boilerplate |

### Choosing a Framework

```
Do you need multi-agent?
  │
  ├── NO → Single agent?
  │         ├── Simple tool use → OpenAI SDK directly
  │         └── Complex workflow → LangGraph
  │
  └── YES → What kind?
            ├── Role-based team → CrewAI
            ├── Conversation-based → AutoGen
            ├── Graph workflows → LangGraph
            └── Enterprise/Microsoft → Semantic Kernel
```

---

## Production Considerations

### Checklist for Production Agents

```
PRE-LAUNCH
□ Rate limiting and token budgets configured
□ All tools have proper error handling
□ Input/output guardrails tested
□ Timeout and max-iteration limits set
□ Fallback responses for failures
□ Logging and tracing enabled
□ PII handling and data privacy reviewed

MONITORING
□ Alert on high error rates
□ Alert on unusual token consumption
□ Track task completion rates
□ Monitor latency percentiles
□ Review guardrail trigger frequency

SECURITY
□ API keys in environment variables (never hardcoded)
□ Tool permissions are principle-of-least-privilege
□ Prompt injection defenses active
□ Output sanitization enabled
□ Audit trail for all agent actions
```

### Cost Optimization

```
┌─────────────────────────────────────────────┐
│          COST OPTIMIZATION TIPS              │
│                                              │
│  1. Use smaller models for routing/classify  │
│     (gpt-4o-mini for triage, gpt-4o for     │
│      complex reasoning)                      │
│                                              │
│  2. Cache tool results                       │
│     (avoid repeated API calls for same data) │
│                                              │
│  3. Set max_tokens on completions            │
│     (prevent runaway generation)             │
│                                              │
│  4. Implement early termination              │
│     (stop if agent is looping)               │
│                                              │
│  5. Batch independent operations             │
│     (parallel tool calls when possible)      │
│                                              │
│  6. Summarize context instead of full history│
│     (compress long conversations)            │
└─────────────────────────────────────────────┘
```

---

## Hands-On Exercises

### Exercise 1: Basic ReAct Agent
Build an agent with 3 tools (calculator, web search mock, note-taking) that can answer questions requiring multiple tool calls.

### Exercise 2: Reflection Agent
Build an agent that writes code, tests it, reviews its own output, and iterates until quality criteria are met.

### Exercise 3: Multi-Agent Pipeline
Create a 3-agent pipeline: Researcher → Analyst → Writer that collaborates to produce a market analysis report.

### Exercise 4: Guarded Agent
Take your Exercise 1 agent and add input validation, output safety checks, prompt injection detection, and action confirmation gates.

### Exercise 5: Agent with Memory
Build an agent that remembers user preferences across multiple queries in a session using a simple memory store.

---

## 📚 Further Reading

- [Anthropic's Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Agent Documentation](https://python.langchain.com/docs/modules/agents/)
- [Agentic Design Patterns (Andrew Ng)](https://www.deeplearning.ai/the-batch/agentic-design-patterns-part-1/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)

---

## 🔗 Related Materials

| Resource | Link |
|----------|------|
| Agent Patterns Deep Dive | [04-agent-patterns.md](./04-agent-patterns.md) |
| Agent Use Cases | [05-agent-use-cases.md](./05-agent-use-cases.md) |
| Agentic Design Patterns (21 patterns) | [08-agentic-patterns/](../08-agentic-patterns/README.md) |
| MCP Fundamentals | [09-mcp/01-mcp-fundamentals.md](../09-mcp/01-mcp-fundamentals.md) |
| Working Examples | [examples/weather_agent/](../examples/weather_agent/) |
