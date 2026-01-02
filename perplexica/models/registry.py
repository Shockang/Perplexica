"""
Model registry for managing different AI providers
"""

from typing import Dict, Any, Optional
from .base import BaseLLM, BaseEmbedding
from .ollama_provider import OllamaProvider, OllamaEmbedding
from .openai_provider import OpenAIProvider, OpenAIEmbedding
from .anthropic_provider import AnthropicProvider


class ModelRegistry:
    """Registry for managing model providers"""

    def __init__(self, config):
        self.config = config
        self._llm_cache: Dict[str, BaseLLM] = {}
        self._embedding_cache: Dict[str, BaseEmbedding] = {}

    def get_llm(self, model_name: Optional[str] = None) -> BaseLLM:
        """Get a language model instance"""
        model_name = model_name or self.config.default_chat_model

        try:
            model_config = self.config.get_model_config(model_name)
        except Exception as e:
            raise ValueError(
                f"Failed to get model configuration for '{model_name}': {e}\n\n"
                f"Tip: Run 'python check_health.py' to diagnose configuration issues"
            ) from e

        # Check cache
        cache_key = f"{model_config['provider']}:{model_config.get('model', model_name)}"
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]

        # Create new instance
        provider = model_config["provider"]

        try:
            if provider == "ollama":
                llm = OllamaProvider(model_config)
            elif provider == "openai":
                llm = OpenAIProvider(model_config)
            elif provider == "anthropic":
                llm = AnthropicProvider(model_config)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            raise ValueError(
                f"Failed to initialize {provider} provider: {e}\n\n"
                f"Tips:\n"
                f"  - Run 'python check_health.py' for detailed diagnostics\n"
                f"  - Run 'python setup_services.py' for interactive setup\n"
                f"  - Check SETUP_GUIDE.md for manual setup instructions"
            ) from e

        self._llm_cache[cache_key] = llm
        return llm

    def get_embedding_model(self, model_name: Optional[str] = None) -> BaseEmbedding:
        """Get an embedding model instance"""
        model_name = model_name or self.config.default_embedding_model
        model_config = self.config.get_model_config(model_name)

        # Check cache
        cache_key = f"{model_config['provider']}:{model_config.get('model', model_name)}"
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]

        # Create new instance
        provider = model_config["provider"]

        if provider == "ollama":
            embedding = OllamaEmbedding(model_config)
        elif provider == "openai":
            embedding = OpenAIEmbedding(model_config)
        else:
            raise ValueError(f"Unknown provider for embeddings: {provider}")

        self._embedding_cache[cache_key] = embedding
        return embedding
