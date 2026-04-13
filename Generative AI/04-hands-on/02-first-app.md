# Building Your First AI Application

## Project: Intelligent Text Summarizer

We'll build a practical application that summarizes articles using OpenAI's API.

## What You'll Learn
- Making API calls to LLMs
- Handling responses and errors
- Processing text inputs
- Best practices for production code

## Project Setup

### 1. Create Project Structure
```bash
mkdir ai-summarizer
cd ai-summarizer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install openai python-dotenv requests
```

### 3. Create `.env` File
```env
OPENAI_API_KEY=your_api_key_here
```

## Code Implementation

### Basic Summarizer (`summarizer.py`)

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_text(text, length="medium", style="bullet_points"):
    """
    Summarize given text using OpenAI's API
    
    Args:
        text (str): The text to summarize
        length (str): "short" (50 words), "medium" (150 words), or "long" (300 words)
        style (str): "bullet_points", "paragraph", or "key_takeaways"
    
    Returns:
        str: The summarized text
    """
    
    # Define length constraints
    length_map = {
        "short": "approximately 50 words",
        "medium": "approximately 150 words",
        "long": "approximately 300 words"
    }
    
    # Define style instructions
    style_map = {
        "bullet_points": "as bullet points highlighting main ideas",
        "paragraph": "as a cohesive paragraph",
        "key_takeaways": "as numbered key takeaways"
    }
    
    # Build the prompt
    prompt = f"""Summarize the following text {length_map[length]} {style_map[style]}:

Text:
{text}

Summary:"""
    
    try:
        # Make API call
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for lower cost
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates clear, concise summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for consistent summaries
            max_tokens=500
        )
        
        # Extract the summary
        summary = response.choices[0].message.content
        
        return summary
        
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Example text
    sample_text = """
    Artificial Intelligence (AI) has revolutionized multiple industries in recent years. 
    From healthcare to finance, AI systems are being deployed to automate tasks, 
    analyze vast amounts of data, and make predictions. Machine learning, a subset of AI, 
    enables computers to learn from data without explicit programming. Deep learning, 
    which uses neural networks with multiple layers, has been particularly successful 
    in areas like image recognition and natural language processing. However, AI also 
    raises important ethical questions about privacy, bias, and job displacement. 
    As AI continues to advance, it's crucial to develop frameworks that ensure 
    responsible and beneficial use of these powerful technologies.
    """
    
    print("=== AI Text Summarizer ===\n")
    
    # Different summary styles
    print("1. Short Bullet Points:")
    print(summarize_text(sample_text, length="short", style="bullet_points"))
    print("\n" + "="*50 + "\n")
    
    print("2. Medium Paragraph:")
    print(summarize_text(sample_text, length="medium", style="paragraph"))
    print("\n" + "="*50 + "\n")
    
    print("3. Key Takeaways:")
    print(summarize_text(sample_text, length="medium", style="key_takeaways"))

if __name__ == "__main__":
    main()
```

### Enhanced Version with URL Support (`url_summarizer.py`)

```python
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_article_text(url):
    """
    Fetch and extract main text content from a URL
    
    Args:
        url (str): The URL of the article
    
    Returns:
        str: Extracted text content
    """
    try:
        # Send request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        return f"Error fetching article: {str(e)}"

