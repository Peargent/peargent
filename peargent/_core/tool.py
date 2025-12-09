#peargent/core/tool.py

from typing import Any, Dict, Optional, Type, Literal
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

class Tool:
    """
    Enhanced Tool class with timeout, retry, and error handling support.

    Args:
        name: Tool name
        description: Tool description for LLM
        input_parameters: Dict of parameter names to types
        call_function: Function to execute
        timeout: Maximum execution time in seconds (None = no limit)
        max_retries: Number of retry attempts on failure (0 = no retries)
        retry_delay: Initial delay between retries in seconds
        retry_backoff: Use exponential backoff for retries
        on_error: Error handling strategy - "raise", "return_error", or "return_none"
        output_schema: Optional Pydantic model for output validation
    """

    def __init__(
        self,
        name: str,
        description: str,
        input_parameters: Dict[str, type],
        call_function,
        timeout: Optional[float] = None,
        max_retries: int = 0,
        retry_delay: float = 1.0,
        retry_backoff: bool = True,
        on_error: Literal["raise", "return_error", "return_none"] = "raise",
        output_schema: Optional[Type] = None
    ):
        self.name = name
        self.description = description
        self.input_parameters = input_parameters
        self.call_function = call_function
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.on_error = on_error
        self.output_schema = output_schema

        # Validate on_error parameter
        if on_error not in ["raise", "return_error", "return_none"]:
            raise ValueError(f"on_error must be 'raise', 'return_error', or 'return_none', got '{on_error}'")

    def run(self, args: Dict[str, Any], timeout_override: Optional[float] = None) -> Any:
        """
        Execute the tool with timeout, retry, and error handling.

        Args:
            args: Tool arguments
            timeout_override: Override the tool's default timeout for this call

        Returns:
            Tool output (validated if output_schema is set)

        Raises:
            Exception: If on_error="raise" and execution fails
        """
        # Validate input parameters
        self._validate_input(args)

        # Run with retry logic
        return self._run_with_retry(args, timeout_override)

    def _validate_input(self, args: Dict[str, Any]) -> None:
        """Validate input parameters match expected types."""
        for key, expected_type in self.input_parameters.items():
            if key not in args:
                raise ValueError(f"Missing required parameter '{key}' for tool '{self.name}'")
            if not isinstance(args[key], expected_type):
                raise TypeError(f"Parameter '{key}' should be of type {expected_type}, got {type(args[key])}")

    def _run_with_retry(self, args: Dict[str, Any], timeout_override: Optional[float] = None) -> Any:
        """Execute with retry logic and exponential backoff."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Execute with timeout
                result = self._execute_with_timeout(args, timeout_override)

                # Validate output if schema is provided
                if self.output_schema:
                    result = self._validate_output(result)

                return result

            except Exception as e:
                last_error = e

                # If this isn't the last attempt, wait and retry
                if attempt < self.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    time.sleep(delay)
                else:
                    # Max retries exhausted, handle error
                    return self._handle_error(last_error)

    def _execute_with_timeout(self, args: Dict[str, Any], timeout_override: Optional[float] = None) -> Any:
        """Execute the tool function with optional timeout."""
        timeout = timeout_override if timeout_override is not None else self.timeout

        if timeout:
            # Execute with timeout using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.call_function, **args)
                try:
                    result = future.result(timeout=timeout)
                    return result
                except FuturesTimeoutError:
                    # Cancel the future
                    future.cancel()
                    raise TimeoutError(f"Tool '{self.name}' timed out after {timeout}s")
        else:
            # No timeout, execute directly
            return self.call_function(**args)

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay before next retry attempt."""
        if self.retry_backoff:
            # Exponential backoff: delay * 2^attempt
            return self.retry_delay * (2 ** attempt)
        else:
            # Fixed delay
            return self.retry_delay

    def _validate_output(self, output: Any) -> Any:
        """Validate output against Pydantic schema if provided."""
        if not self.output_schema:
            return output

        try:
            from pydantic import BaseModel

            # Check if output_schema is a Pydantic model
            if isinstance(self.output_schema, type) and issubclass(self.output_schema, BaseModel):
                # If output is already the right type, return it
                if isinstance(output, self.output_schema):
                    return output

                # If output is a dict, validate and create model instance
                if isinstance(output, dict):
                    return self.output_schema(**output)

                # Otherwise, try to parse it
                return self.output_schema.model_validate(output)

            return output

        except Exception as e:
            raise ValueError(f"Tool '{self.name}' output validation failed: {e}\nOutput: {output}")

    def _handle_error(self, error: Exception) -> Any:
        """Handle error based on on_error strategy."""
        if self.on_error == "raise":
            # Re-raise the original exception
            raise error
        elif self.on_error == "return_error":
            # Return error message as string
            error_msg = f"Tool '{self.name}' failed: {type(error).__name__}: {str(error)}"
            return error_msg
        elif self.on_error == "return_none":
            # Return None silently
            return None
        else:
            # Shouldn't reach here due to validation in __init__
            raise error
