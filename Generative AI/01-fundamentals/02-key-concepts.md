# Key Concepts and Terminology

## Essential Terms

### 1. **Large Language Model (LLM)**
A type of AI model trained on vast amounts of text data to understand and generate human-like text.

**Examples**: GPT-4, Claude, Gemini, LLaMA

**Key Characteristics**:
- Billions of parameters (weights)
- Trained on diverse internet text
- Can perform multiple tasks without specific training

### 2. **Prompt**
The input text you provide to guide the AI's output.

**Example**:
```
Prompt: "Write a haiku about artificial intelligence"

Output:
Silicon minds think
Patterns emerge from the void
Learning never stops
```

### 3. **Token**
The basic unit of text processed by LLMs. Roughly 3-4 characters or about 0.75 words.

**Example**:
```
"Hello, world!" = ~4 tokens
["Hello", ",", " world", "!"]
```

**Why it matters**: API pricing and model limits are based on tokens.

### 4. **Context Window**
The maximum amount of text (in tokens) the model can process at once.

**Example**:
- GPT-4: 8K-128K tokens (~6K-96K words)
- Claude: up to 200K tokens (~150K words)

**Analogy**: Like working memory—the model can only "remember" what fits in the context window.

### 5. **Temperature**
A parameter (0.0 to 2.0) controlling randomness in generation.

| Temperature | Effect | Use Case |
|-------------|--------|----------|
| **0.0-0.3** | Deterministic, focused | Code, facts, analysis |
| **0.4-0.7** | Balanced | General conversation |
| **0.8-1.0** | Creative, varied | Stories, brainstorming |
| **1.0+** | Very random | Experimental creative work |

### 6. **Fine-Tuning**
Training a pre-trained model on specific data to specialize it for a particular task.

**Example**:
```
Base Model (GPT-4) 
    ↓
+ Legal Documents Dataset
    ↓
= Legal-Specialized Model
```

### 7. **Embeddings**
Numerical representations of text that capture semantic meaning.

**Example**:
```
"cat" → [0.2, 0.8, -0.3, 0.5, ...] (1536 dimensions)
"kitten" → [0.21, 0.79, -0.29, 0.51, ...] (similar values!)
"car" → [-0.5, 0.1, 0.6, -0.2, ...] (different values)
```

**Use Cases**:
- Semantic search
- Similarity comparison
- Recommendation systems
- Vector databases

### 8. **Retrieval-Augmented Generation (RAG)**
Enhancing LLM responses by retrieving relevant information from external sources.

**Flow**:
```
User Question 
    ↓
Retrieve relevant docs from database
    ↓
Combine docs + question → LLM
    ↓
Generate informed answer
```

**Benefits**: Up-to-date info, reduced hallucinations, source citations

### 9. **Hallucination**
When the AI generates plausible-sounding but incorrect or fabricated information.

**Example**:
```
Prompt: "Who won the Nobel Prize in Physics in 2025?"
Bad Response: "Dr. Jane Smith won for her work on quantum computing."
(Person may not exist, or fact is made up)
```

### 10. **Few-Shot Learning**
Providing examples in the prompt to guide the model's behavior.

**Example**:
```
Extract names from text:

Text: "John went to the store"
Names: John

Text: "Mary and Bob went hiking"
Names: Mary, Bob

Text: "The CEO met with investors"
Names: [model completes this]
```

### 11. **Zero-Shot Learning**
The model performs a task without any examples, just instructions.

**Example**:
```
Translate this to French: "Hello, how are you?"
```

### 12. **Chain-of-Thought (CoT)**
Prompting technique that encourages step-by-step reasoning.

**Example**:
```
Question: If a train leaves at 2pm traveling 60mph, and needs to go 180 miles, 
when does it arrive?

Let's think step by step:
1. Speed = 60 mph
2. Distance = 180 miles
3. Time = Distance / Speed = 180 / 60 = 3 hours
4. Departure = 2pm + 3 hours = 5pm
Answer: 5pm
```

### 13. **Parameters**
The learned weights in a neural network that determine the model's behavior.

**Model Size Comparison**:
- GPT-3: 175 billion parameters
- GPT-4: Estimated 1.7 trillion (multimodal)
- LLaMA 2: 7B to 70B parameters

**Trade-off**: More parameters → Better performance but slower/more expensive

### 14. **Inference**
The process of using a trained model to generate outputs.

**Training vs Inference**:
```
Training: Learning patterns from data (slow, expensive)
Inference: Using the model to generate (fast, cheaper)
```

### 15. **Multimodal Models**
Models that can process and generate multiple types of content (text, images, audio).

**Examples**:
- GPT-4V (text + images)
- Gemini (text + images + audio + video)

## Model Architecture Terms

### 16. **Transformer**
The neural network architecture underlying most modern LLMs.

**Key Innovation**: Self-attention mechanism that processes all words in relation to each other.

### 17. **Attention Mechanism**
Allows the model to focus on relevant parts of the input when generating output.

**Example**: In "The animal didn't cross the street because it was too tired"
- "it" could refer to "animal" or "street"
- Attention helps model understand "it" → "animal"

### 18. **Pre-training and Post-training**
- **Pre-training**: Initial training on vast text data (unsupervised)
- **Post-training**: Fine-tuning with human feedback (RLHF) for safety and helpfulness

## Practical Glossary

| Term | Simple Definition |
|------|-------------------|
| **API** | Interface to access AI models programmatically |
| **Latency** | Time delay between sending prompt and receiving response |
| **Throughput** | Number of tokens processed per second |
| **Batch Processing** | Processing multiple requests together |
| **Streaming** | Receiving response word-by-word as generated |
| **System Prompt** | Initial instructions that set model behavior |
| **User Prompt** | The actual user's input/question |
| **Completion** | The model's generated response |

## Common Abbreviations

- **LLM**: Large Language Model
- **RAG**: Retrieval-Augmented Generation
- **CoT**: Chain-of-Thought
- **RLHF**: Reinforcement Learning from Human Feedback
- **NLP**: Natural Language Processing
- **GPT**: Generative Pre-trained Transformer
- **API**: Application Programming Interface
- **ML**: Machine Learning
- **AI**: Artificial Intelligence

## Exercise

Match the term to the scenario:

1. You want consistent, factual answers → Use low ___________
2. Processing "The answer is 42" uses about ___ tokens
3. To give examples in your prompt, you're doing ___________ learning
4. A model creating made-up facts is experiencing ___________
5. Combining your database with an LLM is called ___________

**Answers**: 1. Temperature, 2. 4-5, 3. Few-shot, 4. Hallucination, 5. RAG

---

**Next**: [Types of Generative Models](./03-model-types.md)
