"""
RAG (Retrieval-Augmented Generation) Example
Demonstrates: Building a knowledge base Q&A system with source attribution
"""

import os
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RAGSystem:
    """Simple RAG system for question answering"""
    
    def __init__(self, collection_name="rag_demo"):
        """Initialize RAG system with ChromaDB"""
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.Client()
        
        # Create embedding function using OpenAI
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"Created new collection: {collection_name}")
    
    def add_documents(self, documents, metadata=None):
        """
        Add documents to the knowledge base
        
        Args:
            documents (list): List of text documents
            metadata (list): List of metadata dicts for each document
        """
        if metadata is None:
            metadata = [{"source": f"doc_{i}"} for i in range(len(documents))]
        
        # Generate unique IDs
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadata,
            ids=ids
        )
        
        print(f"Added {len(documents)} documents to knowledge base")
    
    def query(self, question, n_results=3, include_sources=True):
        """
        Query the RAG system
        
        Args:
            question (str): User's question
            n_results (int): Number of documents to retrieve
            include_sources (bool): Whether to include source attribution
        
        Returns:
            dict: Answer and sources
        """
        
        # Retrieve relevant documents
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        if not results['documents'][0]:
            return {
                "answer": "I couldn't find any relevant information in the knowledge base.",
                "sources": []
            }
        
        # Extract results
        retrieved_docs = results['documents'][0]
        retrieved_metadata = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results else None
        
        # Build context from retrieved documents
        context_parts = []
        for i, (doc, meta) in enumerate(zip(retrieved_docs, retrieved_metadata)):
            source = meta.get('source', 'Unknown')
            context_parts.append(f"[Source {i+1}: {source}]\n{doc}")
        
        context = "\n\n".join(context_parts)
        
        # Create prompt for LLM
        prompt = f"""Answer the question based on the context below. 
Be specific and cite which source(s) you're using.
If the information is not in the context, say "I don't have information about that in my knowledge base."

Context:
{context}

Question: {question}

Answer (cite sources by number):"""
        
        # Get LLM response
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context. Always cite your sources."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Prepare sources
            sources = []
            for meta, doc, dist in zip(retrieved_metadata, retrieved_docs, distances or [None]*len(retrieved_docs)):
                source_info = {
                    "source": meta.get('source', 'Unknown'),
                    "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                }
                if dist is not None:
                    source_info["similarity_score"] = round(1 - dist, 3)  # Convert distance to similarity
                sources.append(source_info)
            
            return {
                "answer": answer,
                "sources": sources if include_sources else []
            }
        
        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "sources": []
            }
    
    def get_stats(self):
        """Get statistics about the knowledge base"""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name
        }

