#!/usr/bin/env python3
"""
Health check utility for Perplexica
Checks availability of required services and provides helpful setup instructions
"""
import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from perplexica.config import Config
from perplexica.models import ModelRegistry
from perplexica.search import SearxngSearch


class HealthChecker:
    """Health checker for Perplexica services"""

    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)

    def print_check(self, name: str, status: str, message: str = ""):
        """Print check result"""
        status_icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"  {status_icon} {name}: {status}")
        if message:
            print(f"     {message}")

        if status == "PASS":
            self.passed.append(name)
        elif status == "FAIL":
            self.failed.append(name)
        else:
            self.warnings.append(name)

    async def check_config(self):
        """Check configuration file"""
        self.print_header("Configuration Check")

        try:
            config = Config()
            self.print_check("Config file", "PASS", f"Loaded from {config.config_path}")

            # Check required keys
            required_keys = ["search", "models", "optimization"]
            for key in required_keys:
                if key in config.config:
                    self.print_check(f"Config key: {key}", "PASS")
                else:
                    self.print_check(f"Config key: {key}", "FAIL", "Missing required key")

            # Check SearXNG URL
            searxng_url = config.searxng_url
            print(f"\n  SearXNG URL: {searxng_url}")

            # Check model configuration
            default_model = config.default_chat_model
            print(f"  Default Model: {default_model}")

            return config

        except Exception as e:
            self.print_check("Config file", "FAIL", str(e))
            return None

    async def check_searxng(self, config):
        """Check SearXNG connection"""
        self.print_header("SearXNG Search Service Check")

        if not config:
            self.print_check("SearXNG", "FAIL", "Config not loaded")
            return False

        try:
            search = SearxngSearch(
                base_url=config.searxng_url,
                timeout=5
            )

            # Try a simple search
            result = await search.search("test query")
            results = result.get("results", [])

            if results:
                self.print_check(
                    "SearXNG connection",
                    "PASS",
                    f"Connected and returned {len(results)} results"
                )
                print(f"\n  Sample result:")
                print(f"    Title: {results[0].get('title', 'N/A')[:60]}...")
                return True
            else:
                self.print_check("SearXNG connection", "WARN", "Connected but no results")
                return False

        except Exception as e:
            error_msg = str(e)
            if "Cannot connect to host" in error_msg or "Connection refused" in error_msg:
                self.print_check(
                    "SearXNG connection",
                    "FAIL",
                    f"Cannot connect to {config.searxng_url}"
                )
                print("\n  💡 To fix this, choose one of the following:")
                print("     1. Start SearXNG with Docker:")
                print("        docker run -d --name searxng -p 4000:8080 searxng/searxng:latest")
                print("\n     2. Use a public SearXNG instance:")
                print("        export SEARXNG_URL=https://searx.be")
                print("\n     3. Update config.json with your SearXNG URL")
            else:
                self.print_check("SearXNG connection", "FAIL", error_msg)

            return False

    async def check_llm_provider(self, config):
        """Check LLM provider"""
        self.print_header("LLM Provider Check")

        if not config:
            self.print_check("LLM provider", "FAIL", "Config not loaded")
            return False

        try:
            registry = ModelRegistry(config)
            llm = registry.get_llm()

            # Try a simple generation
            messages = [{
                "role": "user",
                "content": 'Respond with JSON: {"status": "ok"}'
            }]

            response = await llm.generate(messages)

            if response and response.get("content"):
                self.print_check(
                    "LLM provider",
                    "PASS",
                    f"Model: {config.default_chat_model}"
                )
                print(f"\n  Test response: {response.get('content', '')[:60]}...")
                return True
            else:
                self.print_check("LLM provider", "FAIL", "Empty response from LLM")
                return False

        except Exception as e:
            error_msg = str(e)
            provider = config.default_chat_model.split(":")[0] if ":" in config.default_chat_model else "unknown"

            self.print_check("LLM provider", "FAIL", f"Provider '{provider}' error: {error_msg}")

            print("\n  💡 To fix this, choose one of the following:")

            if provider == "ollama":
                print("\n     For Ollama (local, free):")
                print("     1. Install Ollama: https://ollama.ai/download")
                print("     2. Start Ollama: ollama serve")
                print("     3. Pull a model: ollama pull llama3.2")
                print("     4. Verify: ollama list")

            elif provider == "openai":
                print("\n     For OpenAI (paid):")
                print("     1. Set API key: export OPENAI_API_KEY='sk-...'")
                print("     2. Or add to config.json: \"openai\": {\"api_key\": \"sk-...\"}")

            elif provider == "anthropic":
                print("\n     For Anthropic/Claude (paid):")
                print("     1. Set API key: export ANTHROPIC_API_KEY='sk-ant-...'")
                print("     2. Or add to config.json: \"anthropic\": {\"api_key\": \"sk-ant-...\"}")

            else:
                print("\n     Configure a model provider in config.json:")
                print("     - Ollama (recommended for local use)")
                print("     - OpenAI (GPT models)")
                print("     - Anthropic (Claude models)")

            return False

    async def check_environment(self, config):
        """Check environment configuration"""
        self.print_header("Environment Check")

        import os

        # Check for API keys
        api_keys = {
            "OPENAI_API_KEY": "OpenAI",
            "ANTHROPIC_API_KEY": "Anthropic/Claude",
            "SEARXNG_URL": "SearXNG URL override"
        }

        found_keys = []
        for key, name in api_keys.items():
            if os.environ.get(key):
                found_keys.append(name)
                self.print_check(f"Environment variable: {key}", "PASS", "Set")
            else:
                self.print_check(f"Environment variable: {key}", "INFO", "Not set (optional)")

        if found_keys:
            print(f"\n  Found API keys for: {', '.join(found_keys)}")

        # Check Python version
        py_version = sys.version_info
        if py_version >= (3, 8):
            self.print_check("Python version", "PASS", f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")
        else:
            self.print_check("Python version", "WARN", f"Python {py_version.major}.{py_version.minor} (3.8+ recommended)")

    def print_summary(self):
        """Print health check summary"""
        self.print_header("Health Check Summary")

        total = len(self.passed) + len(self.failed)
        pass_rate = (len(self.passed) / total * 100) if total > 0 else 0

        print(f"\n  Total Checks: {total}")
        print(f"  Passed: {len(self.passed)} ({pass_rate:.0f}%)")
        print(f"  Failed: {len(self.failed)}")
        print(f"  Warnings: {len(self.warnings)}")

        if len(self.failed) == 0:
            print("\n  ✓ All checks passed! Perplexica is ready to use.")
            print("\n  Try running:")
            print("    python perplexica.py 'What is the capital of France?'")
        else:
            print("\n  ✗ Some checks failed. Please fix the issues above before using Perplexica.")
            print("\n  Quick setup guide:")
            print("    1. Review SETUP_GUIDE.md for detailed instructions")
            print("    2. Run: python check_health.py (this script)")
            print("    3. Fix any failed checks")
            print("    4. Run again to verify")

        return len(self.failed) == 0


async def main():
    """Run health checks"""
    print("\n" + "="*70)
    print("  Perplexica - Service Health Check")
    print("="*70)
    print("\nThis script checks if all required services are properly configured.")
    print("It provides helpful tips for fixing any issues.\n")

    checker = HealthChecker()

    # Run checks
    config = await checker.check_config()
    await checker.check_environment(config)
    searxng_ok = await checker.check_searxng(config)
    llm_ok = await checker.check_llm_provider(config)

    # Print summary
    all_ok = checker.print_summary()

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
