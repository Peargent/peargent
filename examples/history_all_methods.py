"""
Comprehensive History Examples for Peargent

This example demonstrates different storage backends for conversation history,
all using a consistent and intuitive API.

Key Concept: Use HistoryConfig with the desired storage type
"""

import os
from peargent import create_agent, create_pool
from peargent.config.history import HistoryConfig
from peargent.core.history.storage_types import (
    SessionBuffer,
    File,
    Sqlite,
    Postgresql,
    Redis,
)
from peargent.models import groq


# ============================================================================
# EXAMPLE 1: In-Memory Storage (Session Buffer)
# ============================================================================
# Best for: Testing, development, temporary conversations
# Persistence: No (lost when program ends)

def example_session_buffer():
    """Using in-memory session buffer - simplest option."""
    print("\n=== EXAMPLE 1: Session Buffer (In-Memory) ===")

    # Create agent with in-memory history
    agent = create_agent(
        name="Assistant",
        description="A helpful assistant",
        persona="You are helpful and friendly.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            store=SessionBuffer()
        )
    )

    # Use the agent - history is automatically managed
    response1 = agent.run("Hello! My name is Alice.")
    print(f"Agent: {response1}")

    response2 = agent.run("What's my name?")
    print(f"Agent: {response2}")

    return agent


# ============================================================================
# EXAMPLE 2: File-Based Storage (JSON)
# ============================================================================
# Best for: Local development, single-user apps, easy inspection

def example_file_storage():
    """Using file-based storage with JSON files."""
    print("\n=== EXAMPLE 2: File-Based Storage (JSON) ===")

    # Create agent with file-based history
    agent = create_agent(
        name="PythonTutor",
        description="Python programming tutor",
        persona="You are a patient Python teacher.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=10,
            strategy="trim_last",
            store=File(storage_dir="./conversation_history")
        )
    )

    # Use the agent - conversations saved to files
    response1 = agent.run("What is a list comprehension?")
    print(f"Agent: {response1}")

    response2 = agent.run("Can you give me an example?")
    print(f"Agent: {response2}")

    print(f"\nConversations saved to: ./conversation_history/")
    return agent


# ============================================================================
# EXAMPLE 3: SQLite Storage
# ============================================================================
# Best for: Desktop apps, local development, structured persistence

def example_sqlite_storage():
    """Using SQLite database storage."""
    print("\n=== EXAMPLE 3: SQLite Storage ===")

    # Create agent with SQLite history
    agent = create_agent(
        name="Comedian",
        description="A funny assistant",
        persona="You tell programming jokes.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=20,
            strategy="smart",
            summarize_model=groq("llama-3.1-8b-instant"),
            store=Sqlite(
                database_path="./chat_app.db",
                table_prefix="peargent"
            )
        )
    )

    # Use the agent - conversations stored in SQLite
    response = agent.run("Tell me a joke about Python")
    print(f"Agent: {response}")

    print(f"\nDatabase: ./chat_app.db")
    print(f"Tables: peargent_threads, peargent_messages")
    return agent


# ============================================================================
# EXAMPLE 4: PostgreSQL Storage
# ============================================================================
# Best for: Production systems, multi-user apps, ACID guarantees

def example_postgresql_storage():
    """Using PostgreSQL database storage."""
    print("\n=== EXAMPLE 4: PostgreSQL Storage ===")

    # Get connection string from environment or use default
    CONNECTION_STRING = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/peargent_db"
    )

    # Create agent with PostgreSQL history
    agent = create_agent(
        name="SupportAgent",
        description="Technical support specialist",
        persona="You provide clear technical support.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=50,
            strategy="smart",
            store=Postgresql(
                connection_string=CONNECTION_STRING,
                table_prefix="peargent"
            )
        )
    )

    # Use the agent - conversations stored in PostgreSQL
    response = agent.run("I need help with deployment")
    print(f"Agent: {response}")

    print(f"\nDatabase: PostgreSQL")
    print(f"Tables: peargent_threads, peargent_messages")
    return agent


