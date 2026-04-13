"""
AI Code Generator
Demonstrates: Code generation, structured output, error handling
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_code(description, language="python", include_tests=False):
    """
    Generate code based on natural language description
    
    Args:
        description (str): What the code should do
        language (str): Programming language
        include_tests (bool): Whether to generate unit tests
    
    Returns:
        dict: Generated code and explanation
    """
    
    # Build the prompt
    prompt = f"""Generate {language} code for the following requirement:

{description}

Provide:
1. Clean, well-commented code following best practices
2. Brief explanation of the approach
3. Example usage
{'4. Unit tests using pytest' if include_tests else ''}

Format your response as:
```{language}
[code here]
```

Explanation:
[explanation here]

Example Usage:
```{language}
[usage example]
```
{'''
Unit Tests:
```python
[tests here]
```
''' if include_tests else ''}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an expert {language} developer. 
                    Write clean, efficient, well-documented code with proper error handling."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Low temperature for consistent code
            max_tokens=2000
        )
        
        return {
            "success": True,
            "output": response.choices[0].message.content,
            "model": "gpt-4",
            "tokens": response.usage.total_tokens
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def review_code(code, language="python"):
    """
    Get AI code review and suggestions
    
    Args:
        code (str): Code to review
        language (str): Programming language
    
    Returns:
        dict: Review results with suggestions
    """
    
    prompt = f"""Review this {language} code and provide:
1. Overall quality assessment (1-10)
2. Potential bugs or issues
3. Performance considerations
4. Best practice violations
5. Suggested improvements

Code:
```{language}
{code}
```

Provide detailed, actionable feedback."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior code reviewer with expertise in software engineering best practices."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return {
            "success": True,
            "review": response.choices[0].message.content
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def explain_code(code, language="python", audience="beginner"):
    """
    Generate explanation of existing code
    
    Args:
        code (str): Code to explain
        language (str): Programming language
        audience (str): "beginner", "intermediate", or "advanced"
    
    Returns:
        dict: Detailed explanation
    """
    
    audience_prompts = {
        "beginner": "Explain in simple terms, as if teaching someone new to programming",
        "intermediate": "Assume basic programming knowledge, focus on concepts and patterns",
        "advanced": "Provide technical deep-dive, discuss design decisions and trade-offs"
    }
    
    prompt = f"""Explain this {language} code. {audience_prompts.get(audience, '')}.

Code:
```{language}
{code}
```

Provide:
1. High-level overview of what it does
2. Step-by-step breakdown of how it works
3. Key concepts used
4. Potential use cases"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a patient programming instructor who explains code clearly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=1000
        )
        
        return {
            "success": True,
            "explanation": response.choices[0].message.content
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def debug_code(code, error_message, language="python"):
    """
    Help debug code with error message
    
    Args:
        code (str): Code with the bug
        error_message (str): The error message
        language (str): Programming language
    
    Returns:
        dict: Debug analysis and fix
    """
    
    prompt = f"""Debug this {language} code that's producing an error.

Code:
```{language}
{code}
```

Error:
{error_message}

Provide:
1. Root cause of the error
2. Explanation of why it's happening
3. Corrected code
4. Prevention tips for similar issues"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert debugger who identifies issues quickly and explains fixes clearly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        return {
            "success": True,
            "debug_info": response.choices[0].message.content
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Demo of code generation capabilities"""
    
    print("=" * 70)
    print("AI CODE GENERATOR & ASSISTANT".center(70))
    print("=" * 70)
    
    # Example 1: Generate Code
    print("\n1. GENERATING CODE")
    print("-" * 70)
    
    description = """
    Create a function that takes a list of dictionaries representing products 
    (each with 'name', 'price', 'category') and returns the top N most expensive 
    products in each category. Include input validation.
    """
    
    print(f"Request: {description.strip()}")
    print("\nGenerating...\n")
    
    result = generate_code(description, language="python", include_tests=False)
    
    if result["success"]:
        print(result["output"])
        print(f"\n[Tokens used: {result['tokens']}]")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Code Review
    print("\n\n2. CODE REVIEW")
    print("-" * 70)
    
    sample_code = """
def calculate(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a / b
    """
    
    print("Code to review:")
    print(sample_code)
    print("\nReviewing...\n")
    
    review = review_code(sample_code)
    
    if review["success"]:
        print(review["review"])
    else:
        print(f"Error: {review['error']}")
    
    # Example 3: Explain Code
    print("\n\n3. CODE EXPLANATION")
    print("-" * 70)
    
    complex_code = """
@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
    """
    
    print("Code to explain:")
    print(complex_code)
    print("\nExplaining for intermediate audience...\n")
    
    explanation = explain_code(complex_code, audience="intermediate")
    
    if explanation["success"]:
        print(explanation["explanation"])
    else:
        print(f"Error: {explanation['error']}")

if __name__ == "__main__":
    main()
