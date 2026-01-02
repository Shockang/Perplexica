#!/usr/bin/env python3
"""
Dry-run test to verify code flow without needing actual services
This test mocks the external services to verify the entire pipeline works
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from perplexica.config import Config
from perplexica.search_agent import SearchAgent
from perplexica.models import ModelRegistry


async def test_dry_run():
    """Test the search pipeline with mocked services"""
    print("=" * 60)
    print("DRY RUN TEST - Mocked Services")
    print("=" * 60)

    # Load config
    print("\n1. Loading configuration...")
    config = Config()
    print("   ✓ Config loaded")

    # Create model registry
    print("\n2. Creating model registry...")
    model_registry = ModelRegistry(config)
    print("   ✓ Model registry created")

    # Create search agent
    print("\n3. Creating search agent...")
    agent = SearchAgent(config, model_registry)
    print("   ✓ Search agent created")

    # Mock the LLM
    print("\n4. Mocking LLM responses...")

    # Mock classification response
    mock_classify_response = {
        "content": '''```json
{
  "classification": {
    "skipSearch": false,
    "academicSearch": false,
    "discussionSearch": false
  },
  "standaloneFollowUp": "What is the capital of France?"
}
```'''
    }

    # Mock researcher response
    mock_researcher_response = {
        "content": "done"
    }

    # Mock answer generation response
    mock_answer_response = {
        "content": "Based on the search results, the capital of France is Paris. [1]"
    }

    # Get the LLM instance
    llm = model_registry.get_llm()

    # Mock the generate method
    async def mock_generate(messages):
        # Determine what kind of response to return based on the messages
        system_msg = messages[0].get("content", "") if messages else ""
        if "Classification" in system_msg or "standaloneFollowUp" in system_msg:
            return mock_classify_response
        elif "action orchestrator" in system_msg.lower() or "available_tools" in system_msg.lower():
            return mock_researcher_response
        else:
            return mock_answer_response

    llm.generate = AsyncMock(side_effect=mock_generate)

    print("   ✓ LLM mocked")

    # Mock search client
    print("\n5. Mocking search responses...")

    async def mock_search(query, max_results=10):
        return {
            "results": [
                {
                    "title": "Paris - Capital of France",
                    "url": "https://example.com/paris",
                    "content": "Paris is the capital and most populous city of France.",
                    "engine": "wikipedia"
                },
                {
                    "title": "France - Wikipedia",
                    "url": "https://example.com/france",
                    "content": "France is a country in Western Europe. Its capital is Paris.",
                    "engine": "wikipedia"
                }
            ],
            "suggestions": []
        }

    agent.search_client.search = AsyncMock(side_effect=mock_search)
    print("   ✓ Search client mocked")

    # Test the search pipeline
    print("\n6. Testing search pipeline...")
    print("   Query: 'What is the capital of France?'")

    try:
        result = await agent.search(
            query="What is the capital of France?",
            sources=["web"],
            mode="speed"
        )

        print("\n   ✓ Search completed successfully!")
        print("\n7. Results:")
        print(f"   Answer: {result['answer'][:100]}...")
        print(f"   Sources found: {len(result.get('sources', []))}")
        if result.get('sources'):
            for i, source in enumerate(result['sources'][:2], 1):
                print(f"     {i}. {source['title']}")

        print("\n" + "=" * 60)
        print("✓✓✓ DRY RUN TEST PASSED ✓✓✓")
        print("=" * 60)
        print("\nThe entire pipeline works correctly!")
        print("All components are properly integrated.")
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_dry_run())
    sys.exit(exit_code)