def summarize_article(url, num_points=5):
    """
    Fetch article from URL and create summary
    
    Args:
        url (str): Article URL
        num_points (int): Number of bullet points for summary
    
    Returns:
        dict: Summary information
    """
    print(f"Fetching article from: {url}")
    
    # Fetch article text
    article_text = fetch_article_text(url)
    
    if article_text.startswith("Error"):
        return {"error": article_text}
    
    # Limit text length (most models have token limits)
    max_chars = 12000  # Roughly 3000 tokens
    if len(article_text) > max_chars:
        article_text = article_text[:max_chars]
    
    print(f"Article length: {len(article_text)} characters")
    print("Generating summary...")
    
    # Create prompt
    prompt = f"""Analyze and summarize this article in exactly {num_points} bullet points. 
Each point should be clear, concise, and capture a key idea from the article.

Article:
{article_text}

{num_points}-point summary:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing articles and extracting key information."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=600
        )
        
        summary = response.choices[0].message.content
        
        return {
            "url": url,
            "summary": summary,
            "original_length": len(article_text),
            "model": "gpt-4"
        }
        
    except Exception as e:
        return {"error": f"API Error: {str(e)}"}

def main():
    # Example usage
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    
    result = summarize_article(test_url, num_points=5)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("\n" + "="*60)
        print(f"URL: {result['url']}")
        print(f"Original Length: {result['original_length']} characters")
        print(f"Model: {result['model']}")
        print("="*60)
        print("\nSummary:")
        print(result['summary'])

if __name__ == "__main__":
    main()
```

### Interactive CLI Version (`cli_summarizer.py`)

```python
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize(text, length="medium"):
    """Summarize text with specified length"""
    
    length_map = {
        "short": "in 50-75 words",
        "medium": "in 125-175 words",
        "long": "in 250-350 words"
    }
    
    prompt = f"Summarize the following text {length_map[length]}:\n\n{text}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a concise summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("=" * 60)
    print("AI TEXT SUMMARIZER".center(60))
    print("=" * 60)
    print("\nEnter or paste your text (press Ctrl+D or Ctrl+Z when done):\n")
    
    # Read multi-line input
    try:
        lines = []
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    text = "\n".join(lines).strip()
    
    if not text:
        print("\nNo text provided. Exiting.")
        sys.exit(0)
    
    print(f"\n\nText length: {len(text)} characters")
    print("\nChoose summary length:")
    print("1. Short (50-75 words)")
    print("2. Medium (125-175 words)")
    print("3. Long (250-350 words)")
    
    choice = input("\nEnter choice (1-3) [default: 2]: ").strip()
    
    length_options = {"1": "short", "2": "medium", "3": "long"}
    length = length_options.get(choice, "medium")
    
    print(f"\nGenerating {length} summary...\n")
    
    summary = summarize(text, length)
    
    print("=" * 60)
    print("SUMMARY".center(60))
    print("=" * 60)
    print(f"\n{summary}\n")
    
    # Token usage estimation
    estimated_tokens = (len(text) + len(summary)) // 4
    print(f"Estimated tokens used: ~{estimated_tokens}")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

## Running the Application

### Basic Summarizer
```bash
python summarizer.py
```

### URL Summarizer (requires installation)
```bash
pip install beautifulsoup4 requests
python url_summarizer.py
```

### Interactive CLI
```bash
python cli_summarizer.py
```

## Best Practices Demonstrated

### 1. **Error Handling**
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    return f"Error: {str(e)}"
```

### 2. **Environment Variables**
```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

### 3. **Parameterization**
```python
def summarize_text(text, length="medium", style="bullet_points"):
    # Flexible function with options
```

### 4. **Clear Documentation**
```python
"""
Docstrings explaining:
- Purpose
- Parameters
- Return values
"""
```

### 5. **Token Management**
```python
max_chars = 12000  # Limit input size
max_tokens=500     # Limit output size
```

## Exercise: Extend the Application

Try adding these features:

1. **Sentiment Analysis**: Add emotion detection to summaries
2. **Multi-Language**: Support summarization in different languages
3. **Comparison Mode**: Compare summaries from different models
4. **Save to File**: Export summaries to PDF or Markdown
5. **Streaming**: Display summary as it's generated word-by-word

### Example: Streaming Implementation
```python
def summarize_streaming(text):
    """Generate summary with streaming output"""
    
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Summarize: {text}"}],
        stream=True
    )
    
    print("Summary: ", end="")
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")
```

## Common Issues and Solutions

### Issue: API Key Not Found
```python
# Solution: Check .env file exists and is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")
```

### Issue: Rate Limits
```python
# Solution: Add retry logic with exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def api_call_with_retry():
    return client.chat.completions.create(...)
```

### Issue: Text Too Long
```python
# Solution: Chunk the text
def chunk_text(text, chunk_size=3000):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
```

## Next Steps

- [ ] Test with different types of content
- [ ] Experiment with different models (gpt-3.5-turbo vs gpt-4)
- [ ] Try different temperature settings
- [ ] Add a web interface (Flask/Streamlit)
- [ ] Deploy to a cloud platform

---

**Next**: [Working with APIs](./03-api-integration.md)
