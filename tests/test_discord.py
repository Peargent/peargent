"""
Tests for Discord Tool
Tests webhook messaging, embeds, template substitution, and error handling.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timezone

from peargent.tools.discord_tool import (
    DiscordTool,
    send_discord_message,
    _validate_webhook_url,
    _apply_template
)


class TestWebhookValidation:
    """Test Discord webhook URL validation."""
    
    def test_valid_webhook_urls(self):
        """Test that valid webhook URLs pass validation."""
        valid_urls = [
            "https://discord.com/api/webhooks/123456789/abcdefghijklmnop",
            "https://discord.com/api/webhooks/987654321/xyz123-ABC_789",
            "https://discord.com/api/webhooks/111222333444555666/aAbBcCdDeEfFgGhHiIjJ"
        ]
        
        for url in valid_urls:
            assert _validate_webhook_url(url) is True, f"{url} should be valid"
    
    def test_invalid_webhook_urls(self):
        """Test that invalid webhook URLs fail validation."""
        invalid_urls = [
            "https://example.com/webhook",
            "discord.com/api/webhooks/123/abc",
            "https://discord.com/webhooks/123/abc",
            "https://discord.com/api/webhook/123/abc",
            "https://discord.com/api/webhooks/123",
            "https://discord.com/api/webhooks/abc/token",
            ""
        ]
        
        for url in invalid_urls:
            assert _validate_webhook_url(url) is False, f"{url} should be invalid"


class TestTemplateSubstitution:
    """Test template variable substitution."""
    
    def test_simple_substitution(self):
        """Test basic variable substitution with Jinja2."""
        pytest.importorskip("jinja2")
        template = "Hello {{ name }}!"
        variables = {"name": "Discord"}
        
        result = _apply_template(template, variables)
        
        assert result == "Hello Discord!"
    
    def test_multiple_variables(self):
        """Test multiple variable substitution with Jinja2."""
        pytest.importorskip("jinja2")
        template = "Server {{ server }} is {{ status }} with {{ users }} users online."
        variables = {
            "server": "prod-01",
            "status": "online",
            "users": "150"
        }
        
        result = _apply_template(template, variables)
        
        assert result == "Server prod-01 is online with 150 users online."
    
    def test_missing_variables(self):
        """Test that missing variables render as empty string in Jinja2."""
        pytest.importorskip("jinja2")
        template = "Hello {{ name }}, you have {{ count }} messages."
        variables = {"name": "User"}
        
        result = _apply_template(template, variables)
        
        # Jinja2 renders missing variables as empty string
        assert result == "Hello User, you have  messages."
    
    def test_no_variables(self):
        """Test template without any variables."""
        template = "This is a plain text message."
        variables = {}
        
        result = _apply_template(template, variables)
        
        assert result == "This is a plain text message."
    
    def test_jinja2_conditionals(self):
        """Test Jinja2 conditional statements."""
        pytest.importorskip("jinja2")
        template = "Status: {{ status }}{% if critical %} - CRITICAL{% endif %}"
        
        # With critical flag
        result = _apply_template(template, {"status": "Alert", "critical": True})
        assert result == "Status: Alert - CRITICAL"
        
        # Without critical flag
        result = _apply_template(template, {"status": "OK", "critical": False})
        assert result == "Status: OK"
    
    def test_jinja2_loops(self):
        """Test Jinja2 loop statements."""
        pytest.importorskip("jinja2")
        template = "Tasks: {% for task in tasks %}{{ task }}{% if not loop.last %}, {% endif %}{% endfor %}"
        variables = {"tasks": ["backup", "cleanup", "monitor"]}
        
        result = _apply_template(template, variables)
        
        assert result == "Tasks: backup, cleanup, monitor"
    
    def test_simple_fallback_syntax(self):
        """Test simple {variable} syntax works as fallback when Jinja2 unavailable."""
        # Test fallback by mocking Template as None
        with patch('peargent.tools.discord_tool.Template', None):
            template = "Hello {name}! Server {server} is {status}."
            variables = {"name": "Admin", "server": "prod-01", "status": "online"}
            
            result = _apply_template(template, variables)
            assert result == "Hello Admin! Server prod-01 is online."


class TestDiscordMessaging:
    """Test Discord message sending."""
    
    @patch('peargent.tools.discord_tool.requests')
    def test_send_simple_message(self, mock_requests):
        """Test sending simple text message."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Test message",
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is True
        assert result["error"] is None
        mock_requests.post.assert_called_once()
    
    @patch('peargent.tools.discord_tool.requests')
    def test_send_message_with_template(self, mock_requests):
        """Test sending message with template variables."""
        pytest.importorskip("jinja2")
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Hello {{ name }}!",
            webhook_url="https://discord.com/api/webhooks/123/abc",
            template_vars={"name": "World"}
        )
        
        assert result["success"] is True
        # Check that the template was rendered in the request
        call_args = mock_requests.post.call_args
        assert "Hello World!" in call_args[1]["json"]["content"]
    
    @patch('peargent.tools.discord_tool.requests')
    def test_send_embed_only(self, mock_requests):
        """Test sending embed-only message (no content)."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            webhook_url="https://discord.com/api/webhooks/123/abc",
            embed={
                "title": "Embed Only",
                "description": "No content text",
                "color": 0x5865F2
            }
        )
        
        assert result["success"] is True
        call_args = mock_requests.post.call_args
        assert "content" not in call_args[1]["json"] or call_args[1]["json"]["content"] is None
        assert "embeds" in call_args[1]["json"]
    
    @patch('peargent.tools.discord_tool.requests')
    def test_send_message_with_embed(self, mock_requests):
        """Test sending message with embed."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Check this embed:",
            webhook_url="https://discord.com/api/webhooks/123/abc",
            embed={
                "title": "Test Embed",
                "description": "Test description",
                "color": 0x00FF00
            }
        )
        
        assert result["success"] is True
        call_args = mock_requests.post.call_args
        assert "embeds" in call_args[1]["json"]
        assert call_args[1]["json"]["embeds"][0]["title"] == "Test Embed"
    
    @patch('peargent.tools.discord_tool.requests')
    def test_send_embed_with_fields(self, mock_requests):
        """Test sending embed with fields."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Status update:",
            webhook_url="https://discord.com/api/webhooks/123/abc",
            embed={
                "title": "Server Status",
                "description": "Current metrics",
                "color": 0x5865F2,
                "fields": [
                    {"name": "CPU", "value": "45%", "inline": True},
                    {"name": "Memory", "value": "60%", "inline": True}
                ]
            }
        )
        
        assert result["success"] is True
        call_args = mock_requests.post.call_args
        assert len(call_args[1]["json"]["embeds"][0]["fields"]) == 2
    
    @patch('peargent.tools.discord_tool.requests')
    def test_send_embed_with_author_footer(self, mock_requests):
        """Test sending embed with author and footer."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        result = send_discord_message(
            content="Notification:",
            webhook_url="https://discord.com/api/webhooks/123/abc",
            embed={
                "title": "GitHub Update",
                "author": {
                    "name": "GitHub Bot",
                    "url": "https://github.com"
                },
                "footer": {
                    "text": "GitHub Notifications"
                },
                "timestamp": timestamp
            }
        )
        
        assert result["success"] is True
        call_args = mock_requests.post.call_args
        embed = call_args[1]["json"]["embeds"][0]
        assert embed["author"]["name"] == "GitHub Bot"
        assert embed["footer"]["text"] == "GitHub Notifications"
        assert embed["timestamp"] == timestamp
    
    @patch('peargent.tools.discord_tool.requests')
    def test_send_custom_username_avatar(self, mock_requests):
        """Test sending message with custom username and avatar."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Custom bot message",
            webhook_url="https://discord.com/api/webhooks/123/abc",
            username="Custom Bot",
            avatar_url="https://example.com/avatar.png"
        )
        
        assert result["success"] is True
        call_args = mock_requests.post.call_args
        assert call_args[1]["json"]["username"] == "Custom Bot"
        assert call_args[1]["json"]["avatar_url"] == "https://example.com/avatar.png"
    
    @patch('peargent.tools.discord_tool.requests')
    def test_rate_limit_error(self, mock_requests):
        """Test handling rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"retry_after": 5.0}
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Test message",
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is False
        assert "Rate limited" in result["error"]
        assert "5.0 seconds" in result["error"]
    
    @patch('peargent.tools.discord_tool.requests')
    def test_api_error(self, mock_requests):
        """Test handling API error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid payload"}
        mock_response.content = b'{"message": "Invalid payload"}'
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Test message",
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is False
        assert "Invalid payload" in result["error"]
    
    @patch('peargent.tools.discord_tool.requests')
    def test_network_error(self, mock_requests):
        """Test handling network error."""
        mock_requests.post.side_effect = Exception("Connection error")
        
        result = send_discord_message(
            content="Test message",
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is False
        assert "error" in result["error"].lower()
    
    @patch('peargent.tools.discord_tool.os.getenv')
    def test_webhook_url_from_env(self, mock_getenv):
        """Test loading webhook URL from environment."""
        mock_getenv.return_value = None
        
        result = send_discord_message(content="Test")
        
        assert result["success"] is False
        assert "webhook URL is required" in result["error"]
    
    def test_invalid_webhook_url(self):
        """Test error for invalid webhook URL."""
        result = send_discord_message(
            content="Test message",
            webhook_url="https://invalid.com/webhook"
        )
        
        assert result["success"] is False
        assert "Invalid" in result["error"]
    
    def test_no_content_no_embed(self):
        """Test error when neither content nor embed is provided."""
        result = send_discord_message(
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is False
        assert "either content or embed" in result["error"]
    
    @patch('peargent.tools.discord_tool.requests', None)
    def test_missing_requests_library(self):
        """Test error when requests library is not installed."""
        result = send_discord_message(
            content="Test message",
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is False
        assert "requests library is required" in result["error"]


class TestDiscordTool:
    """Test DiscordTool class."""
    
    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = DiscordTool()
        
        assert tool.name == "discord_webhook"
        assert "Discord" in tool.description
        # No required parameters - all optional (webhook from env, content/embed either-or)
        assert tool.input_parameters == {}
    
    @patch('peargent.tools.discord_tool.requests')
    def test_tool_run(self, mock_requests):
        """Test running the tool."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        tool = DiscordTool()
        result = tool.run({
            "content": "Test message",
            "webhook_url": "https://discord.com/api/webhooks/123/abc"
        })
        
        assert result["success"] is True
    
    @patch('peargent.tools.discord_tool.requests')
    def test_tool_with_embed(self, mock_requests):
        """Test tool with embed parameter."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_requests.post.return_value = mock_response
        
        tool = DiscordTool()
        result = tool.run({
            "content": "Embed test:",
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "embed": {
                "title": "Test",
                "description": "Description",
                "color": 0x00FF00
            }
        })
        
        assert result["success"] is True


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('peargent.tools.discord_tool.requests')
    def test_timeout_error(self, mock_requests):
        """Test handling timeout error."""
        mock_requests.post.side_effect = TimeoutError("Request timed out")
        
        result = send_discord_message(
            content="Test message",
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is False
        assert "timed out" in result["error"].lower()
    
    @patch('peargent.tools.discord_tool.requests')
    def test_empty_response(self, mock_requests):
        """Test handling empty response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.content = b''
        mock_response.json.side_effect = ValueError("No JSON")
        mock_requests.post.return_value = mock_response
        
        result = send_discord_message(
            content="Test message",
            webhook_url="https://discord.com/api/webhooks/123/abc"
        )
        
        assert result["success"] is False
        assert "500" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
