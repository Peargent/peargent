"""
Tests for Notification Tool
Tests SMTP and Resend providers, template substitution, and error handling.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import smtplib

from peargent.tools.notification_tool import (
    NotificationTool,
    send_notification,
    _validate_email,
    _apply_template
)


class TestEmailValidation:
    """Test email address validation."""
    
    def test_valid_emails(self):
        """Test that valid email addresses pass validation."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user_name@sub.example.com",
            "123@example.com"
        ]
        
        for email in valid_emails:
            assert _validate_email(email) is True, f"{email} should be valid"
    
    def test_invalid_emails(self):
        """Test that invalid email addresses fail validation."""
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
            ""
        ]
        
        for email in invalid_emails:
            assert _validate_email(email) is False, f"{email} should be invalid"


class TestTemplateSubstitution:
    """Test template variable substitution."""
    
    def test_simple_substitution(self):
        """Test basic variable substitution with Jinja2."""
        pytest.importorskip("jinja2")
        template = "Hello {{ name }}!"
        variables = {"name": "Alice"}
        
        result = _apply_template(template, variables)
        
        assert result == "Hello Alice!"
    
    def test_multiple_variables(self):
        """Test multiple variable substitution with Jinja2."""
        pytest.importorskip("jinja2")
        template = "Hello {{ first_name }} {{ last_name }}, your order #{{ order_id }} is ready."
        variables = {
            "first_name": "John",
            "last_name": "Doe",
            "order_id": "12345"
        }
        
        result = _apply_template(template, variables)
        
        assert result == "Hello John Doe, your order #12345 is ready."
    
    def test_missing_variables(self):
        """Test that missing variables render as empty string in Jinja2."""
        pytest.importorskip("jinja2")
        template = "Hello {{ name }}, you have {{ count }} messages."
        variables = {"name": "Alice"}
        
        result = _apply_template(template, variables)
        
        # Jinja2 renders missing variables as empty string
        assert result == "Hello Alice, you have  messages."
    
    def test_no_variables(self):
        """Test template without any variables."""
        template = "This is a plain text message."
        variables = {}
        
        result = _apply_template(template, variables)
        
        assert result == "This is a plain text message."
    
    def test_jinja2_conditionals(self):
        """Test Jinja2 conditional statements."""
        pytest.importorskip("jinja2")
        template = "Hello {{ name }}!{% if premium %} You are a premium member.{% endif %}"
        
        # With premium
        result = _apply_template(template, {"name": "Alice", "premium": True})
        assert result == "Hello Alice! You are a premium member."
        
        # Without premium
        result = _apply_template(template, {"name": "Bob", "premium": False})
        assert result == "Hello Bob!"
    
    def test_jinja2_loops(self):
        """Test Jinja2 loop statements."""
        pytest.importorskip("jinja2")
        template = "Items: {% for item in items %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}"
        variables = {"items": ["apple", "banana", "cherry"]}
        
        result = _apply_template(template, variables)
        
        assert result == "Items: apple, banana, cherry"
    
    def test_jinja2_filters(self):
        """Test Jinja2 filters."""
        pytest.importorskip("jinja2")
        template = "Hello {{ name|upper }}! Email: {{ email|lower }}"
        variables = {"name": "alice", "email": "ALICE@EXAMPLE.COM"}
        
        result = _apply_template(template, variables)
        
        assert result == "Hello ALICE! Email: alice@example.com"
    
    def test_simple_fallback_syntax(self):
        """Test simple {variable} syntax works as fallback when Jinja2 unavailable."""
        # Test fallback by mocking Template as None
        with patch('peargent.tools.notification_tool.Template', None):
            template = "Hello {name}! Your order #{order_id} is ready."
            variables = {"name": "Alice", "order_id": "12345"}
            
            result = _apply_template(template, variables)
            assert result == "Hello Alice! Your order #12345 is ready."
    
    def test_mixed_syntax_jinja2_preferred(self):
        """Test that Jinja2 syntax is used when both syntaxes present."""
        pytest.importorskip("jinja2")
        # This has both {{ }} and { } - Jinja2 should handle {{ }} properly
        template = "Hello {{ name }}! Simple: {name}"
        variables = {"name": "Alice"}
        
        result = _apply_template(template, variables)
        
        # Jinja2 processes {{ name }} but leaves {name} as-is
        assert result == "Hello Alice! Simple: {name}"
    
    def test_fallback_without_jinja2(self):
        """Test that simple {variable} replacement works when Jinja2 unavailable."""
        # Mock Template as None to simulate Jinja2 not being installed
        with patch('peargent.tools.notification_tool.Template', None):
            template = "Hello {name}! Order: {order_id}"
            variables = {"name": "Bob", "order_id": "999"}
            
            result = _apply_template(template, variables)
            
            # Should use simple replacement
            assert result == "Hello Bob! Order: 999"


