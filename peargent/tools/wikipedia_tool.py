"""
Wikipedia Knowledge Extraction Tool for Peargent
Queries Wikipedia for facts, summaries, and reference links.
"""

import re
from typing import Dict, Any, Optional
from urllib.parse import quote

from peargent import Tool

try:
    import requests
except ImportError:
    requests = None 


def search_wikipedia(
    query: str,
    extract_links: bool = True,
    extract_categories: bool = False,
    max_summary_length: Optional[int] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Search Wikipedia and extract article information.
    
    Handles cases where articles don't exist or have different names by:
    - Using Wikipedia's search API to find the best match
    - Suggesting alternative article titles
    - Providing disambiguation information
    
    Args:
        query: Search term or article title to look up
        extract_links: Whether to extract internal Wikipedia links
        extract_categories: Whether to extract article categories
        max_summary_length: Maximum summary length (truncates if exceeded)
        language: Wikipedia language code (default: "en" for English)
        
    Returns:
        Dictionary containing:
            - text: Article summary/introduction text
            - metadata: Dict with title, url, links, categories, suggestions, disambiguation
            - format: Source type (always "wikipedia")
            - success: Boolean indicating success
            - error: Error message if any
            
    Example:
        >>> result = search_wikipedia("Python programming language")
        >>> print(result["text"])
        >>> print(result["metadata"]["url"])
        >>> print(result["metadata"]["title"])
    """
    if requests is None:
        return {
            "text": "",
            "metadata": {},
            "format": "wikipedia",
            "success": False,
            "error": (
                "requests library is required for Wikipedia extraction. "
                "Install it with: pip install requests"
            )
        }
    
    # Validate language code
    if not re.match(r'^[a-z]{2,3}$', language):
        return {
            "text": "",
            "metadata": {},
            "format": "wikipedia",
            "success": False,
            "error": f"Invalid language code: {language}"
        }
    
    # Wikipedia API endpoint
    base_url = f"https://{language}.wikipedia.org/w/api.php"
    
    try:
        # First, try to search for the article
        search_result = _search_article(base_url, query)
        
        if not search_result["found"]:
            # Article not found, return suggestions
            return {
                "text": "",
                "metadata": {
                    "suggestions": search_result.get("suggestions", []),
                    "message": f"No exact match found for '{query}'. See suggestions for alternatives."
                },
                "format": "wikipedia",
                "success": True,
                "error": None
            }
        
        article_title = search_result["title"]
        
        # Get full article content
        article_data = _get_article_content(
            base_url,
            article_title,
            extract_links,
            extract_categories
        )
        
        # Check if it's a disambiguation page
        if article_data.get("is_disambiguation", False):
            return {
                "text": "Multiple possible meanings found for this term. Choose a more specific topic.",
                "metadata": {
                    "title": article_title,
                    "url": f"https://{language}.wikipedia.org/wiki/{quote(article_title.replace(' ', '_'))}",
                    "disambiguation": article_data.get("disambiguation_options", [])
                },
                "format": "wikipedia",
                "success": True,
                "error": None
            }
        
        # Extract summary
        summary = article_data.get("extract", "")
        
        # Apply max_summary_length if specified
        if max_summary_length and len(summary) > max_summary_length:
            summary = summary[:max_summary_length] + "..."
        
        # Build metadata
        metadata = {
            "title": article_title,
            "url": f"https://{language}.wikipedia.org/wiki/{quote(article_title.replace(' ', '_'))}"
        }
        
        if extract_links:
            metadata["links"] = article_data.get("links", [])
        
        if extract_categories:
            metadata["categories"] = article_data.get("categories", [])
        
        # Build result
        result = {
            "text": summary.strip(),
            "metadata": metadata,
            "format": "wikipedia",
            "success": True,
            "error": None
        }
        
        return result
        
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
            "text": "",
            "metadata": {},
            "format": "wikipedia",
            "success": False,
            "error": error_msg
        }


def _search_article(base_url: str, query: str) -> Dict[str, Any]:
    """
    Search for article using Wikipedia's search API.
    
    Returns:
        Dict with "found" (bool), "title" (str), and "suggestions" (list)
    """
    # Use opensearch API for better search results
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 5,
        "format": "json",
        "redirects": "resolve"
    }
    
    headers = {
        "User-Agent": "Peargent/0.1 (https://github.com/Peargent/peargent) Python/requests"
    }
    
    response = requests.get(base_url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    # OpenSearch returns: [query, [titles], [descriptions], [urls]]
    if len(data) >= 2 and len(data[1]) > 0:
        best_title = data[1][0]
        # Check if it's an exact match (case-insensitive)
        is_exact_match = best_title.lower() == query.lower()
        
        return {
            "found": is_exact_match,
            "title": best_title,
            "suggestions": data[1] if not is_exact_match else data[1][1:]
        }
    
    return {
        "found": False,
        "title": "",
        "suggestions": []
    }


def _get_article_content(
    base_url: str,
    title: str,
    extract_links: bool,
    extract_categories: bool
) -> Dict[str, Any]:
    """
    Get full article content including summary, links, and metadata.
    """
    # Build prop list
    props = ["extracts", "info", "pageprops"]
    if extract_links:
        props.append("links")
    if extract_categories:
        props.append("categories")
    
    params = {
        "action": "query",
        "titles": title,
        "prop": "|".join(props),
        "explaintext": True,
        "exintro": True,  # Get introduction only
        "redirects": 1,
        "format": "json",
        "pllimit": 50,  # Limit links to 50
        "cllimit": 50   # Limit categories to 50
    }
    
    headers = {
        "User-Agent": "Peargent/0.1 (https://github.com/Peargent/peargent) Python/requests"
    }
    
    response = requests.get(base_url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    # Extract page data
    pages = data.get("query", {}).get("pages", {})
    page_id = list(pages.keys())[0]
    page = pages[page_id]
    
    # Check if page exists
    if page_id == "-1" or "missing" in page:
        return {"extract": "", "links": [], "categories": []}
    
    # Check if disambiguation page
    page_props = page.get("pageprops", {})
    is_disambiguation = "disambiguation" in page_props
    
    result = {
        "extract": page.get("extract", ""),
        "is_disambiguation": is_disambiguation
    }
    
    # Handle disambiguation page
    if is_disambiguation:
        # Get links as disambiguation options
        links = page.get("links", [])
        result["disambiguation_options"] = [link["title"] for link in links[:20]]
        return result
    
    # Extract links
    if extract_links:
        links = page.get("links", [])
        result["links"] = [link["title"] for link in links if "title" in link]
    
    # Extract categories
    if extract_categories:
        categories = page.get("categories", [])
        result["categories"] = [
            cat["title"].replace("Category:", "")
            for cat in categories
            if "title" in cat
        ]
    
    return result


class WikipediaKnowledgeTool(Tool):
    """
    Tool for querying Wikipedia and extracting knowledge.
    
    Handles:
    - Article search with fuzzy matching
    - Summary extraction
    - Related links and categories
    - Disambiguation pages
    - Article suggestions when not found
    
    Example:
        >>> from peargent.tools import WikipediaKnowledgeTool
        >>> tool = WikipediaKnowledgeTool()
        >>> result = tool.run({"query": "Python programming"})
        >>> print(result["text"])
        >>> print(result["metadata"]["url"])
    """
    
    def __init__(self):
        super().__init__(
            name="wikipedia_query",
            description=(
                "Search Wikipedia for facts, summaries, and reference links. "
                "Returns article summary, URL, related links, and categories. "
                "Handles cases where articles don't exist by providing suggestions. "
                "Optional parameters: extract_links (bool, default: True), "
                "extract_categories (bool, default: False), max_summary_length (int, optional), "
                "language (str, default: 'en')."
            ),
            input_parameters={
                "query": str
            },
            call_function=search_wikipedia
        )


# Create default instance for easy import
wikipedia_tool = WikipediaKnowledgeTool()
