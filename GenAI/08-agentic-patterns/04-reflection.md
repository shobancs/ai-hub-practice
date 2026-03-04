# Chapter 4: Reflection

> Have the agent critique its own output and iteratively improve it.

## 🧠 Concept

The **Reflection** pattern adds a self-review loop. After generating an output, a separate "critic" prompt evaluates it, identifies weaknesses, and the generator tries again — repeating until quality is acceptable.

```
┌──────────────┐     ┌──────────────┐
│  GENERATOR   │────▶│   CRITIC     │
│  (Produce)   │◀────│  (Evaluate)  │
└──────────────┘     └──────────────┘
       │                    │
       │   Loop until       │
       │   quality ≥ threshold
       ▼
┌──────────────┐
│ FINAL OUTPUT │
└──────────────┘
```

## Why Reflection?

| Benefit | Explanation |
|---------|-------------|
| **Higher quality** | Multiple passes catch mistakes |
| **Self-improving** | No human reviewer needed |
| **Controllable** | Set explicit quality criteria |
| **Transparent** | Each critique is visible for debugging |

## When to Use

- Code generation (generate → review → fix)
- Writing (draft → critique → revise)
- Data extraction (extract → validate → correct)
- Any task where quality varies and can be scored

## Architecture

```
┌────────────────────────────────────────────────┐
│              REFLECTION LOOP                    │
│                                                 │
│  Input ──▶ [Generator] ──▶ Draft                │
│                              │                  │
│                              ▼                  │
│                         [Critic] ──▶ Feedback   │
│                              │                  │
│                         Score ≥ 8?              │
│                          /     \                │
│                        YES      NO              │
│                         │       │               │
│                      Output   Back to Generator │
│                              (with feedback)    │
└────────────────────────────────────────────────┘
```

## Code Example — Self-Improving Code Writer

```python
import os, json
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


# ── Generator ────────────────────────────────────────────

def generate_code(task: str, feedback: str = "") -> str:
    context = f"Task: {task}"
    if feedback:
        context += f"\n\nPrevious feedback to address:\n{feedback}"

    return call_llm(
        "You are an expert Python developer. Write clean, well-documented "
        "code. Include type hints and docstrings. Return ONLY the code.",
        context,
    )


# ── Critic ───────────────────────────────────────────────

def critique_code(task: str, code: str) -> dict:
    result = call_llm(
        "You are a senior code reviewer. Evaluate the code on these criteria:\n"
        "1. Correctness — Does it solve the task?\n"
        "2. Readability — Clean naming, docstrings, comments?\n"
        "3. Edge cases — Are edge cases handled?\n"
        "4. Efficiency — Any obvious performance issues?\n\n"
        "Respond in this exact JSON format:\n"
        '{"score": <1-10>, "issues": ["issue 1", ...], "suggestions": ["fix 1", ...]}',
        f"Task: {task}\n\nCode:\n```python\n{code}\n```",
    )
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"score": 5, "issues": ["Could not parse review"], "suggestions": []}


# ── Reflection Loop ──────────────────────────────────────

def reflect_and_improve(task: str, max_rounds: int = 3, threshold: int = 8) -> str:
    feedback = ""

    for round_num in range(1, max_rounds + 1):
        print(f"\n🔄 Round {round_num}")

        # Generate
        code = generate_code(task, feedback)
        print(f"  ✍️  Code generated ({len(code)} chars)")

        # Critique
        review = critique_code(task, code)
        score = review.get("score", 0)
        print(f"  🔍 Score: {score}/10")

        if review.get("issues"):
            for issue in review["issues"]:
                print(f"     ⚠️  {issue}")

        # Good enough?
        if score >= threshold:
            print(f"  ✅ Quality threshold met!")
            return code

        # Build feedback for next round
        feedback = (
            f"Score: {score}/10\n"
            f"Issues: {', '.join(review.get('issues', []))}\n"
            f"Suggestions: {', '.join(review.get('suggestions', []))}"
        )

    print(f"  ⏱️  Max rounds reached. Returning best effort.")
    return code


if __name__ == "__main__":
    task = "Write a Python function that merges two sorted lists into one sorted list without using built-in sort."
    final_code = reflect_and_improve(task)
    print("\n" + "=" * 50)
    print("FINAL CODE:")
    print(final_code)
```

## Key Design Decisions

1. **Same LLM vs. different LLMs** — Using a stronger model as critic and cheaper model as generator can save cost.
2. **Structured feedback** — JSON scores make it easy to automate the "good enough?" decision.
3. **Max iterations** — Always cap the loop to prevent infinite retries.
4. **What to feed back** — Only pass the *critique*, not the full history, to keep prompts focused.

## Pattern Variants

| Variant | Description |
|---------|-------------|
| **Self-reflection** | Same LLM generates and critiques |
| **Cross-reflection** | Different LLM (or model) critiques |
| **Rubric-based** | Critic scores against a fixed rubric |
| **Test-driven** | Critic runs actual tests on generated code |

## 🏋️ Practice

→ [Exercise: Reflection](../exercises/agentic/04_reflection.py)
