import requests
from typing import Dict, Any, Optional, Union
from peargent._core.tool import Tool


def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: Union[float, int] = 10.0,
) -> Dict[str, Any]:
    headers = headers or {}
    params = params or {}

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json_body,
        timeout=timeout,
    )

    response.raise_for_status()

    return {
        "status_code": response.status_code,
        "url": response.url,
        "headers": dict(response.headers),
        "body": response.text,
    }


class HttpTool(Tool):
    def __init__(self):
        super().__init__(
            name="http_request",
            description=(
                "Make HTTP requests to external APIs using GET, POST, PUT, or DELETE. "
                "Supports headers, query parameters, JSON request bodies, retries, and timeouts."
            ),
            input_parameters={
                "method": str,
                "url": str,
                "headers": (dict,type(None)),
                "params": (dict,type(None)),
                "json_body": (dict,type(None)),
                "timeout": (float,int)
            },
            call_function=http_request,
            timeout=60.0,
            max_retries=2,
            retry_delay=1.0,
            retry_backoff=True,
            on_error="return_error",
        )
        
