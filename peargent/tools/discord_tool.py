"""
Discord Webhook Tool for Peargent
Send messages to Discord channels through webhooks with template support.
"""

import os
import re
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


def _validate_webhook_url(url: str) -> bool:
    """
    Validate Discord webhook URL format.
    
    Args:
        url: Webhook URL to validate
        
    Returns:
        True if valid Discord webhook URL, False otherwise
    """
    pattern = r'^https://discord\.com/api/webhooks/\d+/[\w-]+$'
    return re.match(pattern, url) is not None


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
        except Exception:
            # If Jinja2 rendering fails, fall back to simple replacement
            pass
    
    # Fallback to simple {variable} replacement
    result = template
    for key, value in variables.items():
        placeholder = f"{{{key}}}"
        result = result.replace(placeholder, str(value))
    return result


def _apply_template_recursive(data: Any, variables: Dict[str, Any]) -> Any:
    """
    Recursively apply template variables to nested structures.
    
    Handles strings, dicts, lists, and other types.
    
    Args:
        data: Data structure to process (string, dict, list, etc.)
        variables: Dictionary of template variables
        
    Returns:
        Processed data with templates rendered
    """
    if isinstance(data, str):
        return _apply_template(data, variables)
    elif isinstance(data, dict):
        return {key: _apply_template_recursive(value, variables) for key, value in data.items()}
    elif isinstance(data, list):
        return [_apply_template_recursive(item, variables) for item in data]
    else:
        return data


