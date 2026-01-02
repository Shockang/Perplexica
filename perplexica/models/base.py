"""
Base classes for model providers
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Any, Optional


class BaseLLM(ABC):
    """Base class for Language Model providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the model

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions
            **kwargs: Additional model parameters

        Returns:
            Dictionary with 'content' and optional 'tool_calls'
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream a response from the model

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions
            **kwargs: Additional model parameters

        Yields:
            Dictionaries with 'content_chunk' and optional 'tool_call_chunk'
        """
        pass


class BaseEmbedding(ABC):
    """Base class for Embedding model providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text

        Args:
            text: Text to embed

        Returns:
            List of floating point values representing the embedding
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass
