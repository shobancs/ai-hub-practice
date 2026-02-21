# Practical Exercises and Projects

## Overview

This directory contains hands-on exercises and projects to reinforce your learning. Each exercise includes:
- Problem description
- Difficulty level
- Estimated time
- Solution file (in `/solutions` subdirectory)

---

## 📚 Exercise Structure

### Beginner Exercises (30-60 minutes each)
Focus on fundamental concepts and basic implementations.

### Intermediate Exercises (1-2 hours each)
Combine multiple concepts and require more complex logic.

### Advanced Projects (3-5 hours each)
Build complete applications integrating various techniques.

---

## Beginner Exercises

### Exercise 1: Temperature Explorer
**Difficulty**: ⭐ Beginner  
**Time**: 30 minutes  
**Concepts**: Temperature parameter, response variation

**Task**: Create a program that:
1. Takes a prompt from the user
2. Generates 3 responses with different temperatures (0.0, 0.7, 1.5)
3. Displays all responses side-by-side for comparison
4. Asks user to pick their favorite

**Learning Goals**:
- Understand temperature's effect on outputs
- Practice making multiple API calls
- Handle user input

**Starter Code**: `exercises/beginner/01_temperature_explorer.py`

---

### Exercise 2: Sentiment Analyzer
**Difficulty**: ⭐ Beginner  
**Time**: 45 minutes  
**Concepts**: Zero-shot classification, structured output

**Task**: Build a sentiment analyzer that:
1. Takes product reviews as input
2. Classifies sentiment as Positive/Negative/Neutral
3. Extracts a confidence score
4. Returns results in JSON format

**Test Data** (provided):
```
- "This product is amazing! Best purchase ever."
- "Terrible quality. Broke after one day."
- "It's okay, nothing special."
- "Great value for money, highly recommend!"
```

**Learning Goals**:
- Practice classification tasks
- Work with structured output
- Handle JSON parsing

**Starter Code**: `exercises/beginner/02_sentiment_analyzer.py`

---

### Exercise 3: Text Summarizer with Options
**Difficulty**: ⭐ Beginner  
**Time**: 60 minutes  
**Concepts**: Prompt engineering, parameters

**Task**: Create a flexible summarizer that:
1. Accepts text input
2. Offers summary styles: paragraph, bullets, key points
3. Offers lengths: short, medium, long
4. Saves output to a file

**Learning Goals**:
- Build a reusable function
- Handle multiple options/parameters
- File I/O operations

**Starter Code**: `exercises/beginner/03_text_summarizer.py`

---

## Intermediate Exercises

### Exercise 4: Chain-of-Thought Calculator
**Difficulty**: ⭐⭐ Intermediate  
**Time**: 90 minutes  
**Concepts**: Chain-of-Thought, reasoning, error handling

**Task**: Build a calculator that:
1. Accepts word problems (e.g., "If John has 5 apples and gives away 2...")
2. Uses Chain-of-Thought to solve step-by-step
3. Extracts the final numeric answer
4. Validates the result makes sense

**Test Cases** (provided):
```
- "A store has 25 items at $10 each. After a 20% discount, what's the revenue?"
- "If a train travels 60 mph for 2.5 hours, how far does it go?"
- "Sarah has $100. She spends 1/4 on food and 1/3 on transport. How much is left?"
```

**Learning Goals**:
- Implement Chain-of-Thought prompting
- Extract structured data from text
- Validate AI outputs

**Starter Code**: `exercises/intermediate/04_cot_calculator.py`

---

### Exercise 5: Multi-Document Q&A (Mini RAG)
**Difficulty**: ⭐⭐ Intermediate  
**Time**: 2 hours  
**Concepts**: Document processing, basic retrieval, context management

**Task**: Create a Q&A system that:
1. Loads multiple text files from a directory
2. For each question, finds the most relevant document (simple keyword matching)
3. Uses the relevant document as context for the LLM
4. Provides answer with source citation

**Provided Data**: 5 text files about different topics

**Learning Goals**:
- Work with multiple documents
- Implement basic retrieval logic
- Provide source attribution

**Starter Code**: `exercises/intermediate/05_mini_rag.py`

---

### Exercise 6: Chatbot with Memory
**Difficulty**: ⭐⭐ Intermediate  
**Time**: 90 minutes  
**Concepts**: Conversation history, context management, session handling

**Task**: Build a chatbot that:
1. Maintains conversation history
2. References previous messages in responses
3. Implements commands: /clear, /history, /save
4. Manages token limits (truncates old messages if needed)

**Learning Goals**:
- Manage conversation state
- Handle context window limits
- Implement chat commands

**Starter Code**: `exercises/intermediate/06_chatbot_memory.py`

---

## Advanced Projects

### Project 1: Research Assistant
**Difficulty**: ⭐⭐⭐ Advanced  
**Time**: 4 hours  
**Concepts**: Web scraping, RAG, summarization, citations

**Task**: Build a research assistant that:
1. Accepts a research topic
2. Searches the web for relevant articles (using a search API or scraping)
3. Extracts and summarizes key information
4. Synthesizes findings into a coherent report
5. Includes citations and sources

