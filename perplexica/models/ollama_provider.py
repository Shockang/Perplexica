"""
Ollama model provider implementation
"""

import asyncio
import aiohttp
import json
from typing import AsyncIterator, Dict, List, Any, Optional

from .base import BaseLLM, BaseEmbedding


class OllamaProvider(BaseLLM):
    """Ollama provider for LLM models"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "http://localhost:11434")
        self.model = config.get("model", "llama3.2")
        self.timeout = config.get("timeout", 120)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from Ollama"""

        # Convert messages to Ollama format
        ollama_messages = self._convert_messages(messages)

        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "num_predict": kwargs.get("max_tokens", 2048),
            }
        }

        # Add tools if provided
        if tools:
            payload["tools"] = self._convert_tools(tools)

        url = f"{self.host}/api/chat"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()

                response_data = {
                    "content": result.get("message", {}).get("content", ""),
                }

                # Extract tool calls if present
                if "tool_calls" in result.get("message", {}):
                    response_data["tool_calls"] = [
                        {
                            "id": tc.get("function", {}).get("arguments", ""),
                            "name": tc.get("function", {}).get("name", ""),
                            "arguments": tc.get("function", {}).get("arguments", {})
                        }
                        for tc in result["message"]["tool_calls"]
                    ]

                return response_data

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream a response from Ollama"""

        # Convert messages to Ollama format
        ollama_messages = self._convert_messages(messages)

        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "num_predict": kwargs.get("max_tokens", 2048),
            }
        }

        # Add tools if provided
        if tools:
            payload["tools"] = self._convert_tools(tools)

        url = f"{self.host}/api/chat"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue

                    try:
                        chunk = json.loads(line)
                        message = chunk.get("message", {})

                        yield {
                            "content_chunk": message.get("content", ""),
                            "tool_call_chunk": [],
                            "done": chunk.get("done", False)
                        }
                    except json.JSONDecodeError:
                        continue

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Convert messages to Ollama format"""
        ollama_messages = []

        for msg in messages:
            ollama_msg = {
                "role": msg["role"],
                "content": msg.get("content", "")
            }

            # Handle tool calls
            if "tool_calls" in msg:
                ollama_msg["tool_calls"] = [
                    {
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["arguments"]
                        }
                    }
                    for tc in msg["tool_calls"]
                ]

            ollama_messages.append(ollama_msg)

        return ollama_messages

    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to Ollama format"""
        ollama_tools = []

        for tool in tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            })

        return ollama_tools


class OllamaEmbedding(BaseEmbedding):
    """Ollama provider for embedding models"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "http://localhost:11434")
        self.model = config.get("model", "nomic-embed-text")
        self.timeout = config.get("timeout", 30)

    async def embed(self, text: str) -> List[float]:
        """Generate an embedding for the given text"""
        embeddings = await self.embed_batch([text])
        return embeddings[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        url = f"{self.host}/api/embed"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        embeddings = []

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for text in texts:
                payload = {
                    "model": self.model,
                    "input": text
                }

                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    embedding = result.get("embeddings", [])[0]
                    embeddings.append(embedding)

        return embeddings
