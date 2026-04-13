# Model Context Protocol (MCP) — Fundamentals

> The universal standard for connecting AI agents to tools, data, and services

---

## 📖 Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [The Problem MCP Solves](#the-problem-mcp-solves)
3. [MCP Architecture](#mcp-architecture)
4. [Core Concepts](#core-concepts)
5. [MCP vs. Function Calling](#mcp-vs-function-calling)
6. [The Three Primitives](#the-three-primitives)
7. [Transport Layer](#transport-layer)
8. [MCP Lifecycle](#mcp-lifecycle)
9. [Building an MCP Server](#building-an-mcp-server)
10. [Building an MCP Client](#building-an-mcp-client)
11. [Security and Trust](#security-and-trust)
12. [Ecosystem and Tooling](#ecosystem-and-tooling)

---

## What is MCP?

**Model Context Protocol (MCP)** is an open standard created by Anthropic that provides a **universal, standardized way** for AI applications (agents, chatbots, IDEs) to connect to external tools, data sources, and services.

> Think of MCP as the **USB-C of AI integrations** — one standard protocol that connects any AI model to any tool or data source.

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   BEFORE MCP                        AFTER MCP                │
│   ──────────                        ─────────                │
│                                                              │
│   App ─── Custom API ─── Tool A     App ─┐                  │
│   App ─── SDK ────────── Tool B           ├── MCP ─── Any   │
│   App ─── REST ───────── Tool C     App ─┘         Tool     │
│   App ─── GraphQL ────── Tool D                              │
│                                                              │
│   N apps × M tools = N×M          N apps × M tools = N+M    │
│   integrations                     integrations              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Properties

| Property | Description |
|----------|-------------|
| **Open Standard** | Free, open-source protocol — not locked to any vendor |
| **Language Agnostic** | SDKs available for Python, TypeScript, Java, C#, and more |
| **Transport Flexible** | Works over stdio, HTTP+SSE, WebSocket |
| **Bidirectional** | Both client and server can initiate requests |
| **Composable** | One client can connect to multiple servers simultaneously |

---

## The Problem MCP Solves

### Without MCP: The N×M Integration Problem

Every AI application needs custom code for every tool:

```
                    Tools / Data Sources
                    ┌────┬────┬────┬────┐
                    │ DB │ API│Files│Git │
       ┌────────────┼────┼────┼────┼────┤
       │  Claude     │ ✏️  │ ✏️  │ ✏️  │ ✏️  │  ← Custom code for each
       ├────────────┼────┼────┼────┼────┤
Apps   │  ChatGPT    │ ✏️  │ ✏️  │ ✏️  │ ✏️  │  ← Duplicate work
       ├────────────┼────┼────┼────┼────┤
       │  VS Code    │ ✏️  │ ✏️  │ ✏️  │ ✏️  │  ← Different implementations
       ├────────────┼────┼────┼────┼────┤
       │  Custom App │ ✏️  │ ✏️  │ ✏️  │ ✏️  │  ← More custom code
       └────────────┴────┴────┴────┴────┘
       
       Total integrations: 4 × 4 = 16 custom implementations
```

### With MCP: The N+M Solution

Each app implements MCP **once**, each tool exposes MCP **once**:

```
                         MCP Protocol
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
  ┌────┴────┐           ┌─────┴─────┐          ┌────┴────┐
  │ Claude   │           │ VS Code   │          │ Custom  │
  │ Desktop  │           │ Copilot   │          │ App     │
  │ (Client) │           │ (Client)  │          │(Client) │
  └────┬────┘           └─────┬─────┘          └────┬────┘
       │                      │                      │
       └──────────┬───────────┼──────────────────────┘
                  │           │
       ┌──────────┼───────────┼──────────┐
       │          │           │          │
  ┌────┴────┐ ┌──┴────┐ ┌───┴───┐ ┌───┴───┐
  │  DB     │ │ API   │ │ Files │ │ Git   │
  │ Server  │ │ Server│ │Server │ │Server │
  └─────────┘ └───────┘ └───────┘ └───────┘
  
  Total integrations: 3 + 4 = 7 implementations
```

---

## MCP Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        HOST APPLICATION                       │
│  (Claude Desktop, VS Code, Custom App)                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                      MCP CLIENT                          │ │
│  │                                                          │ │
│  │  Maintains 1:1 connection with an MCP Server             │ │
│  │  Handles capability negotiation                          │ │
│  │  Routes requests and notifications                       │ │
│  └────────────────────────┬────────────────────────────────┘ │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │  Transport Layer
                            │  (stdio / HTTP+SSE / WebSocket)
                            │
┌───────────────────────────┼───────────────────────────────────┐
│                           │                                    │
│  ┌────────────────────────┴────────────────────────────────┐  │
│  │                      MCP SERVER                          │  │
│  │                                                          │  │
│  │  Exposes capabilities via the MCP protocol:              │  │
│  │  • Tools (functions the agent can call)                  │  │
│  │  • Resources (data the agent can read)                   │  │
│  │  • Prompts (reusable prompt templates)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│                        MCP SERVER                              │
│  (Wraps a database, API, file system, or any service)         │
└────────────────────────────────────────────────────────────────┘
```

### Component Roles

| Component | Role | Examples |
|-----------|------|----------|
| **Host** | The application the user interacts with | Claude Desktop, VS Code, IDE plugins, custom apps |
| **Client** | Protocol handler inside the host; manages server connections | Built into the host — one client per server connection |
| **Server** | Exposes tools, resources, and prompts over MCP | Database server, GitHub server, file system server |

### Key Principle: Separation of Concerns

```
┌──────────┐          ┌──────────┐          ┌──────────────┐
│   LLM    │          │   MCP    │          │  External    │
│  (Brain) │◄────────▶│  Server  │◄────────▶│  Service     │
│          │  MCP     │(Adapter) │  Native  │  (DB, API,   │
│ Reasons  │ Protocol │ Exposes  │   API    │   Files)     │
│ & decides│          │ tools &  │          │              │
│          │          │ resources│          │              │
└──────────┘          └──────────┘          └──────────────┘

The LLM never talks directly to external services.
The MCP server is the bridge.
```

---

## Core Concepts

### 1. Capability Negotiation

When a client connects to a server, they exchange capabilities:

```
Client → Server:  "I support tools, resources, prompts"
Server → Client:  "I provide tools and resources (no prompts)"
                  "Here are my tools: [search_db, insert_record, ...]"
                  "Here are my resources: [database://users, ...]"
```

This ensures both sides understand what the other can do.

### 2. JSON-RPC 2.0

MCP uses **JSON-RPC 2.0** as its message format:

```json
// Request (Client → Server)
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "search_database",
        "arguments": {
            "query": "SELECT * FROM users WHERE active = true"
        }
    }
}

// Response (Server → Client)
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "[{\"id\": 1, \"name\": \"Alice\"}, ...]"
            }
        ]
    }
}
```

### 3. Stateful Sessions

Unlike stateless REST APIs, MCP connections are **stateful**:

```
┌──────────────────────────────────────────────┐
│           MCP SESSION LIFECYCLE               │
│                                               │
│  1. Initialize  →  Exchange capabilities      │
│  2. Operate     →  Call tools, read resources │
│  3. Notify      →  Server pushes updates      │
│  4. Shutdown    →  Clean disconnection        │
└──────────────────────────────────────────────┘
```

---

## MCP vs. Function Calling

| Aspect | Function Calling | MCP |
|--------|-----------------|-----|
| **Scope** | Per-API-call tool definitions | Persistent server with discoverable tools |
| **Discovery** | Tools defined inline in each request | Tools discovered dynamically at connection |
| **Standardization** | Vendor-specific (OpenAI, Anthropic, etc.) | Open standard across all vendors |
| **Statefulness** | Stateless per call | Stateful session |
| **Data access** | Via tool functions only | Tools + Resources + Prompts |
| **Reusability** | Defined per application | One server, many clients |
| **Updates** | Re-deploy app to change tools | Server updates independently |
| **Ecosystem** | Build everything yourself | Growing library of pre-built servers |

### How They Work Together

MCP **doesn't replace** function calling — it enhances it:

```
┌──────────────────────────────────────────────────┐
│                                                   │
│  1. MCP Client discovers tools from MCP Server    │
│  2. Client converts MCP tools → function calling  │
│     format for the LLM                            │
│  3. LLM decides which tool to call                │
│  4. Client routes the call to MCP Server          │
│  5. MCP Server executes and returns result        │
│  6. Client feeds result back to LLM               │
│                                                   │
│  MCP = standardized tool HOSTING                  │
│  Function calling = LLM tool SELECTION mechanism  │
└──────────────────────────────────────────────────┘
```

---

## The Three Primitives

MCP servers expose three types of capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP PRIMITIVES                             │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │    🔧 TOOLS     │  │  📄 RESOURCES   │  │  💬 PROMPTS   │  │
│  │                 │  │                │  │               │  │
│  │  Actions the    │  │  Data the      │  │  Reusable     │  │
│  │  model can      │  │  model can     │  │  prompt       │  │
│  │  execute        │  │  read          │  │  templates    │  │
│  │                 │  │                │  │               │  │
│  │  Model-         │  │  Application-  │  │  User-        │  │
│  │  controlled     │  │  controlled    │  │  controlled   │  │
│  │                 │  │                │  │               │  │
│  │  Examples:      │  │  Examples:     │  │  Examples:    │  │
│  │  - query_db()   │  │  - file://     │  │  - code_review│  │
│  │  - send_email() │  │  - db://users  │  │  - summarize  │  │
│  │  - create_issue │  │  - api://data  │  │  - translate  │  │
│  └────────────────┘  └────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Tools — Model-Controlled Actions

Tools are **functions** the LLM can decide to invoke. The model controls when and how to call them.

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_database",
            description="Search the customer database by name or email",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (name or email)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_database":
        results = await db.search(arguments["query"], arguments.get("limit", 10))
        return [TextContent(type="text", text=json.dumps(results))]
    raise ValueError(f"Unknown tool: {name}")
```

### Resources — Application-Controlled Data

Resources provide **read access to data**. The application (host) controls when to fetch them, not the model.

```python
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="database://customers/schema",
            name="Customer Database Schema",
            description="Table structure and column definitions",
            mimeType="application/json"
        ),
        Resource(
            uri="file:///config/settings.yaml",
            name="Application Settings",
            description="Current application configuration",
            mimeType="text/yaml"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "database://customers/schema":
        return json.dumps(get_schema("customers"))
    elif uri.startswith("file://"):
        path = uri.replace("file://", "")
        return open(path).read()
```

### Prompts — User-Controlled Templates

Prompts are **reusable templates** that can be presented to users for selection:

```python
@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="code_review",
            description="Review code for bugs, style, and performance",
            arguments=[
                PromptArgument(
                    name="code",
                    description="The code to review",
                    required=True
                ),
                PromptArgument(
                    name="language",
                    description="Programming language",
                    required=False
                )
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "code_review":
        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Review this {arguments.get('language', '')} code:\n\n{arguments['code']}\n\n"
                             "Check for: bugs, security issues, performance, style."
                    )
                )
            ]
        )
```

---

## Transport Layer

MCP supports multiple transport mechanisms:

### Transport Options

```
┌──────────────────────────────────────────────────────────┐
│                  TRANSPORT OPTIONS                        │
│                                                           │
│  1. STDIO (Standard Input/Output)                        │
│     ─────────────────────────────                        │
│     • Client spawns server as a child process            │
│     • Communication over stdin/stdout                    │
│     • Best for: local tools, CLI integration             │
│     • Simplest setup                                     │
│                                                           │
│  2. HTTP + SSE (Server-Sent Events)                      │
│     ──────────────────────────────                       │
│     • Server runs as HTTP service                        │
│     • Client → Server: HTTP POST requests                │
│     • Server → Client: SSE stream for notifications      │
│     • Best for: remote servers, web deployments          │
│                                                           │
│  3. Streamable HTTP (Newer)                              │
│     ──────────────────────                               │
│     • Single HTTP endpoint with streaming                │
│     • Simpler than SSE for many use cases                │
│     • Best for: modern deployments, serverless           │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### STDIO Example

```json
// claude_desktop_config.json
{
    "mcpServers": {
        "my-database": {
            "command": "python",
            "args": ["/path/to/my_mcp_server.py"],
            "env": {
                "DATABASE_URL": "postgresql://localhost/mydb"
            }
        }
    }
}
```

### HTTP+SSE Example

```python
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

server = Server("my-remote-server")
sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0], streams[1], server.create_initialization_options()
        )

app = Starlette(routes=[
    Route("/sse", endpoint=handle_sse),
    Route("/messages", endpoint=sse.handle_post_message, methods=["POST"]),
])
```

---

## MCP Lifecycle

### Connection Lifecycle

```
┌──────────┐                              ┌──────────┐
│  CLIENT   │                              │  SERVER   │
└─────┬────┘                              └─────┬────┘
      │                                         │
      │  1. initialize (capabilities, info)     │
      │────────────────────────────────────────▶│
      │                                         │
      │  2. initialize response (capabilities)  │
      │◄────────────────────────────────────────│
      │                                         │
      │  3. initialized notification            │
      │────────────────────────────────────────▶│
      │                                         │
      │  ═══════ SESSION ACTIVE ════════════    │
      │                                         │
      │  4. tools/list                          │
      │────────────────────────────────────────▶│
      │  4r. tool list response                 │
      │◄────────────────────────────────────────│
      │                                         │
      │  5. tools/call                          │
      │────────────────────────────────────────▶│
      │  5r. tool result                        │
      │◄────────────────────────────────────────│
      │                                         │
      │  6. resources/read                      │
      │────────────────────────────────────────▶│
      │  6r. resource content                   │
      │◄────────────────────────────────────────│
      │                                         │
      │  7. notifications/tools/list_changed    │
      │◄────────────────────────────────────────│
      │  (server notifies of capability change) │
      │                                         │
      │  ═══════ SHUTDOWN ══════════════════    │
      │                                         │
      │  8. Close connection                    │
      │────────────────────────────────────────▶│
      │                                         │
```

---

## Building an MCP Server

### Complete Python MCP Server Example

```python
"""
A simple MCP server that provides weather data tools.

Usage:
    python weather_mcp_server.py
"""

import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource

# Create the server
server = Server("weather-server")

# --- Mock Data ---
WEATHER_DB = {
    "San Francisco": {"temp_f": 65, "condition": "Foggy", "humidity": 78},
    "New York": {"temp_f": 82, "condition": "Sunny", "humidity": 55},
    "London": {"temp_f": 58, "condition": "Rainy", "humidity": 85},
    "Tokyo": {"temp_f": 75, "condition": "Cloudy", "humidity": 65},
}

# --- Tools ---
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'San Francisco')"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_forecast",
            description="Get 3-day weather forecast for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "description": "Number of days (1-7)", "default": 3}
                },
                "required": ["city"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        city = arguments["city"]
        weather = WEATHER_DB.get(city)
        if weather:
            return [TextContent(type="text", text=json.dumps({
                "city": city, **weather
            }))]
        return [TextContent(type="text", text=json.dumps({
            "error": f"No weather data for {city}"
        }))]
    
    elif name == "get_forecast":
        city = arguments["city"]
        days = arguments.get("days", 3)
        # Mock forecast
        return [TextContent(type="text", text=json.dumps({
            "city": city,
            "forecast": [
                {"day": i+1, "temp_f": 70 + i*2, "condition": "Partly Cloudy"}
                for i in range(days)
            ]
        }))]
    
    raise ValueError(f"Unknown tool: {name}")

# --- Resources ---
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="weather://cities",
            name="Available Cities",
            description="List of cities with weather data",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "weather://cities":
        return json.dumps(list(WEATHER_DB.keys()))
    raise ValueError(f"Unknown resource: {uri}")

# --- Run Server ---
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Installation

```bash
# Install MCP SDK
pip install mcp

# For HTTP transport
pip install mcp[sse]
```

---

## Building an MCP Client

### Python Client Example

```python
"""Connect to an MCP server and use its tools."""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Connect to server via stdio
    server_params = StdioServerParameters(
        command="python",
        args=["weather_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # Discover available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Call a tool
            result = await session.call_tool(
                "get_weather",
                arguments={"city": "San Francisco"}
            )
            print(f"\nWeather result: {result.content[0].text}")
            
            # Read a resource
            resources = await session.list_resources()
            for resource in resources.resources:
                content = await session.read_resource(resource.uri)
                print(f"\nResource ({resource.name}): {content}")
```

### Integrating MCP with an LLM Agent

```python
"""Full agent that uses MCP servers for tool execution."""

import json
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_agent_with_mcp():
    openai_client = AsyncOpenAI()
    
    server_params = StdioServerParameters(
        command="python",
        args=["weather_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Discover MCP tools
            mcp_tools = await session.list_tools()
            
            # 2. Convert to OpenAI function-calling format
            openai_tools = []
            for tool in mcp_tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            # 3. Run agent loop
            messages = [
                {"role": "system", "content": "You are a helpful weather assistant."},
                {"role": "user", "content": "What's the weather like in Tokyo?"}
            ]
            
            while True:
                response = await openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=openai_tools
                )
                
                msg = response.choices[0].message
                messages.append(msg)
                
                if not msg.tool_calls:
                    print(f"Agent: {msg.content}")
                    break
                
                # 4. Route tool calls through MCP
                for tc in msg.tool_calls:
                    result = await session.call_tool(
                        tc.function.name,
                        arguments=json.loads(tc.function.arguments)
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result.content[0].text
                    })
```

---

## Security and Trust

### Security Model

```
┌─────────────────────────────────────────────────────────┐
│                MCP SECURITY LAYERS                       │
│                                                          │
│  1. TRANSPORT SECURITY                                   │
│     • TLS for HTTP transports                            │
│     • Process isolation for stdio                        │
│     • Authentication headers                             │
│                                                          │
│  2. CAPABILITY CONTROL                                   │
│     • Servers declare what they can do                   │
│     • Clients approve which capabilities to use          │
│     • Principle of least privilege                       │
│                                                          │
│  3. HUMAN-IN-THE-LOOP                                    │
│     • Users approve tool calls before execution          │
│     • Sensitive operations require confirmation          │
│     • Hosts control what the LLM can access              │
│                                                          │
│  4. INPUT VALIDATION                                     │
│     • Servers validate all arguments                     │
│     • Schema enforcement via JSON Schema                 │
│     • Sanitize inputs to prevent injection               │
│                                                          │
│  5. AUDIT & LOGGING                                      │
│     • Log all tool calls and results                     │
│     • Track which tools are called and when              │
│     • Monitor for unusual patterns                       │
└─────────────────────────────────────────────────────────┘
```

### Best Practices

| Practice | Description |
|----------|-------------|
| **Validate all inputs** | Never trust arguments from the LLM without validation |
| **Limit permissions** | MCP servers should have minimal database/API permissions |
| **Log everything** | Every tool call, argument, and result should be logged |
| **Use environment variables** | Never hardcode secrets in MCP server code |
| **Scope resources** | Only expose the data and actions the agent truly needs |
| **Timeout requests** | Set max execution time for tool calls |

---

## Ecosystem and Tooling

### Pre-Built MCP Servers

| Server | Description | Source |
|--------|-------------|--------|
| **Filesystem** | Read/write local files | Official (Anthropic) |
| **GitHub** | Repos, issues, PRs, file management | Official |
| **PostgreSQL** | Query and manage PostgreSQL databases | Official |
| **Slack** | Send messages, manage channels | Official |
| **Google Drive** | Search and read documents | Official |
| **Brave Search** | Web search | Official |
| **Puppeteer** | Browser automation | Official |
| **SQLite** | Local database operations | Official |
| **Memory** | Persistent key-value memory for agents | Official |

### Where to Find MCP Servers

- **Official Registry**: [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- **MCP Hub**: Community-maintained server directory
- **npm / PyPI**: Search for `mcp-server-*` packages

### Host Applications Supporting MCP

| Host | Description |
|------|-------------|
| **Claude Desktop** | Anthropic's desktop app — first-class MCP support |
| **VS Code (GitHub Copilot)** | MCP support in Copilot agent mode |
| **Cursor** | AI code editor with MCP integration |
| **Windsurf** | AI IDE with MCP support |
| **Continue** | Open-source coding assistant |
| **Zed** | High-performance editor with MCP |

---

## 📚 Further Reading

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Documentation](https://modelcontextprotocol.io/docs)
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)

---

## 🔗 Related Materials

| Resource | Link |
|----------|------|
| MCP Patterns | [02-mcp-patterns.md](./02-mcp-patterns.md) |
| MCP Use Cases | [03-mcp-use-cases.md](./03-mcp-use-cases.md) |
| Agentic AI Tutorial | [05-advanced/02-agentic-ai-tutorial.md](../05-advanced/02-agentic-ai-tutorial.md) |
| Tool Use Pattern | [08-agentic-patterns/05-tool-use.md](../08-agentic-patterns/05-tool-use.md) |
