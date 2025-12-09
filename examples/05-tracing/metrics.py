"""
Aggregate Metrics Demo

This example demonstrates all the ways to get aggregate statistics
across traces, including filtering by session, user, and agent.
"""

from peargent import create_agent, create_pool, create_routing_agent
from peargent.observability import enable_tracing
from peargent.models import groq
from peargent.observability import set_session_id, set_user_id

# ============================================================================
# Setup: Enable tracing
# ============================================================================

tracer = enable_tracing(
    store_type="memory"
)

# ============================================================================
# Scenario 1: Track costs for a pool execution
# ============================================================================

print("="*80)
print("SCENARIO 1: POOL EXECUTION TRACKING")
print("="*80 + "\n")

# Create a simple pool
agent1 = create_agent(
    name="Analyst",
    description="Data analyst",
    persona="You are a data analyst.",
    model=groq("llama-3.3-70b-versatile"),
    # tracing=True
)

agent2 = create_agent(
    name="Summarizer",
    description="Content summarizer",
    persona="You are a summarizer.",
    model=groq("llama-3.3-70b-versatile"),
    # tracing=True
)

def simple_router(state, call_count, last_result):
    from peargent import RouterResult
    if call_count == 0:
        return RouterResult("Analyst")
    elif call_count == 1:
        return RouterResult("Summarizer")
    return RouterResult(None)

pool = create_pool(
    agents=[agent1, agent2],
    router=simple_router,
    max_iter=2,
    tracing=True
)

# Run the pool
result = pool.run("What are the benefits of renewable energy?")

# Get aggregate stats for the entire pool
print("\nPool Execution Complete!")
tracer.print_summary()

print("\nAggregate statistics for the pool run:")
pool_stats = tracer.get_aggregate_stats()
print(f"  Total Tokens: {pool_stats['total_tokens']:,}")
print(f"  Total LLM Calls: {pool_stats['total_llm_calls']}")
print(f"  Total Duration: {pool_stats['total_duration']:.3f}s")
print(f"  Total Cost: ${pool_stats['total_cost']:.6f}")

# ============================================================================
# Scenario 2: Track costs per agent across multiple runs
# ============================================================================

print("\n" + "="*80)
print("SCENARIO 2: PER-AGENT COST TRACKING")
print("="*80 + "\n")

# Run individual agents multiple times
agent1.run("Question 1")
agent1.run("Question 2")
agent2.run("Question 3")

# Get stats for each agent separately
print("Analyst costs:")
analyst_stats = tracer.get_aggregate_stats(agent_name="Analyst")
print(f"  Total Tokens: {analyst_stats['total_tokens']:,}")
print(f"  Total LLM Calls: {analyst_stats['total_llm_calls']}")
print(f"  Avg Tokens/Call: {analyst_stats['avg_tokens_per_trace']:.1f}")

print("\nSummarizer costs:")
summarizer_stats = tracer.get_aggregate_stats(agent_name="Summarizer")
print(f"  Total Tokens: {summarizer_stats['total_tokens']:,}")
print(f"  Total LLM Calls: {summarizer_stats['total_llm_calls']}")
print(f"  Avg Tokens/Call: {summarizer_stats['avg_tokens_per_trace']:.1f}")

# ============================================================================
# Scenario 3: Session-based tracking
# ============================================================================

print("\n" + "="*80)
print("SCENARIO 3: SESSION-BASED TRACKING")
print("="*80 + "\n")

# Set session context
set_session_id("session-123")

# Create agent with session context
session_agent = create_agent(
    name="SessionAgent",
    description="Agent with session tracking",
    persona="You are helpful.",
    model=groq("llama-3.3-70b-versatile"),
    tracing=True
)

# Run multiple times in the same session
session_agent.run("First question in session")
session_agent.run("Second question in session")
session_agent.run("Third question in session")

# Get aggregate stats for this session
print("Session stats:")
session_stats = tracer.get_aggregate_stats(session_id="session-123")
print(f"  Total Tokens: {session_stats['total_tokens']:,}")
print(f"  Total LLM Calls: {session_stats['total_llm_calls']}")
print(f"  Total Duration: {session_stats['total_duration']:.3f}s")

# ============================================================================
# Summary: All aggregate data
# ============================================================================

print("\n" + "="*80)
print("OVERALL SUMMARY - ALL TRACES")
print("="*80 + "\n")

# Get all traces across all scenarios
all_stats = tracer.get_aggregate_stats()

print("Complete statistics:")
print(f"  Total Traces: {all_stats['total_traces']}")
print(f"  Agents Used: {', '.join(all_stats['agents_used'])}")
print(f"  Total Tokens: {all_stats['total_tokens']:,}")
print(f"  Total LLM Calls: {all_stats['total_llm_calls']}")
print(f"  Total Duration: {all_stats['total_duration']:.3f}s")
print(f"  Total Cost: ${all_stats['total_cost']:.6f}")

print("\n" + "="*80)
print("USE CASES FOR AGGREGATE METRICS")
print("="*80)
print("""
1. POOL MONITORING
   - Track total cost of multi-agent workflows
   - See which agents are most expensive
   - Monitor token usage across the pipeline

2. PER-AGENT ANALYTICS
   - Compare costs between different agents
   - Optimize individual agent prompts
   - Track agent performance over time

3. SESSION TRACKING
   - Monitor user session costs
   - Set budget limits per session
   - Analyze conversation patterns

4. USER-LEVEL TRACKING
   - Track costs per user (set with set_user_id())
   - Implement usage quotas
   - Generate user billing reports

5. PRODUCTION MONITORING
   - Real-time cost tracking
   - Budget alerts and limits
   - Performance optimization

All methods support filtering by:
- session_id: Track costs per conversation
- user_id: Track costs per user
- agent_name: Track costs per agent
- limit: Control how many traces to analyze
""")
