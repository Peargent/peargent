# Long-Term Memory Examples

This directory contains examples demonstrating the long-term memory feature in Peargent.

## What is Long-Term Memory?

Long-term memory allows agents to remember facts and information across multiple conversations using semantic search. Unlike conversation history which stores the full dialogue, long-term memory:

- **Stores semantic facts** using vector embeddings
- **Retrieves relevant information** based on query similarity
- **Persists across sessions** (when using persistent stores)
- **Auto-extracts facts** from conversations (optional)

## Examples

### `basic_ltm.py`

Basic example showing how to create an agent with long-term memory and have it remember facts across different conversation sessions.

**Features demonstrated:**

- Creating `LongTermMemory` with auto-extraction
- Attaching memory to an agent
- Semantic retrieval across sessions
- Inspecting stored memories

**Run it:**

```bash
# Set your Groq API key (free at console.groq.com)
export GROQ_API_KEY="your-key-here"  # Linux/Mac
$env:GROQ_API_KEY = "your-key-here"  # Windows PowerShell

# Run the example
python examples/10-long-term-memory/basic_ltm.py
```

## API Overview

### LongTermMemory Class

```python
from peargent.memory import LongTermMemory

# Create memory
ltm = LongTermMemory(
    store=None,  # Vector store (defaults to InMemoryVectorStore)
    embedding_method="simple",  # "simple", "sentence-transformers", or "openai"
    embedding_model=None,  # Model for embeddings (optional)
    auto_extract=True  # Automatically extract facts from conversations
)

# Store a fact
memory_id = ltm.store("User loves Python programming")

# Retrieve relevant facts
memories = ltm.retrieve("What does the user like?", limit=3)

# Get specific memory
memory = ltm.get(memory_id)

# Delete memory
ltm.delete(memory_id)

# Clear all
ltm.clear()

# Count memories
count = ltm.count()
```

### Using with Agent

```python
from peargent import create_agent
from peargent.memory import LongTermMemory

ltm = LongTermMemory(auto_extract=True)

agent = create_agent(
    name="MemoryBot",
    model=groq("llama-3.3-70b-versatile"),
    persona="You are a helpful assistant.",
    tools=[],
    long_term_memory=ltm  # Enable long-term memory
)

# Agent automatically retrieves relevant memories
# and stores new facts after each conversation
response = agent.run("My name is Alex")
```

## Vector Stores

### In-Memory (Default)

```python
from peargent.memory.stores import InMemoryVectorStore

ltm = LongTermMemory(store=InMemoryVectorStore())
```

### ChromaDB (Persistent)

```python
from peargent.memory.stores import ChromaVectorStore

ltm = LongTermMemory(store=ChromaVectorStore(path="./chroma_db"))
```

## Embedding Methods

1. **simple** - Fast hash-based embeddings (no dependencies)
2. **sentence-transformers** - High-quality local embeddings (requires `sentence-transformers`)
3. **openai** - OpenAI embeddings API (requires API key)

```python
# Simple (default)
ltm = LongTermMemory(embedding_method="simple")

# Sentence Transformers (better quality)
ltm = LongTermMemory(
    embedding_method="sentence-transformers",
    embedding_model="all-MiniLM-L6-v2"
)

# OpenAI
ltm = LongTermMemory(
    embedding_method="openai",
    embedding_model="text-embedding-3-small"
)
```

## Next Steps

- Try persistent storage with ChromaDB
- Experiment with different embedding methods
- Build a multi-session chatbot that remembers user preferences
- Combine with conversation history for full context
