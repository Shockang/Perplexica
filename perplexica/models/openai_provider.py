"""
OpenAI model provider implementation
"""

import asyncio
import aiohttp
from typing import AsyncIterator, Dict, List, Any, Optional

from .base import BaseLLM, BaseEmbedding


class OpenAIProvider(BaseLLM):
    """OpenAI provider for LLM models"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-4")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.timeout = config.get("timeout", 120)

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from OpenAI"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }

        # Add tools if provided
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/chat/completions"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()

                message = result["choices"][0]["message"]

                response_data = {
                    "content": message.get("content", ""),
                }

                # Extract tool calls if present
                if "tool_calls" in message:
                    response_data["tool_calls"] = [
                        {
                            "id": tc["id"],
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"])
                        }
                        for tc in message["tool_calls"]
                    ]

                return response_data

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream a response from OpenAI"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": True
        }

        # Add tools if provided
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/chat/completions"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()

                    if not line.startswith("data: "):
                        continue

                    data = line[6:]  # Remove "data: " prefix

                    if data == "[DONE]":
                        break

                    try:
                        import json
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})

                        yield {
                            "content_chunk": delta.get("content", ""),
                            "tool_call_chunk": [],
                            "done": chunk["choices"][0].get("finish_reason") is not None
                        }
                    except (json.JSONDecodeError, KeyError):
                        continue


class OpenAIEmbedding(BaseEmbedding):
    """OpenAI provider for embedding models"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "text-embedding-3-small")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.timeout = config.get("timeout", 30)

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    async def embed(self, text: str) -> List[float]:
        """Generate an embedding for the given text"""
        embeddings = await self.embed_batch([text])
        return embeddings[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": texts
        }

        url = f"{self.base_url}/embeddings"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                embeddings = [item["embedding"] for item in result["data"]]
                return embeddings
