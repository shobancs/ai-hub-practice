"""
Simulated tools for the Research Assistant Agent.

These simulate real APIs so the agent can be practised without
external dependencies.  Swap in real implementations (e.g. Tavily,
Wikipedia API, Notion API) when ready for production.
"""

import json
import random
from typing import Any


# ─────────────────────────────────────────────────────────────────────
# Simulated knowledge base — rich enough for the agent to reason over
# ─────────────────────────────────────────────────────────────────────

_KNOWLEDGE_BASE: dict[str, list[dict]] = {
    "artificial intelligence": [
        {
            "title": "What is Artificial Intelligence? — IBM",
            "url": "https://www.ibm.com/topics/artificial-intelligence",
            "snippet": "Artificial intelligence (AI) is technology that enables computers and machines to simulate human learning, comprehension, problem solving, decision making, creativity and autonomy.",
        },
        {
            "title": "History of AI — Stanford Encyclopedia of Philosophy",
            "url": "https://plato.stanford.edu/entries/artificial-intelligence/",
            "snippet": "AI research began at a workshop at Dartmouth College in 1956. Early pioneers include Alan Turing, John McCarthy, Marvin Minsky, and Claude Shannon.",
        },
        {
            "title": "Types of AI: Narrow, General, and Super Intelligence",
            "url": "https://arxiv.org/abs/2301.10001",
            "snippet": "Narrow AI (ANI) performs specific tasks. Artificial General Intelligence (AGI) would match human-level reasoning across domains. Superintelligence (ASI) would surpass human intelligence.",
        },
    ],
    "large language models": [
        {
            "title": "Language Models are Few-Shot Learners — OpenAI",
            "url": "https://arxiv.org/abs/2005.14165",
            "snippet": "GPT-3 demonstrated that scaling language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches.",
        },
        {
            "title": "Attention Is All You Need — Google Brain",
            "url": "https://arxiv.org/abs/1706.03762",
            "snippet": "The Transformer architecture relies entirely on self-attention mechanisms, dispensing with recurrence and convolutions. It achieves state-of-the-art results in machine translation.",
        },
        {
            "title": "A Survey of Large Language Models — 2024",
            "url": "https://arxiv.org/abs/2303.18223",
            "snippet": "LLMs like GPT-4, Claude, Gemini, and LLaMA are pre-trained on massive text corpora using next-token prediction. Key techniques include RLHF, instruction tuning, and chain-of-thought prompting.",
        },
    ],
    "agentic ai": [
        {
            "title": "The Rise of Agentic AI — Sequoia Capital",
            "url": "https://www.sequoiacap.com/agentic-ai",
            "snippet": "Agentic AI refers to systems that can autonomously perceive, reason, plan, and act to achieve goals — going beyond simple question-answering to multi-step task completion.",
        },
        {
            "title": "ReAct: Synergizing Reasoning and Acting in LLMs",
            "url": "https://arxiv.org/abs/2210.03629",
            "snippet": "ReAct prompts LLMs to generate both reasoning traces and task-specific actions in an interleaved manner, allowing for greater synergy between the two.",
        },
        {
            "title": "Building Effective Agents — Anthropic",
            "url": "https://www.anthropic.com/research/building-effective-agents",
            "snippet": "Effective agents combine tool use, planning, memory, and guardrails. The key patterns are prompt chaining, routing, parallelization, reflection, and multi-agent orchestration.",
        },
    ],
    "machine learning": [
        {
            "title": "Introduction to Machine Learning — MIT",
            "url": "https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning/",
            "snippet": "Machine learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed. Main paradigms: supervised, unsupervised, and reinforcement learning.",
        },
        {
            "title": "Deep Learning — Yann LeCun, Yoshua Bengio, Geoffrey Hinton",
            "url": "https://www.nature.com/articles/nature14539",
            "snippet": "Deep learning discovers intricate structure in large data sets by using the backpropagation algorithm to indicate how a machine should change its internal parameters.",
        },
    ],
    "python programming": [
        {
            "title": "Python Official Documentation",
            "url": "https://docs.python.org/3/",
            "snippet": "Python is a high-level, interpreted programming language known for readability and versatility. It supports multiple paradigms including OOP, functional, and procedural programming.",
        },
        {
            "title": "Asyncio in Python — Real Python",
            "url": "https://realpython.com/async-io-python/",
            "snippet": "asyncio is a library to write concurrent code using the async/await syntax. It's used as a foundation for high-performance network and web servers, database connection libraries, and distributed task queues.",
        },
    ],
    "climate change": [
        {
            "title": "IPCC Sixth Assessment Report — Climate Change 2023",
            "url": "https://www.ipcc.ch/assessment-report/ar6/",
            "snippet": "Human activities have unequivocally caused global warming. Global surface temperature has increased faster since 1970 than in any other 50-year period over the last 2000 years.",
        },
        {
            "title": "NASA Climate Evidence",
            "url": "https://climate.nasa.gov/evidence/",
            "snippet": "Earth's climate has changed throughout history. The current warming trend is significant because it is human-caused and proceeding at an unprecedented rate. CO2 levels are at 421 ppm, highest in 800,000 years.",
        },
    ],
}

