# Module 09 — Model Context Protocol (MCP)

> The universal standard for connecting AI agents to tools, data, and services

---

## 🎯 Purpose

This module teaches you **MCP (Model Context Protocol)** — the open standard that solves the N×M integration problem by providing a single protocol for any AI application to connect to any tool or data source.

---

## 📖 Contents

| # | Topic | Description |
|---|-------|-------------|
| 1 | [MCP Fundamentals](./01-mcp-fundamentals.md) | What MCP is, architecture, core concepts, three primitives, transport layer, building servers and clients |
| 2 | [MCP Patterns](./02-mcp-patterns.md) | 10 design patterns: Single Server, Multi-Server, Gateway, Proxy, Dynamic Tools, Caching, and more |
| 3 | [MCP Use Cases](./03-mcp-use-cases.md) | 16 real-world use cases across developer tooling, data analytics, enterprise ops, DevOps, and industry-specific applications |

---

## 🚀 Quick Start

```bash
# Install MCP SDK
pip install mcp

# For HTTP transport support
pip install mcp[sse]

# Run a pre-built MCP server (e.g., filesystem)
npx -y @modelcontextprotocol/server-filesystem /path/to/directory
```

---

## 🗺️ Learning Path

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  01 Fundamentals  │────▶│  02 Patterns      │────▶│  03 Use Cases    │
│                   │     │                   │     │                   │
│  • What is MCP?   │     │  • Single Server  │     │  • Developer      │
│  • Architecture   │     │  • Gateway        │     │  • Enterprise     │
│  • 3 Primitives   │     │  • Proxy          │     │  • DevOps         │
│  • Build Server   │     │  • Dynamic Tools  │     │  • Industry       │
│  • Build Client   │     │  • Caching        │     │  • Templates      │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## 🔗 Related Modules

| Module | Relevance |
|--------|-----------|
| [05-advanced/02-agentic-ai-tutorial.md](../05-advanced/02-agentic-ai-tutorial.md) | Comprehensive Agentic AI tutorial |
| [08-agentic-patterns/05-tool-use.md](../08-agentic-patterns/05-tool-use.md) | Tool Use pattern (MCP standardizes tool access) |
| [08-agentic-patterns/10-mcp.md](../08-agentic-patterns/10-mcp.md) | MCP pattern in the agentic design patterns series |
| [examples/weather_agent/](../examples/weather_agent/) | Working agent example that could be extended with MCP |
