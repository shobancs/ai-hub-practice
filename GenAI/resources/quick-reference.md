# Quick Reference Guide - Generative AI

## 📋 Essential Commands and Patterns

### OpenAI API - Basic Usage

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple chat completion
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=150
)

print(response.choices[0].message.content)
```

---

## 🎯 Prompt Engineering Patterns

### Zero-Shot
```python
"Classify the sentiment: 'This product is great!'"
```

### Few-Shot
```python
"""Classify sentiment:
'I love it!' -> Positive
'It's terrible' -> Negative
'It's okay' -> Neutral
'Amazing quality!' -> """
```

### Chain-of-Thought
```python
"""Solve step by step:
If John has 5 apples and gives 2 to Mary, how many does he have?

Let's think through this:
1. Starting amount
2. Amount given away
3. Remaining amount
"""
```

### Structured Output
```python
"""Extract info as JSON:
Text: 'John Smith, engineer at TechCorp, john@email.com'

JSON: {
  "name": "",
  "occupation": "",
  "company": "",
  "email": ""
}"""
```

---

## 🔧 Common Code Snippets

### Chat with History
```python
messages = [
    {"role": "system", "content": "You are helpful."}
]

def chat(user_input):
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})
    
    return assistant_reply
```

### Error Handling
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def call_api(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        raise
```

### Streaming Responses
```python
stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## 🗄️ RAG Implementation

### Basic RAG Setup
```python
import chromadb
from chromadb.utils import embedding_functions

# Initialize
client = chromadb.Client()
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Create collection
collection = client.create_collection(
    name="my_docs",
    embedding_function=openai_ef
)

# Add documents
collection.add(
    documents=["Doc 1 text", "Doc 2 text"],
    ids=["doc1", "doc2"]
)

# Query
results = collection.query(
    query_texts=["search query"],
    n_results=3
)
```

### RAG Query
```python
def rag_query(question):
    # 1. Retrieve relevant docs
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    context = "\n".join(results['documents'][0])
    
    # 2. Generate answer with context
    prompt = f"""Answer based on this context:

Context: {context}

Question: {question}

Answer:"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

---

## 🤖 Agent Pattern

### Simple Agent
```python
def agent_loop(goal, max_iterations=5):
    """ReAct agent pattern"""
    
    for i in range(max_iterations):
        # Reasoning
        prompt = f"Goal: {goal}\nWhat should I do next?"
        thought = call_llm(prompt)
        
        # Check if done
        if "FINAL ANSWER:" in thought:
            return extract_answer(thought)
        
        # Extract action
        action = extract_action(thought)
        
        # Execute tool
        observation = execute_tool(action)
        
        # Update goal with observation
        goal += f"\nObservation: {observation}"
    
    return "Max iterations reached"
```

---

## 💰 Cost Estimation

### Token Pricing (2026 estimates)
```python
# GPT-3.5-turbo
INPUT_PRICE = 0.0005   # per 1K tokens
OUTPUT_PRICE = 0.0015  # per 1K tokens

# GPT-4
GPT4_INPUT_PRICE = 0.03   # per 1K tokens
GPT4_OUTPUT_PRICE = 0.06  # per 1K tokens

def estimate_cost(prompt_tokens, completion_tokens, model="gpt-3.5-turbo"):
    if model == "gpt-4":
        cost = (prompt_tokens / 1000 * GPT4_INPUT_PRICE + 
                completion_tokens / 1000 * GPT4_OUTPUT_PRICE)
    else:
        cost = (prompt_tokens / 1000 * INPUT_PRICE + 
                completion_tokens / 1000 * OUTPUT_PRICE)
    return cost

# Usage
response = client.chat.completions.create(...)
cost = estimate_cost(
    response.usage.prompt_tokens,
    response.usage.completion_tokens
)
print(f"Cost: ${cost:.4f}")
```

---

## 🧪 Testing Prompts

### A/B Testing
```python
def test_prompts(prompts, test_inputs):
    """Test multiple prompt versions"""
    results = {}
    
    for name, prompt_template in prompts.items():
        results[name] = []
        
        for input_text in test_inputs:
            prompt = prompt_template.format(input=input_text)
            response = call_llm(prompt)
            results[name].append(response)
    
    return results

# Usage
prompts = {
    "v1": "Summarize: {input}",
    "v2": "Provide a concise summary of: {input}",
    "v3": "In 2-3 sentences, summarize: {input}"
}

test_inputs = ["long text 1", "long text 2"]
results = test_prompts(prompts, test_inputs)
```

---

## 🎨 Advanced Techniques

### Self-Consistency
```python
def self_consistency(prompt, n=5):
    """Generate multiple answers, take majority"""
    responses = []
    
    for _ in range(n):
        response = call_llm(prompt, temperature=0.7)
        responses.append(response)
    
    # Find most common answer
    from collections import Counter
    counter = Counter(responses)
    most_common = counter.most_common(1)[0][0]
    
    return most_common, responses
```

### Prompt Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_call(prompt, temperature=0.7):
    """Cache responses for identical prompts"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content
```

---

## 📊 Monitoring and Logging

### Basic Logging
```python
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logged_api_call(prompt):
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        duration = time.time() - start_time
        
        logger.info(f"API call successful - Duration: {duration:.2f}s, "
                   f"Tokens: {response.usage.total_tokens}")
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise
```

---

## 🛡️ Safety and Validation

### Content Filtering
```python
def is_safe_content(text):
    """Check if content is appropriate"""
    response = client.moderations.create(input=text)
    
    results = response.results[0]
    
    if results.flagged:
        categories = [cat for cat, flagged in results.categories 
                     if flagged]
        return False, categories
    
    return True, []

# Usage
user_input = "Some text..."
is_safe, issues = is_safe_content(user_input)

if not is_safe:
    print(f"Content flagged: {issues}")
```

### Output Validation
```python
import json

def validate_json_output(response_text):
    """Ensure output is valid JSON"""
    try:
        # Clean markdown wrapping
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        
        data = json.loads(response_text.strip())
        return True, data
    except json.JSONDecodeError as e:
        return False, str(e)
```

---

## 🚀 Quick Starts

### Start a New Project
```bash
# Create project
mkdir my-ai-app && cd my-ai-app

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install openai python-dotenv

# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Create main.py
cat > main.py << 'EOF'
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
EOF

# Run
python main.py
```

---

## 🔍 Debugging Tips

### Common Issues

**Issue**: `AuthenticationError`
```python
# Check API key
import os
print(os.getenv("OPENAI_API_KEY"))  # Should start with 'sk-'
```

**Issue**: `RateLimitError`
```python
# Add delays between requests
import time
time.sleep(1)  # Wait 1 second
```

**Issue**: Token limit exceeded
```python
# Count tokens first
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
num_tokens = len(encoding.encode(text))
print(f"Tokens: {num_tokens}")
```

---

**Keep this guide handy for quick reference!** 🎯