# Fallback for unknown topics
_GENERIC_RESULTS = [
    {
        "title": "Wikipedia — The Free Encyclopedia",
        "url": "https://en.wikipedia.org/",
        "snippet": "Wikipedia is a free online encyclopedia with over 6.7 million articles in English, covering virtually every topic of human knowledge.",
    },
    {
        "title": "Google Scholar",
        "url": "https://scholar.google.com/",
        "snippet": "Google Scholar provides a simple way to broadly search for scholarly literature across many disciplines and sources.",
    },
]


# ─────────────────────────────────────────────────────────────────────
# Tool implementations
# ─────────────────────────────────────────────────────────────────────

async def search_web(query: str, num_results: int = 3) -> str:
    """
    Simulate a web search.  Returns JSON array of search results.
    Matches query keywords against the knowledge base.
    """
    query_lower = query.lower()
    results = []

    # Find matching topic(s) from the knowledge base
    for topic, entries in _KNOWLEDGE_BASE.items():
        # Check if any keyword in the topic appears in the query
        topic_words = topic.split()
        if any(word in query_lower for word in topic_words):
            results.extend(entries)

    # Deduplicate and limit
    if not results:
        results = _GENERIC_RESULTS.copy()

    seen_urls = set()
    unique = []
    for r in results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique.append(r)

    # Shuffle for variety and limit to requested count
    random.shuffle(unique)
    unique = unique[:num_results]

    return json.dumps(unique, indent=2)


async def read_webpage(url: str) -> str:
    """
    Simulate reading a webpage.  Returns expanded content for known URLs.
    """
    # Map known URLs to richer content
    _CONTENT_MAP = {
        "https://arxiv.org/abs/2210.03629": (
            "ReAct: Synergizing Reasoning and Acting in Language Models\n\n"
            "Abstract: While large language models (LLMs) have demonstrated impressive "
            "capabilities across tasks in language understanding and interactive decision making, "
            "their abilities for reasoning (e.g., chain-of-thought prompting) and acting "
            "(e.g., action plan generation) have been studied separately. This paper proposes "
            "ReAct, a general paradigm that synergizes reasoning and acting in language models.\n\n"
            "Key Findings:\n"
            "1. Interleaving reasoning and actions outperforms either alone\n"
            "2. ReAct achieves state-of-the-art on HotpotQA and FEVER\n"
            "3. The approach reduces hallucination by grounding in real observations\n"
            "4. Human-in-the-loop editing of reasoning traces improves performance\n\n"
            "The ReAct Loop:\n"
            "  Thought → Action → Observation → Thought → ... → Final Answer"
        ),
        "https://www.anthropic.com/research/building-effective-agents": (
            "Building Effective Agents — Anthropic Research\n\n"
            "Key insights for building production-ready AI agents:\n\n"
            "1. Start simple — prompt chaining before complex agents\n"
            "2. Use tools judiciously — each tool is a potential failure point\n"
            "3. Implement guardrails at every layer (input, output, action)\n"
            "4. Design for graceful degradation — agents WILL make mistakes\n"
            "5. Test with adversarial inputs and edge cases\n\n"
            "The 8 Agentic Patterns:\n"
            "  • Prompt Chaining, Routing, Parallelization, Reflection\n"
            "  • Tool Use, Planning, Multi-Agent, Guardrails\n\n"
            "Best Practices:\n"
            "  - Keep agent scope narrow and well-defined\n"
            "  - Log everything for observability\n"
            "  - Use structured outputs for tool calls\n"
            "  - Set iteration limits to prevent runaway loops"
        ),
    }

    if url in _CONTENT_MAP:
        return _CONTENT_MAP[url]

    # Generic response for unknown URLs
    return (
        f"Content from {url}:\n\n"
        f"This is a simulated page. In production, this tool would use "
        f"requests + BeautifulSoup or a headless browser to extract the "
        f"main content from the webpage."
    )


async def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    Supports basic arithmetic, powers, and common functions.
    """
    # Whitelist of allowed names for safe eval
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "len": len, "pow": pow,
    }

    try:
        # Only allow digits, operators, parentheses, and dots
        sanitized = expression.replace(" ", "")
        allowed_chars = set("0123456789+-*/().,%^")
        if not all(c in allowed_chars or c.isalpha() for c in sanitized):
            return f"Error: Expression contains disallowed characters."

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"expression": expression, "error": str(e)})
