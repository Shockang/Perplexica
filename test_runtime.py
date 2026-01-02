#!/usr/bin/env python3
"""
Runtime integration tests for Perplexica
Tests actual functionality with real services (SearXNG, LLM providers)
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from perplexica.config import Config
from perplexica.models import ModelRegistry
from perplexica.search_agent import SearchAgent
from perplexica.search import SearxngSearch
from perplexica.classifier import Classifier


class TestRunner:
    """Test runner for runtime tests"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def print_test(self, test_name: str):
        """Print test header"""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print('='*60)

    def print_result(self, passed: bool, message: str = ""):
        """Print test result"""
        if passed:
            print(f"✓ PASS{': ' + message if message else ''}")
            self.passed += 1
        else:
            print(f"✗ FAIL{': ' + message if message else ''}")
            self.failed += 1

    def print_skip(self, reason: str):
        """Print skipped test"""
        print(f"⊘ SKIP: {reason}")
        self.skipped += 1

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Skipped: {self.skipped}")
        print(f"Total: {self.passed + self.failed + self.skipped}")

        if self.failed == 0:
            print("\n✓ All tests passed!")
            return 0
        else:
            print(f"\n✗ {self.failed} test(s) failed")
            return 1


async def test_config_loading(runner: TestRunner):
    """Test configuration loading"""
    runner.print_test("Configuration Loading")

    try:
        config = Config()
        runner.print_result(True, "Config loaded successfully")

        # Check required keys
        required_keys = ["search", "models", "optimization"]
        for key in required_keys:
            if key in config.config:
                runner.print_result(True, f"Has key: {key}")
            else:
                runner.print_result(False, f"Missing key: {key}")

        # Check SearXNG URL
        searxng_url = config.searxng_url
        print(f"  SearXNG URL: {searxng_url}")
        runner.print_result(True, f"SearXNG URL configured: {searxng_url}")

    except Exception as e:
        runner.print_result(False, f"Exception: {e}")


async def test_searxng_connection(runner: TestRunner):
    """Test SearXNG connection"""
    runner.print_test("SearXNG Connection")

    try:
        config = Config()

        # Test connection
        search = SearxngSearch(
            base_url=config.searxng_url,
            timeout=5
        )

        # Try a simple search
        result = await search.search("test query")
        results = result.get("results", [])

        if results:
            runner.print_result(True, f"Connected to SearXNG, got {len(results)} results")
            print(f"  First result: {results[0].get('title', 'N/A')[:60]}...")
        else:
            runner.print_result(False, "Connected but got no results")

    except Exception as e:
        error_msg = str(e)
        if "Cannot connect to host" in error_msg or "Connection refused" in error_msg:
            runner.print_result(False, f"SearXNG not reachable at {config.searxng_url}")
            print(f"  💡 Tip: Start SearXNG or set SEARXNG_URL environment variable")
        else:
            runner.print_result(False, f"Exception: {e}")


async def test_model_registry(runner: TestRunner):
    """Test model registry"""
    runner.print_test("Model Registry")

    try:
        config = Config()
        registry = ModelRegistry(config)

        # Get default model
        try:
            llm = registry.get_llm()
            runner.print_result(True, f"Default model loaded: {config.default_chat_model}")
        except Exception as e:
            runner.print_result(False, f"Failed to load default model: {e}")
            print(f"  💡 Tip: Set up Ollama (ollama pull llama3.2) or configure another provider")
            return

        # Try a simple generation
        try:
            messages = [{"role": "user", "content": "Say 'Hello, World!' in JSON format: {{\"message\": \"...\"}}"}]
            response = await llm.generate(messages)

            if response and response.get("content"):
                runner.print_result(True, "LLM generation works")
                print(f"  Response: {response.get('content', '')[:100]}...")
            else:
                runner.print_result(False, "LLM returned empty response")

        except Exception as e:
            runner.print_result(False, f"LLM generation failed: {e}")
            print(f"  💡 Tip: Make sure your LLM service is running")

    except Exception as e:
        runner.print_result(False, f"Exception: {e}")


async def test_classifier(runner: TestRunner):
    """Test query classification"""
    runner.print_test("Query Classification")

    try:
        config = Config()
        registry = ModelRegistry(config)

        # Check if LLM is available
        try:
            llm = registry.get_llm()
            # Quick test
            await llm.generate([{"role": "user", "content": "test"}])
        except Exception as e:
            runner.print_skip("LLM not available, skipping classifier test")
            return

        classifier = Classifier(config, registry)

        # Test different queries
        test_queries = [
            "What is the capital of France?",
            "Hello, how are you?",
            "Find academic papers about machine learning"
        ]

        for query in test_queries:
            try:
                result = await classifier.classify(
                    query=query,
                    chat_history=[],
                    enabled_sources=["web", "academic"]
                )

                if result and isinstance(result, dict):
                    runner.print_result(True, f"Classified: '{query[:40]}...'")
                    print(f"  → Skip search: {result.get('skip_search', 'N/A')}")
                    print(f"  → Query type: {result.get('query_type', 'N/A')}")
                else:
                    runner.print_result(False, f"Invalid classification for: '{query}'")

            except Exception as e:
                runner.print_result(False, f"Classification failed for '{query}': {e}")

    except Exception as e:
        runner.print_result(False, f"Exception: {e}")


