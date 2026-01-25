"""
Tests for Web Search Tool
Tests DuckDuckGo search, filtering options, and error cases.
"""

import pytest
from unittest.mock import patch, Mock


from peargent.tools.websearch_tool import (
    WebSearchTool,
    web_search,
    _parse_duckduckgo_html
)


@patch('peargent.tools.websearch_tool.requests')
class TestWebSearch:
    """Test basic web search functionality."""
    
    def test_successful_search(self, mock_requests):
        """Test a successful web search."""
        # Mock DuckDuckGo response with HTML
        mock_response = Mock()
        mock_response.text = """
        <div class="result">
            <a class="result__a" href="https://example.com/python">Python Tutorial</a>
            <a class="result__snippet">Learn Python programming basics...</a>
        </div>
        <div class="result">
            <a class="result__a" href="https://example.com/python2">Advanced Python</a>
            <a class="result__snippet">Advanced Python concepts and techniques...</a>
        </div>
        """
        mock_response.raise_for_status = Mock()
        
        mock_requests.post.return_value = mock_response
        
        result = web_search("Python programming")
        
        assert result["success"] is True
        assert len(result["results"]) >= 1
        assert result["metadata"]["query"] == "Python programming"
        assert result["metadata"]["search_engine"] == "DuckDuckGo"
        assert result["error"] is None
    
    def test_empty_query(self, mock_requests):
        """Test that empty query returns error."""
        result = web_search("")
        
        assert result["success"] is False
        assert result["error"] == "Query cannot be empty"
        assert result["results"] == []
    
    def test_max_results_limit(self, mock_requests):
        """Test that max_results is properly limited."""
        mock_response = Mock()
        # Create HTML with many results
        results_html = ""
        for i in range(30):
            results_html += f"""
            <div class="result">
                <a class="result__a" href="https://example.com/{i}">Result {i}</a>
                <a class="result__snippet">Snippet for result {i}...</a>
            </div>
            """
        mock_response.text = results_html
        mock_response.raise_for_status = Mock()
        
        mock_requests.post.return_value = mock_response
        
        # Request 30 results (should be limited to 25)
        result = web_search("test query", max_results=30)
        
        assert result["success"] is True
        assert len(result["results"]) <= 25
    
    def test_safesearch_options(self, mock_requests):
        """Test different safesearch settings."""
        mock_response = Mock()
        mock_response.text = """
        <div class="result">
            <a class="result__a" href="https://example.com">Test Result</a>
            <a class="result__snippet">Test snippet...</a>
        </div>
        """
        mock_response.raise_for_status = Mock()
        
        mock_requests.post.return_value = mock_response
        
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
    
    def test_time_range_filter(self, mock_requests):
        """Test time-based filtering."""
        mock_response = Mock()
        mock_response.text = """
        <div class="result">
            <a class="result__a" href="https://example.com">Recent Result</a>
            <a class="result__snippet">Recent content...</a>
        </div>
        """
        mock_response.raise_for_status = Mock()
        
        mock_requests.post.return_value = mock_response
        
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
    
    def test_regional_search(self, mock_requests):
        """Test regional filtering."""
        mock_response = Mock()
        mock_response.text = """
        <div class="result">
            <a class="result__a" href="https://example.com">Regional Result</a>
            <a class="result__snippet">Regional content...</a>
        </div>
        """
        mock_response.raise_for_status = Mock()
        
        mock_requests.post.return_value = mock_response
        
        result = web_search("test", region="us-en")
        
        assert result["success"] is True
        assert result["metadata"]["region"] == "us-en"
    
    def test_no_results_found(self, mock_requests):
        """Test handling when no results are found."""
        mock_response = Mock()
        mock_response.text = "<html><body>No results</body></html>"
        mock_response.raise_for_status = Mock()
        
        mock_requests.post.return_value = mock_response
        
        result = web_search("veryrandomquery12345")
        
        assert result["success"] is True
        assert len(result["results"]) == 0
        assert "message" in result["metadata"]
    
    def test_network_error(self, mock_requests):
        """Test handling of network errors."""
        mock_requests.post.side_effect = Exception("Connection error")
        
        result = web_search("test query")
        
        assert result["success"] is False
        assert "error" in result
        assert result["results"] == []
    
    def test_timeout_error(self, mock_requests):
        """Test handling of timeout errors."""
        from requests.exceptions import Timeout
        mock_requests.post.side_effect = Timeout("Request timed out")
        
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
    
    @patch('peargent.tools.websearch_tool.requests')
    def test_tool_run(self, mock_requests):
        """Test running the tool."""
        mock_response = Mock()
        mock_response.text = """
        <div class="result">
            <a class="result__a" href="https://example.com">Test</a>
            <a class="result__snippet">Test snippet...</a>
        </div>
        """
        mock_response.raise_for_status = Mock()
        
        mock_requests.post.return_value = mock_response
        
        tool = WebSearchTool()
        result = tool.run({"query": "test"})
        
        assert result["success"] is True
        assert len(result["results"]) >= 1


class TestHTMLParsing:
    """Test HTML parsing functionality."""
    
    def test_parse_with_beautifulsoup(self):
        """Test parsing with BeautifulSoup."""
        html = """
        <div class="result">
            <a class="result__a" href="https://example.com/1">Title 1</a>
            <a class="result__snippet">Snippet 1</a>
        </div>
        <div class="result">
            <a class="result__a" href="https://example.com/2">Title 2</a>
            <a class="result__snippet">Snippet 2</a>
        </div>
        """
        
        try:
            results = _parse_duckduckgo_html(html, max_results=5)
            assert len(results) >= 1
            if results:
                assert "title" in results[0]
                assert "url" in results[0]
                assert "snippet" in results[0]
        except ImportError:
            # BeautifulSoup not available, skip test
            pytest.skip("BeautifulSoup not available")
    
    def test_parse_empty_html(self):
        """Test parsing empty HTML."""
        html = "<html><body></body></html>"
        
        results = _parse_duckduckgo_html(html, max_results=5)
        assert results == []
    
    def test_parse_malformed_html(self):
        """Test parsing malformed HTML doesn't crash."""
        html = "<div><a>Incomplete..."
        
        results = _parse_duckduckgo_html(html, max_results=5)
        # Should not crash, may return empty list
        assert isinstance(results, list)


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


def test_requests_import_error():
    """Test behavior when requests is not installed."""
    with patch('peargent.tools.websearch_tool.requests', None):
        result = web_search("test")
        
        assert result["success"] is False
        assert "requests library is required" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
