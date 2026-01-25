"""
Basic Web Search Tool Example

Demonstrates how to search the web using DuckDuckGo
with the WebSearchTool.
"""

from peargent import create_agent
from peargent.tools import websearch_tool
from peargent.models import gemini


def main():
    print("=" * 60)
    print("Web Search Tool - Basic Example")
    print("=" * 60)
    
    # Example 1: Simple web search
    print("\n1. Searching for 'Python programming tutorials':")
    print("-" * 60)
    
    result = websearch_tool.run({"query": "Python programming tutorials"})
    
    if result["success"] and result["results"]:
        print(f"Found {result['metadata']['result_count']} results")
        print(f"Search engine: {result['metadata']['search_engine']}")
        print("\nTop results:")
        for i, r in enumerate(result["results"][:3], 1):
            print(f"\n{i}. {r['title']}")
            print(f"   URL: {r['url']}")
            print(f"   Snippet: {r['snippet'][:150]}...")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Search with limited results
    print("\n\n2. Searching with max 3 results:")
    print("-" * 60)
    
    result = websearch_tool.run({
        "query": "latest AI developments",
        "max_results": 3
    })
    
    if result["success"] and result["results"]:
        print(f"Found {len(result['results'])} results")
        for i, r in enumerate(result["results"], 1):
            print(f"\n{i}. {r['title']}")
            print(f"   {r['url']}")
    
    # Example 3: Search with time filter
    print("\n\n3. Searching for recent content (past week):")
    print("-" * 60)
    
    result = websearch_tool.run({
        "query": "technology news",
        "max_results": 5,
        "time_range": "w"  # w = week, d = day, m = month, y = year
    })
    
    if result["success"] and result["results"]:
        print(f"Found {len(result['results'])} recent results")
        if 'time_range' in result['metadata']:
            print(f"Time range: {result['metadata']['time_range']}")
        for i, r in enumerate(result["results"][:3], 1):
            print(f"\n{i}. {r['title']}")
    
    # Example 4: Using web search with an agent
    print("\n\n4. Using web search with an agent:")
    print("-" * 60)
    
    try:
        agent = create_agent(
            name="ResearchAssistant",
            description="A research assistant that uses web search",
            persona=(
                "You are a helpful research assistant. "
                "When asked questions, use the web search tool to find current information. "
                "Provide concise, accurate answers based on search results."
            ),
            model=gemini("gemini-2.5-flash-lite"),
            tools=[websearch_tool]
        )
    
        response = agent.run(
            "What are the latest developments in quantum computing?"
        )
        
        print(f"\nAgent response:\n{response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"\nNote: Agent requires API key. Skipping agent demo.")
        print("Set GEMINI_API_KEY in your .env file to run this example.")
        print("\nDirect web search works without API key:")
        result = websearch_tool.run({"query": "quantum computing developments"})
        if result["success"] and result["results"]:
            print(f"Found {len(result['results'])} results:")
            for i, r in enumerate(result["results"][:2], 1):
                print(f"\n{i}. {r['title']}")
                print(f"   {r['url']}")


if __name__ == "__main__":
    main()
