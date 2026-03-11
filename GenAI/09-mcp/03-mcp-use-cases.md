# MCP Use Cases — Real-World Applications of Model Context Protocol

> Practical examples of how MCP transforms AI agent integrations across industries

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Developer Tooling](#developer-tooling)
3. [Data & Analytics](#data--analytics)
4. [Enterprise Operations](#enterprise-operations)
5. [Customer-Facing Applications](#customer-facing-applications)
6. [DevOps & Infrastructure](#devops--infrastructure)
7. [Content & Knowledge Management](#content--knowledge-management)
8. [Security & Compliance](#security--compliance)
9. [Industry-Specific Use Cases](#industry-specific-use-cases)
10. [Building Your Own MCP Server — Starter Templates](#building-your-own-mcp-server--starter-templates)

---

## Overview

MCP enables AI agents to interact with **any external system** through a standardized protocol. Below are categorized, real-world use cases — each with architecture, tool designs, and implementation guidance.

```
┌────────────────────────────────────────────────────────────────┐
│                 MCP USE CASE CATEGORIES                         │
│                                                                 │
│  🔧 Developer Tooling      📊 Data & Analytics                 │
│  ─────────────────          ─────────────────                   │
│  • Code repo management     • Database exploration              │
│  • CI/CD pipelines          • BI dashboard queries              │
│  • Issue tracking           • Data pipeline monitoring          │
│                                                                 │
│  🏢 Enterprise Ops          💬 Customer-Facing                  │
│  ────────────────           ─────────────────                   │
│  • CRM integration          • Support chatbots                  │
│  • Document management      • E-commerce assistants             │
│  • Internal knowledge base  • Personalized recommendations      │
│                                                                 │
│  ⚙️ DevOps & Infra          📝 Content & Knowledge             │
│  ──────────────             ──────────────────                  │
│  • Cloud resource mgmt      • CMS integration                   │
│  • Monitoring & alerting     • Search engines                    │
│  • Incident response         • Wiki & documentation              │
└────────────────────────────────────────────────────────────────┘
```

---

## Developer Tooling

### Use Case 1: GitHub Repository Manager

**Scenario**: An AI coding assistant that can browse repos, create issues, manage PRs, and search code — all through MCP.

```
┌──────────────────────────────────────────────────────────┐
│                GITHUB MCP SERVER                          │
│                                                           │
│  Tools:                        Resources:                 │
│  ─────                         ──────────                 │
│  create_issue()                repo://owner/repo/README   │
│  list_pull_requests()          repo://owner/repo/tree     │
│  create_pull_request()         repo://owner/repo/issues   │
│  search_code()                                            │
│  get_file_contents()           Prompts:                   │
│  create_branch()               ───────                    │
│  merge_pull_request()          code_review                │
│  add_comment()                 pr_description             │
│                                commit_message             │
└──────────────────────────────────────────────────────────┘
```

**Tool Design**:
```python
tools = [
    Tool(
        name="search_code",
        description="Search for code across repositories",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Code search query"},
                "repo": {"type": "string", "description": "owner/repo format"},
                "language": {"type": "string", "description": "Filter by language"}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="create_issue",
        description="Create a new GitHub issue",
        inputSchema={
            "type": "object",
            "properties": {
                "repo": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}},
                "assignees": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["repo", "title", "body"]
        }
    )
]
```

**Agent Interaction Example**:
```
User: "Find all TODO comments in our auth service and create issues for each"

Agent:
  1. search_code(query="TODO", repo="acme/auth-service")
  2. For each TODO found:
     create_issue(repo="acme/auth-service", title="TODO: ...", labels=["tech-debt"])
  3. "Created 5 issues for TODO items found in the auth service"
```

---

### Use Case 2: CI/CD Pipeline Controller

**Scenario**: Agent that monitors, triggers, and troubleshoots CI/CD pipelines.

```
┌──────────────────────────────────────────────────────────┐
│              CI/CD MCP SERVER                             │
│                                                           │
│  Tools:                                                   │
│  ─────                                                    │
│  trigger_pipeline(repo, branch)                          │
│  get_pipeline_status(pipeline_id)                        │
│  get_build_logs(build_id, tail_lines)                    │
│  list_recent_builds(repo, status_filter)                 │
│  retry_failed_job(job_id)                                │
│  cancel_pipeline(pipeline_id)                            │
│  get_test_results(build_id)                              │
│  deploy_to_environment(build_id, environment)            │
│                                                           │
│  Resources:                                               │
│  ──────────                                               │
│  pipeline://configs                                       │
│  pipeline://environments                                  │
│  pipeline://deployment-history                            │
└──────────────────────────────────────────────────────────┘
```

**Agent Interaction**:
```
User: "The staging deployment failed — investigate and fix"

Agent:
  1. list_recent_builds(repo="acme/api", status_filter="failed")
  2. get_build_logs(build_id="12345", tail_lines=100)
  3. get_test_results(build_id="12345")
  4. "The failure is in 3 integration tests due to a database migration
     issue. The migration V15 has a column type mismatch. Would you
     like me to retry after the fix is merged?"
```

---

### Use Case 3: Code Review Assistant

**Scenario**: Agent reviews PRs, suggests improvements, and checks for common issues.

```python
# Tools for code review MCP server
tools = [
    "get_pr_diff(repo, pr_number) → file changes",
    "get_pr_comments(repo, pr_number) → existing review comments",
    "add_review_comment(repo, pr_number, file, line, body) → comment",
    "approve_pr(repo, pr_number, body) → approval",
    "request_changes(repo, pr_number, body) → change request",
    "check_lint_results(repo, pr_number) → lint issues",
    "check_test_coverage(repo, pr_number) → coverage report",
]

# Prompts for consistent review style
prompts = [
    Prompt(
        name="security_review",
        description="Review code for security vulnerabilities",
        arguments=[PromptArgument(name="diff", required=True)]
    ),
    Prompt(
        name="performance_review",
        description="Review code for performance issues",
        arguments=[PromptArgument(name="diff", required=True)]
    )
]
```

---

## Data & Analytics

### Use Case 4: Database Explorer & Analyst

**Scenario**: AI assistant that explores database schemas, writes queries, and generates insights.

```
┌──────────────────────────────────────────────────────────┐
│            DATABASE EXPLORER MCP SERVER                    │
│                                                           │
│  Tools:                        Resources:                 │
│  ─────                         ──────────                 │
│  execute_query(sql)            db://schema/tables          │
│  explain_query(sql)            db://schema/table/{name}    │
│  get_sample_data(table, n)     db://stats/table_sizes      │
│  list_tables()                 db://stats/slow_queries     │
│  describe_table(name)                                     │
│  get_relationships(table)      Prompts:                   │
│  suggest_indexes(table)        ───────                    │
│  export_csv(sql, filename)     query_builder               │
│                                data_analysis               │
│                                migration_script            │
└──────────────────────────────────────────────────────────┘
```

**Agent Interaction**:
```
User: "What are our top 10 customers by revenue this quarter?"

Agent:
  1. list_tables()  → finds "orders", "customers", "payments"
  2. describe_table("orders")  → sees columns and types
  3. describe_table("customers")
  4. execute_query("""
       SELECT c.name, SUM(o.total) as revenue
       FROM customers c
       JOIN orders o ON c.id = o.customer_id
       WHERE o.created_at >= '2026-01-01'
       GROUP BY c.name
       ORDER BY revenue DESC
       LIMIT 10
     """)
  5. Returns formatted table with results
```

---

### Use Case 5: Data Pipeline Monitor

**Scenario**: Monitor ETL/ELT pipelines, check data quality, alert on anomalies.

```python
tools = [
    Tool(name="list_pipelines", description="List all data pipelines and their status"),
    Tool(name="get_pipeline_run", description="Get details of a specific pipeline run",
         inputSchema={"type": "object", "properties": {
             "pipeline_id": {"type": "string"},
             "run_id": {"type": "string"}
         }}),
    Tool(name="check_data_quality", description="Run data quality checks on a table",
         inputSchema={"type": "object", "properties": {
             "table": {"type": "string"},
             "checks": {"type": "array", "items": {"type": "string"},
                        "description": "Quality checks: nulls, duplicates, freshness, schema"}
         }}),
    Tool(name="get_row_counts", description="Get row counts for tables with time comparison",
         inputSchema={"type": "object", "properties": {
             "tables": {"type": "array", "items": {"type": "string"}},
             "compare_with": {"type": "string", "enum": ["yesterday", "last_week", "last_month"]}
         }}),
    Tool(name="trigger_backfill", description="Trigger a data backfill for a date range",
         inputSchema={"type": "object", "properties": {
             "pipeline_id": {"type": "string"},
             "start_date": {"type": "string"},
             "end_date": {"type": "string"}
         }})
]
```

---

### Use Case 6: Business Intelligence Assistant

**Scenario**: Query BI dashboards, generate reports, and answer business questions using data.

```
Agent → MCP Server → Connects to:
  ├── Looker / Tableau / Metabase API
  ├── Data Warehouse (Snowflake / BigQuery)
  └── Google Sheets / Excel for output

Tools:
  - query_dashboard(dashboard_id, filters)
  - get_metric(metric_name, timeframe, dimensions)
  - create_report(title, sections, format)
  - export_to_sheets(data, spreadsheet_id, sheet_name)
  - schedule_report(report_config, frequency)
```

---

## Enterprise Operations

### Use Case 7: CRM Integration (Salesforce / HubSpot)

**Scenario**: AI sales assistant that accesses customer data, updates records, and manages opportunities.

```
┌──────────────────────────────────────────────────────────┐
│                  CRM MCP SERVER                           │
│                                                           │
│  Tools:                                                   │
│  ─────                                                    │
│  search_contacts(query) → matching contacts               │
│  get_contact_details(id) → full contact record            │
│  update_contact(id, fields) → updated record              │
│  create_opportunity(data) → new opportunity               │
│  list_opportunities(filters) → pipeline view              │
│  log_activity(contact_id, type, notes) → activity logged  │
│  get_deal_history(opportunity_id) → timeline              │
│  generate_proposal(opportunity_id) → proposal draft       │
│                                                           │
│  Resources:                                               │
│  ──────────                                               │
│  crm://pipeline/stages → deal stage definitions           │
│  crm://templates/email → email templates                  │
│  crm://fields/contact → custom field definitions          │
└──────────────────────────────────────────────────────────┘
```

**Agent Interaction**:
```
User: "Prepare a summary of our interactions with Acme Corp before my call"

Agent:
  1. search_contacts(query="Acme Corp")
  2. get_contact_details(id="C-12345")
  3. get_deal_history(opportunity_id="OPP-789")
  4. Returns: "Acme Corp (Enterprise plan) — 3 meetings in last 30 days,
     last discussed pricing concerns. Open deal: $150K, at Negotiation stage.
     Key contact: Jane Smith (VP Engineering). Recent notes: 'Need SOC2
     compliance docs before signing.'"
```

---

### Use Case 8: Internal Knowledge Base / Wiki

**Scenario**: AI assistant that searches and answers from internal documentation (Confluence, Notion, SharePoint).

```python
# Knowledge base MCP server tools
tools = [
    Tool(
        name="search_knowledge_base",
        description="Semantic search across all internal documentation",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query"},
                "space": {"type": "string", "description": "Filter by space/team", 
                         "enum": ["engineering", "product", "hr", "sales", "all"]},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_page",
        description="Get full content of a knowledge base page by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string"}
            },
            "required": ["page_id"]
        }
    ),
    Tool(
        name="list_recent_updates",
        description="List recently updated pages in a space",
        inputSchema={
            "type": "object",
            "properties": {
                "space": {"type": "string"},
                "days": {"type": "integer", "default": 7}
            },
            "required": ["space"]
        }
    ),
    Tool(
        name="create_page",
        description="Create a new knowledge base page",
        inputSchema={
            "type": "object",
            "properties": {
                "space": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string", "description": "Page content in Markdown"},
                "parent_page_id": {"type": "string"}
            },
            "required": ["space", "title", "content"]
        }
    )
]
```

---

### Use Case 9: HR & People Operations

**Scenario**: Employee self-service agent for PTO, policies, benefits, and onboarding.

```
Tools:
  - check_pto_balance(employee_id) → days remaining
  - request_pto(employee_id, start_date, end_date, type) → request status
  - search_policies(query) → matching HR policies
  - get_benefits_info(plan_type) → plan details
  - lookup_org_chart(name_or_dept) → reporting structure
  - get_onboarding_checklist(role) → onboarding steps

Resources:
  - hr://policies/handbook → employee handbook
  - hr://benefits/2026 → current year benefits guide
  - hr://holidays/2026 → company holidays
```

---

## Customer-Facing Applications

### Use Case 10: E-Commerce Shopping Assistant

**Scenario**: AI shopping assistant that searches products, checks inventory, and manages orders.

```
┌──────────────────────────────────────────────────────────┐
│            E-COMMERCE MCP SERVER                          │
│                                                           │
│  Tools:                                                   │
│  ─────                                                    │
│  search_products(query, filters) → product list           │
│  get_product_details(sku) → full product info             │
│  check_inventory(sku, location) → stock status            │
│  get_price_history(sku) → price trends                    │
│  compare_products(skus[]) → comparison table              │
│  add_to_cart(user_id, sku, quantity) → cart update         │
│  get_order_status(order_id) → tracking info               │
│  initiate_return(order_id, items, reason) → return label  │
│                                                           │
│  Resources:                                               │
│  ──────────                                               │
│  store://categories → product category tree               │
│  store://promotions/active → current promotions           │
│  store://shipping/rates → shipping options                │
└──────────────────────────────────────────────────────────┘
```

**Agent Interaction**:
```
User: "I'm looking for a waterproof bluetooth speaker under $50"

Agent:
  1. search_products(query="bluetooth speaker waterproof", filters={"max_price": 50})
  2. For top 3 results: get_product_details(sku)
  3. compare_products(skus=["SPK-001", "SPK-042", "SPK-099"])
  4. "I found 3 great options under $50:
     1. SoundBlast Mini ($39.99) — 4.5★, 12hr battery, IPX7
     2. AquaBeats Pro ($45.99) — 4.7★, 20hr battery, IPX8
     3. WaveRider ($29.99) — 4.2★, 8hr battery, IPX5
     The AquaBeats Pro has the best reviews and battery life.
     Would you like to add one to your cart?"
```

---

### Use Case 11: Customer Support Agent

**Scenario**: AI support agent that resolves tickets using knowledge base, order data, and CRM.

```
┌──────────────────────────────────────────────────────────────┐
│           CUSTOMER SUPPORT — MULTI-SERVER SETUP               │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ Knowledge   │  │  Orders      │  │  Ticketing          │ │
│  │ Base Server │  │  Server      │  │  Server             │ │
│  │             │  │              │  │                     │ │
│  │ search_faq  │  │ get_order    │  │ create_ticket       │ │
│  │ get_article │  │ track_ship   │  │ update_ticket       │ │
│  │ find_policy │  │ process_     │  │ escalate_ticket     │ │
│  │             │  │  refund      │  │ add_internal_note   │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
│                                                               │
│  Agent decides which server's tools to use based on the query │
└──────────────────────────────────────────────────────────────┘
```

**Agent Interaction**:
```
User: "My order #ORD-5678 hasn't arrived and it's been 2 weeks"

Agent:
  1. get_order(order_id="ORD-5678")
     → Shipped 12 days ago, tracking shows "stuck in transit"
  2. search_faq(query="delayed shipment policy")
     → Policy: Refund or reship after 10 business days
  3. "Your order appears stuck in transit for 12 days. Per our policy,
     you're eligible for a full refund or free reshipment. Which
     would you prefer?"
  
User: "Refund please"

Agent:
  4. process_refund(order_id="ORD-5678", reason="delayed_shipment")
  5. create_ticket(subject="Refund processed - delayed order", ...)
  6. "Done! A refund of $89.99 has been processed to your original
     payment method. You'll see it in 3-5 business days. Ticket
     #TKT-9012 created for your records."
```

---

## DevOps & Infrastructure

### Use Case 12: Cloud Resource Manager

**Scenario**: AI assistant that manages cloud infrastructure (AWS/Azure/GCP) through MCP.

```python
tools = [
    Tool(name="list_resources", description="List cloud resources by type and region",
         inputSchema={"type": "object", "properties": {
             "resource_type": {"type": "string", "enum": ["vm", "database", "storage", "network"]},
             "region": {"type": "string"},
             "status": {"type": "string", "enum": ["running", "stopped", "all"]}
         }}),
    
    Tool(name="get_resource_metrics", description="Get metrics for a cloud resource",
         inputSchema={"type": "object", "properties": {
             "resource_id": {"type": "string"},
             "metric": {"type": "string", "enum": ["cpu", "memory", "disk", "network"]},
             "period": {"type": "string", "enum": ["1h", "6h", "24h", "7d"]}
         }}),
    
    Tool(name="scale_resource", description="Scale a cloud resource up or down",
         inputSchema={"type": "object", "properties": {
             "resource_id": {"type": "string"},
             "action": {"type": "string", "enum": ["scale_up", "scale_down", "auto"]},
             "target_size": {"type": "string"}
         }}),
    
    Tool(name="get_cost_report", description="Get cost breakdown for resources",
         inputSchema={"type": "object", "properties": {
             "period": {"type": "string", "enum": ["today", "this_week", "this_month"]},
             "group_by": {"type": "string", "enum": ["service", "team", "region", "tag"]}
         }}),
    
    Tool(name="check_security_compliance", description="Run security compliance checks",
         inputSchema={"type": "object", "properties": {
             "resource_id": {"type": "string"},
             "framework": {"type": "string", "enum": ["cis", "soc2", "hipaa", "pci"]}
         }})
]
```

---

### Use Case 13: Incident Response System

**Scenario**: AI on-call assistant that helps diagnose and resolve production incidents.

```
┌──────────────────────────────────────────────────────────┐
│            INCIDENT RESPONSE MCP SERVER                    │
│                                                           │
│  DIAGNOSTIC TOOLS:                                        │
│  check_service_health(service) → status + metrics         │
│  get_error_logs(service, severity, minutes) → log entries │
│  get_recent_deployments(service) → deploy history         │
│  query_metrics(service, metric, window) → time series     │
│  trace_request(trace_id) → distributed trace              │
│                                                           │
│  ACTION TOOLS:                                            │
│  rollback_deployment(service) → rollback status           │
│  restart_service(service) → restart confirmation          │
│  scale_replicas(service, count) → scaling result          │
│  toggle_feature_flag(flag_name, enabled) → flag status    │
│                                                           │
│  COMMUNICATION TOOLS:                                     │
│  create_incident(title, severity) → incident record       │
│  update_incident(id, status, notes) → updated record      │
│  page_oncall(team, message) → page confirmation           │
│  post_status_update(channel, message) → posted            │
└──────────────────────────────────────────────────────────┘
```

**Agent Interaction**:
```
Alert: "HTTP 500 error rate spike on payment-service"

Agent:
  1. check_service_health("payment-service")
     → 23% error rate (normal: <1%)
  2. get_error_logs("payment-service", severity="ERROR", minutes=15)
     → "ConnectionRefusedError: redis-cache:6379"
  3. check_service_health("redis-cache")
     → DOWN — OOM killed 12 minutes ago
  4. create_incident(title="Redis OOM → payment-service 500s", severity="P1")
  5. restart_service("redis-cache")
  6. post_status_update("#incidents", "P1: Payment service errors due to
     Redis OOM. Redis restarted. Monitoring recovery.")
  7. "Root cause: Redis ran out of memory and was killed, causing payment
     service to fail. I've restarted Redis and created incident INC-456.
     Error rate is recovering — currently at 5% and dropping."
```

---

## Content & Knowledge Management

### Use Case 14: CMS & Content Workflow

**Scenario**: AI assistant for content teams — create, edit, publish, and analyze content.

```
Tools:
  - list_articles(status, author, date_range) → article list
  - get_article(id) → full article content
  - create_draft(title, body, category, tags) → new draft
  - update_article(id, changes) → updated article
  - publish_article(id, schedule_time) → published/scheduled
  - get_analytics(article_id, metric) → pageviews, engagement
  - suggest_topics(category, trending) → topic ideas
  - check_seo(article_id) → SEO score + recommendations

Resources:
  - cms://style-guide → brand voice and style guidelines
  - cms://editorial-calendar → upcoming content schedule
  - cms://templates → article templates by type
```

---

### Use Case 15: Semantic Document Search

**Scenario**: MCP server backed by a vector database for semantic search across documents.

```python
"""Vector-search MCP server using ChromaDB."""

import chromadb
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("semantic-search")
chroma = chromadb.PersistentClient(path="./vectordb")
collection = chroma.get_collection("documents")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="semantic_search",
            description="Search documents using natural language. Returns most relevant passages.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language query"},
                    "n_results": {"type": "integer", "default": 5},
                    "filter_source": {"type": "string", "description": "Filter by source: docs, wiki, slack"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="index_document",
            description="Add a document to the search index",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "source": {"type": "string"},
                    "title": {"type": "string"},
                    "url": {"type": "string"}
                },
                "required": ["content", "title"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "semantic_search":
        where = {}
        if "filter_source" in arguments:
            where = {"source": arguments["filter_source"]}
        
        results = collection.query(
            query_texts=[arguments["query"]],
            n_results=arguments.get("n_results", 5),
            where=where if where else None
        )
        
        formatted = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            formatted.append({
                "rank": i + 1,
                "title": meta.get("title", "Untitled"),
                "source": meta.get("source", "unknown"),
                "excerpt": doc[:500],
                "score": results["distances"][0][i] if results["distances"] else None
            })
        
        return [TextContent(type="text", text=json.dumps(formatted, indent=2))]
```

---

## Security & Compliance

### Use Case 16: Security Scanner & Advisor

**Scenario**: MCP server that scans code, checks dependencies, and provides security guidance.

```
┌──────────────────────────────────────────────────────────┐
│            SECURITY MCP SERVER                            │
│                                                           │
│  Tools:                                                   │
│  ─────                                                    │
│  scan_dependencies(project_path) → CVE list               │
│  check_secrets(file_path) → leaked secret findings        │
│  analyze_permissions(resource) → permission audit          │
│  get_cve_details(cve_id) → vulnerability details          │
│  suggest_fix(cve_id, package) → remediation steps         │
│  check_compliance(framework) → compliance report          │
│                                                           │
│  Resources:                                               │
│  ──────────                                               │
│  security://policies/password → password policy           │
│  security://policies/access → access control policy       │
│  security://owasp/top10 → OWASP Top 10 reference         │
└──────────────────────────────────────────────────────────┘
```

---

## Industry-Specific Use Cases

### Healthcare: Patient Record Assistant
```
Tools:
  - search_patient(query) → patient matches (with HIPAA-compliant filtering)
  - get_patient_summary(id) → medical summary
  - check_drug_interactions(medications[]) → interaction warnings
  - get_lab_results(patient_id, test_type) → lab data
  - schedule_appointment(patient_id, provider, datetime) → confirmation
```

### Finance: Trading & Portfolio Assistant
```
Tools:
  - get_market_data(symbol, timeframe) → OHLCV data
  - analyze_portfolio(portfolio_id) → allocation, risk metrics
  - screen_stocks(criteria) → matching stocks
  - get_earnings_calendar(days_ahead) → upcoming earnings
  - calculate_risk_metrics(portfolio_id, metric) → VaR, Sharpe, etc.
```

### Legal: Contract Analysis Assistant
```
Tools:
  - analyze_contract(document_id) → key terms, obligations, risks
  - compare_contracts(doc_id_1, doc_id_2) → differences
  - search_precedents(query) → relevant case law
  - check_compliance(document_id, regulations) → compliance issues
  - generate_clause(type, parameters) → contract clause draft
```

### Education: Learning Management Assistant
```
Tools:
  - get_student_progress(student_id, course_id) → grades, completion
  - create_assignment(course_id, details) → new assignment
  - generate_quiz(topic, difficulty, count) → quiz questions
  - get_class_analytics(course_id) → performance distribution
  - suggest_resources(topic, level) → learning resources
```

---

## Building Your Own MCP Server — Starter Templates

### Template: REST API Wrapper

Use this template when wrapping any REST API as an MCP server:

```python
"""Template: Wrap a REST API as an MCP server.

Replace:
  - API_BASE_URL with your API endpoint
  - Add your tools based on API endpoints
  - Implement authentication
"""

import os
import json
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("api-wrapper")

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.example.com/v1")
API_KEY = os.environ.get("API_KEY", "")

async def api_request(method: str, path: str, **kwargs) -> dict:
    """Make an authenticated API request."""
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}{path}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            **kwargs
        )
        response.raise_for_status()
        return response.json()

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_items",
            description="List items from the API with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["active", "archived", "all"]},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="get_item",
            description="Get details of a specific item by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Item ID"}
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="create_item",
            description="Create a new item",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_items":
            params = {k: v for k, v in arguments.items() if v is not None}
            data = await api_request("GET", "/items", params=params)
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_item":
            data = await api_request("GET", f"/items/{arguments['id']}")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "create_item":
            data = await api_request("POST", "/items", json=arguments)
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        raise ValueError(f"Unknown tool: {name}")
    
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=json.dumps({
            "error": True,
            "status": e.response.status_code,
            "message": str(e)
        }))]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Template: Database Wrapper

```python
"""Template: Wrap a database as an MCP server with read-only access."""

# See Pattern 1 in 02-mcp-patterns.md for full implementation
# Key additions for production:
#   - Connection pooling
#   - Query timeout
#   - SQL injection prevention (parameterized queries)
#   - Row limit enforcement
#   - Schema-level access control
```

---

## Summary: Choosing the Right Use Case

| If You Need... | Start With... |
|----------------|---------------|
| Database access for AI | Use Case 4: Database Explorer |
| Code repo management | Use Case 1: GitHub Manager |
| Customer support automation | Use Case 11: Support Agent |
| Internal knowledge search | Use Case 8: Knowledge Base |
| Production monitoring | Use Case 13: Incident Response |
| Any REST API integration | Starter Template: API Wrapper |

---

## 📚 Further Reading

- [MCP Example Servers](https://github.com/modelcontextprotocol/servers)
- [Building MCP with Python](https://modelcontextprotocol.io/docs/guides/building-servers)
- [MCP Showcase](https://modelcontextprotocol.io/showcase)

---

## 🔗 Related Materials

| Resource | Link |
|----------|------|
| MCP Fundamentals | [01-mcp-fundamentals.md](./01-mcp-fundamentals.md) |
| MCP Patterns | [02-mcp-patterns.md](./02-mcp-patterns.md) |
| Agent Use Cases | [05-advanced/05-agent-use-cases.md](../05-advanced/05-agent-use-cases.md) |
| Agentic AI Tutorial | [05-advanced/02-agentic-ai-tutorial.md](../05-advanced/02-agentic-ai-tutorial.md) |
