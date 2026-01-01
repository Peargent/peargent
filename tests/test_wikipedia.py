"""
Tests for Wikipedia Knowledge Tool
Tests article search, disambiguation handling, and error cases.
"""

import pytest
from unittest.mock import patch, Mock


from peargent.tools.wikipedia_tool import (
    WikipediaKnowledgeTool,
    search_wikipedia
)


@patch('peargent.tools.wikipedia_tool.requests')
class TestWikipediaSearch:
    """Test basic Wikipedia article search functionality."""
    
    def test_successful_article_search(self, mock_requests):
        """Test searching for an existing article."""
        # Mock opensearch response
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = [
            "Python (programming language)",
            ["Python (programming language)", "Python (genus)"],
            ["", ""],
            ["https://en.wikipedia.org/wiki/Python_(programming_language)", ""]
        ]
        mock_opensearch.raise_for_status = Mock()
        
        # Mock query response
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Python (programming language)",
                        "extract": "Python is a high-level programming language.",
                        "pageprops": {}
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        result = search_wikipedia("Python (programming language)")
        
        assert result["success"] is True
        assert result["format"] == "wikipedia"
        assert result["text"] == "Python is a high-level programming language."
        assert result["metadata"]["title"] == "Python (programming language)"
        assert result["metadata"]["url"].startswith("https://en.wikipedia.org")
    
    def test_article_not_found(self, mock_requests):
        """Test searching for non-existent article."""
        # Mock opensearch with no results
        mock_response = Mock()
        mock_response.json.return_value = ["asdfghjkl", [], [], []]
        mock_response.raise_for_status = Mock()
        
        mock_requests.get.return_value = mock_response
        
        result = search_wikipedia("asdfghjkl")
        
        assert result["success"] is True
        assert result["text"] == ""
        assert "suggestions" in result["metadata"]
    
    def test_article_with_suggestions(self, mock_requests):
        """Test that suggestions are provided when article not found exactly."""
        # Mock opensearch with suggestions
        mock_response = Mock()
        mock_response.json.return_value = [
            "Pythn",
            ["Python (programming language)", "Python (genus)", "Pythonidae"],
            ["", "", ""],
            ["", "", ""]
        ]
        mock_response.raise_for_status = Mock()
        
        # Mock query response for first suggestion
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Python (programming language)",
                        "extract": "Python is a programming language.",
                        "pageprops": {}
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_response]
        
        result = search_wikipedia("Pythn")
        
        # Should return suggestions since it's not exact match
        assert result["success"] is True
        assert result["text"] == ""
        assert len(result["metadata"]["suggestions"]) > 0


