# AI Agents and Workflows

## What are AI Agents?

**AI Agent**: An autonomous system that can perceive its environment, make decisions, and take actions to achieve specific goals.

### Traditional LLM vs. AI Agent

**Traditional LLM (Stateless)**:
```
User: "What's the weather?"
LLM: "I can't check real-time weather."
[End]
```

**AI Agent (Autonomous)**:
```
User: "What's the weather?"
Agent:
  1. Decides to use weather tool
  2. Calls weather API with user's location
  3. Retrieves current conditions
  4. Formats and returns: "It's 72°F and sunny"
[Success]
```

## Key Characteristics of AI Agents

### 1. **Autonomy**
- Makes decisions independently
- Determines which actions to take
- Handles multi-step tasks

### 2. **Tool Use**
- Can call external APIs
- Access databases
- Execute code
- Use calculators, search engines, etc.

### 3. **Memory**
- Maintains conversation context
- Remembers previous actions
- Learns from interactions (in session)

### 4. **Planning**
- Breaks down complex tasks
- Creates action sequences
- Adjusts plans based on results

### 5. **Reasoning**
- Analyzes situations
- Makes logical decisions
- Handles edge cases

## Agent Architecture

### Basic Agent Loop

```
┌─────────────────────────────────────┐
│         User Input/Goal             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Agent (LLM) Reasoning          │
│   "What do I need to do?"           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Decide on Action                │
│  - Use tool                          │
│  - Provide final answer              │
│  - Ask for clarification             │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   ┌─────────┐   ┌──────────┐
   │  Tool   │   │  Respond │
   │  Call   │   │  to User │
   └────┬────┘   └──────────┘
        │
        ▼
   ┌─────────────┐
   │ Observation │
   └──────┬──────┘
          │
          ▼
   [Loop back to reasoning until complete]
```

## ReAct Pattern (Reasoning + Acting)

The most common agent pattern.

### How it Works

**Format**:
```
Thought: [Agent's reasoning]
Action: [Tool to use]
Action Input: [Parameters]
Observation: [Tool result]
... (repeat until solved)
Thought: I now know the final answer
Final Answer: [Response to user]
```

### Example Execution

**User**: "What's 25% of the population of Tokyo?"

```
Thought: I need to find Tokyo's population, then calculate 25%
Action: search
Action Input: "Tokyo population 2026"
Observation: Tokyo has approximately 14 million people

Thought: Now I can calculate 25% of 14 million
Action: calculator
Action Input: 14000000 * 0.25
Observation: 3500000

Thought: I now have the final answer
Final Answer: 25% of Tokyo's population is approximately 3.5 million people
```

## Building an AI Agent

### Simple Agent Implementation

```python
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define available tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. San Francisco"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate, e.g. '2 + 2'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# Tool implementations
def get_weather(location):
    """Mock weather API"""
    # In real implementation, call actual weather API
    weather_data = {
        "San Francisco": "Sunny, 68°F",
        "New York": "Cloudy, 55°F",
        "Tokyo": "Rainy, 60°F",
        "London": "Foggy, 50°F"
    }
    return weather_data.get(location, f"Weather data not available for {location}")

def calculator(expression):
    """Safe calculator"""
    try:
        # Safe eval for simple math
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Map function names to implementations
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "calculator": calculator
}

class SimpleAgent:
    """Basic AI Agent with tool use"""
    
    def __init__(self, model="gpt-4"):
        self.model = model
        self.messages = [
            {
                "role": "system",
                "content": """You are a helpful AI agent with access to tools.
                Use tools when needed to answer questions accurately.
                Think step-by-step and explain your reasoning."""
            }
        ]
    
    def run(self, user_input, max_iterations=5):
        """Execute agent loop"""
        
        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Get agent response
            response = client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # Add assistant response to history
            self.messages.append(assistant_message.model_dump())
            
            # Check if agent wants to use a tool
            if assistant_message.tool_calls:
                print("Agent is using tools...")
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"  Tool: {function_name}")
                    print(f"  Args: {function_args}")
                    
                    # Call the function
                    function_response = TOOL_FUNCTIONS[function_name](**function_args)
                    
                    print(f"  Result: {function_response}")
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response
                    })
            
            else:
                # Agent has final answer
                final_answer = assistant_message.content
                print(f"\nFinal Answer: {final_answer}")
                return final_answer
        
        return "Agent exceeded maximum iterations"

# Example usage
def demo():
    """Demo the agent"""
    print("=" * 60)
    print("AI AGENT DEMO")
    print("=" * 60)
    
    agent = SimpleAgent()
    
    # Example 1: Simple tool use
    print("\n📝 Example 1: Weather Query")
    print("-" * 60)
    agent.run("What's the weather in Tokyo?")
    
    # Example 2: Multi-step reasoning
    print("\n\n📝 Example 2: Calculation")
    print("-" * 60)
    agent = SimpleAgent()  # Fresh agent
    agent.run("If the weather in San Francisco is 68°F, what is that in Celsius?")
    
    # Example 3: No tool needed
    print("\n\n📝 Example 3: Direct Answer")
    print("-" * 60)
    agent = SimpleAgent()  # Fresh agent
    agent.run("What is the capital of France?")

if __name__ == "__main__":
    demo()
```

## Advanced Agent Patterns

### 1. **Plan-and-Execute**

Break down complex tasks into subtasks.

```
User: "Research competitors and write a report"

Plan:
1. Identify top 3 competitors
2. Research each competitor's products
3. Research each competitor's pricing
4. Analyze strengths and weaknesses
5. Write comparative report

Execute each step sequentially
```

