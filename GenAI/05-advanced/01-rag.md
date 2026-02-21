# Retrieval-Augmented Generation (RAG)

## What is RAG?

**RAG** combines the power of LLMs with external information retrieval to provide accurate, up-to-date, and contextually relevant responses.

### The Problem RAG Solves

**Without RAG**:
```
User: "What were our Q4 2025 sales figures?"
LLM: "I don't have access to your company's data..."
```

**With RAG**:
```
User: "What were our Q4 2025 sales figures?"
System: [Retrieves relevant data from company database]
LLM: "According to your Q4 2025 report, sales were $2.3M, 
up 15% from Q3..."
```

## How RAG Works

### Basic Flow

```
1. User asks a question
    ↓
2. System converts question to embedding (vector)
    ↓
3. Search for similar content in vector database
    ↓
4. Retrieve top N most relevant documents
    ↓
5. Combine question + retrieved docs → LLM
    ↓
6. LLM generates informed answer with context
    ↓
7. Return answer (often with sources)
```

### Visual Diagram

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Embed Query     │ (Convert to vector)
└──────┬──────────┘
       │
       ▼
┌─────────────────────────┐
│ Vector Database Search  │
│ (ChromaDB, Pinecone,    │
│  Weaviate, etc.)        │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Retrieved Documents     │
│ (Top 3-5 most relevant) │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Combine: Query +        │
│ Context → LLM           │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Generated Answer        │
│ (with citations)        │
└─────────────────────────┘
```

## Why RAG is Powerful

### 1. **Overcome Knowledge Cutoff**
```
LLM Training: Data up to 2023
User Question: "What happened in the 2025 Olympics?"

RAG: Retrieves recent articles → LLM can answer accurately
```

### 2. **Access Private Data**
```
Company documents, internal wikis, databases
→ RAG enables LLM to answer about proprietary information
```

### 3. **Reduce Hallucinations**
```
Without RAG: LLM might invent facts
With RAG: LLM answers based on actual retrieved documents
```

### 4. **Provide Source Attribution**
```
Answer: "Revenue was $5M in Q3 (Source: Q3_Report.pdf, page 3)"
→ Users can verify information
```

### 5. **Domain Specialization**
```
Medical, legal, technical domains
→ Feed specialized knowledge without retraining
```

## Key Components

### 1. Document Ingestion

**Process**:
```python
# Step 1: Load documents
documents = load_documents("./company_docs/")

# Step 2: Split into chunks (to fit context window)
chunks = split_documents(documents, chunk_size=500)

# Step 3: Generate embeddings
embeddings = embed_chunks(chunks)

# Step 4: Store in vector database
vector_db.add(chunks, embeddings)
```

**Why chunk?**
- Documents are often too long for context window
- Smaller chunks = more precise retrieval
- Typical size: 200-500 words per chunk

### 2. Embeddings

**What are they?**
Numerical representations capturing semantic meaning.

**Example**:
```
"dog" → [0.2, 0.8, -0.3, ..., 0.5]  (1536 dimensions)
"puppy" → [0.21, 0.79, -0.29, ..., 0.51]  (very similar!)
"car" → [-0.5, 0.1, 0.6, ..., -0.2]  (different)
```

**Popular Embedding Models**:
- OpenAI `text-embedding-3-small` / `text-embedding-3-large`
- `all-MiniLM-L6-v2` (open source, fast)
- `BGE` models (high quality)
- Azure OpenAI embeddings

### 3. Vector Database

**Purpose**: Efficiently search millions of embeddings for similarity.

**Popular Options**:
| Database | Type | Best For |
|----------|------|----------|
| **ChromaDB** | In-memory/persistent | Simple projects, prototyping |
| **Pinecone** | Managed cloud | Production, scalability |
| **Weaviate** | Self-hosted/cloud | Hybrid search, complex queries |
| **Qdrant** | Self-hosted/cloud | High performance, filtering |
| **FAISS** | Library | Research, local development |
| **Azure AI Search** | Managed cloud | Enterprise, Azure integration |

### 4. Retrieval Strategy

**Simple Retrieval**:
```python
# Get top K most similar chunks
results = vector_db.search(query_embedding, k=3)
```

**Advanced Strategies**:
- **Hybrid Search**: Combine semantic + keyword search
- **Re-ranking**: Use second model to reorder results
- **Metadata Filtering**: Filter by date, author, category
- **Multi-query**: Generate multiple query variants
- **Parent-Child**: Retrieve small chunks, include larger context

## Practical Implementation

### Basic RAG System

```python
import os
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

# Initialize
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.Client()

# Create collection with OpenAI embeddings
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

collection = chroma_client.create_collection(
    name="knowledge_base",
    embedding_function=openai_ef
)

# 1. ADD DOCUMENTS
def add_documents(texts, metadata_list):
    """Add documents to vector database"""
    collection.add(
        documents=texts,
        metadatas=metadata_list,
        ids=[f"doc_{i}" for i in range(len(texts))]
    )

# Example: Add company knowledge
documents = [
    "Our company was founded in 2020 by Jane Smith and John Doe.",
    "We offer three products: Basic ($10/mo), Pro ($50/mo), Enterprise (custom).",
    "Q4 2025 revenue was $2.3M, up 15% from Q3.",
    "Customer support is available 24/7 via email and chat.",
]

metadata = [
    {"source": "about.txt", "category": "company"},
    {"source": "pricing.txt", "category": "products"},
    {"source": "financials.txt", "category": "finance"},
    {"source": "support.txt", "category": "operations"},
]

add_documents(documents, metadata)

