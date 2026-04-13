# Chapter 7: Multi-Agent

> Multiple specialised agents collaborate, each owning a distinct role.

## 🧠 Concept

Instead of one agent doing everything, **Multi-Agent** systems split work across specialists. A coordinator decides who works on what, and agents can pass messages to each other.

```
┌─────────────────────────────────────────────────────┐
│                  MULTI-AGENT SYSTEM                   │
│                                                       │
│  ┌─────────────┐                                      │
│  │ COORDINATOR  │──────────┐                          │
│  └──────┬──────┘           │                          │
│         │            ┌─────┴─────┐                    │
│    ┌────┴────┐       │  Agent C  │                    │
│    ▼         ▼       │ (Editor)  │                    │
│  Agent A  Agent B    └───────────┘                    │
│ (Research)(Writer)                                    │
│    │         │             ▲                           │
│    └────┬────┘             │                          │
│         └──────────────────┘                          │
│              (pass work along)                        │
└─────────────────────────────────────────────────────┘
```

## Common Topologies

| Topology | Description | Use Case |
|----------|-------------|----------|
| **Hub-and-spoke** | Coordinator assigns work | Project management |
| **Pipeline** | Agent A → B → C | Content creation |
| **Debate** | Agents argue → consensus | Decision-making |
| **Swarm** | Agents self-organise | Exploration |

## Code Example — Article Writing Team

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Agent:
    """A simple agent with a role and system prompt."""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def run(self, task: str) -> str:
        print(f"  🤖 {self.name} working...")
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": task},
            ],
        )
        result = r.choices[0].message.content
        print(f"  ✅ {self.name} done.\n")
        return result


# ── Define Agents ────────────────────────────────────────

researcher = Agent(
    "Researcher",
    "You are a research specialist. Given a topic, find 5-7 key facts, "
    "statistics, and insights. Cite sources where possible.",
)

writer = Agent(
    "Writer",
    "You are a skilled article writer. Given research notes, write a "
    "well-structured 500-word article. Use engaging language.",
)

editor = Agent(
    "Editor",
    "You are a senior editor. Review the article for clarity, grammar, "
    "factual accuracy, and flow. Fix issues and return the polished version.",
)

fact_checker = Agent(
    "Fact Checker",
    "You are a fact-checker. Review the article and flag any claims "
    "that seem inaccurate or unsupported. List issues found.",
)


# ── Coordinator ──────────────────────────────────────────

def coordinate(topic: str) -> str:
    print(f"📝 Topic: {topic}\n")

    # Step 1: Research
    research = researcher.run(f"Research this topic thoroughly: {topic}")

    # Step 2: Write (uses research)
    draft = writer.run(
        f"Write an article on: {topic}\n\nResearch notes:\n{research}"
    )

    # Step 3: Fact-check and edit in parallel-ish (sequential here)
    issues = fact_checker.run(f"Fact-check this article:\n\n{draft}")

    # Step 4: Final edit incorporating fact-check results
    final = editor.run(
        f"Edit this article. Also address these fact-check issues:\n\n"
        f"ISSUES:\n{issues}\n\nARTICLE:\n{draft}"
    )

    return final


if __name__ == "__main__":
    article = coordinate("The impact of AI agents on software development in 2026")
    print("=" * 60)
    print(article)
```

## Communication Patterns

```
Direct:    Agent A ──message──▶ Agent B
Broadcast: Agent A ──message──▶ [All Agents]
Blackboard: Agent A ──write──▶ [Shared State] ◀──read── Agent B
Mediator:  Agent A ──▶ [Coordinator] ──▶ Agent B
```

## Key Design Decisions

1. **How many agents?** — Start with 2-3. Only add more when a role is clearly distinct.
2. **Communication** — Direct message passing is simplest. Shared memory adds complexity.
3. **Conflict resolution** — When agents disagree, the coordinator decides or uses voting.
4. **Termination** — Define clear "done" conditions to avoid infinite loops.

## 🏋️ Practice

→ [Exercise: Multi-Agent](../exercises/agentic/07_multi_agent.py)
