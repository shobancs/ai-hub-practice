# Chapter 5: Tool Use

> Give agents the ability to call external functions, APIs, and services.

## 🧠 Concept

An LLM by itself can only generate text. **Tool Use** extends it with callable functions — search engines, databases, calculators, APIs — turning it into an agent that can *act* in the world.

```
┌─────────────────────────────────────────────┐
│                AGENT + TOOLS                 │
│                                              │
│  User ──▶ [LLM Brain]                       │
│                │                             │
│          Decide: talk or use a tool?         │
│                │                             │
│       ┌────────┴────────┐                    │
│       ▼                 ▼                    │
│   Respond          Call Tool                 │
│   directly          │                        │
│                      ▼                       │
│               ┌─────────────┐                │
│               │ Tool Result │                │
│               └──────┬──────┘                │
│                      ▼                       │
│              Feed result back to LLM         │
│              (loop continues)                │
└─────────────────────────────────────────────┘
```

## The Tool-Use Loop (OpenAI Function Calling)

```
1. Send messages + tool definitions to API
2. Model returns: tool_calls (or final text)
3. Execute each tool call locally
4. Append tool results to messages
5. Send updated messages back → goto 2
```

## Code Example — Calculator + Web Search Agent

```python
import json, os, math
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Tool Definitions ─────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression. Supports +, -, *, /, **, sqrt, sin, cos, log.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression (e.g. '2**10 + sqrt(144)')"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get today's date.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unit_convert",
            "description": "Convert between units (km/miles, kg/lbs, C/F, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "from_unit": {"type": "string"},
                    "to_unit": {"type": "string"},
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        },
    },
]


# ── Tool Implementations ─────────────────────────────────

def calculate(expression: str) -> str:
    """Safe math evaluation."""
    allowed = {
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "tan": math.tan, "log": math.log, "pi": math.pi, "e": math.e,
        "abs": abs, "round": round,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"
    except Exception as ex:
        return f"Error: {ex}"


def get_current_date() -> str:
    from datetime import date
    return f"Today is {date.today().isoformat()}"


def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    conversions = {
        ("km", "miles"): lambda v: v * 0.621371,
        ("miles", "km"): lambda v: v * 1.60934,
        ("kg", "lbs"): lambda v: v * 2.20462,
        ("lbs", "kg"): lambda v: v * 0.453592,
        ("c", "f"): lambda v: v * 9/5 + 32,
        ("f", "c"): lambda v: (v - 32) * 5/9,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.2f} {to_unit}"
    return f"Unknown conversion: {from_unit} → {to_unit}"


TOOL_MAP = {
    "calculate": calculate,
    "get_current_date": get_current_date,
    "unit_convert": unit_convert,
}


# ── Agent Loop ───────────────────────────────────────────

def run_agent(query: str, max_turns: int = 5) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools. Use them when needed."},
        {"role": "user", "content": query},
    ]

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg.model_dump())

        if not msg.tool_calls:
            return msg.content

        for tc in msg.tool_calls:
            fn = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"  🔧 {fn}({args})")
            result = TOOL_MAP[fn](**args)
            print(f"  📋 {result}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return "Max turns reached."


if __name__ == "__main__":
    queries = [
        "What is 2^10 + sqrt(144)?",
        "Convert 100 km to miles",
        "What's today's date, and how many days until 2027?",
    ]
    for q in queries:
        print(f"\n{'='*50}\n📩 {q}")
        print(f"💬 {run_agent(q)}")
```

## Best Practices

1. **Clear tool descriptions** — The model decides *which* tool to call based on descriptions. Be precise.
2. **Required vs. optional params** — Mark parameters `required` only when truly necessary.
3. **Return strings** — Tool results must be strings (the model reads text, not objects).
4. **Error messages** — Return helpful error strings so the model can recover.

## 🏋️ Practice

→ [Exercise: Tool Use](../exercises/agentic/05_tool_use.py)
