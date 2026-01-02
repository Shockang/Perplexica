#!/usr/bin/env python3
"""
Example usage of the Perplexica Python refactored version
"""

import asyncio
from perplexica.config import Config
from perplexica.models import ModelRegistry
from perplexica.search_agent import SearchAgent


async def main():
    """Example usage"""
    # Load configuration
    config = Config("config.json")

    # Initialize model registry
    model_registry = ModelRegistry(config)

    # Initialize search agent
    agent = SearchAgent(config, model_registry)

    # Example 1: Simple search
    print("=" * 80)
    print("Example 1: Simple web search")
    print("=" * 80)

    result = await agent.search(
        query="What is Python programming language?",
        sources=["web"],
        mode="balanced"
    )

    print(f"\nAnswer:\n{result['answer']}\n")

    if result['sources']:
        print("Sources:")
        for source in result['sources'][:3]:
            print(f"  - {source['title']}")
            print(f"    {source['url']}\n")

    # Example 2: Academic search with quality mode
    print("\n" + "=" * 80)
    print("Example 2: Academic search with quality mode")
    print("=" * 80)

    result = await agent.search(
        query="Recent advances in transformer architecture",
        sources=["academic"],
        mode="quality"
    )

    print(f"\nAnswer:\n{result['answer']}\n")

    # Example 3: Conversation with context
    print("\n" + "=" * 80)
    print("Example 3: Conversation with context")
    print("=" * 80)

    chat_history = []

    first_query = "What is machine learning?"
    result = await agent.search(
        query=first_query,
        chat_history=chat_history
    )

    print(f"\nQ: {first_query}")
    print(f"A: {result['answer'][:300]}...\n")

    chat_history.append({"role": "user", "content": first_query})
    chat_history.append({"role": "assistant", "content": result['answer']})

    followup_query = "What are its main applications?"
    result = await agent.search(
        query=followup_query,
        chat_history=chat_history
    )

    print(f"Q: {followup_query}")
    print(f"A: {result['answer'][:300]}...\n")


if __name__ == "__main__":
    print("Perplexica Python - Example Usage")
    print("Make sure SearxNG is running and config.json is configured\n")

    asyncio.run(main())
