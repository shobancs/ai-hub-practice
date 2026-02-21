# Prompt Engineering Basics

## What is Prompt Engineering?

**Prompt Engineering** is the practice of designing and refining inputs to get the best possible outputs from AI models. It's the bridge between what you want and what the AI delivers.

## Why Prompt Engineering Matters

The same model can produce vastly different results based on how you phrase your request:

### ❌ Poor Prompt
```
write about dogs
```

**Output**: Generic, unfocused content about dogs

### ✅ Good Prompt
```
Write a 200-word informative article about Golden Retrievers for 
first-time dog owners, covering temperament, exercise needs, and grooming.
```

**Output**: Specific, targeted, useful content

## Core Principles

### 1. **Be Specific and Clear**

**Vague** → **Specific**
- "Tell me about Python" → "Explain Python list comprehensions with 3 examples for beginners"
- "Write code" → "Write a Python function that validates email addresses using regex"
- "Summarize this" → "Summarize this article in 3 bullet points focusing on key findings"

### 2. **Provide Context**

Without context:
```
What's the best approach?
```

With context:
```
I'm building a web application that needs to handle 10,000 concurrent users. 
What's the best database approach for storing user session data?
```

### 3. **Specify the Format**

```
Create a Python tutorial on loops.

Output format:
1. Brief explanation (2-3 sentences)
2. Code example with comments
3. Practice exercise
4. Common pitfalls
```

### 4. **Define the Audience**

Same topic, different audiences:

```
For a 5-year-old: "Explain how computers work"
For a CS student: "Explain von Neumann architecture"
For a CEO: "Explain cloud computing ROI"
```

### 5. **Set the Tone and Style**

```
Explain APIs in a:
- Professional technical style → Use formal language, precise terminology
- Casual conversational style → Use analogies, simple language
- Humorous style → Include jokes, pop culture references
```

## The Basic Prompt Structure

### Template:
```
[Role/Persona] + [Task] + [Context] + [Format] + [Constraints]
```

### Example:
```
You are a senior software engineer.
Help me debug this Python function that's throwing a KeyError.
The function processes user data from a JSON API response.
Explain the issue and provide a corrected version with error handling.
Keep the solution under 20 lines of code.
```

## Essential Prompt Patterns

### 1. **Instruction Pattern**
Direct, clear commands.

```
Translate the following text to Spanish:
"Hello, how are you today?"
```

### 2. **Question Pattern**
Ask specific questions.

```
What are the pros and cons of using MongoDB vs PostgreSQL 
for a social media application?
```

### 3. **Completion Pattern**
Start a pattern for the AI to continue.

```
Here are examples of strong passwords:
1. Tr0ub4dor&3
2. correcthorsebatterystaple
3. X@9mK#pL2qR
4. [AI completes]
```

### 4. **Role-Playing Pattern**
Assign the AI a specific role.

```
You are an experienced UX designer. Review this website layout 
and provide feedback on usability issues.
```

### 5. **Example-Based Pattern** (Few-Shot)
Provide examples to establish the pattern.

```
Convert product names to SKU codes:

Product: Blue Cotton T-Shirt Size M
SKU: BLU-TEE-COT-M

Product: Red Wool Sweater Size L
SKU: RED-SWE-WOL-L

Product: Green Silk Scarf
SKU: [AI generates]
```

## Common Prompt Elements

### System Instructions
Set the AI's behavior and constraints.

```
You are a helpful coding assistant that always:
1. Writes clean, commented code
2. Follows PEP 8 style guide
3. Includes error handling
4. Provides brief explanations
```

### Input/Output Delimiters
Clearly separate different parts.

```
Summarize the following text:

---TEXT START---
[Your long text here]
---TEXT END---

Summary:
```

### Constraints and Requirements
Define boundaries explicitly.

```
Write a product description with these requirements:
- Exactly 150 words
- Include keywords: "eco-friendly", "sustainable"
- Avoid technical jargon
- Write in second person ("you")
- End with a call-to-action
```

