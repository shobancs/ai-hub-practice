# Context Engineering

## What is Context Engineering?

**Context Engineering** is the discipline of designing and managing the *information environment* that surrounds a prompt before it reaches an AI model. While prompt engineering focuses on *how you ask*, context engineering focuses on *what the model knows* when it answers.

> **Analogy**: If prompt engineering is writing a good exam question, context engineering is preparing the entire briefing packet a consultant receives before walking into a meeting.

## Why Context Engineering Matters

A perfectly crafted prompt will still fail if the model lacks the right information:

### ❌ Great Prompt, No Context
```
You are a senior backend engineer.
Review this API endpoint for security vulnerabilities and suggest fixes.
```
**Result**: Generic security advice — the model doesn't know your stack, auth system, or threat model.

### ✅ Great Prompt, Great Context
```
System: You are a senior backend engineer specializing in Node.js/Express security.

Context:
- Application: Healthcare patient portal (HIPAA-compliant)
- Auth: OAuth 2.0 with JWT tokens
- Database: PostgreSQL with row-level security
- Known issue: Recently failed penetration test on input validation
- Code: [relevant endpoint code injected here]

Task: Review this API endpoint for security vulnerabilities and suggest fixes.
```
**Result**: Targeted, actionable security review with relevant recommendations.

## Context Engineering vs Prompt Engineering

| Aspect | Prompt Engineering | Context Engineering |
|---|---|---|
| **Focus** | Wording & structure of the request | Information selection & orchestration |
| **Scope** | Single query/interaction | Entire information pipeline |
| **Question** | "How do I phrase this?" | "What does the model need to know?" |
| **Analogy** | Writing a good question | Preparing a briefing document |
| **Operates at** | Request level | System/architecture level |
| **Changes** | Per-query | Per-system or per-session |

## The Context Window: Your Working Space

### What Goes Into the Context Window?

```
┌──────────────────────────────────────────────┐
│              CONTEXT WINDOW                   │
│                                               │
│  ┌─────────────────────────────────────────┐  │
│  │ System Prompt / Instructions            │  │
│  │ (Role, behavior, constraints)           │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ Retrieved Knowledge (RAG)               │  │
│  │ (Docs, code, database results)          │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ Conversation History / Memory           │  │
│  │ (Prior messages, summaries)             │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ Tool Outputs / Function Results         │  │
│  │ (API responses, calculations)           │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ User Metadata & Preferences             │  │
│  │ (Role, permissions, settings)           │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ Current User Prompt                     │  │
│  │ (The actual question/request)           │  │
│  └─────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Context Budget Management

Models have finite context windows. Context engineering means being **strategic** about what to include:

```python
# Context budget example (GPT-4 Turbo: 128K tokens)

context_budget = {
    "system_prompt": 500,        # ~1% - Core instructions
    "retrieved_docs": 8000,      # ~6% - RAG results
    "conversation_history": 4000, # ~3% - Recent messages
    "tool_outputs": 2000,        # ~2% - Function results
    "user_metadata": 200,        # <1% - User preferences
    "current_prompt": 500,       # ~1% - User's question
    "reserved_for_output": 4000, # ~3% - Model's response
    # Remaining: ~84% buffer for complex tasks
}
```

## Core Components of Context Engineering

### 1. **System Prompts & Instructions**

The foundational context that defines model behavior.

```
You are a medical coding assistant for a US-based hospital network.

Rules:
- Always reference ICD-10 codes
- Flag any codes that may require prior authorization
- Never provide medical diagnoses — only coding suggestions
- When uncertain, list multiple possible codes with confidence levels
- Cite the specific ICD-10 guideline section when applicable

