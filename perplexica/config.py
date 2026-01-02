"""
Configuration management for Perplexica
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class Config:
    """Configuration manager"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self.get_default_config()
            self.save_config()

        # Override with environment variables
        self._load_from_env()

    def save_config(self):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "version": 1,
            "search": {
                "searxng_url": os.getenv("SEARXNG_URL", "http://localhost:4000"),
                "timeout": 30,
                "max_results": 10
            },
            "models": {
                "default_chat_model": os.getenv("DEFAULT_MODEL", "ollama:llama3.2"),
                "default_embedding_model": os.getenv("DEFAULT_EMBEDDING_MODEL", "ollama:nomic-embed-text"),
                "providers": []
            },
            "optimization": {
                "speed": {
                    "max_iterations": 2,
                    "max_results": 5
                },
                "balanced": {
                    "max_iterations": 6,
                    "max_results": 10
                },
                "quality": {
                    "max_iterations": 25,
                    "max_results": 15
                }
            },
            "system_instructions": "You are a helpful AI assistant that provides accurate, well-sourced answers."
        }

    def _load_from_env(self):
        """Load configuration from environment variables"""
        # SearXNG URL
        if searxng_url := os.getenv("SEARXNG_URL"):
            self.config["search"]["searxng_url"] = searxng_url

        # Ollama configuration
        if ollama_host := os.getenv("OLLAMA_HOST"):
            self.config.setdefault("ollama", {})["host"] = ollama_host

        # OpenAI API key
        if openai_key := os.getenv("OPENAI_API_KEY"):
            self.config.setdefault("openai", {})["api_key"] = openai_key

        # Anthropic API key
        if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
            self.config.setdefault("anthropic", {})["api_key"] = anthropic_key

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any):
        """Set configuration value by dot-separated key"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

    @property
    def searxng_url(self) -> str:
        """Get SearXNG URL"""
        return self.get("search.searxng_url", "http://localhost:4000")

    @property
    def default_chat_model(self) -> str:
        """Get default chat model"""
        return self.get("models.default_chat_model", "ollama:llama3.2")

    @property
    def default_embedding_model(self) -> str:
        """Get default embedding model"""
        return self.get("models.default_embedding_model", "ollama:nomic-embed-text")

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        provider_name, model = model_name.split(":", 1) if ":" in model_name else ("ollama", model_name)

        model_configs = {
            "ollama": {
                "provider": "ollama",
                "host": self.get("ollama.host", "http://localhost:11434"),
                "model": model
            },
            "openai": {
                "provider": "openai",
                "api_key": self.get("openai.api_key", os.getenv("OPENAI_API_KEY")),
                "model": model
            },
            "anthropic": {
                "provider": "anthropic",
                "api_key": self.get("anthropic.api_key", os.getenv("ANTHROPIC_API_KEY")),
                "model": model
            }
        }

        return model_configs.get(provider_name, model_configs["ollama"])

    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """Get configuration for optimization mode"""
        return self.get(f"optimization.{mode}", self.get("optimization.balanced"))