def demo_company_knowledge():
    """Demo: Company knowledge base"""
    
    print("=" * 70)
    print("RAG DEMO: Company Knowledge Base".center(70))
    print("=" * 70)
    
    # Initialize RAG system
    rag = RAGSystem(collection_name="company_kb")
    
    # Sample company documents
    documents = [
        """TechCorp was founded in 2020 by Sarah Johnson and Michael Chen. 
        The company is headquartered in San Francisco, California, with 
        additional offices in New York and Austin. We currently employ 
        over 250 people across all locations.""",
        
        """TechCorp offers three pricing tiers for our SaaS platform:
        
        Starter Plan: $29/month - Up to 5 users, 10GB storage, email support
        Professional Plan: $99/month - Up to 25 users, 100GB storage, priority support
        Enterprise Plan: Custom pricing - Unlimited users, unlimited storage, 
        dedicated account manager, 24/7 phone support, SLA guarantee
        
        All plans include a 14-day free trial.""",
        
        """Q4 2025 Financial Summary:
        - Total Revenue: $3.2 million (up 23% from Q3)
        - New Customers: 487 (up 15% from Q3)
        - Customer Retention Rate: 94%
        - Average Revenue Per User (ARPU): $156/month
        - Operating Expenses: $2.1 million
        - Net Income: $1.1 million""",
        
        """Our customer support team is available:
        - Email support: 24/7 response within 24 hours for all plans
        - Chat support: Monday-Friday 9am-6pm PST for Professional and Enterprise
        - Phone support: 24/7 for Enterprise customers only
        - Knowledge base and documentation: Always available at docs.techcorp.com
        - Community forum: community.techcorp.com""",
        
        """TechCorp's mission is to empower businesses with intuitive, 
        powerful collaboration tools. Our core values are:
        1. Customer Success First
        2. Innovation Through Simplicity
        3. Transparency and Integrity
        4. Continuous Learning
        5. Sustainable Growth
        
        We believe in building products that genuinely solve problems 
        and improve people's work lives."""
    ]
    
    metadata = [
        {"source": "about_company.txt", "category": "company_info", "date": "2025-01-15"},
        {"source": "pricing_page.txt", "category": "products", "date": "2025-02-01"},
        {"source": "q4_financial_report.pdf", "category": "finance", "date": "2025-12-31"},
        {"source": "support_policy.txt", "category": "operations", "date": "2025-01-10"},
        {"source": "mission_values.txt", "category": "company_info", "date": "2020-05-01"}
    ]
    
    # Add documents
    print("\n📚 Adding documents to knowledge base...")
    rag.add_documents(documents, metadata)
    
    # Get stats
    stats = rag.get_stats()
    print(f"\n✓ Knowledge base ready: {stats['total_documents']} documents loaded\n")
    
    # Example queries
    queries = [
        "When was TechCorp founded and who are the founders?",
        "What are the pricing plans and their features?",
        "How much revenue did we make in Q4 2025?",
        "What customer support options are available?",
        "What are TechCorp's core values?",
        "Do you offer a mobile app?"  # This should say "no info available"
    ]
    
    for i, question in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {question}")
        print('='*70)
        
        result = rag.query(question, n_results=2)
        
        print(f"\n📝 Answer:\n{result['answer']}")
        
        if result['sources']:
            print(f"\n📚 Sources:")
            for j, source in enumerate(result['sources'], 1):
                print(f"\n  {j}. {source['source']}")
                if 'similarity_score' in source:
                    print(f"     Relevance: {source['similarity_score']}")
                print(f"     Preview: {source['content_preview']}")

def demo_interactive():
    """Interactive RAG demo"""
    
    print("\n" + "=" * 70)
    print("INTERACTIVE RAG DEMO".center(70))
    print("=" * 70)
    print("\nCommands:")
    print("  'quit' - Exit")
    print("  'add' - Add a new document")
    print("  'stats' - Show knowledge base statistics")
    print("  Or just ask a question!\n")
    
    rag = RAGSystem(collection_name="interactive_kb")
    
    # Add some initial documents
    initial_docs = [
        "Python is a high-level programming language known for its readability and versatility.",
        "Machine learning is a subset of AI that enables systems to learn from data.",
        "REST APIs use HTTP methods like GET, POST, PUT, and DELETE to interact with resources."
    ]
    rag.add_documents(initial_docs)
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\nGoodbye! 👋")
            break
        
        if user_input.lower() == 'stats':
            stats = rag.get_stats()
            print(f"\n📊 Knowledge Base Stats:")
            print(f"   Total documents: {stats['total_documents']}")
            print(f"   Collection: {stats['collection_name']}")
            continue
        
        if user_input.lower() == 'add':
            doc = input("Enter document text: ").strip()
            if doc:
                source = input("Enter source name (optional): ").strip() or "user_added"
                rag.add_documents([doc], [{"source": source}])
                print("✓ Document added!")
            continue
        
        # Process as question
        result = rag.query(user_input)
        print(f"\n🤖 Assistant: {result['answer']}")
        
        if result['sources']:
            print(f"\n   Sources: {', '.join([s['source'] for s in result['sources']])}")

def main():
    """Run RAG demos"""
    
    # Demo 1: Company knowledge base
    demo_company_knowledge()
    
    # Demo 2: Interactive mode (optional)
    print("\n\n" + "=" * 70)
    choice = input("\nWould you like to try interactive mode? (yes/no): ").strip().lower()
    if choice in ['yes', 'y']:
        demo_interactive()

if __name__ == "__main__":
    main()