### 2. **Multi-Agent System**

Multiple specialized agents working together.

```
┌─────────────────┐
│  Coordinator    │ ← User Request
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│Research│ │Writing │
│ Agent  │ │ Agent  │
└───┬────┘ └────┬───┘
    │           │
    └─────┬─────┘
          ▼
    Combined Result
```

**Example**:
```python
class MultiAgentSystem:
    def __init__(self):
        self.researcher = ResearchAgent()
        self.writer = WritingAgent()
        self.coordinator = CoordinatorAgent()
    
    def execute(self, task):
        # Coordinator breaks down task
        plan = self.coordinator.create_plan(task)
        
        # Assign to specialized agents
        research_data = self.researcher.execute(plan['research'])
        report = self.writer.execute(plan['writing'], research_data)
        
        return report
```

### 3. **Reflexion (Self-Critique)**

Agent evaluates and improves its own outputs.

```
Agent generates output
    ↓
Self-critique: "Is this accurate? Complete? Well-formatted?"
    ↓
If not satisfactory → Regenerate with improvements
    ↓
Repeat until quality threshold met
```

### 4. **Tree of Thoughts**

Explore multiple reasoning paths.

```
                [Problem]
                    │
        ┌───────────┼───────────┐
        │           │           │
    [Path A]    [Path B]    [Path C]
        │           │           │
   [Continue]   [Dead end]  [Continue]
        │                       │
    [Result A]             [Result C]
        │                       │
        └───────────┬───────────┘
                    │
            [Select Best Result]
```

## Real-World Agent Applications

### 1. **Customer Support Agent**

```python
Tools:
- search_knowledge_base()
- create_support_ticket()
- escalate_to_human()
- check_order_status()
- process_refund()

Workflow:
1. Understand customer issue
2. Search knowledge base
3. If solved → Provide answer
4. If not solved → Create ticket or escalate
5. Follow up confirmation
```

### 2. **Data Analysis Agent**

```python
Tools:
- query_database()
- generate_visualization()
- statistical_analysis()
- export_report()

Workflow:
1. Understand analysis request
2. Query relevant data
3. Perform calculations
4. Create visualizations
5. Generate insights
6. Format report
```

### 3. **Research Agent**

```python
Tools:
- web_search()
- scrape_webpage()
- summarize_article()
- fact_check()
- cite_sources()

Workflow:
1. Break down research question
2. Search for sources
3. Extract relevant information
4. Synthesize findings
5. Verify facts
6. Compile report with citations
```

### 4. **Code Assistant Agent**

```python
Tools:
- read_file()
- write_file()
- run_tests()
- search_documentation()
- execute_code()

Workflow:
1. Understand coding task
2. Read existing code
3. Plan changes
4. Implement changes
5. Run tests
6. Fix errors if any
7. Document changes
```

## Agent Frameworks & Libraries

### LangChain Agents

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# Define tools
tools = [
    Tool(
        name="Weather",
        func=get_weather,
        description="Get weather for a location"
    ),
    Tool(
        name="Calculator",
        func=calculator,
        description="Perform calculations"
    )
]

# Create agent
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Run
result = agent_executor.invoke({"input": "What's the weather in Tokyo?"})
```

### AutoGPT Pattern

Fully autonomous agent that:
1. Sets own goals
2. Searches internet
3. Executes code
4. Remembers long-term
5. Self-improves

**Caution**: Requires careful guardrails!

### Microsoft AutoGen

Multi-agent conversation framework:

```python
from autogen import AssistantAgent, UserProxyAgent

# Create agents
assistant = AssistantAgent(name="assistant")
user_proxy = UserProxyAgent(name="user")

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Research the latest AI trends and write a summary"
)
```

## Best Practices

### 1. **Clear Tool Descriptions**
```python
# ❌ Bad
description="Do math"

# ✅ Good
description="Evaluate mathematical expressions like '2+2' or '15*3'. Returns numerical result."
```

### 2. **Error Handling**
```python
def safe_tool_call(tool, **kwargs):
    try:
        return tool(**kwargs)
    except Exception as e:
        return f"Error: {str(e)}. Please try a different approach."
```

### 3. **Iteration Limits**
```python
max_iterations = 10  # Prevent infinite loops
```

### 4. **Cost Controls**
```python
# Track tokens
total_tokens = 0
max_tokens = 100000  # Budget limit

if total_tokens > max_tokens:
    raise BudgetExceededError()
```

### 5. **Human-in-the-Loop**
```python
if action.requires_approval:
    approved = ask_human(action)
    if not approved:
        return "Action rejected by user"
```

## Challenges & Limitations

### 1. **Reliability**
- Agents can make mistakes
- May use wrong tools
- Can get stuck in loops

**Solution**: Add validation, human oversight

### 2. **Cost**
- Multiple LLM calls per task
- Can be expensive for complex tasks

**Solution**: Use cheaper models, cache results

### 3. **Latency**
- Sequential tool use takes time
- User may wait for multiple iterations

**Solution**: Show progress, async execution

### 4. **Security**
- Agents executing code can be risky
- Tool access needs careful control

**Solution**: Sandboxing, permissions, audit logs

## Key Takeaways

✅ AI agents autonomously use tools to achieve goals  
✅ ReAct pattern (Reasoning + Acting) is most common  
✅ Useful for complex, multi-step tasks  
✅ Requires careful design of tools and prompts  
✅ Best with human oversight for critical applications  
✅ Rapidly evolving field with new patterns emerging  

---

**Next**: [Project Ideas](../../06-applications/03-project-ideas.md)
