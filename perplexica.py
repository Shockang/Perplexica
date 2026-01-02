#!/usr/bin/env python3
"""
Perplexica - Privacy-focused AI-powered search engine
Main entry point for the Python refactored version
"""

import argparse
import sys
from pathlib import Path

from perplexica.config import Config
from perplexica.search_agent import SearchAgent
from perplexica.models import ModelRegistry
from perplexica.utils import setup_logging


def main():
    """Main entry point for Perplexica"""
    parser = argparse.ArgumentParser(
        description="Perplexica - Privacy-focused AI-powered search engine"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (if not provided, enters interactive mode)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Override the default model"
    )
    parser.add_argument(
        "--sources",
        type=str,
        nargs="+",
        choices=["web", "academic", "social", "uploads"],
        default=["web"],
        help="Search sources to use (default: web)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["speed", "balanced", "quality"],
        default="balanced",
        help="Optimization mode (default: balanced)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    # Load configuration
    config = Config(args.config)

    # Initialize model registry
    model_registry = ModelRegistry(config)

    # Initialize search agent
    agent = SearchAgent(config, model_registry)

    # Process query
    if args.query:
        # Single query mode
        result = agent.search(
            query=args.query,
            sources=args.sources,
            mode=args.mode,
            model=args.model
        )
        print(result["answer"])
        if result.get("sources"):
            print("\nSources:")
            for source in result["sources"]:
                print(f"  - {source['title']}: {source['url']}")
    else:
        # Interactive mode
        print("Perplexica - Interactive Mode")
        print("Type 'quit' or 'exit' to end the session\n")
        chat_history = []

        while True:
            try:
                query = input("You: ").strip()
                if not query:
                    continue
                if query.lower() in ["quit", "exit"]:
                    print("Goodbye!")
                    break

                result = agent.search(
                    query=query,
                    sources=args.sources,
                    mode=args.mode,
                    model=args.model,
                    chat_history=chat_history
                )

                print(f"\nAssistant: {result['answer']}")
                if result.get("sources"):
                    print("\nSources:")
                    for source in result["sources"]:
                        print(f"  - {source['title']}: {source['url']}")
                print()

                # Add to chat history
                chat_history.append({"role": "user", "content": query})
                chat_history.append({"role": "assistant", "content": result["answer"]})

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