# ============================================================================
# EXAMPLE 5: Redis Storage
# ============================================================================
# Best for: High-performance, distributed apps, real-time updates

def example_redis_storage():
    """Using Redis for high-performance distributed storage."""
    print("\n=== EXAMPLE 5: Redis Storage ===")

    # Create agent with Redis history
    agent = create_agent(
        name="WeatherBot",
        description="Real-time weather assistant",
        persona="You provide weather information.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=15,
            strategy="trim_last",
            store=Redis(
                host="localhost",
                port=6379,
                db=0,
                key_prefix="peargent"
            )
        )
    )

    # Use the agent - conversations stored in Redis
    response = agent.run("What's the weather like?")
    print(f"Agent: {response}")

    print(f"\nRedis: localhost:6379")
    return agent


# ============================================================================
# EXAMPLE 6: History with Agent Pools
# ============================================================================
# Best for: Multi-agent workflows with shared conversation history

def example_agent_pools():
    """Using history with agent pools for multi-agent conversations."""
    print("\n=== EXAMPLE 6: History with Agent Pools ===")

    # Create multiple agents
    researcher = create_agent(
        name="Researcher",
        description="Research and gather information",
        persona="You are a thorough researcher who finds accurate information.",
        model=groq("llama-3.3-70b-versatile"),
        tools=[]
    )

    writer = create_agent(
        name="Writer",
        description="Write clear summaries and articles",
        persona="You are a skilled writer who creates engaging content.",
        model=groq("llama-3.3-70b-versatile"),
        tools=[]
    )

    # Create pool with shared history
    pool = create_pool(
        agents=[researcher, writer],
        default_model=groq("llama-3.3-70b-versatile"),
        max_iter=5,
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=20,
            strategy="smart",
            store=File(storage_dir="./pool_conversations")
        )
    )

    # Use the pool - all agents share the same conversation history
    result = pool.run("Research the benefits of exercise and write a brief summary.")
    print(f"Pool result: {result}")

    print(f"\nShared history stored in: ./pool_conversations/")
    return pool


# ============================================================================
# EXAMPLE 7: Advanced Context Management
# ============================================================================
# Best for: Long conversations, token optimization

def example_context_management():
    """Using advanced context management strategies."""
    print("\n=== EXAMPLE 7: Advanced Context Management ===")

    # Option 1: Automatic trimming (keep last N messages)
    agent_trim = create_agent(
        name="TrimAgent",
        description="Agent with trimming strategy",
        persona="You maintain context efficiently.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=10,
            strategy="trim_last",
            store=Sqlite(database_path="./trim_agent.db")
        )
    )

    # Option 2: Automatic summarization (summarize old messages)
    agent_summarize = create_agent(
        name="SummarizeAgent",
        description="Agent with summarization strategy",
        persona="You maintain context efficiently.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=20,
            strategy="summarize",
            summarize_model=groq("llama-3.1-8b-instant"),
            store=Sqlite(database_path="./summarize_agent.db")
        )
    )

    # Option 3: Smart strategy (auto-decides best approach)
    agent_smart = create_agent(
        name="SmartAgent",
        description="Agent with smart context management",
        persona="You maintain context efficiently.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=15,
            strategy="smart",  # Automatically chooses trim or summarize
            summarize_model=groq("llama-3.1-8b-instant"),
            store=Sqlite(database_path="./smart_agent.db")
        )
    )

    print("Created agents with different context management strategies:")
    print("  - TrimAgent: Keeps last 10 messages")
    print("  - SummarizeAgent: Summarizes old messages, keeps last 20")
    print("  - SmartAgent: Auto-selects best strategy for context")

    return agent_trim, agent_summarize, agent_smart


# ============================================================================
# EXAMPLE 8: Multi-User Application Pattern
# ============================================================================
# Best for: Multi-user apps, organizing conversations with metadata

