"""
HTTP Client Tool for peargent.

This module provides a secure HTTP request tool that allows agents to make
external REST API calls (GET, POST, PUT, DELETE) with support for headers,
query parameters, JSON bodies, retries, timeouts, and response size limiting.

Security features include:
- SSRF protection via URL validation
- Blocking localhost and private IP ranges
- Restricting schemes to HTTP/HTTPS only
"""



import requests
from typing import Dict, Any, Optional, Union
from peargent import Tool
from urllib.parse import urlparse
import ipaddress

def _validate_url(url: str) -> None:
    """
    Validate URL to prevent SSRF attacks.
    
    Args:
        url: URL to validate
        
    Raises:
        ValueError: If URL is invalid or potentially dangerous
    """
    try:
        parsed = urlparse(url)
        
        # Only allow http and https schemes
        if parsed.scheme not in ('http', 'https'):
            raise ValueError(f"Only HTTP and HTTPS URLs are allowed, got: {parsed.scheme}")
        
        # Check if hostname exists
        if not parsed.hostname:
            raise ValueError("URL must have a valid hostname")
        
        # Block localhost and loopback addresses
        hostname_lower = parsed.hostname.lower()
        if hostname_lower in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
            raise ValueError("Access to localhost is not allowed")
        
        # Try to resolve and check if it's a private IP
        try:
            # Check if hostname is an IP address
            ip = ipaddress.ip_address(parsed.hostname)
        except ValueError:
            # Not an IP address, it's a hostname - that's okay
            # We could add DNS resolution here, but it adds complexity
            # and might block legitimate internal hostnames
            pass
        else:
            # Block private, loopback, link-local, and multicast addresses
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                raise ValueError(f"Access to private/internal IP addresses is not allowed: {ip}")
            
    except Exception as e:
        if isinstance(e, ValueError) and "not allowed" in str(e):
            raise
        raise ValueError(f"Invalid URL: {e}")

# HTTP REQUEST FUNCTION

def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: Union[float, int] = 10.0,
    data_body: Optional[Union[Dict[str, Any], str]] = None,
    max_response_size: int = 1_000_000, #1 MB
) -> Dict[str, Any]:
    """
    Makes an HTTP request to the specified URL with security validations.

    Args:
        method: The HTTP method (e.g., "GET", "POST", "PUT", "DELETE").
        url: The URL to make the request to. Must be HTTP/HTTPS and not a private IP/localhost.
        headers: Optional dictionary of HTTP headers.
        params: Optional dictionary of query parameters.
        json_body: Optional dictionary to be sent as a JSON request body.
        data_body: Optional dictionary or string to be sent as form-encoded data or raw body.
        timeout: Request timeout in seconds.
        max_response_size: Maximum allowed response size in bytes.

    Returns:
        A dictionary containing:
            - "success": True if the request was successful, False otherwise.
            - "status_code": HTTP status code of the response.
            - "url": Final URL of the request.
            - "headers": Dictionary of response headers.
            - "data": Parsed JSON response, or text content, or error message.
            - "error": Error message if the request failed.
    """
    _validate_url(url)
    
    
    headers = headers or {}
    params = params or {}
    
    if json_body and data_body:
        raise ValueError("Cannot provide both 'json_body' and 'data_body'. Choose one.")

    try:
        if json_body:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=float(timeout),
            )
        elif data_body:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data_body, # Use 'data' for form-encoded or raw body
                timeout=float(timeout),
            )
        else:
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=float(timeout),
                
            )
        
        content=response.content
        
        if len(content)>max_response_size:
            return{
                "success": False,
                "error":"Response size exceeded limit",
                "status_code":response.status_code, 
            }
            
        # Auto-parse JSON if possible
        if "application/json" in response.headers.get("Content-Type", ""):
            body = response.json()
        else:
            body = response.text

        return {
            "success": True,
            "status_code": response.status_code,
            "url": response.url,
            "headers": dict(response.headers),
            "data": body,
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}

    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Network connection error"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


class HttpTool(Tool):
    """
    HTTP Client Tool.

    Allows agents to safely make external REST API calls.

    Features:
    - GET / POST / PUT / DELETE support
    - Headers, query params, JSON bodies
    - Automatic JSON response parsing
    - Retries with exponential backoff
    - Timeout handling
    - Response size limiting
    - SSRF protection

    Example usage:
        tool = HttpTool()
        agent = create_agent(..., tools=[tool])
        
    """
    OPTIONAL_PARAMS={
        "headers": None,
        "params": None,
        "json_body": None,
        "data_body": None,
        "timeout": None,
        "max_response_size": None,
    }
    def run(self, args: Dict[str, Any], timeout_override: Optional[float] = None):
        # Inject defaults for optional params so Tool validation passes
        for key, default in self.OPTIONAL_PARAMS.items():
            args.setdefault(key, default)

        return super().run(args, timeout_override)
    
    def __init__(self):
        super().__init__(
            name="http_request",
            description=(
                "Make HTTP requests to external APIs. Supports GET, POST, PUT, DELETE. "
                "Includes security features like URL validation and response size limits. "
                "Can send JSON or form-encoded/raw data."
            ),
            input_parameters={
                "method": str,
                "url": str,
                "headers":(dict, type(None)),
                "params": (dict, type(None)),
                "json_body": (dict, type(None)),
                "data_body": (dict, str, type(None)),
                "timeout": (int, float),
                "max_response_size": (int, type(None)),   
            },
            
            call_function=http_request,
            timeout=60.0,
            max_retries=2,
            retry_delay=1.0,
            retry_backoff=True,
            on_error="return_error",
        )   
        
        
        