@patch.dict('os.environ', {
    'SMTP_HOST': 'smtp.example.com',
    'SMTP_PORT': '587',
    'SMTP_USERNAME': 'test@example.com',
    'SMTP_PASSWORD': 'password123'
})
@patch('peargent.tools.notification_tool.smtplib.SMTP')
class TestSMTPProvider:
    """Test SMTP email sending functionality."""
    
    def test_successful_smtp_send(self, mock_smtp):
        """Test successful email sending via SMTP."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test body",
            from_email="sender@example.com"
        )
        
        assert result["success"] is True
        assert result["provider"] == "smtp"
        assert result["message_id"] is None
        assert result["error"] is None
        
        # Verify SMTP methods were called
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    def test_smtp_with_template_variables(self, mock_smtp):
        """Test SMTP email with template variables."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = send_notification(
            to_email="user@example.com",
            subject="Hello {name}",
            body="Welcome {name}! Your account is ready.",
            from_email="noreply@example.com",
            template_vars={"name": "Alice"}
        )
        
        assert result["success"] is True
        mock_server.send_message.assert_called_once()
    
    def test_smtp_html_email(self, mock_smtp):
        """Test sending HTML email via SMTP."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        html_body = "<html><body><h1>Test</h1></body></html>"
        
        result = send_notification(
            to_email="user@example.com",
            subject="HTML Email",
            body=html_body,
            from_email="sender@example.com"
        )
        
        assert result["success"] is True
        mock_server.send_message.assert_called_once()
    
    def test_smtp_authentication_error(self, mock_smtp):
        """Test SMTP authentication failure."""
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
        mock_smtp.return_value = mock_server
        
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test",
            body="Test body",
            from_email="sender@example.com"
        )
        
        assert result["success"] is False
        assert result["provider"] == "smtp"
        assert result["message_id"] is None
        assert "authentication failed" in result["error"].lower()
    
    def test_smtp_connection_error(self, mock_smtp):
        """Test SMTP connection failure."""
        mock_smtp.side_effect = smtplib.SMTPConnectError(421, b"Cannot connect")
        
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test",
            body="Test body",
            from_email="sender@example.com"
        )
        
        assert result["success"] is False
        assert result["provider"] == "smtp"
        assert result["message_id"] is None
        assert "connect" in result["error"].lower()
    
    def test_smtp_no_template_vars(self, mock_smtp):
        """Test that email is sent as-is when template_vars is None."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Subject and body with Jinja2 syntax but no template_vars
        result = send_notification(
            to_email="user@example.com",
            subject="Hello {{ name }}",
            body="Welcome {{ name }}!",
            from_email="sender@example.com"
            # No template_vars parameter
        )
        
        assert result["success"] is True
        # Message should be sent with literal Jinja2 syntax (not rendered)
        mock_server.send_message.assert_called_once()
        
        # Verify the message was sent with literal text (no template rendering)
        sent_message = mock_server.send_message.call_args[0][0]
        assert "{{ name }}" in str(sent_message) or "Hello {{ name }}" in sent_message.get("Subject", "")

