"""
Tests for Web Search Tool
Tests DuckDuckGo search, filtering options, and error cases.
"""

import pytest
from unittest.mock import patch, Mock


from peargent.tools.websearch_tool import (
    WebSearchTool,
    web_search
)


@patch('peargent.tools.websearch_tool.DDGS')
class TestWebSearch:
    """Test basic web search functionality."""
    
    def test_successful_search(self, mock_ddgs_class):
        """Test a successful web search."""
        # Mock DDGS instance and text method
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = [
            {
                "title": "Python Tutorial",
                "body": "Learn Python programming basics...",
                "href": "https://example.com/python"
            },
            {
                "title": "Advanced Python",
                "body": "Advanced Python concepts and techniques...",
                "href": "https://example.com/python2"
            }
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        result = web_search("Python programming")
        
        assert result["success"] is True
        assert len(result["results"]) == 2
        assert result["metadata"]["query"] == "Python programming"
        assert result["metadata"]["search_engine"] == "DuckDuckGo"
        assert result["error"] is None
        assert result["results"][0]["title"] == "Python Tutorial"
        assert result["results"][0]["snippet"] == "Learn Python programming basics..."
        assert result["results"][0]["url"] == "https://example.com/python"
    
    def test_empty_query(self, mock_ddgs_class):
        """Test that empty query returns error."""
        result = web_search("")
        
        assert result["success"] is False
        assert result["error"] == "Query cannot be empty"
        assert result["results"] == []
    
    def test_max_results_limit(self, mock_ddgs_class):
        """Test that max_results is properly limited."""
        # Create more results than max
        mock_results = [
            {
                "title": f"Result {i}",
                "body": f"Snippet for result {i}...",
                "href": f"https://example.com/{i}"
            }
            for i in range(30)
        ]
        
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = mock_results[:25]  # DDGS will return max 25
        mock_ddgs_class.return_value = mock_ddgs
        
        # Request 30 results (should be limited to 25)
        result = web_search("test query", max_results=30)
        
        assert result["success"] is True
        assert len(result["results"]) <= 25
    
    def test_safesearch_options(self, mock_ddgs_class):
        """Test different safesearch settings."""
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = [
            {
                "title": "Test Result",
                "body": "Test snippet...",
                "href": "https://example.com"
            }
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        # Test strict safesearch
        result = web_search("test", safesearch="strict")
        assert result["success"] is True
        assert result["metadata"]["safesearch"] == "strict"
        
        # Test moderate safesearch
        result = web_search("test", safesearch="moderate")
        assert result["success"] is True
        assert result["metadata"]["safesearch"] == "moderate"
        
        # Test invalid safesearch (should default to moderate)
        result = web_search("test", safesearch="invalid")
        assert result["success"] is True
        assert result["metadata"]["safesearch"] == "moderate"
    
    def test_time_range_filter(self, mock_ddgs_class):
        """Test time-based filtering."""
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = [
            {
                "title": "Recent Result",
                "body": "Recent content...",
                "href": "https://example.com"
            }
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        # Test day filter
        result = web_search("test", time_range="d")
        assert result["success"] is True
        assert "time_range" in result["metadata"]
        assert result["metadata"]["time_range"] == "d"
        
        # Test week filter
        result = web_search("test", time_range="w")
        assert result["success"] is True
        assert result["metadata"]["time_range"] == "w"
        
        # Test invalid time range (should be ignored)
        result = web_search("test", time_range="invalid")
        assert result["success"] is True
        assert "time_range" not in result["metadata"]
    
    def test_regional_search(self, mock_ddgs_class):
        """Test regional filtering."""
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = [
            {
                "title": "Regional Result",
                "body": "Regional content...",
                "href": "https://example.com"
            }
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        result = web_search("test", region="us-en")
        
        assert result["success"] is True
        assert result["metadata"]["region"] == "us-en"
    
    def test_no_results_found(self, mock_ddgs_class):
        """Test handling when no results are found."""
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = []
        mock_ddgs_class.return_value = mock_ddgs
        
        result = web_search("veryrandomquery12345")
        
        assert result["success"] is True
        assert len(result["results"]) == 0
        assert "message" in result["metadata"]
    
    def test_network_error(self, mock_ddgs_class):
        """Test handling of network errors."""
        mock_ddgs = Mock()
        mock_ddgs.text.side_effect = Exception("Connection error")
        mock_ddgs_class.return_value = mock_ddgs
        
        result = web_search("test query")
        
        assert result["success"] is False
        assert "error" in result
        assert result["results"] == []
    
    def test_timeout_error(self, mock_ddgs_class):
        """Test handling of timeout errors."""
        mock_ddgs = Mock()
        mock_ddgs.text.side_effect = Exception("Request timed out")
        mock_ddgs_class.return_value = mock_ddgs
        
        result = web_search("test query")
        
        assert result["success"] is False
        assert "timed out" in result["error"].lower()


class TestWebSearchTool:
    """Test WebSearchTool class."""
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly."""
        tool = WebSearchTool()
        
        assert tool.name == "web_search"
        assert "DuckDuckGo" in tool.description
        assert "query" in tool.input_parameters
    
    @patch('peargent.tools.websearch_tool.DDGS')
    def test_tool_run(self, mock_ddgs_class):
        """Test running the tool."""
        mock_ddgs = Mock()
        mock_ddgs.text.return_value = [
            {
                "title": "Test",
                "body": "Test snippet...",
                "href": "https://example.com"
            }
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        tool = WebSearchTool()
        result = tool.run({"query": "test"})
        
        assert result["success"] is True
        assert len(result["results"]) >= 1


@pytest.mark.skipif(
    True,  # Skip by default as it requires network access
    reason="Integration test requires network access"
)
class TestWebSearchIntegration:
    """Integration tests with real DuckDuckGo searches."""
    
    def test_real_search(self):
        """Test a real search query."""
        result = web_search("Python programming language")
        
        assert result["success"] is True
        assert len(result["results"]) > 0
        assert result["metadata"]["search_engine"] == "DuckDuckGo"
        
        # Check first result structure
        first_result = result["results"][0]
        assert "title" in first_result
        assert "url" in first_result
        assert "snippet" in first_result
        assert first_result["url"].startswith("http")
    
    def test_real_search_with_filters(self):
        """Test search with various filters."""
        result = web_search(
            "latest technology news",
            max_results=3,
            time_range="w",
            safesearch="moderate"
        )
        
        assert result["success"] is True
        assert len(result["results"]) <= 3
        assert result["metadata"]["time_range"] == "w"
        assert result["metadata"]["safesearch"] == "moderate"


def test_ddgs_import_error():
    """Test behavior when ddgs is not installed."""
    with patch('peargent.tools.websearch_tool.DDGS_AVAILABLE', False):
        result = web_search("test")
        
        assert result["success"] is False
        assert "ddgs library is required" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