**Features**:
- Web search integration
- Content extraction and cleaning
- Multi-document summarization
- Report generation
- Source citation

**Learning Goals**:
- Integrate multiple APIs
- Implement complete RAG pipeline
- Handle unstructured web data
- Generate professional reports

**Starter Code**: `exercises/advanced/project_01_research_assistant/`

---

### Project 2: Code Review Agent
**Difficulty**: ⭐⭐⭐ Advanced  
**Time**: 4 hours  
**Concepts**: Code analysis, structured feedback, multi-step processing

**Task**: Create a code review tool that:
1. Accepts code files or GitHub gists
2. Analyzes for:
   - Bugs and errors
   - Security vulnerabilities
   - Performance issues
   - Style violations
   - Best practice violations
3. Generates detailed report with:
   - Issue severity (critical/high/medium/low)
   - Line numbers
   - Explanation of issues
   - Suggested fixes
4. Outputs as HTML or Markdown

**Learning Goals**:
- Process code files
- Multi-aspect analysis
- Structured output generation
- Report formatting

**Starter Code**: `exercises/advanced/project_02_code_review/`

---

### Project 3: Personal Knowledge Base
**Difficulty**: ⭐⭐⭐ Advanced  
**Time**: 5 hours  
**Concepts**: RAG, vector database, document ingestion, Q&A

**Task**: Build a personal knowledge base that:
1. Ingests documents (PDFs, text files, markdown)
2. Chunks and embeds content
3. Stores in vector database (ChromaDB)
4. Answers questions about your documents
5. Provides source citations with page numbers
6. Supports document management (add, remove, list)

**Features**:
- Document parsing (PDF, TXT, MD)
- Chunk optimization
- Semantic search
- Source attribution
- CLI interface

**Learning Goals**:
- Complete RAG implementation
- Document processing pipeline
- Vector database operations
- Production-ready error handling

**Starter Code**: `exercises/advanced/project_03_knowledge_base/`

---

### Project 4: Content Generation Pipeline
**Difficulty**: ⭐⭐⭐ Advanced  
**Time**: 4 hours  
**Concepts**: Multi-step generation, quality control, templating

**Task**: Build a content pipeline that:
1. Generates blog post outlines from topics
2. Expands each section with detailed content
3. Generates SEO-optimized title and meta description
4. Creates social media posts (Twitter, LinkedIn, Instagram)
5. Generates featured image prompt
6. Outputs complete content package

**Features**:
- Multi-stage generation
- Quality checks between stages
- Template system
- Batch processing
- Output organization

**Learning Goals**:
- Multi-step AI workflows
- Content quality control
- Template-based generation
- File management

**Starter Code**: `exercises/advanced/project_04_content_pipeline/`

---

## How to Use These Exercises

### 1. Start with Your Level
- New to AI? Start with Beginner exercises
- Comfortable with basics? Jump to Intermediate
- Ready for a challenge? Tackle Advanced projects

### 2. Read the Problem First
- Understand what you need to build
- Identify which concepts are required
- Think about your approach before coding

### 3. Try Before Looking at Solutions
- Attempt the exercise on your own first
- Use documentation and course materials
- Only check solutions when stuck or to compare approaches

### 4. Solutions are Learning Tools
- Solutions show one way to solve the problem
- Your solution might be different and still correct
- Focus on understanding the approach, not memorizing code

### 5. Extend and Experiment
- Add your own features
- Try different approaches
- Combine concepts from multiple exercises

---

## Submission and Sharing

If you're taking this as a course:
1. Complete exercises in order
2. Save your work in a personal repository
3. Document your approach and any challenges
4. Share interesting solutions or variations

---

## Additional Challenges

Once you complete an exercise, try these enhancements:

### For Beginners:
- Add error handling
- Create a simple UI (using `input()` or basic web interface)
- Add logging to track usage
- Save results to files

### For Intermediate:
- Add caching to reduce API calls
- Implement rate limiting
- Create unit tests
- Add configuration files

### For Advanced:
- Deploy as a web service
- Add authentication
- Implement database storage
- Create a REST API
- Add monitoring and analytics

---

## Getting Help

### Resources:
1. Course materials in `/GenAI/`
2. Example code in `/examples/`
3. Jupyter notebooks in `/notebooks/`
4. [OpenAI Documentation](https://platform.openai.com/docs)

### Tips:
- Start simple, then add features
- Test frequently with small inputs
- Use print statements for debugging
- Check token usage to manage costs
- Read error messages carefully

---

## Exercise Checklist

Track your progress:

**Beginner**:
- [ ] Exercise 1: Temperature Explorer
- [ ] Exercise 2: Sentiment Analyzer  
- [ ] Exercise 3: Text Summarizer

**Intermediate**:
- [ ] Exercise 4: Chain-of-Thought Calculator
- [ ] Exercise 5: Multi-Document Q&A
- [ ] Exercise 6: Chatbot with Memory

**Advanced**:
- [ ] Project 1: Research Assistant
- [ ] Project 2: Code Review Agent
- [ ] Project 3: Personal Knowledge Base
- [ ] Project 4: Content Generation Pipeline

---

**Good luck and have fun building! 🚀**

Remember: The goal is learning, not perfection. Every bug is a learning opportunity!
