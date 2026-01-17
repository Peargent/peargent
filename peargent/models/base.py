# peargent/models/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Iterator, AsyncIterator

class BaseModel(ABC):
    """
    All model implementations should inherit from this interface.
    """

    def __init__(self, model_name: str, parameters: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.parameters = parameters or {}

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text completion from the prompt."""
        pass

    def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the input text.
        
        Args:
            text: The text to embed
            
        Returns:
            list[float]: The embedding vector
            
        Raises:
            NotImplementedError: If the model provider does not support embeddings.
        """
        raise NotImplementedError(f"Model {self.__class__.__name__} does not support embeddings.")

    def stream(self, prompt: str) -> Iterator[str]:
        """
        Stream text completion, yielding chunks as they arrive.

        Default implementation falls back to non-streaming.
        Models that support streaming should override this method.

        Args:
            prompt: The input prompt

        Yields:
            String chunks of the generated text
        """
        # Default fallback: yield entire response at once
        response = self.generate(prompt)
        yield response

    async def agenerate(self, prompt: str) -> str:
        """Async version of the generate method."""
        from asyncio import to_thread
        return await to_thread(self.generate, prompt)

    async def astream(self, prompt: str) -> AsyncIterator[str]:
        """
        Async version of stream method.

        Default implementation wraps sync stream in async.
        Models with native async streaming should override this.

        Args:
            prompt: The input prompt

        Yields:
            String chunks of the generated text
        """
        from asyncio import to_thread

        # Run stream in thread and yield results
        for chunk in await to_thread(lambda: list(self.stream(prompt))):
            yield chunk
