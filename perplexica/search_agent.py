"""
Search Agent - Main orchestration for search and response generation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional

from .search import SearxngSearch
from .classifier import Classifier
from .researcher import Researcher
from .utils import format_chat_history


class SearchAgent:
    """Main search agent that orchestrates the search process"""

    def __init__(self, config, model_registry):
        self.config = config
        self.model_registry = model_registry
        self.search_client = SearxngSearch(
            base_url=config.searxng_url,
            timeout=config.get("search.timeout", 30)
        )
        self.classifier = Classifier(config, model_registry)
        self.researcher = Researcher(config, model_registry, self.search_client)

    async def search(
        self,
        query: str,
        sources: List[str] = None,
        mode: str = "balanced",
        model: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        system_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform a search and generate a response

        Args:
            query: User's search query
            sources: List of search sources to use
            mode: Optimization mode (speed, balanced, quality)
            model: Model to use for generation
            chat_history: Previous conversation history
            system_instructions: Optional custom system instructions

        Returns:
            Dictionary with answer and sources
        """
        sources = sources or ["web"]
        chat_history = chat_history or []
        system_instructions = system_instructions or self.config.get(
            "system_instructions",
            "You are a helpful AI assistant that provides accurate, well-sourced answers."
        )

        # Get LLM
        llm = self.model_registry.get_llm(model)

        # Step 1: Classify the query
        classification = await self.classifier.classify(
            query=query,
            chat_history=chat_history,
            enabled_sources=sources
        )

        # Step 2: Research (if needed)
        search_results = []
        if not classification.get("skip_search", False):
            search_results = await self.researcher.research(
                query=query,
                standalone_query=classification.get("standalone_query", query),
                classification=classification,
                sources=sources,
                mode=mode,
                llm=llm,
                chat_history=chat_history
            )

        # Step 3: Generate final answer
        answer = await self._generate_answer(
            query=query,
            search_results=search_results,
            classification=classification,
            chat_history=chat_history,
            system_instructions=system_instructions,
            llm=llm
        )

        # Extract sources from search results
        sources_list = []
        for result in search_results:
            sources_list.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("content", "")[:200] + "..."
            })

        return {
            "answer": answer,
            "sources": sources_list,
            "classification": classification
        }

    async def _generate_answer(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        classification: Dict[str, Any],
        chat_history: List[Dict[str, str]],
        system_instructions: str,
        llm
    ) -> str:
        """Generate the final answer based on search results"""

        # Format search results for context
        search_context = ""
        if search_results:
            formatted_results = []
            for i, result in enumerate(search_results, 1):
                formatted_results.append(
                    f'<result index="{i}" title="{result.get("title", "")}">'
                    f'{result.get("content", "")}</result>'
                )
            search_context = "\n".join(formatted_results)
        else:
            search_context = "No search results available."

        # Build prompt
        prompt = f"""{system_instructions}

You are given a user query and search results. Your task is to answer the query using information from the search results. Cite your sources using [index] notation where index corresponds to the search result number.

<search_results>
{search_context}
</search_results>

<chat_history>
{format_chat_history(chat_history[-5:])}
</chat_history>

User Query: {query}

Provide a comprehensive answer based on the search results. Cite sources using [index] notation."""

        # Generate response
        messages = [
            {"role": "system", "content": prompt},
        ]

        # Add recent chat history
        messages.extend(chat_history[-5:])

        # Add current query
        messages.append({"role": "user", "content": query})

        response = await llm.generate(messages)

        return response.get("content", "")
