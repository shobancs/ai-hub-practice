# Agentic Design Patterns — Comprehensive Practice Guide

> Based on *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems* by Antonio Gulli

## 🎯 Purpose

This module is your **hands-on practice companion** for mastering the 21 core agentic design patterns. Each pattern includes concepts, architecture diagrams, runnable code, and exercises.

---

## 📖 Table of Contents

### Part One — Core Patterns (Chapters 1–7)
| # | Pattern | Tutorial | Exercise |
|---|---------|----------|----------|
| 1 | [Prompt Chaining](./01-prompt-chaining.md) | Decompose complex tasks into chained LLM calls | [Exercise](../exercises/agentic/01_prompt_chaining.py) |
| 2 | [Routing](./02-routing.md) | Classify input and route to specialised handlers | [Exercise](../exercises/agentic/02_routing.py) |
| 3 | [Parallelization](./03-parallelization.md) | Run independent sub-tasks concurrently | [Exercise](../exercises/agentic/03_parallelization.py) |
| 4 | [Reflection](./04-reflection.md) | Self-critique and iterative improvement | [Exercise](../exercises/agentic/04_reflection.py) |
| 5 | [Tool Use](./05-tool-use.md) | Equip agents with callable functions | [Exercise](../exercises/agentic/05_tool_use.py) |
| 6 | [Planning](./06-planning.md) | Break goals into steps, execute, re-plan | [Exercise](../exercises/agentic/06_planning.py) |
| 7 | [Multi-Agent](./07-multi-agent.md) | Coordinate multiple specialised agents | [Exercise](../exercises/agentic/07_multi_agent.py) |

### Part Two — Memory & Adaptation (Chapters 8–11)
| # | Pattern | Tutorial | Exercise |
|---|---------|----------|----------|
| 8 | [Memory Management](./08-memory-management.md) | Short-term, long-term & retrieval-augmented memory | — |
| 9 | [Learning and Adaptation](./09-learning-adaptation.md) | In-context learning, feedback loops | — |
| 10 | [Model Context Protocol (MCP)](./10-mcp.md) | Standardised tool/resource interface | — |
| 11 | [Goal Setting and Monitoring](./11-goal-monitoring.md) | Track progress, detect stalls, adjust plans | — |

### Part Three — Resilience (Chapters 12–14)
| # | Pattern | Tutorial | Exercise |
|---|---------|----------|----------|
| 12 | [Exception Handling & Recovery](./12-exception-handling.md) | Graceful failure, fallback strategies | — |
| 13 | [Human-in-the-Loop](./13-human-in-the-loop.md) | Approval gates, escalation, feedback | — |
| 14 | [Knowledge Retrieval (RAG)](./14-rag-pattern.md) | Retrieve → Augment → Generate | — |

### Part Four — Advanced (Chapters 15–21)
| # | Pattern | Tutorial | Exercise |
|---|---------|----------|----------|
| 15 | [Inter-Agent Communication (A2A)](./15-a2a.md) | Agent-to-agent messaging protocols | — |
| 16 | [Resource-Aware Optimization](./16-resource-optimization.md) | Token budgets, model selection, caching | — |
| 17 | [Reasoning Techniques](./17-reasoning.md) | CoT, ToT, ReAct, self-consistency | — |
| 18 | [Guardrails & Safety](./18-guardrails.md) | Input/output validation, content filtering | [Exercise](../exercises/agentic/08_guardrails.py) |
| 19 | [Evaluation and Monitoring](./19-evaluation.md) | Metrics, logging, observability | — |
| 20 | [Prioritization](./20-prioritization.md) | Task ranking, urgency, resource allocation | — |
| 21 | [Exploration and Discovery](./21-exploration.md) | Autonomous research, curiosity-driven agents | — |

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install openai python-dotenv asyncio

# 2. Set your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Run any pattern exercise
python exercises/agentic/01_prompt_chaining.py
```

## 🗺️ Pattern Decision Flowchart

```
                        ┌─────────────────────┐
                        │   What's your task?  │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼               ▼
             Simple task    Multi-step task   Multi-domain task
                    │              │               │
                    ▼              ▼               ▼
             ┌──────────┐  ┌──────────────┐  ┌──────────────┐
             │ Tool Use  │  │ Steps depend │  │ Steps are    │
             │ (Ch. 5)   │  │ on each      │  │ independent? │
             └──────────┘  │ other?        │  └───────┬──────┘
                           └──────┬───────┘          │
                                  │            ┌─────┴─────┐
                           ┌──────┴──────┐     ▼           ▼
                           ▼             ▼   Parallel   Routing
                     Prompt Chaining  Planning (Ch. 3)  (Ch. 2)
                       (Ch. 1)       (Ch. 6)
                                                │
                                   Need quality check?
                                         │
                                    ┌────┴────┐
                                    ▼         ▼
                               Reflection  Human-in-Loop
                                (Ch. 4)     (Ch. 13)
```

## 📚 Learning Path

| Week | Focus | Patterns |
|------|-------|----------|
| 1 | **Foundation** | Prompt Chaining → Routing → Tool Use |
| 2 | **Orchestration** | Parallelization → Planning → Multi-Agent |
| 3 | **Quality** | Reflection → Guardrails → Human-in-the-Loop |
| 4 | **Production** | Memory → RAG → Evaluation → MCP |
