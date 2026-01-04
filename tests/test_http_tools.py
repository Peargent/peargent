import pytest
import requests
from unittest.mock import patch, Mock
from peargent.tools.http_tools import _validate_url, http_request, HttpTool

class TestValidateUrl:
    """Tests for the _validate_url function."""

    def test_valid_http_url(self):
        """Should not raise error for a valid HTTP URL."""
        _validate_url("http://example.com/path")
        _validate_url("http://1.1.1.1")

    def test_valid_https_url(self):
        """Should not raise error for a valid HTTPS URL."""
        _validate_url("https://secure.example.com/api")
        _validate_url("https://8.8.8.8")

    def test_invalid_scheme(self):
        """Should raise ValueError for non-HTTP/HTTPS schemes."""
        with pytest.raises(ValueError, match="Only HTTP and HTTPS URLs are allowed"):
            _validate_url("ftp://example.com")
        with pytest.raises(ValueError, match="Only HTTP and HTTPS URLs are allowed"):
            _validate_url("file:///etc/passwd")

    def test_no_hostname(self):
        """Should raise ValueError for URLs without a hostname."""
        with pytest.raises(ValueError, match="URL must have a valid hostname"):
            _validate_url("http:///path")

    def test_block_localhost(self):
        """Should raise ValueError for localhost URLs."""
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            _validate_url("http://localhost")
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            _validate_url("http://127.0.0.1")
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            _validate_url("http://0.0.0.0")
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            _validate_url("http://[::1]")

    def test_block_private_ip(self):
        """Should raise ValueError for private IP addresses."""
        with pytest.raises(ValueError, match="Access to private/internal IP addresses is not allowed"):
            _validate_url("http://192.168.1.1")
        with pytest.raises(ValueError, match="Access to private/internal IP addresses is not allowed"):
            _validate_url("http://10.0.0.1")
        with pytest.raises(ValueError, match="Access to private/internal IP addresses is not allowed"):
            _validate_url("http://172.16.0.1")

    def test_invalid_url_format(self):
        """Should raise ValueError for malformed URLs."""
        with pytest.raises(ValueError, match="Invalid URL"):
            _validate_url("not a url")
        with pytest.raises(ValueError, match="Invalid URL"):
            _validate_url("http://")