async def test_search_integration(runner: TestRunner):
    """Test full search integration"""
    runner.print_test("Full Search Integration")

    try:
        config = Config()

        # Check if SearXNG is available
        try:
            search = SearxngSearch(base_url=config.searxng_url, timeout=3)
            await search.search("test")
        except Exception as e:
            runner.print_skip("SearXNG not available, skipping search integration test")
            print(f"  💡 Tip: Start SearXNG at {config.searxng_url}")
            return

        # Check if LLM is available
        registry = ModelRegistry(config)
        try:
            llm = registry.get_llm()
            await llm.generate([{"role": "user", "content": "test"}])
        except Exception as e:
            runner.print_skip("LLM not available, skipping search integration test")
            print(f"  💡 Tip: Set up an LLM provider")
            return

        # Run actual search
        agent = SearchAgent(config, registry)

        test_query = "What is Python programming language?"
        print(f"  Running query: '{test_query}'")

        result = await agent.search(
            query=test_query,
            sources=["web"],
            mode="speed"  # Use speed mode for faster testing
        )

        if result and result.get("answer"):
            runner.print_result(True, "Search completed successfully")
            print(f"  Answer length: {len(result.get('answer', ''))} chars")
            print(f"  Sources found: {len(result.get('sources', []))}")

            if result.get('sources'):
                print(f"  First source: {result['sources'][0].get('title', 'N/A')[:50]}...")
        else:
            runner.print_result(False, "Search returned empty result")

    except Exception as e:
        runner.print_result(False, f"Exception: {e}")


async def test_different_modes(runner: TestRunner):
    """Test different optimization modes"""
    runner.print_test("Different Optimization Modes")

    try:
        config = Config()
        registry = ModelRegistry(config)
        agent = SearchAgent(config, registry)

        # Quick availability check
        try:
            search = SearxngSearch(base_url=config.searxng_url, timeout=2)
            await search.search("test")
            llm = registry.get_llm()
            await llm.generate([{"role": "user", "content": "test"}])
        except Exception as e:
            runner.print_skip("Services not available, skipping mode test")
            return

        modes = ["speed", "balanced"]
        test_query = "What is the capital of France?"

        for mode in modes:
            try:
                print(f"\n  Testing mode: {mode}")
                result = await agent.search(
                    query=test_query,
                    sources=["web"],
                    mode=mode
                )

                if result and result.get("answer"):
                    runner.print_result(True, f"Mode '{mode}' works")
                    print(f"    Answer length: {len(result['answer'])} chars")
                else:
                    runner.print_result(False, f"Mode '{mode}' returned empty result")

            except Exception as e:
                runner.print_result(False, f"Mode '{mode}' failed: {e}")

    except Exception as e:
        runner.print_result(False, f"Exception: {e}")


async def test_different_sources(runner: TestRunner):
    """Test different search sources"""
    runner.print_test("Different Search Sources")

    try:
        config = Config()
        registry = ModelRegistry(config)
        agent = SearchAgent(config, registry)

        # Quick availability check
        try:
            search = SearxngSearch(base_url=config.searxng_url, timeout=2)
            await search.search("test")
            llm = registry.get_llm()
            await llm.generate([{"role": "user", "content": "test"}])
        except Exception as e:
            runner.print_skip("Services not available, skipping sources test")
            return

        sources_to_test = [
            (["web"], "web search"),
            (["academic"], "academic search")
        ]

        for sources, description in sources_to_test:
            try:
                print(f"\n  Testing: {description}")
                result = await agent.search(
                    query="machine learning algorithms",
                    sources=sources,
                    mode="speed"
                )

                if result and result.get("answer"):
                    runner.print_result(True, f"{description} works")
                    print(f"    Sources returned: {len(result.get('sources', []))}")
                else:
                    runner.print_result(False, f"{description} returned empty result")

            except Exception as e:
                runner.print_result(False, f"{description} failed: {e}")

    except Exception as e:
        runner.print_result(False, f"Exception: {e}")


async def main():
    """Run all runtime tests"""
    print("="*60)
    print("Perplexica - Runtime Integration Tests")
    print("="*60)
    print("\nThese tests require real services to be running:")
    print("  - SearXNG (or set SEARXNG_URL)")
    print("  - LLM provider (Ollama, OpenAI, or Anthropic)")
    print()

    runner = TestRunner()

    # Run tests
    await test_config_loading(runner)
    await test_searxng_connection(runner)
    await test_model_registry(runner)
    await test_classifier(runner)
    await test_search_integration(runner)
    await test_different_modes(runner)
    await test_different_sources(runner)

    # Print summary
    exit_code = runner.print_summary()

    # Print helpful message
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)

    if runner.failed > 0:
        print("\nSome tests failed. Here's how to fix common issues:")
        print("\n1. SearXNG Connection Issues:")
        print("   - Start SearXNG: docker run -p 4000:8080 searxng/searxng")
        print("   - Or set SEARXNG_URL=https://your-searxng-instance.com")
        print("\n2. LLM Issues:")
        print("   - For Ollama: Install and run 'ollama pull llama3.2'")
        print("   - For OpenAI: Set OPENAI_API_KEY environment variable")
        print("   - For Anthropic: Set ANTHROPIC_API_KEY environment variable")
        print("\n3. Run CLI test:")
        print("   python perplexica.py 'What is the capital of France?'")
    else:
        print("\n✓ All tests passed! Try running the CLI:")
        print("   python perplexica.py 'Your question here'")
        print("\nOr test different modes:")
        print("   python perplexica.py --mode speed 'Your question'")
        print("   python perplexica.py --mode quality 'Your question'")
        print("   python perplexica.py --sources academic 'Your question'")

    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
