"""
Research Assistant Agent — Core Orchestrator

Implements an OpenAI function-calling agent loop (ReAct pattern) that:
1. Searches the web for information on a given research topic
2. Reads webpages for deeper understanding
3. Takes structured notes with tags
4. Performs calculations when needed
5. Compiles findings into a structured research brief

Architecture:
    ┌──────────────────────────────────────────────────────┐
    │               RESEARCH ASSISTANT AGENT                │
    │                                                       │
    │  User Query ──► System Prompt + Tools ──► LLM         │
    │                                            │          │
    │                                    ┌───────┴───────┐  │
    │                                    │  Tool Calls?   │  │
    │                                    └──┬─────────┬──┘  │
    │                                  Yes  │         │ No  │
    │                                       ▼         ▼     │
    │                                  Execute     Return   │
    │                                  Tools      Answer    │
    │                                    │                   │
    │                                    ▼                   │
    │                              Observe Results           │
    │                                    │                   │
    │                                    └──► Loop back      │
    └──────────────────────────────────────────────────────┘

Tool definitions follow the OpenAI function-calling schema.
"""

import json
import logging
from typing import Any, Callable, Coroutine

from openai import AsyncOpenAI, OpenAIError

from .config import ResearchAgentConfig, config as default_config
from .models import ResearchSession
from .tools import search_web, read_webpage, calculate

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# OpenAI Tool Definitions (JSON Schema)
# ─────────────────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for information on a topic. Returns a JSON array "
                "of results with title, url, and snippet. Use this to discover "
                "sources and gather initial information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 3, max 5)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": (
                "Read and extract the main content from a webpage URL. "
                "Use after search_web to get detailed information from a source."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to read",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": (
                "Save a research note with optional tags and source URL. "
                "Use this to record key findings, facts, and insights during research. "
                "Notes are accumulated and can be reviewed later."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The note content — a key finding or fact",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags to categorize the note (e.g., ['definition', 'history'])",
                    },
                    "source": {
                        "type": "string",
                        "description": "URL or name of the source for this note",
                    },
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_notes",
            "description": (
                "Retrieve all research notes taken so far in this session. "
                "Use to review findings before writing a summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Evaluate a mathematical expression. Supports basic arithmetic, "
                "powers, and functions like abs, round, min, max. "
                "Use for any numerical calculations during research."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '(3.14 * 2) + 10')",
                    },
                },
                "required": ["expression"],
            },
        },
    },
]


# ─────────────────────────────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a thorough and methodical Research Assistant AI Agent.

Your job is to help users research topics by:
1. Searching the web for relevant information
2. Reading webpages to extract detailed content
3. Taking structured notes on key findings
4. Compiling everything into a clear, well-organized research brief

## Your Research Process

Follow this systematic approach:
1. **Search** — Run 2-3 web searches with different query angles
2. **Deep Dive** — Read the most promising sources for detailed information
3. **Note-Taking** — Save key facts, definitions, and insights as notes with tags
4. **Synthesize** — Review your notes and compile a structured research brief

## Rules

- Always search before answering — never guess or fabricate information
- Take notes on every important finding (use save_note liberally)
- Tag notes for easy categorization (e.g., "definition", "history", "statistic", "example")
- Include source URLs in your notes when available
- When calculations are needed, use the calculate tool — never do mental math
- Review your notes (get_notes) before writing the final summary
- Structure your final answer with clear headings and bullet points
- If information is uncertain, say so explicitly

## Output Format for Final Brief

