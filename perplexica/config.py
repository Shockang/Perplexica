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

        # Anthropic API key (support both ANTHROPIC_API_KEY and ANTHROPIC_AUTH_TOKEN)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
        if anthropic_key:
            self.config.setdefault("anthropic", {})["api_key"] = anthropic_key

        # Anthropic base URL
        if anthropic_base_url := os.getenv("ANTHROPIC_BASE_URL"):
            self.config.setdefault("anthropic", {})["base_url"] = anthropic_base_url

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
                "api_key": self.get("anthropic.api_key", os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")),
                "base_url": self.get("anthropic.base_url", os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")),
                "model": model,
                "verify_ssl": self.get("anthropic.verify_ssl", True)
            }
        }

        return model_configs.get(provider_name, model_configs["ollama"])

    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """Get configuration for optimization mode"""
        return self.get(f"optimization.{mode}", self.get("optimization.balanced"))

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate configuration

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required top-level keys
        required_keys = ["search", "models", "optimization"]
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Missing required key: {key}")

        # Validate search configuration
        if "search" in self.config:
            if not self.config["search"].get("searxng_url"):
                errors.append("search.searxng_url is required")

        # Validate models configuration
        if "models" in self.config:
            if not self.config["models"].get("default_chat_model"):
                errors.append("models.default_chat_model is required")

        # Validate optimization modes
        if "optimization" in self.config:
            for mode in ["speed", "balanced", "quality"]:
                if mode in self.config["optimization"]:
                    mode_config = self.config["optimization"][mode]
                    if not isinstance(mode_config.get("max_iterations"), int):
                        errors.append(f"optimization.{mode}.max_iterations must be an integer")
                    if not isinstance(mode_config.get("max_results"), int):
                        errors.append(f"optimization.{mode}.max_results must be an integer")

        # Validate model provider configuration
        default_model = self.default_chat_model
        if ":" in default_model:
            provider, _ = default_model.split(":", 1)

            if provider == "openai":
                api_key = self.get("openai.api_key", os.getenv("OPENAI_API_KEY"))
                if not api_key:
                    errors.append("OpenAI provider requires OPENAI_API_KEY in config or environment")

            elif provider == "anthropic":
                api_key = self.get("anthropic.api_key", os.getenv("ANTHROPIC_API_KEY"))
                if not api_key:
                    errors.append("Anthropic provider requires ANTHROPIC_API_KEY in config or environment")

        return len(errors) == 0, errors
