"""
Anthropic (Claude) model provider implementation
"""

import asyncio
import aiohttp
import json
from typing import AsyncIterator, Dict, List, Any, Optional

from .base import BaseLLM


class AnthropicProvider(BaseLLM):
    """Anthropic provider for Claude models"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "claude-3-5-sonnet-20241022")
        self.base_url = config.get("base_url", "https://api.anthropic.com")
        self.timeout = config.get("timeout", 120)
        self.max_tokens = config.get("max_tokens", 4096)
        self.verify_ssl = config.get("verify_ssl", True)

        if not self.api_key:
            raise ValueError("Anthropic API key is required")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from Anthropic"""

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] in ["user", "assistant"]:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })

        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
        }

        if system_message:
            payload["system"] = system_message

        # Add tools if provided
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/v1/messages"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        # Create connector with SSL verification control
        ssl_context = None if self.verify_ssl else False
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()

                response_data = {
                    "content": result.get("content", [{}])[0].get("text", ""),
                }

                # Extract tool calls if present
                if result.get("stop_reason") == "tool_use":
                    tool_blocks = [
                        block for block in result.get("content", [])
                        if block.get("type") == "tool_use"
                    ]
                    if tool_blocks:
                        response_data["tool_calls"] = [
                            {
                                "id": tb["id"],
                                "name": tb["name"],
                                "arguments": tb["input"]
                            }
                            for tb in tool_blocks
                        ]

                return response_data

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream a response from Anthropic"""

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] in ["user", "assistant"]:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })

        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": True
        }

        if system_message:
            payload["system"] = system_message

        # Add tools if provided
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/v1/messages"
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        # Create connector with SSL verification control
        ssl_context = None if self.verify_ssl else False
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()

                    if not line.startswith("data: "):
                        continue

                    data = line[6:]  # Remove "data: " prefix

                    try:
                        chunk = json.loads(data)

                        if chunk.get("type") == "content_block_delta":
                            yield {
                                "content_chunk": chunk.get("delta", {}).get("text", ""),
                                "tool_call_chunk": [],
                                "done": False
                            }
                        elif chunk.get("type") == "message_stop":
                            yield {
                                "content_chunk": "",
                                "tool_call_chunk": [],
                                "done": True
                            }
                    except (json.JSONDecodeError, KeyError):
                        continue
