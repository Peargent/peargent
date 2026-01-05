"""
Notification Tool for Peargent
Send emails through SMTP or Resend with template support for dynamic content.
"""

import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from peargent import Tool

try:
    import requests
except ImportError:
    requests = None

try:
    from jinja2 import Template
except ImportError:
    Template = None


def _validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _apply_template(template: str, variables: Dict[str, Any]) -> str:
    """
    Apply template rendering with variable substitution.
    
    Supports both Jinja2 and simple templating:
    - Jinja2 (preferred if available): {{ variable }}, {% if %}, {% for %}, filters
    - Simple fallback: {variable} string replacement
    
    Args:
        template: Template string with Jinja2 or simple syntax
        variables: Dictionary of variable values
        
    Returns:
        Rendered template with variables substituted
    """
    # Try Jinja2 first if available (supports advanced features)
    if Template is not None:
        try:
            jinja_template = Template(template)
            return jinja_template.render(**variables)
        except Exception as e:
            # If Jinja2 rendering fails, fall back to simple replacement
            pass
    
    # Fallback to simple {variable} replacement
    result = template
    for key, value in variables.items():
        placeholder = f"{{{key}}}"
        result = result.replace(placeholder, str(value))
    return result


def _send_smtp(
    to_email: str,
    subject: str,
    body: str,
    from_email: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    use_tls: bool = True
) -> Dict[str, Any]:
    """
    Send email via SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text or HTML)
        from_email: Sender email address
        smtp_host: SMTP server host
        smtp_port: SMTP server port
        smtp_username: SMTP username
        smtp_password: SMTP password
        use_tls: Whether to use TLS encryption
        
    Returns:
        Result dictionary with success status
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Determine if body is HTML by checking for HTML tags
        html_tag_pattern = re.compile(r'<\s*(html|head|body|div|p|span|table|h[1-6]|ul|ol|li|a|img|br|hr)\b', re.IGNORECASE)
        is_html = bool(html_tag_pattern.search(body))
        
        if is_html:
            part = MIMEText(body, 'html')
        else:
            part = MIMEText(body, 'plain')
        
        msg.attach(part)
        
        # Connect and send
        server = None
        try:
            if use_tls:
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
            return {
                "success": True,
                "provider": "smtp",
                "message_id": None,
                "error": None
            }
        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    pass  # Ignore errors during cleanup
        
    except Exception as e:
        error_type = type(e).__name__
        if "SMTPAuthenticationError" in error_type:
            error_msg = "SMTP authentication failed. Check username and password."
        elif "SMTPConnectError" in error_type:
            error_msg = f"Failed to connect to SMTP server: {smtp_host}:{smtp_port}"
        elif "SMTPException" in error_type:
            error_msg = f"SMTP error: {str(e)}"
        else:
            error_msg = f"Unexpected error: {str(e)}"
        
        return {
            "success": False,
            "provider": "smtp",
            "message_id": None,
            "error": error_msg
        }


def _send_resend(
    to_email: str,
    subject: str,
    body: str,
    from_email: str,
    resend_api_key: str
) -> Dict[str, Any]:
    """
    Send email via Resend API.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text or HTML)
        from_email: Sender email address
        resend_api_key: Resend API key
        
    Returns:
        Result dictionary with success status
    """
    if requests is None:
        return {
            "success": False,
            "provider": "resend",
            "message_id": None,
            "error": (
                "requests library is required for Resend. "
                "Install it with: pip install requests"
            )
        }
    
    try:
        # Determine if body is HTML by checking for HTML tags
        html_tag_pattern = re.compile(r'<\s*(html|head|body|div|p|span|table|h[1-6]|ul|ol|li|a|img|br|hr)\b', re.IGNORECASE)
        is_html = bool(html_tag_pattern.search(body))
        
        # Build payload
        payload = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
        }
        
        if is_html:
            payload["html"] = body
        else:
            payload["text"] = body
        
        # Send request
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "provider": "resend",
                "message_id": response.json().get("id"),
                "error": None
            }
        else:
            error_data = response.json()
            return {
                "success": False,
                "provider": "resend",
                "message_id": None,
                "error": f"Resend API error: {error_data.get('message', 'Unknown error')}"
            }
        
    except Exception as e:
        error_type = type(e).__name__
        if "Timeout" in error_type:
            error_msg = "Request timed out. Please try again."
        elif "RequestException" in error_type or "ConnectionError" in error_type:
            error_msg = f"Network error: {str(e)}"
        else:
            error_msg = f"Unexpected error: {str(e)}"
        
        return {
            "success": False,
            "provider": "resend",
            "message_id": None,
            "error": error_msg
        }


def send_notification(
    to_email: str,
    subject: str,
    body: str,
    from_email: str,
    template_vars: Optional[Dict[str, Any]] = None,
    provider: str = "smtp",
    smtp_use_tls: bool = True
) -> Dict[str, Any]:
    """
    Send email notification with template support.
    
    Supports both Jinja2 (preferred) and simple {variable} templating.
    - If Jinja2 is installed: Uses {{ variable }}, conditionals, loops, filters
    - If Jinja2 not available: Falls back to simple {variable} replacement
    
    Automatically detects and uses available email provider:
    - If SMTP credentials not available but Resend API key is: uses Resend
    - If Resend API key not available but SMTP credentials are: uses SMTP
    - Explicit provider parameter overrides with fallback if not available
    
    Credentials are loaded from environment variables:
    - SMTP: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
    - Resend: RESEND_API_KEY
    
    Args:
        to_email: Recipient email address
        subject: Email subject (supports templating when template_vars provided)
        body: Email body (supports templating when template_vars provided, plain text or HTML)
        from_email: Sender email address
        template_vars: Dictionary of variables for template rendering (optional)
        provider: Email provider ('smtp' or 'resend', default: 'smtp', auto-fallback enabled)
        smtp_use_tls: Whether to use TLS encryption for SMTP (default: True)
        
    Returns:
        Dictionary containing:
            - success: Boolean indicating success
            - provider: Provider used ('smtp' or 'resend')
            - message_id: Message ID if available, None otherwise
            - error: Error message if failed, None otherwise
            
    Example:
        >>> # Using SMTP with Jinja2 template (if available)
        >>> result = send_notification(
        ...     to_email="user@example.com",
        ...     subject="Hello {{ name }}",
        ...     body="Welcome {{ name }}! Your account is ready.",
        ...     from_email="noreply@example.com",
        ...     template_vars={"name": "Alice"}
        ... )
        >>> print(result["success"])
        
        >>> # Using simple {variable} replacement (works without Jinja2)
        >>> result = send_notification(
        ...     to_email="user@example.com",
        ...     subject="Hello {name}",
        ...     body="Welcome {name}!",
        ...     from_email="noreply@example.com",
        ...     template_vars={"name": "Bob"}
        ... )
        >>> print(result["success"])
        
        >>> # Without template_vars (sent as-is)
        >>> result = send_notification(
        ...     to_email="user@example.com",
        ...     subject="Static Subject",
        ...     body="Static body text.",
        ...     from_email="noreply@example.com"
        ... )
        >>> print(result["success"])
        
        >>> # Using Resend
        >>> result = send_notification(
        ...     to_email="user@example.com",
        ...     subject="Account Alert",
        ...     body="Your account has been activated.",
        ...     from_email="noreply@example.com",
        ...     provider="resend"
        ... )
    """
    # Validate recipient email
    if not _validate_email(to_email):
        return {
            "success": False,
            "provider": provider,
            "message_id": None,
            "error": f"Invalid recipient email address: {to_email}"
        }
    
    # Validate sender email
    if not from_email:
        return {
            "success": False,
            "provider": provider,
            "message_id": None,
            "error": "Sender email address (from_email) is required"
        }
    
    if not _validate_email(from_email):
        return {
            "success": False,
            "provider": provider,
            "message_id": None,
            "error": f"Invalid sender email address: {from_email}"
        }
    
    # Apply template variables only if provided (non-empty)
    if template_vars:
        subject = _apply_template(subject, template_vars)
        body = _apply_template(body, template_vars)
    
    # Auto-detect provider based on available credentials
    # Check what credentials are available
    smtp_host = os.getenv("SMTP_HOST")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_available = all([smtp_host, smtp_username, smtp_password])
    
    resend_api_key = os.getenv("RESEND_API_KEY")
    resend_available = bool(resend_api_key)
    
    # If default provider (smtp) is requested but not available, try fallback
    if provider == "smtp" and not smtp_available and resend_available:
        provider = "resend"
    # If resend is requested but not available, try fallback to smtp
    elif provider == "resend" and not resend_available and smtp_available:
        provider = "smtp"
    
    # Validate provider
    if provider not in ["smtp", "resend"]:
        return {
            "success": False,
            "provider": provider,
            "message_id": None,
            "error": f"Unsupported provider: {provider}. Use 'smtp' or 'resend'."
        }
    
    # Send via SMTP
    if provider == "smtp":
        # Load from environment variables (some already loaded for detection)
        smtp_host = os.getenv("SMTP_HOST")
        try:
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
        except (ValueError, TypeError):
            return {
                "success": False,
                "provider": "smtp",
                "message_id": None,
                "error": "Invalid SMTP_PORT: must be a numeric value"
            }
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Validate SMTP configuration
        if not all([smtp_host, smtp_username, smtp_password]):
            missing = []
            if not smtp_host:
                missing.append("SMTP_HOST")
            if not smtp_username:
                missing.append("SMTP_USERNAME")
            if not smtp_password:
                missing.append("SMTP_PASSWORD")
            
            # Check if alternative provider is available
            alternative_msg = ""
            if os.getenv("RESEND_API_KEY"):
                alternative_msg = " Alternatively, set RESEND_API_KEY to use Resend provider."
            
            return {
                "success": False,
                "provider": "smtp",
                "message_id": None,
                "error": (
                    f"Missing SMTP configuration: {', '.join(missing)}. "
                    f"Set these in .env file.{alternative_msg}"
                )
            }
        
        return _send_smtp(
            to_email=to_email,
            subject=subject,
            body=body,
            from_email=from_email,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            use_tls=smtp_use_tls
        )
    
    # Send via Resend
    elif provider == "resend":
        # Load from environment variables (already loaded for detection)
        resend_api_key = os.getenv("RESEND_API_KEY")
        
        if not resend_api_key:
            # Check if alternative provider is available
            alternative_msg = ""
            smtp_host = os.getenv("SMTP_HOST")
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            if all([smtp_host, smtp_username, smtp_password]):
                alternative_msg = " Alternatively, configure SMTP credentials to use SMTP provider."
            
            return {
                "success": False,
                "provider": "resend",
                "message_id": None,
                "error": (
                    f"Missing Resend API key. Set RESEND_API_KEY in .env file.{alternative_msg}"
                )
            }
        
        return _send_resend(
            to_email=to_email,
            subject=subject,
            body=body,
            from_email=from_email,
            resend_api_key=resend_api_key
        )


class EmailTool(Tool):
    """
    Tool for sending email notifications with template support.
    
    Supports:
    - SMTP with TLS/SSL
    - Resend API
    - Jinja2 template rendering (preferred) or simple {variable} replacement (fallback)
    - Plain text and HTML emails
    - Auto-detection of email format
    
    SMTP credentials are automatically loaded from environment variables:
    - SMTP_HOST
    - SMTP_PORT (default: 587)
    - SMTP_USERNAME
    - SMTP_PASSWORD
    
    For Resend, set RESEND_API_KEY in environment.
    
    Example:
        >>> from peargent.tools import EmailTool
        >>> tool = EmailTool()
        >>> result = tool.run({
        ...     "to_email": "user@example.com",
        ...     "subject": "Hello {{ name }}",
        ...     "body": "Welcome {{ name }}!",
        ...     "template_vars": {"name": "Alice"},
        ...     "from_email": "noreply@example.com"
        ... })
        >>> print(result["success"])
    """
    
    def __init__(self):
        super().__init__(
            name="send_notification",
            description=(
                "Send email notifications via SMTP or Resend. "
                "Supports Jinja2 templating when available ({{ variable }}, loops, conditionals, filters) "
                "or simple {variable} replacement as fallback. "
                "SMTP credentials loaded from .env (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD). "
                "Resend API key from RESEND_API_KEY. "
                "Required parameters: to_email (str), subject (str), body (str), from_email (str). "
                "Optional parameters: template_vars (dict), provider (str, default: 'smtp'), "
                "smtp_use_tls (bool, default: True)."
            ),
            input_parameters={
                # Only required parameters - optional params handled by function defaults
                "to_email": str,
                "subject": str,
                "body": str,
                "from_email": str
            },
            call_function=send_notification
        )


# Create default instance for easy import
email_tool = EmailTool()
