# peargent/models/gemini.py

import os
import requests
from typing import Optional, Dict
from .base import BaseModel

class GeminiModel(BaseModel):
    ENDPOINT_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        parameters: Optional[Dict] = None,
        api_key: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ):
        super().__init__(model_name, parameters)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Gemini API key not found. Set GEMINI_API_KEY in environment or pass `api_key=`.")
        
        # Build dynamic endpoint URL with model name
        self.endpoint_url = endpoint_url or self.ENDPOINT_URL_TEMPLATE.format(model_name=self.model_name)

    def generate(self, prompt: str) -> str:
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Construct system prompt if provided
        contents = []
        
        # Add system prompt as a separate content block if provided
        system_prompt = self.parameters.get("system_prompt", "")
        if system_prompt:
            contents.append({
                "parts": [{"text": system_prompt}]
            })
        
        # Add user prompt
        contents.append({
            "parts": [{"text": prompt}]
        })
        
        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.parameters.get("temperature", 0.7),
                "maxOutputTokens": self.parameters.get("max_tokens", 8192),
            }
        }
        
        response = requests.post(self.endpoint_url, headers=headers, json=body)
        
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error: {response.status_code}, {response.text}")
        
        # Extract text from Gemini response format
        response_data = response.json()
        candidates = response_data.get("candidates", [])
        if not candidates:
            return ""
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return ""
        
        return parts[0].get("text", "")

    def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the input text using Gemini API.
        Defaults to 'text-embedding-004' if not specified in parameters.
        """
        model = self.parameters.get("embedding_model", "text-embedding-004")
        # Embedding endpoint format: .../models/{model}:embedContent
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"
        
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        body = {
            "content": {"parts": [{"text": text}]}
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            raise RuntimeError(f"Gemini Embedding error: {response.status_code}, {response.text}")
            
        data = response.json()
        if "embedding" not in data or "values" not in data["embedding"]:
            raise RuntimeError(f"Gemini returned valid response but no embedding data: {data}")
            
        return data["embedding"]["values"]