## Temperature and Other Parameters

### Temperature Impact

```python
# Temperature: 0.0 (Deterministic)
Prompt: "Name the capital of France"
Output: "Paris" (always the same)

# Temperature: 0.7 (Balanced)
Prompt: "Write a creative tagline for a coffee shop"
Output: Varied but coherent responses

# Temperature: 1.5 (Very creative/random)
Prompt: "Write a creative tagline for a coffee shop"
Output: Highly varied, sometimes unusual responses
```

### Other Key Parameters

```python
# max_tokens: Limit response length
max_tokens=100  # Short response

# top_p: Alternative to temperature (0.0-1.0)
top_p=0.9  # Consider top 90% probability tokens

# presence_penalty: Reduce repetition (-2.0 to 2.0)
presence_penalty=0.6  # Penalize repeated topics

# frequency_penalty: Reduce word repetition (-2.0 to 2.0)
frequency_penalty=0.5  # Penalize repeated words
```

## Practical Examples by Use Case

### 1. **Code Generation**
```
Write a Python function that:
- Takes a list of dictionaries as input
- Filters items where 'active' is True
- Sorts by 'created_date' in descending order
- Returns the top 5 items
- Includes type hints and docstring
```

### 2. **Data Analysis**
```
Given this sales data, provide:
1. Total revenue by quarter
2. Top 3 selling products
3. Average order value
4. Month-over-month growth rate

Present as a formatted table and include key insights.
```

### 3. **Content Writing**
```
Write a LinkedIn post about the importance of continuous learning in tech.

Requirements:
- 150-200 words
- Professional but conversational tone
- Include a personal anecdote
- End with an engaging question
- Use 2-3 relevant hashtags
```

### 4. **Problem Solving**
```
I'm getting a "TypeError: 'NoneType' object is not subscriptable" 
error in my Python code when processing user input.

Code: [paste your code]

Help me:
1. Identify the cause
2. Explain why it's happening
3. Provide a fix with error handling
4. Suggest how to prevent this in the future
```

## Iterative Refinement

Prompting is iterative. Start simple and refine:

**Iteration 1**:
```
Explain machine learning
```

**Iteration 2** (add context):
```
Explain machine learning to someone with basic programming knowledge
```

**Iteration 3** (add format):
```
Explain machine learning to someone with basic programming knowledge.
Use an analogy, then provide a technical definition.
```

**Iteration 4** (add constraints):
```
Explain machine learning to someone with basic programming knowledge.
Use an analogy, then provide a technical definition.
Keep it under 150 words and avoid mathematical formulas.
```

## Common Mistakes to Avoid

### ❌ Too Vague
```
Make it better
```

### ❌ Assuming Context
```
Fix the bug (without providing code)
```

### ❌ Conflicting Instructions
```
Write a detailed summary in 10 words
```

### ❌ No Format Specified
```
Give me information about Python
```

### ❌ Ignoring Limitations
```
Tell me tomorrow's lottery numbers
```

## Hands-On Exercise

Practice writing prompts for these scenarios:

1. **Email Response**: Draft a professional reply declining a meeting invitation
2. **Code Review**: Request review of a SQL query for performance issues
3. **Learning**: Ask for an explanation of REST APIs with examples
4. **Creative**: Generate 5 unique names for a productivity app
5. **Analysis**: Request comparison of React vs Vue for a project

Try different variations and observe how outputs change!

## Quick Reference Checklist

Before submitting a prompt, ask:
- [ ] Is my goal clear?
- [ ] Have I provided necessary context?
- [ ] Have I specified the desired format?
- [ ] Have I defined constraints (length, style, etc.)?
- [ ] Is my audience/tone appropriate?
- [ ] Have I included examples if needed?

---

**Next**: [Advanced Prompt Techniques](./02-advanced-techniques.md)