# 2. QUERY WITH RAG
def query_rag(question, n_results=3):
    """Answer question using RAG"""
    
    # Retrieve relevant documents
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    # Extract retrieved documents
    retrieved_docs = results['documents'][0]
    retrieved_metadata = results['metadatas'][0]
    
    # Build context from retrieved documents
    context = "\n\n".join([
        f"[Source: {meta['source']}]\n{doc}" 
        for doc, meta in zip(retrieved_docs, retrieved_metadata)
    ])
    
    # Create prompt with context
    prompt = f"""Answer the question based on the context below. 
If the answer is not in the context, say "I don't have that information."

Context:
{context}

Question: {question}

Answer:"""
    
    # Get LLM response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return {
        "answer": response.choices[0].message.content,
        "sources": [meta['source'] for meta in retrieved_metadata]
    }

# Example usage
result = query_rag("What are your pricing plans?")
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

### Output:
```
Answer: We offer three pricing plans: Basic for $10/month, 
Pro for $50/month, and Enterprise with custom pricing.

Sources: ['pricing.txt']
```

## Advanced RAG Techniques

### 1. Chunking Strategies

**Fixed-Size Chunking**:
```python
def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks
```

**Semantic Chunking**:
```python
# Split by paragraphs or sections
chunks = text.split('\n\n')
```

**Recursive Chunking**:
```python
# Try splitting by large units first, then smaller
# Example: Chapter → Section → Paragraph → Sentence
```

### 2. Hybrid Search

Combine semantic and keyword search:

```python
# Semantic: Find similar meaning
semantic_results = vector_search(query, k=10)

# Keyword: Find exact matches (BM25)
keyword_results = keyword_search(query, k=10)

# Combine and re-rank
final_results = rerank(semantic_results + keyword_results)
```

### 3. Query Expansion

Generate multiple query variations:

```python
def expand_query(original_query):
    """Generate query variations"""
    prompt = f"""Generate 3 different ways to ask this question:
    "{original_query}"
    
    Return as a list."""
    
    # LLM generates variations
    variations = llm.generate(prompt)
    
    # Search with all variations
    all_results = []
    for query in variations:
        results = vector_db.search(query)
        all_results.extend(results)
    
    # Deduplicate and return
    return deduplicate(all_results)
```

### 4. Re-ranking

Use a second model to reorder results:

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, documents):
    """Re-rank documents by relevance"""
    # Score each doc against query
    scores = reranker.predict([(query, doc) for doc in documents])
    
    # Sort by score
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked]
```

## Common Challenges & Solutions

### Challenge 1: Retrieving Too Much/Too Little

**Problem**: 
- Too little context → LLM can't answer
- Too much context → Exceeds token limit, costs more

**Solution**:
```python
# Adaptive retrieval
def adaptive_retrieve(query, min_k=2, max_k=10, threshold=0.7):
    """Retrieve variable number of documents based on similarity"""
    results = vector_db.search(query, k=max_k)
    
    # Only keep results above threshold
    filtered = [r for r in results if r.similarity > threshold]
    
    # Ensure at least min_k results
    if len(filtered) < min_k:
        filtered = results[:min_k]
    
    return filtered
```

### Challenge 2: Outdated Information

**Problem**: Documents in database become stale

**Solution**:
```python
# Add timestamps and filter
def retrieve_recent(query, days_old=30):
    """Retrieve only recent documents"""
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    results = vector_db.search(
        query,
        filter={"date": {"$gte": cutoff_date}}
    )
    return results
```

### Challenge 3: Answer Not in Retrieved Docs

**Problem**: Wrong chunks retrieved

**Solution**:
```python
# Improve embeddings and chunking
# Use query expansion
# Implement fallback:

if no_relevant_context:
    return "I couldn't find information about that in the knowledge base."
```

## RAG vs Fine-Tuning

| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| **Cost** | Low (just retrieval) | High (retraining) |
| **Update Speed** | Instant (add new docs) | Slow (retrain model) |
| **Accuracy** | High (fresh data) | High (specialized) |
| **Use Case** | Dynamic knowledge | Fixed domain |
| **Transparency** | High (show sources) | Low (black box) |

**Best Practice**: Use both! RAG for dynamic knowledge, fine-tuning for task behavior.

## Real-World Applications

### 1. Customer Support
```
User: "How do I reset my password?"
RAG: Retrieves from support docs → Provides step-by-step
```

### 2. Internal Knowledge Base
```
Employee: "What's our vacation policy?"
RAG: Retrieves from HR documents → Accurate answer
```

### 3. Research Assistant
```
Researcher: "Summarize recent papers on quantum computing"
RAG: Retrieves papers → LLM summarizes
```

### 4. Code Documentation
```
Developer: "How do I use the authentication API?"
RAG: Retrieves API docs → Provides examples
```

### 5. Legal/Compliance
```
User: "What are GDPR requirements for data storage?"
RAG: Retrieves regulations → Explains requirements
```

## Exercise: Build Your Own RAG System

**Task**: Create a RAG system for your personal documents

**Steps**:
1. Collect 5-10 documents (PDFs, text files)
2. Set up ChromaDB
3. Chunk and embed documents
4. Implement query function
5. Test with various questions

**Starter Code**: See [rag_example.py](../examples/rag_example.py)

## Key Takeaways

✅ RAG combines LLMs with external knowledge retrieval  
✅ Solves knowledge cutoff, hallucination, and private data issues  
✅ Core components: embeddings, vector DB, retrieval, LLM generation  
✅ Advanced techniques: hybrid search, re-ranking, query expansion  
✅ Essential for production AI applications with dynamic knowledge  

---

**Next**: [Fine-Tuning Models](./02-fine-tuning.md)