class TestHttpRequest:
    """Tests for the http_request function."""

    @patch('requests.request')
    def test_successful_get_request(self, mock_requests_request):
        """Test a successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {'key': 'value'}
        mock_response.content = b'{"key": "value"}'
        mock_response.url = "http://example.com/api"
        mock_requests_request.return_value = mock_response

        result = http_request(method="GET", url="http://example.com/api", params={"a": "1"})

        mock_requests_request.assert_called_once_with(
            method="GET",
            url="http://example.com/api",
            headers={},
            params={"a": "1"},
            timeout=10.0,
        )
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["data"] == {'key': 'value'}

    @patch('requests.request')
    def test_successful_post_json_request(self, mock_requests_request):
        """Test a successful POST request with JSON body."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {'status': 'created'}
        mock_response.content = b'{"status": "created"}'
        mock_response.url = "http://example.com/create"
        mock_requests_request.return_value = mock_response

        json_data = {"name": "test", "value": 123}
        result = http_request(method="POST", url="http://example.com/create", json_body=json_data)

        mock_requests_request.assert_called_once_with(
            method="POST",
            url="http://example.com/create",
            headers={},
            params={},
            json=json_data,
            timeout=10.0,
        )
        assert result["success"] is True
        assert result["status_code"] == 201
        assert result["data"] == {'status': 'created'}

    @patch('requests.request')
    def test_successful_post_data_body_request(self, mock_requests_request):
        """Test a successful POST request with data body (form-encoded)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.text = 'data received'
        mock_response.content = b'data received'
        mock_response.url = "http://example.com/submit"
        mock_requests_request.return_value = mock_response

        data_body = "field1=value1&field2=value2"
        result = http_request(method="POST", url="http://example.com/submit", data_body=data_body)

        mock_requests_request.assert_called_once_with(
            method="POST",
            url="http://example.com/submit",
            headers={},
            params={},
            data=data_body,
            timeout=10.0,
        )
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["data"] == 'data received'

    def test_cannot_provide_both_json_and_data_body(self):
        """Should raise ValueError if both json_body and data_body are provided."""
        with pytest.raises(ValueError, match="Cannot provide both 'json_body' and 'data_body'"):
            http_request(method="POST", url="http://example.com", json_body={"a": 1}, data_body="b=2")

    @patch('requests.request')
    def test_request_timeout(self, mock_requests_request):
        """Test handling of requests.exceptions.Timeout."""
        mock_requests_request.side_effect = requests.exceptions.Timeout("Request timed out")

        result = http_request(method="GET", url="http://example.com", timeout=0.1)

        assert result["success"] is False
        assert result["error"] == "Request timed out"

    @patch('requests.request')
    def test_connection_error(self, mock_requests_request):
        """Test handling of requests.exceptions.ConnectionError."""
        mock_requests_request.side_effect = requests.exceptions.ConnectionError("Network connection error")

        result = http_request(method="GET", url="http://example.com")

        assert result["success"] is False
        assert result["error"] == "Network connection error"

    @patch('requests.request')
    def test_general_request_exception(self, mock_requests_request):
        """Test handling of a general requests.exceptions.RequestException."""
        mock_requests_request.side_effect = requests.exceptions.RequestException("Something unexpected happened")

        result = http_request(method="GET", url="http://example.com")

        assert result["success"] is False
        assert result["error"] == "Something unexpected happened"

    @patch('requests.request')
    def test_max_response_size_exceeded(self, mock_requests_request):
        """Test when response content exceeds max_response_size."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'a' * 1000
        mock_requests_request.return_value = mock_response

        result = http_request(method="GET", url="http://example.com", max_response_size=500)

        assert result["success"] is False
        assert result["error"] == "Response size exceeded limit"
        assert result["status_code"] == 200

    @patch('requests.request')
    def test_non_json_response(self, mock_requests_request):
        """Test handling of non-JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = '<html><body>Hello</body></html>'
        mock_response.content = b'<html><body>Hello</body></html>'
        mock_response.url = "http://example.com/page"
        mock_requests_request.return_value = mock_response

        result = http_request(method="GET", url="http://example.com/page")

        assert result["success"] is True
        assert result["data"] == '<html><body>Hello</body></html>'

    def test_url_validation_integration(self):
        """Ensure _validate_url is called and blocks invalid URLs."""
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            http_request(method="GET", url="http://localhost")

class TestHttpTool:
    """Tests for the HttpTool class."""

    def test_tool_initialization(self):
        """Test that HttpTool initializes correctly with expected properties."""
        tool = HttpTool()
        assert tool.name == "http_request"
        assert "Make HTTP requests" in tool.description
        assert "method" in tool.input_parameters
        assert "url" in tool.input_parameters
        assert "json_body" in tool.input_parameters
        assert "data_body" in tool.input_parameters
        assert tool.call_function == http_request
        assert tool.timeout == 60.0
        assert tool.max_retries == 2
        assert tool.retry_delay == 1.0
        assert tool.retry_backoff is True
        assert tool.on_error == "return_error"

    @patch('peargent.tools.http_tools.http_request')
    def test_tool_run_method(self, mock_http_request):
        """Test the run method of HttpTool."""
        mock_http_request.return_value = {"success": True, "status_code": 200, "data": "mocked response"}
        tool = HttpTool()
        
        params = {
            "method": "GET",
            "url": "http://example.com/test",
            "headers": {"Authorization": "Bearer token"},
            "params": {"query": "test"},
            "timeout": 5.0,
            "max_response_size": 500000
        }
        result = tool.run(params)
        
        mock_http_request.assert_called_once_with(
            method="GET",
            url="http://example.com/test",
            headers={"Authorization": "Bearer token"},
            params={"query": "test"},
            json_body=None,
            data_body=None,
            timeout=5.0,
            max_response_size=500000
        )
        assert result["success"] is True
        assert result["data"] == "mocked response"