def _send_webhook_message(
    webhook_url: str,
    content: Optional[str] = None,
    username: Optional[str] = None,
    avatar_url: Optional[str] = None,
    embed: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send message to Discord via webhook.
    
    Args:
        webhook_url: Discord webhook URL
        content: Message content (plain text)
        username: Override webhook username
        avatar_url: Override webhook avatar
        embed: Single embed object (dict)
        
    Returns:
        Result dictionary with success status
    """
    if requests is None:
        return {
            "success": False,
            "error": (
                "requests library is required for Discord webhooks. "
                "Install it with: pip install requests"
            )
        }
    
    try:
        # Build payload
        payload = {}
        
        if content:
            payload["content"] = content
        
        if username:
            payload["username"] = username
        
        if avatar_url:
            payload["avatar_url"] = avatar_url
        
        if embed:
            payload["embeds"] = [embed]
        
        # Validate payload has at least content or embed
        if not content and not embed:
            return {
                "success": False,
                "error": "Message must have either content or embed"
            }
        
        # Send request
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 204:
            return {
                "success": True,
                "error": None
            }
        elif response.status_code == 429:
            # Rate limited - return error (no automatic retry)
            retry_after = response.json().get("retry_after", "unknown") if response.content else "unknown"
            return {
                "success": False,
                "error": f"Rate limited by Discord API. Retry after {retry_after} seconds."
            }
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get("message", f"HTTP {response.status_code}")
            return {
                "success": False,
                "error": f"Discord API error: {error_msg}"
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
            "error": error_msg
        }


def send_discord_message(
    content: Optional[str] = None,
    webhook_url: Optional[str] = None,
    template_vars: Optional[Dict[str, Any]] = None,
    username: Optional[str] = None,
    avatar_url: Optional[str] = None,
    embed: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send message to Discord channel via webhook.
    
    Supports both Jinja2 (preferred) and simple {variable} templating for content.
    - If Jinja2 is installed: Uses {{ variable }}, conditionals, loops, filters
    - If Jinja2 not available: Falls back to simple {variable} replacement
    
    Webhook URL is loaded from DISCORD_WEBHOOK_URL environment variable if not provided.
    
    Args:
        content: Message content (supports templating, optional if embed is provided)
        webhook_url: Discord webhook URL (loaded from env if not provided)
        template_vars: Dictionary of variables for template rendering (optional)
        username: Override webhook username (optional)
        avatar_url: Override webhook avatar URL (optional)
        embed: Single embed object as dict (optional). Can include:
               - title: Embed title
               - description: Embed description
               - color: Color code as decimal integer (e.g., 0x5865F2 or 5793522)
               - url: URL for title hyperlink
               - fields: List of dicts with 'name', 'value', optional 'inline'
               - footer: Dict with 'text' and optional 'icon_url'
               - image: Dict with 'url' for large image
               - thumbnail: Dict with 'url' for thumbnail
               - author: Dict with 'name' and optional 'url', 'icon_url'
               - timestamp: ISO 8601 timestamp string
        
    Returns:
        Dictionary containing:
            - success: Boolean indicating success
            - error: Error message if failed, None otherwise
            
    Example:
        >>> # Simple text message
        >>> result = send_discord_message(
        ...     content="Hello from Peargent!"
        ... )
        
        >>> # Message with template variables
        >>> result = send_discord_message(
        ...     content="Hello {{ name }}! Your task {{ task }} is complete.",
        ...     template_vars={"name": "Alice", "task": "data processing"}
        ... )
        
        >>> # Message with embed
        >>> result = send_discord_message(
        ...     content="System alert:",
        ...     embed={
        ...         "title": "Status Update",
        ...         "description": "All systems operational",
        ...         "color": 0x00FF00,
        ...         "fields": [
        ...             {"name": "CPU", "value": "45%", "inline": True},
        ...             {"name": "Memory", "value": "60%", "inline": True}
        ...         ]
        ...     }
        ... )
    """
    # Load webhook URL from environment if not provided
    if not webhook_url:
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    # Validate webhook URL
    if not webhook_url:
        return {
            "success": False,
            "error": (
                "Discord webhook URL is required. "
                "Set DISCORD_WEBHOOK_URL in .env file or provide webhook_url parameter."
            )
        }
    
    if not _validate_webhook_url(webhook_url):
        return {
            "success": False,
            "error": (
                "Invalid Discord webhook URL format. "
                "Expected: https://discord.com/api/webhooks/ID/TOKEN"
            )
        }
    
    # Apply template variables if provided
    if template_vars:
        if content:
            content = _apply_template(content, template_vars)
        if embed:
            embed = _apply_template_recursive(embed, template_vars)
    
    # Send message
    return _send_webhook_message(
        webhook_url=webhook_url,
        content=content,
        username=username,
        avatar_url=avatar_url,
        embed=embed
    )


class DiscordTool(Tool):
    """
    Tool for sending messages to Discord channels via webhooks.
    
    Supports:
    - Plain text messages with optional templating
    - Single rich embed per message (pass as dict)
    - Custom username and avatar per message
    - Jinja2 template rendering (preferred) or simple {variable} replacement (fallback)
    
    Webhook URL is automatically loaded from DISCORD_WEBHOOK_URL environment variable.
    
    Example:
        >>> from peargent.tools import DiscordTool
        >>> tool = DiscordTool()
        >>> result = tool.run({
        ...     "content": "Hello {{ name }}!",
        ...     "template_vars": {"name": "Team"},
        ...     "embed": {
        ...         "title": "Alert",
        ...         "description": "System is operational",
        ...         "color": 0x00FF00
        ...     }
        ... })
        >>> print(result["success"])
    """
    
    def __init__(self):
        super().__init__(
            name="discord_webhook",
            description=(
                "Send messages to Discord channels via webhooks. "
                "Supports templating and single embed per message. "
                "Webhook URL loaded from DISCORD_WEBHOOK_URL env variable if not provided. "
                "Supports Jinja2 templating when available ({{ variable }}, loops, conditionals, filters) "
                "or simple {variable} replacement as fallback. "
                "Either content (str) or embed (dict) is required. "
                "Optional parameters: webhook_url (str), template_vars (dict), "
                "username (str), avatar_url (str)."
            ),
            input_parameters={},  # No strictly required parameters - webhook from env, content/embed either-or
            call_function=send_discord_message
        )


# Create default instance for easy import
discord_tool = DiscordTool()
