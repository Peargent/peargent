"""
Async Streaming Examples

Demonstrates async streaming with astream() and aobserve().
"""

import asyncio
import sys
from peargent import create_agent, create_pool
from peargent.observability import enable_tracing
from peargent.models import groq
from peargent import UpdateType

# Enable tracing
tracer = enable_tracing()


async def example_1_basic_astream():
    """Basic async streaming with astream()"""
    print("="*80)
    print("EXAMPLE 1: Basic astream()")
    print("="*80 + "\n")

    agent = create_agent(
        name="AsyncAgent",
        description="An async streaming agent",
        persona="You are helpful and concise.",
        model=groq("llama-3.3-70b-versatile"),
        tracing=True
    )

    print("Q: What is async programming?")
    print("A: ", end="", flush=True)

    async for chunk in agent.astream("Explain async programming in 2 sentences"):
        print(chunk, end="", flush=True)
        sys.stdout.flush()

    print("\n\n" + "-"*80 + "\n")


async def example_2_astream_observe():
    """Async streaming with metadata using astream_observe()"""
    print("="*80)
    print("EXAMPLE 2: astream_observe() with metadata")
    print("="*80 + "\n")

    agent = create_agent(
        name="ObservableAgent",
        description="An observable async agent",
        persona="You are helpful.",
        model=groq("llama-3.3-70b-versatile"),
        tracing=True
    )

    print("Q: What is Python used for?")
    print()

    async for update in agent.astream_observe("What is Python used for? Give 3 use cases."):
        if update.is_agent_start:
            print(f"[START] {update.agent}")
            print("A: ", end="", flush=True)

        elif update.is_token:
            print(update.content, end="", flush=True)
            sys.stdout.flush()

        elif update.is_agent_end:
            print(f"\n\n[DONE] {update.tokens} tokens, ${update.cost:.6f}, {update.duration:.2f}s")

    print("\n" + "-"*80 + "\n")


async def example_3_concurrent_agents():
    """Run multiple agents concurrently"""
    print("="*80)
    print("EXAMPLE 3: Concurrent agent execution")
    print("="*80 + "\n")

    # Create multiple agents
    agent1 = create_agent(
        name="Agent1",
        description="First agent",
        persona="You are concise.",
        model=groq("llama-3.3-70b-versatile"),
        tracing=True
    )

    agent2 = create_agent(
        name="Agent2",
        description="Second agent",
        persona="You are concise.",
        model=groq("llama-3.3-70b-versatile"),
        tracing=True
    )

    agent3 = create_agent(
        name="Agent3",
        description="Third agent",
        persona="You are concise.",
        model=groq("llama-3.3-70b-versatile"),
        tracing=True
    )

    # Define async tasks
    async def run_agent(agent, query, label):
        print(f"[{label}] Starting: {query[:30]}...")
        response = ""
        async for chunk in agent.astream(query):
            response += chunk
        print(f"[{label}] Complete: {len(response)} chars")
        return response

    # Run agents concurrently
    results = await asyncio.gather(
        run_agent(agent1, "What is 2+2?", "Agent1"),
        run_agent(agent2, "What is the capital of France?", "Agent2"),
        run_agent(agent3, "What color is the sky?", "Agent3"),
    )

    print("\nResults:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result[:50]}...")

    print("\n" + "-"*80 + "\n")


async def example_4_pool_astream_observe():
    """Async pool observation"""
    print("="*80)
    print("EXAMPLE 4: Pool astream_observe()")
    print("="*80 + "\n")

    # Create agents
    researcher = create_agent(
        name="Researcher",
        description="Research specialist",
        persona="Be brief and factual.",
        model=groq("llama-3.3-70b-versatile"),
        tracing=True
    )

    writer = create_agent(
        name="Writer",
        description="Content writer",
        persona="Be clear and brief.",
        model=groq("llama-3.3-70b-versatile"),
        tracing=True
    )

    # Create pool
    def router(state, call_count, last_result):
        from peargent import RouterResult
        agents = ["Researcher", "Writer"]
        if call_count < len(agents):
            return RouterResult(agents[call_count])
        return RouterResult(None)

    pool = create_pool(
        agents=[researcher, writer],
        router=router,
        max_iter=2,
        tracing=True
    )

    print("Query: Explain machine learning briefly\n")

    async for update in pool.astream_observe("Explain machine learning briefly"):
        if update.type == UpdateType.POOL_START:
            print("[POOL START]\n")

        elif update.is_agent_start:
            print(f"\n[{update.agent}] ", end="", flush=True)

        elif update.is_token:
            print(update.content, end="", flush=True)
            sys.stdout.flush()

        elif update.is_agent_end:
            print(f"\n[{update.agent} DONE] {update.tokens} tokens, ${update.cost:.6f}")

        elif update.type == UpdateType.POOL_END:
            print(f"\n[POOL END] Total: {update.metadata.get('total_tokens')} tokens, ${update.metadata.get('total_cost', 0):.6f}")

    print("\n" + "-"*80 + "\n")


async def main():
    """Run all examples"""
    print("\n")
    print("="*80)
    print("ASYNC STREAMING EXAMPLES")
    print("="*80)
    print("\n")

    await example_1_basic_astream()
    await example_2_astream_observe()
    await example_3_concurrent_agents()
    await example_4_pool_astream_observe()

    # Final summary
    print("="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    tracer.print_summary()

    print("\n" + "="*80)
    print("ASYNC STREAMING BENEFITS")
    print("="*80)
    print("""
1. NON-BLOCKING
   - Run multiple agents concurrently
   - Better resource utilization
   - Faster total execution time

2. SCALABILITY
   - Handle many concurrent requests
   - Perfect for web servers
   - Efficient for high-load scenarios

3. SAME API
   - agent.stream() => agent.astream()
   - agent.stream_observe() => agent.astream_observe()
   - pool.stream() => pool.astream()
   - pool.stream_observe() => pool.astream_observe()

4. USE CASES
   - Web applications (FastAPI, Django)
   - Concurrent agent execution
   - Real-time streaming APIs
   - High-throughput systems

EXAMPLE:
    # Sync
    for chunk in agent.stream("query"):
        print(chunk, end="")

    # Async
    async for chunk in agent.astream("query"):
        print(chunk, end="")
""")


if __name__ == "__main__":
    asyncio.run(main())