When delivering your research, use this structure:
- **Topic Overview** — 2-3 sentence summary
- **Key Findings** — Numbered list of main discoveries
- **Details** — Expanded explanation of each finding
- **Sources** — List of sources consulted
"""


# ─────────────────────────────────────────────────────────────────────
# Agent class
# ─────────────────────────────────────────────────────────────────────

class ResearchAgent:
    """
    AI-powered research assistant using the ReAct loop.

    Usage:
        agent = ResearchAgent()
        result = await agent.research("What is agentic AI?")
    """

    def __init__(self, config: ResearchAgentConfig | None = None):
        self.config = config or default_config
        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)
        self.session: ResearchSession | None = None

        # Map tool names → async callables
        self._tool_map: dict[str, Callable[..., Coroutine]] = {
            "search_web": self._handle_search_web,
            "read_webpage": self._handle_read_webpage,
            "save_note": self._handle_save_note,
            "get_notes": self._handle_get_notes,
            "calculate": self._handle_calculate,
        }

    # ── Tool handlers (bridge between OpenAI schema and tool functions) ──

    async def _handle_search_web(self, **kwargs) -> str:
        query = kwargs["query"]
        num_results = kwargs.get("num_results", 3)
        if self.session:
            self.session.searches_performed.append(query)
        result = await search_web(query, num_results)
        logger.info("🔍 Searched: %s → %d results", query, len(json.loads(result)))
        return result

    async def _handle_read_webpage(self, **kwargs) -> str:
        url = kwargs["url"]
        if self.session:
            self.session.sources_consulted.append(url)
        result = await read_webpage(url)
        logger.info("📖 Read: %s (%d chars)", url, len(result))
        return result

    async def _handle_save_note(self, **kwargs) -> str:
        content = kwargs["content"]
        tags = kwargs.get("tags", [])
        source = kwargs.get("source")
        if self.session:
            note = self.session.add_note(content, tags, source)
            logger.info("📝 Note #%d saved: %s", note.id, content[:60])
            return json.dumps({
                "status": "saved",
                "note_id": note.id,
                "total_notes": len(self.session.notes),
            })
        return json.dumps({"status": "error", "message": "No active session"})

    async def _handle_get_notes(self, **kwargs) -> str:
        if self.session:
            return self.session.get_notes_summary()
        return "No active session."

    async def _handle_calculate(self, **kwargs) -> str:
        return await calculate(kwargs["expression"])

    # ── Core ReAct loop ─────────────────────────────────────────────────

    async def research(
        self,
        query: str,
        on_tool_call: Callable[[str, dict], None] | None = None,
        on_thinking: Callable[[str], None] | None = None,
    ) -> str:
        """
        Execute a full research cycle using the ReAct loop.

        Args:
            query: The research question / topic.
            on_tool_call: Optional callback fired before each tool execution.
                          Receives (tool_name, tool_args).
            on_thinking:  Optional callback for intermediate LLM reasoning.

        Returns:
            The agent's final research brief as a string.
        """
        # Start a new session
        self.session = ResearchSession(topic=query)

        # Build initial messages
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Research this topic thoroughly: {query}"},
        ]

        iteration = 0

        while iteration < self.config.max_iterations:
            iteration += 1
            logger.debug("── Iteration %d ──", iteration)

            try:
                # REASON: Ask the LLM what to do next
                response = await self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=messages,
                    tools=TOOLS,
                    temperature=self.config.temperature,
                )
            except OpenAIError as e:
                logger.error("OpenAI API error: %s", e)
                return f"❌ Research failed due to an API error: {e}"

            message = response.choices[0].message
            messages.append(message)

            # If no tool calls → agent is done, return final answer
            if not message.tool_calls:
                if on_thinking and message.content:
                    on_thinking(message.content)
                logger.info(
                    "✅ Research complete in %d iterations (%d notes, %d searches)",
                    iteration,
                    len(self.session.notes),
                    len(self.session.searches_performed),
                )
                return message.content or "Research complete — no summary generated."

            # ACT + OBSERVE: Execute each tool call
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                # Notify callback
                if on_tool_call:
                    on_tool_call(func_name, func_args)

                # Execute the tool
                handler = self._tool_map.get(func_name)
                if handler:
                    try:
                        result = await handler(**func_args)
                    except Exception as e:
                        logger.error("Tool %s failed: %s", func_name, e)
                        result = json.dumps({"error": str(e)})
                else:
                    result = json.dumps({"error": f"Unknown tool: {func_name}"})

                # Feed observation back into the conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

        # Safety: max iterations reached
        logger.warning("⚠️ Max iterations (%d) reached", self.config.max_iterations)
        return (
            "⚠️ Research stopped — maximum iterations reached.\n\n"
            f"Notes collected so far:\n{self.session.get_notes_summary()}"
        )

    async def ask(self, question: str) -> str:
        """
        Ask a follow-up question in the context of the current session.
        Re-uses existing notes for continuity.
        """
        if not self.session:
            return await self.research(question)

        notes_context = self.session.get_notes_summary()
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Current research topic: {self.session.topic}\n"
                    f"Notes so far:\n{notes_context}\n\n"
                    f"Follow-up question: {question}"
                ),
            },
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages,
                tools=TOOLS,
                temperature=self.config.temperature,
            )
            return response.choices[0].message.content or "No answer generated."
        except OpenAIError as e:
            return f"❌ Error: {e}"
