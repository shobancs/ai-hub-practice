# 🔬 Research Assistant Agent — AI-Powered Research with ReAct Pattern

An intelligent research assistant that **autonomously searches, reads, takes notes, and synthesizes findings** into a structured research brief — demonstrating the core agentic AI patterns.

> **Learning Focus**: ReAct loop, tool use (function calling), session memory, and planning via system prompt.

---

## Features

| Feature | Description |
|---|---|
| 🔍 **Web Search** | Searches for information across multiple query angles |
| 📖 **Webpage Reading** | Reads and extracts content from discovered sources |
| 📝 **Note-Taking** | Stores structured notes with tags and source attribution |
| 🧮 **Calculator** | Evaluates mathematical expressions when needed |
| 📄 **Research Brief** | Compiles findings into a well-organized summary |
| 💬 **Follow-Up Q&A** | Ask follow-up questions using session context |
| 📊 **Session Stats** | Track searches, sources, and notes per session |

---

## Architecture

```
research_agent/
├── main.py                     # Entry point — CLI args & bootstrap
├── requirements.txt            # Python dependencies
├── README.md                   # You are here
│
├── core/
│   ├── config.py               # Configuration (@dataclass + env vars)
│   ├── models.py               # Data models (Note, SearchResult, Session)
│   ├── tools.py                # Tool implementations (simulated APIs)
│   └── agent.py                # ReAct loop orchestrator + tool definitions
│
└── interfaces/
    └── cli.py                  # Rich terminal UI (menu, research, notes)
```

### ReAct Loop Flow

```
User Query: "Research agentic AI"
     │
     ▼
┌─────────────────────────────────────────────────┐
│  REASON: "I should search for agentic AI first" │◄──┐
└──────────────────────┬──────────────────────────┘   │
                       │                               │
                       ▼                               │
              ┌─────────────────┐                      │
              │ ACT: search_web │                      │
              │ "agentic AI"    │                      │
              └────────┬────────┘                      │
                       │                               │
                       ▼                               │
              ┌─────────────────┐                      │
              │ OBSERVE: 3 results                     │
              │ returned        │──────────────────────┘
              └─────────────────┘
                    ...repeats...

              ┌─────────────────┐
              │ REASON: "I have │
              │ enough notes to │
              │ write a brief"  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────────┐
              │ 📄 Final Research   │
              │    Brief            │
              └─────────────────────┘
```

---

## Agentic Patterns Demonstrated

| Pattern | How It's Used |
|---------|---------------|
| **ReAct** | Agent reasons about what to do, acts (calls tools), observes results, and loops |
| **Tool Use** | 5 tools via OpenAI function calling: search, read, note, get_notes, calculate |
| **Memory** | `ResearchSession` accumulates notes, searches, and sources across iterations |
| **Planning** | System prompt encodes a research methodology (search → read → note → synthesize) |

---

## Quick Start

### 1. Install dependencies

```bash
cd GenAI/examples/research_agent
pip install -r requirements.txt
```

### 2. Set your API key

```bash
export OPENAI_API_KEY="sk-..."
# Or add to GenAI/.env
```

### 3. Run

```bash
# Interactive menu
python main.py

# Direct research
python main.py --research "What is agentic AI?"

# Verbose mode (see all tool calls in logs)
python main.py --research "machine learning basics" --verbose
```

---

## Example Session

```
🔬 AI Research Assistant Agent
   Powered by OpenAI function-calling + ReAct pattern

Choose an option:
  1  Research a new topic
  2  Ask a follow-up question
  3  View research notes
  4  View session stats
  q  Quit

› 1

Enter research topic: agentic AI

┌─ Researching: agentic AI ────────────────────────────────┐
│ Agent is working — watch the tool calls below             │
└──────────────────────────────────────────────────────────┘

  🔍  search_web      query="agentic AI overview and definition"
  🔍  search_web      query="ReAct pattern AI agents"
  📖  read_webpage     url="https://www.anthropic.com/..."
  📝  save_note        "Agentic AI refers to systems that..."
  📝  save_note        "The ReAct pattern interleaves..."
  📝  save_note        "Key patterns: prompt chaining, routing..."
  📋  get_notes
  
┌─ 📄 Research Brief ─────────────────────────────────────┐
│                                                          │
│  ## Topic Overview                                       │
│  Agentic AI refers to AI systems that can autonomously   │
│  perceive, reason, plan, and act to achieve goals...     │
│                                                          │
│  ## Key Findings                                         │
│  1. Agentic AI goes beyond simple Q&A to multi-step...   │
│  2. The ReAct pattern is foundational — it interleaves...│
│  3. Eight agentic patterns form the design toolkit...    │
│                                                          │
│  ## Sources                                              │
│  - Anthropic Research: Building Effective Agents         │
│  - arXiv: ReAct — Synergizing Reasoning and Acting      │
│  - Sequoia Capital: The Rise of Agentic AI              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Key Code Concepts

### 1. Tool Definitions (OpenAI Function Calling Schema)

```python
# From core/agent.py — tools follow the OpenAI JSON schema format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information on a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
    # ... more tools
]
```

### 2. The ReAct Loop

```python
# From core/agent.py — the core reasoning-acting loop
async def research(self, query: str) -> str:
    while iteration < self.config.max_iterations:
        # REASON: Ask the LLM what to do next
        response = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=messages,
            tools=TOOLS,
        )
        message = response.choices[0].message

        # Done? Return final answer
        if not message.tool_calls:
            return message.content

        # ACT + OBSERVE: Execute tools, feed results back
        for tool_call in message.tool_calls:
            result = await self._tool_map[tool_call.function.name](**args)
            messages.append({"role": "tool", "content": result})
```

### 3. Session Memory

```python
# From core/models.py — notes persist across the agent loop
session = ResearchSession(topic="agentic AI")
session.add_note("ReAct interleaves reasoning and acting", tags=["pattern"])
session.add_note("8 agentic design patterns", tags=["architecture"])
print(session.get_notes_summary())
```

---

## Extending This Agent

| Extension | How |
|-----------|-----|
| **Real web search** | Replace `tools.search_web` with Tavily or SerpAPI |
| **Real webpage reading** | Use `requests` + `BeautifulSoup` in `tools.read_webpage` |
| **Persistent memory** | Save notes to SQLite or a JSON file between sessions |
| **Export to Markdown** | Add a `write_report` tool that writes to a `.md` file |
| **Add more tools** | Wikipedia API, arXiv API, Notion API, etc. |
| **Multi-agent** | Add a "reviewer" agent that critiques the research brief |

---

## Related Materials

- [Agentic AI Tutorial](../../05-advanced/02-agentic-ai-tutorial.md) — comprehensive theory guide
- [Weather Agent](../weather_agent/) — production-grade agent with real APIs
- [Agentic Patterns](../../08-agentic-patterns/) — all 8 patterns explained