@patch.dict('os.environ', {'RESEND_API_KEY': 'test-api-key'})
@patch('peargent.tools.notification_tool.requests')
class TestResendProvider:
    """Test Resend API email sending functionality."""
    
    def test_successful_resend_send(self, mock_requests):
        """Test successful email sending via Resend."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_123456"}
        mock_requests.post.return_value = mock_response
        
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test body",
            from_email="sender@example.com",
            provider="resend"
        )
        
        assert result["success"] is True
        assert result["provider"] == "resend"
        assert result["message_id"] == "email_123456"
        assert result["error"] is None
        
        # Verify API call
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        assert "https://api.resend.com/emails" in str(call_args)
        assert "Bearer test-api-key" in str(call_args)
    
    def test_resend_with_html(self, mock_requests):
        """Test Resend with HTML body."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_html"}
        mock_requests.post.return_value = mock_response
        
        html_body = "<html><body><p>Test</p></body></html>"
        
        result = send_notification(
            to_email="user@example.com",
            subject="HTML Email",
            body=html_body,
            from_email="sender@example.com",
            provider="resend"
        )
        
        assert result["success"] is True
        assert result["message_id"] == "email_html"
        
        # Check that HTML was sent
        call_kwargs = mock_requests.post.call_args.kwargs
        assert "html" in call_kwargs["json"]
    
    def test_resend_api_error(self, mock_requests):
        """Test Resend API error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid email address"}
        mock_requests.post.return_value = mock_response
        
        result = send_notification(
            to_email="invalid@example.com",
            subject="Test",
            body="Test body",
            from_email="sender@example.com",
            provider="resend"
        )
        
        assert result["success"] is False
        assert result["provider"] == "resend"
        assert result["message_id"] is None
        assert "Invalid email address" in result["error"]
    
    def test_resend_network_error(self, mock_requests):
        """Test Resend network/timeout error."""
        mock_requests.post.side_effect = Exception("Connection timeout")
        
        result = send_notification(
            to_email="user@example.com",
            subject="Test",
            body="Test body",
            from_email="sender@example.com",
            provider="resend"
        )
        
        assert result["success"] is False
        assert result["provider"] == "resend"
        assert result["message_id"] is None
        assert "error" in result["error"].lower()


class TestValidation:
    """Test input validation."""
    
    def test_invalid_recipient_email(self):
        """Test validation of invalid recipient email."""
        result = send_notification(
            to_email="invalid-email",
            subject="Test",
            body="Test body",
            from_email="sender@example.com"
        )
        
        assert result["success"] is False
        assert result["message_id"] is None
        assert "Invalid recipient email" in result["error"]
    
    def test_invalid_sender_email(self):
        """Test validation of invalid sender email."""
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test",
            body="Test body",
            from_email="invalid-email"
        )
        
        assert result["success"] is False
        assert result["message_id"] is None
        assert "Invalid sender email" in result["error"]
    
    def test_missing_sender_email(self):
        """Test that sender email is required."""
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test",
            body="Test body",
            from_email=""
        )
        
        assert result["success"] is False
        assert result["message_id"] is None
        assert "required" in result["error"].lower()
    
    def test_invalid_provider(self):
        """Test validation of invalid provider."""
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test",
            body="Test body",
            from_email="sender@example.com",
            provider="invalid-provider"
        )
        
        assert result["success"] is False
        assert result["message_id"] is None
        assert "Unsupported provider" in result["error"]
    
    @patch.dict('os.environ', {}, clear=True)
    def test_missing_smtp_config(self):
        """Test error when SMTP configuration is missing."""
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test",
            body="Test body",
            from_email="sender@example.com"
        )
        
        assert result["success"] is False
        assert result["message_id"] is None
        assert "Missing SMTP configuration" in result["error"]
    
    @patch.dict('os.environ', {}, clear=True)
    def test_missing_resend_api_key(self):
        """Test error when Resend API key is missing."""
        result = send_notification(
            to_email="recipient@example.com",
            subject="Test",
            body="Test body",
            from_email="sender@example.com",
            provider="resend"
        )
        
        assert result["success"] is False
        assert result["message_id"] is None
        assert "Missing Resend API key" in result["error"]


class TestNotificationToolClass:
    """Test NotificationTool class."""
    
    def test_tool_initialization(self):
        """Test that NotificationTool initializes correctly."""
        tool = NotificationTool()
        
        assert tool.name == "send_notification"
        assert "email" in tool.description.lower()
        assert "smtp" in tool.description.lower()
        assert "resend" in tool.description.lower()
        # Check required parameters
        assert "to_email" in tool.input_parameters
        assert "subject" in tool.input_parameters
        assert "body" in tool.input_parameters
        assert "from_email" in tool.input_parameters
        # Optional parameters are not in input_parameters (only required ones)
    
    @patch.dict('os.environ', {
        'SMTP_HOST': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': 'test@test.com',
        'SMTP_PASSWORD': 'pass123'
    })
    @patch('peargent.tools.notification_tool.smtplib.SMTP')
    def test_tool_run_method(self, mock_smtp):
        """Test NotificationTool run method."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        tool = NotificationTool()
        result = tool.run({
            "to_email": "user@example.com",
            "subject": "Test",
            "body": "Test message",
            "from_email": "sender@example.com"
        })
        
        assert result["success"] is True
        assert result["provider"] == "smtp"


@patch.dict('os.environ', {
    'SMTP_HOST': 'smtp.test.com',
    'SMTP_PORT': '587',
    'SMTP_USERNAME': 'test@test.com',
    'SMTP_PASSWORD': 'pass123'
})
class TestIntegration:
    """Integration tests combining multiple features."""
    
    @patch('peargent.tools.notification_tool.smtplib.SMTP')
    def test_full_template_workflow(self, mock_smtp):
        """Test complete workflow with templates."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        template_vars = {
            "user_name": "John Doe",
            "order_id": "12345",
            "total": "$99.99",
            "delivery_date": "January 5, 2026"
        }
        
        result = send_notification(
            to_email="customer@example.com",
            subject="Order {order_id} Confirmation",
            body="""
Hello {user_name},

Your order #{order_id} has been confirmed!
Total: {total}
Expected delivery: {delivery_date}

Thank you for your purchase!
            """,
            template_vars=template_vars,
            from_email="orders@shop.com",
            provider="smtp"
        )
        
        assert result["success"] is True
        assert result["provider"] == "smtp"
        
        # Verify SMTP was used correctly
        mock_server.send_message.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
