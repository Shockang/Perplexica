"""
Researcher - Performs multi-step research using web search
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

from .search import SearxngSearch
from .models.base import BaseLLM
from .prompts.researcher import get_researcher_prompt


logger = logging.getLogger(__name__)


class Researcher:
    """Performs iterative research using web search and LLM reasoning"""

    def __init__(self, config, model_registry, search_client: SearxngSearch):
        self.config = config
        self.model_registry = model_registry
        self.search_client = search_client

    async def research(
        self,
        query: str,
        standalone_query: str,
        classification: Dict[str, Any],
        sources: List[str],
        mode: str,
        llm: BaseLLM,
        chat_history: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Perform research using web search and LLM reasoning

        Args:
            query: Original user query
            standalone_query: Standalone version of the query
            classification: Query classification results
            sources: Search sources to use
            mode: Optimization mode
            llm: Language model to use
            chat_history: Conversation history

        Returns:
            List of search results with content
        """
        mode_config = self.config.get_mode_config(mode)
        max_iterations = mode_config.get("max_iterations", 6)
        max_results = mode_config.get("max_results", 10)

        # Collect all search results
        all_results = []
        seen_urls = set()

        # Perform initial searches based on sources
        search_tasks = []
        for source in sources:
            if source == "web":
                search_tasks.append(
                    self.search_client.search(standalone_query, max_results=max_results)
                )
            elif source == "academic":
                search_tasks.append(
                    self.search_client.academic_search(standalone_query, max_results=max_results)
                )
            elif source == "social":
                search_tasks.append(
                    self.search_client.social_search(standalone_query, max_results=max_results)
                )

        # Execute searches in parallel
        if search_tasks:
            search_responses = await asyncio.gather(*search_tasks, return_exceptions=True)

            for response in search_responses:
                if isinstance(response, Exception):
                    continue

                results = response.get("results", [])
                for result in results:
                    url = result.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(result)

        # If mode is quality, do iterative research
        if mode == "quality" and len(all_results) > 0:
            all_results = await self._iterative_research(
                query=standalone_query,
                initial_results=all_results,
                max_iterations=max_iterations,
                llm=llm
            )

        return all_results

    async def _iterative_research(
        self,
        query: str,
        initial_results: List[Dict[str, Any]],
        max_iterations: int,
        llm: BaseLLM
    ) -> List[Dict[str, Any]]:
        """
        Perform iterative research with follow-up searches

        Args:
            query: Research query
            initial_results: Initial search results
            max_iterations: Maximum number of research iterations
            llm: Language model

        Returns:
            Enhanced search results
        """
        all_results = initial_results.copy()
        seen_urls = {r.get("url", "") for r in initial_results}

        for iteration in range(max_iterations):
            # Build context from current results
            context = self._format_results_for_context(all_results[:10])

            # Build action description for the prompt
            action_desc = self._get_action_description()

            # Get the appropriate researcher prompt
            today = datetime.now().strftime("%B %d, %Y")

            # Build a simplified prompt that works with our architecture
            prompt = f"""You are a research assistant conducting deep research on: {query}

Today's date: {today}
Iteration {iteration + 1}/{max_iterations}

Current research findings:
{context}

Determine if more information is needed:
1. Do we have enough information to comprehensively answer the query?
2. If not, what specific follow-up searches would provide missing information?

Respond in JSON format:
{{
    "done": false,
    "follow_up_query": "specific search query if needed",
    "reasoning": "why this follow-up is needed",
    "coverage_assessment": "what aspects are covered vs missing"
}}

Set done to true only when you have comprehensive, multi-angle coverage."""

            messages = [
                {"role": "system", "content": "You are a research assistant. Respond only in valid JSON."},
                {"role": "user", "content": prompt}
            ]

            try:
                response = await llm.generate(messages)
                content = response.get("content", "{}")

                # Extract JSON
                content = content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                decision = json.loads(content)

                if decision.get("done", False):
                    logger.info(f"Research complete after {iteration + 1} iterations")
                    break

                follow_up_query = decision.get("follow_up_query", "")
                if not follow_up_query:
                    logger.info(f"No follow-up query provided, ending research")
                    break

                logger.info(f"Follow-up search: {follow_up_query}")

                # Perform follow-up search
                search_result = await self.search_client.search(follow_up_query, max_results=5)

                # Add new results
                new_results = search_result.get("results", [])
                for result in new_results:
                    url = result.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(result)

                logger.info(f"Added {len(new_results)} new results (total: {len(all_results)})")

            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Iteration {iteration + 1} failed: {e}, continuing with available results")
                # If iteration fails, continue with what we have
                break

        return all_results

    def _get_action_description(self) -> str:
        """Generate description of available search actions"""
        return """
- web_search: Search the web for general information
- academic_search: Search academic databases and scholarly articles
- social_search: Search discussion forums and community platforms
"""

    def _format_results_for_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM context"""
        if not results:
            return "No results yet."

        formatted = []
        for i, result in enumerate(results[:10], 1):
            formatted.append(
                f"{i}. {result.get('title', '')}\n"
                f"   URL: {result.get('url', '')}\n"
                f"   {result.get('content', '')[:200]}..."
            )

        return "\n\n".join(formatted)
