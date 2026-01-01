"""
Basic Wikipedia Knowledge Tool Example

Demonstrates how to search Wikipedia and extract knowledge
using the WikipediaKnowledgeTool.
"""

from peargent import create_agent
from peargent.tools import wikipedia_tool
from peargent.models import gemini


def main():
    print("=" * 60)
    print("Wikipedia Knowledge Tool - Basic Example")
    print("=" * 60)
    
    # Example 1: Search for a well-known article
    print("\n1. Searching for 'Grand Theft Auto V':")
    print("-" * 60)
    
    result = wikipedia_tool.run({"query": "Grand Theft Auto V"})
    
    if result["success"] and result["text"]:
        print(f"Title: {result['metadata']['title']}")
        print(f"URL: {result['metadata']['url']}")
        print(f"\nSummary:\n{result['text'][:300]}...")
        if 'links' in result['metadata']:
            print(f"\nRelated links (first 5): {result['metadata']['links'][:5]}")
    else:
        print(f"Error or not found: {result['error']}")
        if 'suggestions' in result.get('metadata', {}):
            print(f"Suggestions: {result['metadata']['suggestions']}")
    
    # Example 2: Search that doesn't exist
    print("\n\n2. Searching for non-existent article 'asdfghjkl':")
    print("-" * 60)
    
    result = wikipedia_tool.run({"query": "asdfghjkl"})
    
    if not result["text"]:
        print(f"Article not found: {result.get('error') or result['metadata'].get('message', 'Not found')}")
        if 'suggestions' in result.get('metadata', {}):
            print(f"Suggestions: {result['metadata']['suggestions']}")
    
    # Example 3: Search with categories
    print("\n\n3. Searching with categories enabled:")
    print("-" * 60)
    
    result = wikipedia_tool.run({
        "query": "Artificial Intelligence",
        "extract_categories": True
    })
    
    if result["success"] and result["text"]:
        print(f"Title: {result['metadata']['title']}")
        if 'categories' in result['metadata']:
            print(f"Categories (first 5): {result['metadata']['categories'][:5]}")
    
    # Example 4: Using Wikipedia tool with an agent
    print("\n\n4. Using Wikipedia tool with an agent:")
    print("-" * 60)
    
    try:
        agent = create_agent(
            name="WikipediaAgent",
            description="A Wikipedia research assistant",
            persona=(
                "You are a helpful research assistant. When asked about topics, "
                "use Wikipedia to find accurate information and provide concise summaries."
            ),
            model=gemini("gemini-2.5-flash-lite"),
            tools=[wikipedia_tool]
        )
        
        response = agent.run("Tell me about the Grand Theft Auto V")
        print(f"\nAgent Response:\n{response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"\nNote: Agent requires API key. Skipping agent demo.")
        print("Set GEMINI_API_KEY in your .env file to run this example.")
        print("\nDirect Wikipedia lookup works without API key:")
        result = wikipedia_tool.run({"query": "Grand Theft Auto V"})
        if result["success"] and result["text"]:
            print(f"Title: {result['metadata']['title']}")
            print(f"Summary: {result['text'][:200]}...")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