def example_multi_user():
    """Pattern for multi-user applications with organized threads."""
    print("\n=== EXAMPLE 8: Multi-User Application Pattern ===")

    # Create agent with SQLite storage for multi-user app
    agent = create_agent(
        name="CustomerSupport",
        description="Customer support assistant",
        persona="You provide helpful customer support.",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,
            max_context_messages=30,
            strategy="smart",
            store=Sqlite(database_path="./multi_user.db")
        )
    )

    # In a real app, you would:
    # 1. Create a new thread for each user session
    # 2. Store user metadata in the thread
    # 3. Switch between threads as needed

    print("Multi-user pattern:")
    print("  1. Each user gets their own thread")
    print("  2. Thread metadata stores user info (user_id, session, etc.)")
    print("  3. Agent switches between threads for different users")
    print("  4. All conversations stored in one database")

    return agent


# ============================================================================
# SUMMARY: Choose Your Storage Backend
# ============================================================================

def print_summary():
    """Print summary of all storage options."""
    print("\n" + "=" * 80)
    print("CHOOSING THE RIGHT STORAGE BACKEND")
    print("=" * 80)
    print("""
📝 ALL HISTORY CONFIGURATION USES THE SAME PATTERN:

    agent = create_agent(
        name="YourAgent",
        model=groq("llama-3.3-70b-versatile"),
        history=HistoryConfig(
            auto_manage_context=True,      # Optional: auto-manage context
            max_context_messages=20,       # Optional: max messages to keep
            strategy="smart",              # Optional: "smart", "trim_last", "summarize"
            summarize_model=groq(...),     # Optional: model for summarization
            store=<StorageType>            # Choose your storage backend
        )
    )

🗄️  STORAGE BACKEND OPTIONS:

1. SessionBuffer()
   └─ In-memory (temporary)
   └─ Best for: Testing, development
   └─ Example: store=SessionBuffer()

2. File(storage_dir="./path")
   └─ JSON files on disk
   └─ Best for: Local dev, single-user apps
   └─ Example: store=File(storage_dir="./conversations")

3. Sqlite(database_path="./db.db")
   └─ SQLite database
   └─ Best for: Desktop apps, local persistence
   └─ Example: store=Sqlite(database_path="./chat.db")

4. Postgresql(connection_string="...")
   └─ PostgreSQL database
   └─ Best for: Production, multi-user systems
   └─ Example: store=Postgresql(connection_string="postgresql://...")

5. Redis(host="localhost", port=6379)
   └─ Redis in-memory store
   └─ Best for: High-performance, distributed apps
   └─ Example: store=Redis(host="localhost", port=6379)

⚙️  CONTEXT MANAGEMENT STRATEGIES:

- auto_manage_context=False
  └─ Manual control (no automatic management)

- strategy="trim_last"
  └─ Keep only the last N messages

- strategy="summarize"
  └─ Summarize old messages, keep recent ones
  └─ Requires: summarize_model=groq("llama-3.1-8b-instant")

- strategy="smart"
  └─ Automatically choose best strategy
  └─ Recommended for most use cases

💡 QUICK START:

For development:
    history=HistoryConfig(store=SessionBuffer())

For production:
    history=HistoryConfig(
        auto_manage_context=True,
        max_context_messages=20,
        strategy="smart",
        summarize_model=groq("llama-3.1-8b-instant"),
        store=Sqlite(database_path="./app.db")
    )
    """)


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Run demonstrations."""
    print("=" * 80)
    print("PEARGENT HISTORY EXAMPLES")
    print("All storage backends use the same intuitive HistoryConfig API")
    print("=" * 80)

    # Uncomment the examples you want to run:

    # Example 1: In-Memory Storage
    # agent1 = example_session_buffer()

    # Example 2: File-Based Storage
    # agent2 = example_file_storage()

    # Example 3: SQLite Storage
    # agent3 = example_sqlite_storage()

    # Example 4: PostgreSQL Storage (requires PostgreSQL server)
    # agent4 = example_postgresql_storage()

    # Example 5: Redis Storage (requires Redis server)
    # agent5 = example_redis_storage()

    # Example 6: Agent Pools
    # pool6 = example_agent_pools()

    # Example 7: Context Management
    # agents7 = example_context_management()

    # Example 8: Multi-User Pattern
    # agent8 = example_multi_user()

    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
