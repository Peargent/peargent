"""
Embedding generation for long-term memory.

Provides simple embeddings using sentence-transformers or OpenAI API.
"""

from typing import List, Optional
import hashlib


class EmbeddingGenerator:
    """
    Generate vector embeddings for text.
    
    Supports multiple backends:
    - sentence-transformers (local, free)
    - OpenAI API (requires API key)
    - Simple hash-based (for testing)
    """
    
    def __init__(self, method: str = "simple", model: Optional[str] = None):
        """
        Initialize embedding generator.
        
        Args:
            method: "simple", "sentence-transformers", or "openai"
            model: Model name (e.g., "all-MiniLM-L6-v2" for sentence-transformers)
        """
        self.method = method
        self.model = model
        self._encoder = None
        
        if method == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                model_name = model or "all-MiniLM-L6-v2"
                self._encoder = SentenceTransformer(model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
    
    def generate(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Vector embedding
        """
        if self.method == "simple":
            return self._simple_embedding(text)
        elif self.method == "sentence-transformers":
            return self._sentence_transformer_embedding(text)
        elif self.method == "openai":
            return self._openai_embedding(text)
        else:
            raise ValueError(f"Unknown embedding method: {self.method}")
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Create a simple hash-based embedding (for testing only).
        
        This is NOT suitable for production - it's just for testing the architecture.
        """
        # Create a deterministic hash
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 128-dimensional vector
        embedding = []
        for i in range(0, len(hash_bytes), 2):
            # Convert pairs of bytes to float between -1 and 1
            val = (int.from_bytes(hash_bytes[i:i+2], 'big') / 65535.0) * 2 - 1
            embedding.append(val)
        
        # Pad to 128 dimensions
        while len(embedding) < 128:
            embedding.append(0.0)
        
        return embedding[:128]
    
    def _sentence_transformer_embedding(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers."""
        if not self._encoder:
            raise RuntimeError("Sentence transformer not initialized")
        
        embedding = self._encoder.encode(text)
        return embedding.tolist()
    
    def _openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        try:
            import openai
            import os
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            client = openai.OpenAI(api_key=api_key)
            model_name = self.model or "text-embedding-3-small"
            
            response = client.embeddings.create(
                input=text,
                model=model_name
            )
            
            return response.data[0].embedding
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
