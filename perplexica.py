#!/usr/bin/env python3
"""
Perplexica - Privacy-focused AI-powered search engine
Main entry point for the Python refactored version
"""

import argparse
import asyncio
import sys
from pathlib import Path

from perplexica.config import Config
from perplexica.search_agent import SearchAgent
from perplexica.models import ModelRegistry
from perplexica.utils import setup_logging


async def run_single_query(args, agent):
    """Run a single query and display results"""
    try:
        result = await agent.search(
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
        return 0
    except Exception as e:
        print(f"Error during search: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


async def run_interactive_mode(args, agent):
    """Run interactive chat mode"""
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

            result = await agent.search(
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
            if args.verbose:
                import traceback
                traceback.print_exc()

    return 0


async def async_main(args):
    """Async main function"""
    # Load configuration
    config = Config(args.config)

    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        print("Configuration validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("\nPlease fix these errors in config.json or config.example.json", file=sys.stderr)
        print("Run 'python check_health.py' for detailed diagnostics", file=sys.stderr)
        sys.exit(1)

    # Initialize model registry
    try:
        model_registry = ModelRegistry(config)
    except Exception as e:
        print(f"Failed to initialize model registry: {e}", file=sys.stderr)
        print("\nTips:")
        print("  - Run 'python check_health.py' to diagnose issues")
        print("  - Check that your LLM provider is configured correctly")
        sys.exit(1)

    # Initialize search agent
    agent = SearchAgent(config, model_registry)

    # Process query
    if args.query:
        return await run_single_query(args, agent)
    else:
        return await run_interactive_mode(args, agent)


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

    # Run async main
    try:
        exit_code = asyncio.run(async_main(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