Current user role: Certified Medical Coder (CPC)
Department: Cardiology
```

### 2. **Retrieval-Augmented Generation (RAG)**

Dynamically fetching relevant information at query time.

```python
def build_context(user_query: str) -> str:
    """Context engineering pipeline for a support chatbot."""
    
    # 1. Retrieve relevant documentation
    docs = vector_store.similarity_search(user_query, k=5)
    
    # 2. Retrieve user's account information
    user_info = get_user_profile(session.user_id)
    
    # 3. Retrieve recent support tickets
    recent_tickets = get_recent_tickets(session.user_id, limit=3)
    
    # 4. Retrieve product-specific context
    product = detect_product(user_query)
    product_context = get_product_docs(product)
    
    # 5. Assemble context with priority ordering
    context = f"""
    ## User Profile
    Name: {user_info.name}
    Plan: {user_info.plan}
    Account age: {user_info.tenure}
    
    ## Recent Support History
    {format_tickets(recent_tickets)}
    
    ## Relevant Documentation
    {format_docs(docs)}
    
    ## Product Information
    {product_context}
    """
    
    return context
```

### 3. **Conversation History & Memory**

Managing what the model remembers across turns.

```python
# Naive approach: dump all messages (wasteful, hits token limits)
messages = conversation.get_all_messages()  # ❌

# Context-engineered approach: smart summarization
def manage_conversation_context(messages: list) -> list:
    """Keep recent messages detailed, summarize older ones."""
    
    recent = messages[-6:]  # Keep last 3 exchanges verbatim
    
    older = messages[:-6]
    if older:
        summary = summarize(older)  # Compress older context
        return [{"role": "system", "content": f"Prior conversation summary: {summary}"}] + recent
    
    return recent
```

### 4. **Tool Outputs & Function Results**

Injecting real-time data from external tools.

```python
# Before answering "What's the status of order #12345?"
# Context engineering gathers:

tool_results = {
    "order_lookup": {
        "order_id": "12345",
        "status": "shipped",
        "tracking": "1Z999AA10123456784",
        "estimated_delivery": "2026-03-02"
    },
    "shipping_carrier": {
        "last_scan": "Distribution Center, Chicago IL",
        "scan_time": "2026-02-27 14:30 CST"
    }
}
# These results are injected into context before the model responds
```

### 5. **User Metadata & Personalization**

Tailoring context based on who is asking.

```python
user_context = {
    "role": "junior_developer",
    "preferred_language": "Python",
    "experience_level": "1 year",
    "current_project": "REST API with FastAPI",
    "learning_goals": ["async programming", "testing"],
    "communication_preference": "detailed explanations with examples"
}
# Model automatically adjusts depth and terminology
```

## Context Engineering Patterns

### Pattern 1: **Layered Context**

Build context in layers from general to specific.

```
Layer 1 (System):    Company policies, brand voice, general rules
Layer 2 (Domain):    Product documentation, technical specs
Layer 3 (Session):   Current user profile, conversation history  
Layer 4 (Query):     Retrieved docs relevant to this specific question
Layer 5 (Real-time): Tool outputs, live data, current state
```

### Pattern 2: **Context Filtering**

Not all retrieved information is relevant — filter aggressively.

```python
def filter_context(retrieved_docs, user_query, max_tokens=4000):
    """Score and filter retrieved documents by relevance."""
    
    scored_docs = []
    for doc in retrieved_docs:
        score = calculate_relevance(doc, user_query)
        recency_boost = get_recency_score(doc.timestamp)
        authority_boost = get_source_authority(doc.source)
        final_score = score * 0.6 + recency_boost * 0.2 + authority_boost * 0.2
        scored_docs.append((doc, final_score))
    
    # Sort by score and fit within token budget
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    selected = []
    token_count = 0
    for doc, score in scored_docs:
        doc_tokens = count_tokens(doc.content)
        if token_count + doc_tokens <= max_tokens:
            selected.append(doc)
            token_count += doc_tokens
    
    return selected
