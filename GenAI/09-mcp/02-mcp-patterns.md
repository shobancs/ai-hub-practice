# MCP Patterns — Design Patterns for Model Context Protocol

> Proven architectural patterns for building robust, scalable MCP integrations

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Pattern 1: Single Server — Direct Integration](#pattern-1-single-server--direct-integration)
3. [Pattern 2: Multi-Server Composition](#pattern-2-multi-server-composition)
4. [Pattern 3: Gateway / Aggregator](#pattern-3-gateway--aggregator)
5. [Pattern 4: Resource-First Pattern](#pattern-4-resource-first-pattern)
6. [Pattern 5: Tool Chaining Pattern](#pattern-5-tool-chaining-pattern)
7. [Pattern 6: Proxy / Middleware Pattern](#pattern-6-proxy--middleware-pattern)
8. [Pattern 7: Dynamic Tool Registration](#pattern-7-dynamic-tool-registration)
9. [Pattern 8: Event-Driven Notifications](#pattern-8-event-driven-notifications)
10. [Pattern 9: Caching and Rate Limiting](#pattern-9-caching-and-rate-limiting)
11. [Pattern 10: Multi-Tenant Server](#pattern-10-multi-tenant-server)
12. [Pattern Selection Guide](#pattern-selection-guide)
13. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Overview

MCP patterns are **reusable architectural approaches** for connecting AI agents to external tools and data via the Model Context Protocol. Choosing the right pattern depends on:

- **How many data sources** you need to integrate
- **Where** the server runs (local vs. remote)
- **Who** consumes the server (single app vs. multiple)
- **Security** and **performance** requirements

```
┌──────────────────────────────────────────────────────────────┐
│                   MCP PATTERN MAP                             │
│                                                               │
│  BASIC                  COMPOSITION            ADVANCED        │
│  ─────                  ───────────            ────────        │
│  Single Server          Multi-Server           Gateway         │
│  Resource-First         Tool Chaining          Proxy/Middleware│
│                                                Dynamic Tools   │
│                                                Event-Driven    │
│                                                Multi-Tenant    │
│                                                Caching/RateLimit│
└──────────────────────────────────────────────────────────────┘
```

---

## Pattern 1: Single Server — Direct Integration

### When to Use
- You have **one data source** or service to integrate
- Simple use case (e.g., database access, file operations)
- Getting started with MCP

### Architecture

```
┌──────────────┐         ┌──────────────┐         ┌────────────┐
│  Host App     │  MCP    │  MCP Server   │  Native │  Service   │
│  (Claude,     │◄──────▶│  (Python/TS)  │◄───────▶│  (DB, API) │
│   VS Code)    │  stdio  │               │  SQL/   │            │
└──────────────┘         └──────────────┘  HTTP    └────────────┘
```

### Example: PostgreSQL MCP Server

```python
import json
import asyncpg
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("postgres-server")

# Connection pool
pool = None

async def get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(os.environ["DATABASE_URL"])
    return pool

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query",
            description="Execute a read-only SQL query against the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL SELECT query"}
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    db = await get_pool()
    
    if name == "query":
        sql = arguments["sql"].strip()
        # Safety: only allow SELECT queries
        if not sql.upper().startswith("SELECT"):
            return [TextContent(type="text", text="Error: Only SELECT queries allowed")]
        
        rows = await db.fetch(sql)
        return [TextContent(type="text", text=json.dumps([dict(r) for r in rows], default=str))]
    
    elif name == "list_tables":
        rows = await db.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        return [TextContent(type="text", text=json.dumps([r["table_name"] for r in rows]))]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
```

### Pros & Cons

| ✅ Pros | ❌ Cons |
|---------|---------|
| Simple to build and debug | One server = one data source |
| Low latency (direct connection) | Client must manage multiple server configs |
| Easy to understand | No shared logic between servers |

---

## Pattern 2: Multi-Server Composition

### When to Use
- Your agent needs access to **multiple independent services**
- Each service has different access patterns and credentials
- You want **separation of concerns**

### Architecture

```
┌──────────────────────────────────────────────────────┐
│                    HOST APPLICATION                    │
│                                                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │             │
│  └────┬────┘  └────┬────┘  └────┬────┘             │
└───────┼────────────┼────────────┼────────────────────┘
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ GitHub   │  │ Database │  │ Slack    │
   │ Server   │  │ Server   │  │ Server   │
   └─────────┘  └─────────┘  └─────────┘
```

### Configuration

```json
{
    "mcpServers": {
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": { "GITHUB_TOKEN": "ghp_..." }
        },
        "postgres": {
            "command": "python",
            "args": ["mcp_servers/postgres_server.py"],
            "env": { "DATABASE_URL": "postgresql://..." }
        },
        "slack": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": { "SLACK_TOKEN": "xoxb-..." }
        }
    }
}
```

### How It Works

1. Host creates **one MCP client per server**
2. Each client manages its own connection lifecycle
3. When the LLM requests a tool, the host routes to the **correct client**
4. Tools from all servers appear as a **unified tool list** to the LLM

```python
# Host-side tool routing (simplified)
async def route_tool_call(tool_name: str, arguments: dict):
    """Route a tool call to the correct MCP server."""
    
    # Map tools to their servers
    tool_server_map = {
        "create_issue": github_session,
        "query_db": postgres_session,
        "send_message": slack_session,
    }
    
    session = tool_server_map.get(tool_name)
    if session is None:
        raise ValueError(f"No server found for tool: {tool_name}")
    
    return await session.call_tool(tool_name, arguments)
```

---

## Pattern 3: Gateway / Aggregator

### When to Use
- You want **one server** that unifies multiple backends
- Simplify client configuration (one server instead of many)
- Add **cross-cutting concerns** (auth, logging, caching)

### Architecture

```
┌──────────────┐         ┌──────────────────────────────┐
│  Host App     │  MCP    │       GATEWAY SERVER          │
│  (Single      │◄──────▶│                               │
│   Client)     │         │  ┌─────────────────────────┐ │
└──────────────┘         │  │  Tool Router             │ │
                          │  │  ┌───┐ ┌───┐ ┌───┐     │ │
                          │  │  │ DB│ │API│ │Git│     │ │
                          │  │  └─┬─┘ └─┬─┘ └─┬─┘     │ │
                          │  └────┼─────┼─────┼───────┘ │
                          │       │     │     │         │
                          └───────┼─────┼─────┼─────────┘
                                  ▼     ▼     ▼
                              ┌─────┐┌─────┐┌─────┐
                              │ DB  ││ API ││ Git │
                              └─────┘└─────┘└─────┘
```

### Implementation

```python
"""Gateway MCP server that aggregates multiple backends."""

from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("gateway")

# Backend handlers
from backends import database, github_api, slack_api

# Aggregate tools from all backends
ALL_TOOLS = {
    **database.TOOLS,      # query_db, list_tables
    **github_api.TOOLS,    # create_issue, list_repos
    **slack_api.TOOLS,     # send_message, list_channels
}

TOOL_HANDLERS = {
    **database.HANDLERS,
    **github_api.HANDLERS,
    **slack_api.HANDLERS,
}

@server.list_tools()
async def list_tools() -> list[Tool]:
    return list(ALL_TOOLS.values())

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        raise ValueError(f"Unknown tool: {name}")
    
    # Cross-cutting: logging
    logger.info(f"Tool call: {name}", extra={"arguments": arguments})
    
    # Cross-cutting: rate limiting
    await rate_limiter.check(name)
    
    # Execute
    result = await handler(arguments)
    
    # Cross-cutting: audit trail
    await audit_log.record(name, arguments, result)
    
    return result
```

### Benefits

- Single configuration point for the client
- Centralized logging, authentication, rate limiting
- Can implement cross-server tool orchestration

---

## Pattern 4: Resource-First Pattern

### When to Use
- Your primary need is **data access** (reading files, configs, schemas)
- Agent needs **context** before taking actions
- Building knowledge-enriched agents

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  RESOURCE-FIRST SERVER                     │
│                                                           │
│  Resources (data access)          Tools (actions)         │
│  ────────────────────             ───────────────         │
│  docs://api/endpoints             update_doc              │
│  docs://api/schemas               deploy_docs             │
│  docs://guides/{topic}            validate_links          │
│  config://app/settings                                    │
│  metrics://dashboard/today                                │
│                                                           │
│  Agent reads resources FIRST, then uses tools to act      │
└──────────────────────────────────────────────────────────┘
```

### Implementation

```python
"""Resource-first MCP server for documentation."""

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent

server = Server("docs-server")

@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="docs://api/openapi-spec",
            name="OpenAPI Specification",
            description="Full API specification in OpenAPI 3.0 format",
            mimeType="application/json"
        ),
        Resource(
            uri="docs://guides/getting-started",
            name="Getting Started Guide",
            description="Onboarding guide for new developers",
            mimeType="text/markdown"
        ),
        Resource(
            uri="docs://changelog/latest",
            name="Latest Changelog",
            description="Most recent API changes and version notes",
            mimeType="text/markdown"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "docs://api/openapi-spec":
        return load_file("openapi.json")
    elif uri == "docs://guides/getting-started":
        return load_file("guides/getting-started.md")
    elif uri == "docs://changelog/latest":
        return fetch_latest_changelog()
    raise ValueError(f"Unknown resource: {uri}")

# Tools complement resources — act on what was read
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_docs",
            description="Search documentation by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "section": {"type": "string", "enum": ["api", "guides", "changelog"]}
                },
                "required": ["query"]
            }
        )
    ]
```

### When to Use Resources vs. Tools

| Use Resources When... | Use Tools When... |
|----------------------|-------------------|
| Agent needs background context | Agent needs to perform an action |
| Data is relatively static | Operation has side effects |
| Content is read-only | User input drives the parameters |
| Application controls when to load | Model controls when to call |

---

## Pattern 5: Tool Chaining Pattern

### When to Use
- Tools need to be called **in sequence** where output of one feeds the next
- Complex workflows with dependencies between steps
- Building pipeline-style integrations

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   TOOL CHAINING                           │
│                                                           │
│  Agent decides the chain, server provides the tools:      │
│                                                           │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐  │
│  │ search_  │────▶│ get_details  │────▶│ create_      │  │
│  │ customers│     │ (customer_id)│     │ invoice      │  │
│  └──────────┘     └──────────────┘     └──────────────┘  │
│                                                           │
│  The LLM orchestrates: it calls tools in order,           │
│  passing results from one to the next.                    │
└──────────────────────────────────────────────────────────┘
```

### Implementation: CRM Tool Chain

```python
"""MCP server with tools designed for chaining."""

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_customers",
            description="Search customers by name/email. Returns customer IDs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_customer_details",
            description="Get full details for a customer by ID. Use after search_customers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Customer ID from search"}
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="get_customer_orders",
            description="Get order history for a customer. Use after get_customer_details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["pending", "shipped", "delivered", "all"]}
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="create_support_ticket",
            description="Create a support ticket for a customer. Use after getting customer context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "subject": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
                },
                "required": ["customer_id", "subject", "description"]
            }
        )
    ]
```

### Best Practices for Chain-Friendly Tools

1. **Return IDs** — Each tool should return identifiers the next tool can use
2. **Describe dependencies** — Tool descriptions should say "Use after X"
3. **Consistent naming** — Use `entity_action` format (e.g., `customer_search`, `customer_details`)
4. **Atomic operations** — Each tool does one thing well

---

## Pattern 6: Proxy / Middleware Pattern

### When to Use
- Add **cross-cutting concerns** without modifying existing servers
- Implement **auth, logging, caching, rate limiting** as a layer
- Wrap existing MCP servers with additional behavior

### Architecture

```
┌──────────┐       ┌──────────────────┐       ┌──────────────┐
│  Client   │  MCP  │    PROXY SERVER   │  MCP  │  Upstream    │
│           │◄────▶│                   │◄────▶│  Server      │
└──────────┘       │  + Auth checking  │       └──────────────┘
                    │  + Rate limiting  │
                    │  + Caching        │
                    │  + Logging        │
                    │  + Transformation │
                    └──────────────────┘
```

### Implementation

```python
"""MCP proxy that adds logging and caching to any upstream server."""

from mcp.server import Server
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from functools import lru_cache
import time

proxy = Server("mcp-proxy")

# Connect to upstream server
upstream_params = StdioServerParameters(
    command="python", args=["upstream_server.py"]
)

class ProxyMiddleware:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.call_count = {}
        self.rate_limit = 100  # calls per minute
    
    def check_rate_limit(self, tool_name: str) -> bool:
        now = time.time()
        minute_key = f"{tool_name}:{int(now / 60)}"
        self.call_count[minute_key] = self.call_count.get(minute_key, 0) + 1
        return self.call_count[minute_key] <= self.rate_limit
    
    def get_cached(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return value
        return None
    
    def set_cached(self, key: str, value):
        self.cache[key] = (value, time.time())

middleware = ProxyMiddleware()

@proxy.call_tool()
async def proxied_call_tool(name: str, arguments: dict):
    # Rate limiting
    if not middleware.check_rate_limit(name):
        return [TextContent(type="text", text="Rate limit exceeded. Try again later.")]
    
    # Caching (for read-only tools)
    cache_key = f"{name}:{json.dumps(arguments, sort_keys=True)}"
    cached = middleware.get_cached(cache_key)
    if cached is not None:
        logger.info(f"Cache hit: {name}")
        return cached
    
    # Forward to upstream
    async with stdio_client(upstream_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
    
    # Cache result
    middleware.set_cached(cache_key, result.content)
    
    # Logging
    logger.info(f"Tool call: {name}", extra={
        "arguments": arguments,
        "result_length": len(str(result.content))
    })
    
    return result.content
```

---

## Pattern 7: Dynamic Tool Registration

### When to Use
- Tools change at runtime (e.g., based on user permissions, loaded plugins)
- Building **extensible** MCP servers that support plugins
- Tools depend on **discovered schemas** or configurations

### Architecture

```
┌────────────────────────────────────────────────────┐
│            DYNAMIC TOOL SERVER                      │
│                                                     │
│  Startup:                                           │
│  1. Scan plugin directory                           │
│  2. Load plugin definitions                         │
│  3. Register tools dynamically                      │
│                                                     │
│  Runtime:                                           │
│  4. New plugin added → notify clients               │
│  5. Plugin removed → update tool list               │
│                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │Plugin A  │  │Plugin B  │  │Plugin C  │  ← loaded │
│  │(2 tools) │  │(3 tools) │  │(1 tool)  │  at runtime│
│  └─────────┘  └─────────┘  └─────────┘            │
└────────────────────────────────────────────────────┘
```

### Implementation

```python
"""MCP server with dynamic tool loading from plugins."""

import importlib
import os
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("dynamic-tools")

# Registry of dynamically loaded tools
tool_registry: dict[str, dict] = {}

def load_plugins(plugin_dir: str = "./plugins"):
    """Discover and load tool plugins."""
    for file in Path(plugin_dir).glob("*.py"):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Each plugin exports TOOLS and HANDLERS
        if hasattr(module, "TOOLS") and hasattr(module, "HANDLERS"):
            for tool_name, tool_def in module.TOOLS.items():
                tool_registry[tool_name] = {
                    "definition": tool_def,
                    "handler": module.HANDLERS[tool_name],
                    "plugin": module_name
                }
            print(f"Loaded plugin: {module_name} ({len(module.TOOLS)} tools)")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry["definition"] for entry in tool_registry.values()]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    entry = tool_registry.get(name)
    if entry is None:
        raise ValueError(f"Unknown tool: {name}")
    return await entry["handler"](arguments)

# Load plugins on startup
load_plugins()
```

### Plugin Example

```python
# plugins/math_tools.py
"""Math tools plugin."""

from mcp.types import Tool, TextContent
import math

TOOLS = {
    "calculate": Tool(
        name="calculate",
        description="Evaluate a mathematical expression",
        inputSchema={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression to evaluate"}
            },
            "required": ["expression"]
        }
    )
}

async def handle_calculate(arguments: dict) -> list[TextContent]:
    expr = arguments["expression"]
    # Safe evaluation with limited builtins
    allowed = {"abs": abs, "round": round, "min": min, "max": max,
               "sum": sum, "pow": pow, "sqrt": math.sqrt, "pi": math.pi}
    result = eval(expr, {"__builtins__": {}}, allowed)
    return [TextContent(type="text", text=str(result))]

HANDLERS = {
    "calculate": handle_calculate
}
```

---

## Pattern 8: Event-Driven Notifications

### When to Use
- Server needs to **push updates** to the client
- Monitoring scenarios (new data, status changes)
- Real-time dashboards or alert systems

### Architecture

```
┌──────────┐                           ┌──────────────┐
│  Client   │◄── notifications ────────│  Server      │
│           │                           │              │
│  Reacts   │                           │  Watches:    │
│  to push  │                           │  - DB changes│
│  events   │  ──── tool calls ────────▶│  - File mods │
│           │                           │  - API events│
└──────────┘                           └──────────────┘
```

### Implementation

```python
"""MCP server with notification support."""

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="subscribe_to_changes",
            description="Subscribe to database change notifications",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {"type": "string"},
                    "event": {"type": "string", "enum": ["insert", "update", "delete", "all"]}
                },
                "required": ["table"]
            }
        )
    ]

# Server can notify clients when tools change
async def on_schema_change():
    """Called when the database schema changes."""
    # Notify connected clients that tools have changed
    await server.request_context.session.send_tools_list_changed()

# Server can notify when resources change
async def on_data_update(resource_uri: str):
    """Called when underlying data changes."""
    await server.request_context.session.send_resource_updated(resource_uri)
```

---

## Pattern 9: Caching and Rate Limiting

### When to Use
- Tools call expensive external APIs
- Need to **reduce costs** and improve **latency**
- Protect upstream services from overload

### Implementation

```python
"""Caching and rate limiting patterns for MCP servers."""

import time
import hashlib
import json
from collections import defaultdict

class ToolCache:
    """LRU cache with TTL for tool results."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.tool_ttls = {
            "get_weather": 600,      # Cache weather for 10 min
            "search_web": 60,        # Cache search for 1 min
            "get_stock_price": 30,   # Cache stocks for 30 sec
            "get_user_profile": 0,   # Never cache (always fresh)
        }
    
    def _key(self, tool_name: str, arguments: dict) -> str:
        arg_str = json.dumps(arguments, sort_keys=True)
        return hashlib.sha256(f"{tool_name}:{arg_str}".encode()).hexdigest()
    
    def get(self, tool_name: str, arguments: dict):
        ttl = self.tool_ttls.get(tool_name, self.default_ttl)
        if ttl == 0:
            return None  # Caching disabled for this tool
        
        key = self._key(tool_name, arguments)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < ttl:
                return result  # Cache hit
            del self.cache[key]  # Expired
        return None
    
    def set(self, tool_name: str, arguments: dict, result):
        ttl = self.tool_ttls.get(tool_name, self.default_ttl)
        if ttl == 0:
            return
        
        key = self._key(tool_name, arguments)
        self.cache[key] = (result, time.time())
        
        # Evict oldest if over max size
        if len(self.cache) > self.max_size:
            oldest = min(self.cache, key=lambda k: self.cache[k][1])
            del self.cache[oldest]


class RateLimiter:
    """Token bucket rate limiter per tool."""
    
    def __init__(self):
        self.limits = {
            "search_web": {"calls_per_minute": 30},
            "send_email": {"calls_per_minute": 10},
            "default": {"calls_per_minute": 60},
        }
        self.buckets = defaultdict(list)
    
    def check(self, tool_name: str) -> bool:
        config = self.limits.get(tool_name, self.limits["default"])
        limit = config["calls_per_minute"]
        
        now = time.time()
        window = now - 60
        
        # Remove old entries
        self.buckets[tool_name] = [
            t for t in self.buckets[tool_name] if t > window
        ]
        
        if len(self.buckets[tool_name]) >= limit:
            return False
        
        self.buckets[tool_name].append(now)
        return True
```

---

## Pattern 10: Multi-Tenant Server

### When to Use
- One server serves **multiple users or organizations**
- Need **data isolation** between tenants
- Deploying MCP servers as a **shared service**

### Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Tenant A  │  │ Tenant B  │  │ Tenant C  │
│ (Client)  │  │ (Client)  │  │ (Client)  │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
           ┌────────┴────────┐
           │  MULTI-TENANT   │
           │  MCP SERVER     │
           │                 │
           │  Auth → Route   │
           │  to tenant DB   │
           └─────────────────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 ┌─────────┐  ┌─────────┐  ┌─────────┐
 │ DB: A   │  │ DB: B   │  │ DB: C   │
 └─────────┘  └─────────┘  └─────────┘
```

### Implementation Sketch

```python
"""Multi-tenant MCP server with data isolation."""

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Extract tenant from session context
    tenant_id = get_current_tenant()
    
    # Get tenant-specific connection
    db = await get_tenant_db(tenant_id)
    
    if name == "query_data":
        # Automatically scope queries to tenant
        sql = arguments["sql"]
        results = await db.fetch(sql)
        return [TextContent(type="text", text=json.dumps(results, default=str))]
```

---

## Pattern Selection Guide

```
┌─────────────────────────────────────────────────────────────────┐
│                   WHICH PATTERN DO I NEED?                       │
│                                                                  │
│  How many data sources?                                          │
│  ├── 1 → Pattern 1: Single Server                               │
│  ├── 2-5 → Do they share auth/logic?                            │
│  │         ├── Yes → Pattern 3: Gateway                         │
│  │         └── No  → Pattern 2: Multi-Server                    │
│  └── 5+ → Pattern 3: Gateway + Pattern 7: Dynamic              │
│                                                                  │
│  Need caching/rate limiting?                                     │
│  └── Yes → Pattern 9 (add to any pattern)                       │
│                                                                  │
│  Need auth/logging layer?                                        │
│  └── Yes → Pattern 6: Proxy Middleware                          │
│                                                                  │
│  Data access primary?                                            │
│  └── Yes → Pattern 4: Resource-First                            │
│                                                                  │
│  Tools depend on each other?                                     │
│  └── Yes → Pattern 5: Tool Chaining                             │
│                                                                  │
│  Multiple users/orgs?                                            │
│  └── Yes → Pattern 10: Multi-Tenant                             │
│                                                                  │
│  Need real-time updates?                                         │
│  └── Yes → Pattern 8: Event-Driven                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Anti-Patterns to Avoid

### ❌ God Server
**Problem**: One MCP server that does everything — database, email, search, files, etc.
**Fix**: Split into focused servers or use the Gateway pattern.

### ❌ Leaky Abstractions
**Problem**: Exposing raw SQL or internal API details through tool descriptions.
**Fix**: Provide high-level, domain-specific tools (e.g., `search_customers` not `execute_sql`).

### ❌ Stateful Tools Without Cleanup
**Problem**: Tools that create temporary resources (files, connections) without cleanup.
**Fix**: Implement proper lifecycle management and cleanup on session end.

### ❌ Missing Error Context
**Problem**: Tools that return generic errors without actionable information.
**Fix**: Return structured errors with suggestions for the LLM to retry or adjust.

### ❌ Unbounded Tool Calls
**Problem**: No limits on how many times the agent can call expensive tools.
**Fix**: Implement rate limiting and cost tracking (Pattern 9).

### ❌ Tool Description Overload
**Problem**: Tools with vague or overly long descriptions that confuse the LLM.
**Fix**: Keep descriptions concise (1-2 sentences), with clear parameter docs.

---

## 📚 Further Reading

- [MCP Specification — Architecture](https://spec.modelcontextprotocol.io/specification/architecture/)
- [Building MCP Servers Guide](https://modelcontextprotocol.io/docs/guides/building-servers)
- [MCP Best Practices](https://modelcontextprotocol.io/docs/guides/best-practices)

---

## 🔗 Related Materials

| Resource | Link |
|----------|------|
| MCP Fundamentals | [01-mcp-fundamentals.md](./01-mcp-fundamentals.md) |
| MCP Use Cases | [03-mcp-use-cases.md](./03-mcp-use-cases.md) |
| Tool Use Pattern | [08-agentic-patterns/05-tool-use.md](../08-agentic-patterns/05-tool-use.md) |
