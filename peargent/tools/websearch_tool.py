"""
Web Search Tool for Peargent
Queries search engines (DuckDuckGo) for up-to-date information and retrieves results.
"""

from typing import Dict, Any, Optional, List

from peargent import Tool

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


def web_search(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    time_range: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo and retrieve search results.
    
    Provides:
    - Search result titles and snippets
    - URLs for each result
    - Source metadata
    - Safe search filtering
    - Regional and time-based filtering
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5, max: 25)
        region: Region code for localized results (default: "wt-wt" for worldwide)
                Examples: "us-en" (US English), "uk-en" (UK English), "de-de" (Germany)
        safesearch: Safe search level - "strict", "moderate", or "off" (default: "moderate")
        time_range: Filter by time - "d" (day), "w" (week), "m" (month), "y" (year), None (all time)
        
    Returns:
        Dictionary containing:
            - results: List of search results with title, snippet, url
            - metadata: Dict with query info, result count, search engine
            - success: Boolean indicating success
            - error: Error message if any
            
    Example:
        >>> result = web_search("Python programming tutorials")
        >>> for r in result["results"]:
        ...     print(f"{r['title']}: {r['url']}")
        ...     print(r['snippet'])
    """
    if not DDGS_AVAILABLE:
        return {
            "results": [],
            "metadata": {},
            "success": False,
            "error": (
                "ddgs library is required for web search. "
                "Install it with: pip install ddgs"
            )
        }
    
    # Validate parameters
    if not query or not query.strip():
        return {
            "results": [],
            "metadata": {},
            "success": False,
            "error": "Query cannot be empty"
        }
    
    # Limit max_results
    max_results = min(max(1, max_results), 25)
    
    # Validate safesearch
    if safesearch not in ["strict", "moderate", "off"]:
        safesearch = "moderate"
    
    # Validate time_range
    if time_range and time_range not in ["d", "w", "m", "y"]:
        time_range = None
    
    try:
        # Use DuckDuckGo search via DDGS library
        results = _search_duckduckgo_api(query, max_results, region, safesearch, time_range)
        
        if not results:
            return {
                "results": [],
                "metadata": {
                    "query": query,
                    "result_count": 0,
                    "search_engine": "DuckDuckGo",
                    "message": "No results found for your query"
                },
                "success": True,
                "error": None
            }
        
        # Build metadata
        metadata = {
            "query": query,
            "result_count": len(results),
            "search_engine": "DuckDuckGo",
            "region": region,
            "safesearch": safesearch
        }
        
        if time_range:
            metadata["time_range"] = time_range
        
        return {
            "results": results,
            "metadata": metadata,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        # Handle different request exceptions
        error_type = type(e).__name__
        if "Timeout" in error_type:
            error_msg = "Request timed out. Please try again."
        elif "RequestException" in error_type or "ConnectionError" in error_type:
            error_msg = f"Network error: {str(e)}"
        else:
            error_msg = f"Unexpected error: {str(e)}"
        
        return {
            "results": [],
            "metadata": {},
            "success": False,
            "error": error_msg
        }


def _search_duckduckgo_api(
    query: str,
    max_results: int,
    region: str,
    safesearch: str,
    time_range: Optional[str]
) -> List[Dict[str, str]]:
    """
    Perform search using DuckDuckGo API via duckduckgo-search library.
    
    Returns:
        List of dicts with 'title', 'snippet', 'url' keys
    """
    # Map safesearch to DDGS parameter
    safesearch_map = {
        "strict": "strict",
        "moderate": "moderate",
        "off": "off"
    }
    
    # Map time_range to DDGS parameter
    timelimit_map = {
        "d": "d",  # day
        "w": "w",  # week
        "m": "m",  # month
        "y": "y"   # year
    }
    
    try:
        ddgs = DDGS()
        
        # Prepare search parameters
        search_kwargs = {
            "max_results": max_results,
            "region": region,
            "safesearch": safesearch_map.get(safesearch, "moderate")
        }
        
        # Add time limit if specified
        if time_range and time_range in timelimit_map:
            search_kwargs["timelimit"] = timelimit_map[time_range]
        
        # Perform search
        search_results = ddgs.text(query, **search_kwargs)
        
        # Convert to our format
        results = []
        for r in search_results:
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", "")
            })
        
        return results
        
    except Exception as e:
        raise Exception(f"DuckDuckGo search failed: {str(e)}")


class WebSearchTool(Tool):
    """
    Tool for searching the web using DuckDuckGo.
    
    Features:
    - Web search with customizable result count
    - Regional filtering for localized results
    - Safe search filtering
    - Time-based filtering (day, week, month, year)
    - Returns titles, snippets, and URLs
    
    Use cases:
    - Research and information gathering
    - Fact-checking and verification
    - RAG (Retrieval Augmented Generation) applications
    - Real-time information lookup
    - Grounding agent responses with current data
    
    Example:
        >>> from peargent.tools import WebSearchTool
        >>> tool = WebSearchTool()
        >>> result = tool.run({"query": "latest AI developments"})
        >>> for r in result["results"]:
        ...     print(f"{r['title']}: {r['url']}")
    """
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description=(
                "Search the web using DuckDuckGo for up-to-date information. "
                "Returns search results with titles, snippets, and URLs. "
                "Supports filtering by region, safe search level, and time range. "
                "Optional parameters: max_results (int, default: 5, max: 25), "
                "region (str, default: 'wt-wt'), safesearch (str: 'strict'/'moderate'/'off'), "
                "time_range (str: 'd'/'w'/'m'/'y' or None for all time)."
            ),
            input_parameters={
                "query": str
            },
            call_function=web_search
        )


# Create default instance for easy import
websearch_tool = WebSearchTool()