```

### Pattern 3: **Dynamic Context Assembly**

Adjust context based on query type.

```python
def assemble_context(query_type: str, user_query: str) -> dict:
    """Build different context packages for different query types."""
    
    base_context = get_system_prompt()
    
    if query_type == "troubleshooting":
        return {
            "system": base_context,
            "knowledge": get_troubleshooting_docs(user_query),
            "history": get_error_logs(user_query),
            "similar_cases": get_resolved_tickets(user_query),
        }
    elif query_type == "code_generation":
        return {
            "system": base_context,
            "codebase": get_relevant_source_files(user_query),
            "style_guide": get_coding_standards(),
            "dependencies": get_project_dependencies(),
        }
    elif query_type == "data_analysis":
        return {
            "system": base_context,
            "schema": get_database_schema(),
            "sample_data": get_sample_rows(user_query),
            "prior_queries": get_related_queries(user_query),
        }
```

### Pattern 4: **Context Compression**

Fit more information into limited windows.

```python
# Instead of raw document text...
raw = """
The quarterly financial report for Q3 2025 shows that the company's 
total revenue was $45.2 million, which represents an increase of 12% 
compared to Q2 2025 when revenue was $40.4 million. The operating 
expenses for the quarter were $38.1 million, resulting in an operating 
profit of $7.1 million...
[2000 more words]
"""

# ...use structured summaries
compressed = """
Q3 2025 Financial Summary:
- Revenue: $45.2M (+12% QoQ)
- Operating expenses: $38.1M
- Operating profit: $7.1M
- Key driver: Enterprise SaaS growth (+23%)
- Risk: Rising infrastructure costs (+8%)
"""
```

## Context Engineering in AI Agents

For autonomous AI agents, context engineering becomes critical:

```python
class AgentContextManager:
    """Manages context for an AI agent across multiple steps."""
    
    def __init__(self, agent_config):
        self.working_memory = []      # Current task context
        self.episodic_memory = []     # Past task summaries
        self.semantic_memory = None   # Knowledge base connection
        self.tool_history = []        # Recent tool results
    
    def build_step_context(self, current_goal, step_number):
        """Build context for each agent reasoning step."""
        return {
            "goal": current_goal,
            "progress": self.get_progress_summary(),
            "working_memory": self.working_memory[-10:],  # Recent items
            "relevant_knowledge": self.semantic_memory.query(current_goal),
            "tool_results": self.tool_history[-3:],  # Last 3 tool calls
            "constraints": self.get_active_constraints(),
            "step": step_number,
        }
    
    def update_after_step(self, step_result):
        """Update context after each agent step."""
        self.working_memory.append(step_result.summary)
        if step_result.tool_used:
            self.tool_history.append(step_result.tool_output)
        
        # Compress if getting too large
        if self.get_total_tokens() > self.token_budget * 0.8:
            self.compress_working_memory()
```

## Common Mistakes in Context Engineering

### ❌ Context Overload
```
Dumping every document into the context window
→ Dilutes relevant information, confuses the model
```

### ❌ Stale Context
```
Using cached context that's out of date
→ Model gives answers based on old information
```

### ❌ Missing Critical Context
```
Asking for code review without including the codebase conventions
→ Model suggests changes that violate team standards
```

### ❌ Unstructured Context
```
Injecting raw text blobs without labels or organization
→ Model struggles to find relevant pieces
```

### ❌ Ignoring Context Window Limits
```
Exceeding token limits silently truncates important information
→ Model loses access to key context (often system prompts)
```

## Best Practices Checklist

Before deploying an AI system, verify:

- [ ] Have I identified all context sources the model needs?
- [ ] Is the context prioritized (most important first)?
- [ ] Am I within token budget with room for the response?
- [ ] Is retrieved context filtered for relevance?
- [ ] Is the context structured and labeled clearly?
- [ ] Do I handle stale/outdated context?
- [ ] Is conversation history summarized rather than dumped?
- [ ] Are tool outputs formatted consistently?
- [ ] Have I tested with missing/partial context?
- [ ] Is the context pipeline monitored and observable?

## Key Takeaway

> **Prompt engineering is writing the question. Context engineering is building the entire information system that ensures the model has what it needs to answer correctly.** As AI applications grow in complexity — from simple chatbots to autonomous agents — context engineering becomes the primary driver of output quality.

---

**Previous**: [Prompt Engineering Basics](./01-prompt-basics.md)  
**Next**: [Intent Engineering](./03-intent-engineering.md)