@patch('peargent.tools.wikipedia_tool.requests')
class TestDisambiguation:
    """Test handling of disambiguation pages."""
    
    def test_disambiguation_page(self, mock_requests):
        """Test handling of disambiguation pages."""
        # Mock opensearch
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = [
            "Mercury",
            ["Mercury", "Mercury (planet)"],
            ["", ""],
            ["", ""]
        ]
        mock_opensearch.raise_for_status = Mock()
        
        # Mock query response with disambiguation flag
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "456": {
                        "title": "Mercury",
                        "pageprops": {"disambiguation": ""},
                        "links": [
                            {"title": "Mercury (planet)"},
                            {"title": "Mercury (element)"},
                            {"title": "Mercury (mythology)"}
                        ]
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        result = search_wikipedia("Mercury")
        
        assert result["success"] is True
        assert result["metadata"]["title"] == "Mercury"
        assert "Multiple possible meanings" in result["text"]
        assert "disambiguation" in result["metadata"]
        assert len(result["metadata"]["disambiguation"]) > 0
        assert "Mercury (planet)" in result["metadata"]["disambiguation"]


@patch('peargent.tools.wikipedia_tool.requests')
class TestLinksAndCategories:
    """Test extraction of links and categories."""
    
    def test_extract_links(self, mock_requests):
        """Test extracting internal links from article."""
        # Mock responses
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = [
            "Python (programming language)",
            ["Python (programming language)"],
            [""],
            [""]
        ]
        mock_opensearch.raise_for_status = Mock()
        
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Python (programming language)",
                        "extract": "Python is a programming language.",
                        "pageprops": {},
                        "links": [
                            {"title": "Programming language"},
                            {"title": "Guido van Rossum"},
                            {"title": "Object-oriented programming"}
                        ]
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        result = search_wikipedia("Python (programming language)", extract_links=True)
        
        assert result["success"] is True
        assert "links" in result["metadata"]
        assert len(result["metadata"]["links"]) > 0
        assert "Programming language" in result["metadata"]["links"]
    
    def test_extract_categories(self, mock_requests):
        """Test extracting categories from article."""
        # Mock responses
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = [
            "Python (programming language)",
            ["Python (programming language)"],
            [""],
            [""]
        ]
        mock_opensearch.raise_for_status = Mock()
        
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Python (programming language)",
                        "extract": "Python is a programming language.",
                        "pageprops": {},
                        "categories": [
                            {"title": "Category:Programming languages"},
                            {"title": "Category:Python (programming language)"}
                        ]
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        result = search_wikipedia("Python (programming language)", extract_categories=True)
        
        assert result["success"] is True
        assert "categories" in result["metadata"]
        assert len(result["metadata"]["categories"]) > 0
        assert "Programming languages" in result["metadata"]["categories"]


@patch('peargent.tools.wikipedia_tool.requests')
class TestSummaryControl:
    """Test summary length control."""
    
    def test_max_summary_length(self, mock_requests):
        """Test truncating summary to max length."""
        long_text = "A" * 1000
        
        # Mock responses
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = [
            "Test Article",
            ["Test Article"],
            [""],
            [""]
        ]
        mock_opensearch.raise_for_status = Mock()
        
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Test Article",
                        "extract": long_text,
                        "pageprops": {}
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        result = search_wikipedia("Test Article", max_summary_length=100)
        
        assert result["success"] is True
        assert len(result["text"]) <= 103  # 100 + "..."
        assert result["text"].endswith("...")


@patch('peargent.tools.wikipedia_tool.requests')
class TestLanguageSupport:
    """Test multi-language support."""
    
    def test_french_wikipedia(self, mock_requests):
        """Test querying French Wikipedia."""
        # Mock responses
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = [
            "Python (langage)",
            ["Python (langage)"],
            [""],
            [""]
        ]
        mock_opensearch.raise_for_status = Mock()
        
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Python (langage)",
                        "extract": "Python est un langage de programmation.",
                        "pageprops": {}
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        result = search_wikipedia("Python (langage)", language="fr")
        
        assert result["success"] is True
        assert result["metadata"]["url"].startswith("https://fr.wikipedia.org")
    
    def test_invalid_language_code(self, mock_requests):
        """Test that invalid language codes are rejected."""
        result = search_wikipedia("Test", language="invalid123")
        
        assert result["success"] is False
        assert "Invalid language code" in result["error"]


@patch('peargent.tools.wikipedia_tool.requests')
class TestErrorHandling:
    """Test error handling for various failure scenarios."""
    
    def test_timeout_error(self, mock_requests):
        """Test handling of timeout errors."""
        # Create a custom exception class for Timeout
        class TimeoutError(Exception):
            pass
        
        mock_requests.exceptions.Timeout = TimeoutError
        mock_requests.get.side_effect = TimeoutError()
        
        result = search_wikipedia("Test")
        
        assert result["success"] is False
        assert "timed out" in result["error"].lower()
    
    def test_network_error(self, mock_requests):
        """Test handling of network errors."""
        # Create a custom exception class for ConnectionError
        class ConnectionErr(Exception):
            pass
        
        mock_requests.exceptions.ConnectionError = ConnectionErr
        mock_requests.exceptions.RequestException = Exception
        mock_requests.get.side_effect = ConnectionErr("Network error")
        
        result = search_wikipedia("Test")
        
        assert result["success"] is False
        assert "error" in result["error"].lower()


class TestToolIntegration:
    """Test WikipediaKnowledgeTool class integration."""
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly."""
        tool = WikipediaKnowledgeTool()
        
        assert tool.name == "wikipedia_query"
        assert "Wikipedia" in tool.description
        assert "query" in tool.input_parameters
    
    @patch('peargent.tools.wikipedia_tool.requests')
    def test_tool_run_method(self, mock_requests):
        """Test running tool through its run method."""
        # Mock responses
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = [
            "Test Article",
            ["Test Article"],
            [""],
            [""]
        ]
        mock_opensearch.raise_for_status = Mock()
        
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Test Article",
                        "extract": "This is a test.",
                        "pageprops": {}
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        tool = WikipediaKnowledgeTool()
        result = tool.run({"query": "Test Article"})
        
        assert result["success"] is True
        assert result["metadata"]["title"] == "Test Article"
        assert result["text"] == "This is a test."


class TestOutputSchema:
    """Test that output schema matches TextExtractionTool pattern."""
    
    @patch('peargent.tools.wikipedia_tool.requests')
    def test_output_structure(self, mock_requests):
        """Test that output has correct structure: text, metadata, format, success, error."""
        mock_opensearch = Mock()
        mock_opensearch.json.return_value = ["Test", ["Test"], [""], [""]]
        mock_opensearch.raise_for_status = Mock()
        
        mock_query = Mock()
        mock_query.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "title": "Test",
                        "extract": "Test content",
                        "pageprops": {}
                    }
                }
            }
        }
        mock_query.raise_for_status = Mock()
        
        mock_requests.get.side_effect = [mock_opensearch, mock_query]
        
        result = search_wikipedia("Test")
        
        # Must have these fields
        assert "text" in result
        assert "metadata" in result
        assert "format" in result
        assert "success" in result
        assert "error" in result
        
        # Format should be "wikipedia"
        assert result["format"] == "wikipedia"
        
        # Metadata should be a dict
        assert isinstance(result["metadata"], dict)
        
        # Agent-relevant data should be in metadata
        assert "title" in result["metadata"]
        assert "url" in result["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
