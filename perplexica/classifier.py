"""
Query classifier for determining search strategy
"""

import json
from typing import Dict, List, Any

from .models.base import BaseLLM


class Classifier:
    """Classifies queries to determine search strategy"""

    def __init__(self, config, model_registry):
        self.config = config
        self.model_registry = model_registry

    async def classify(
        self,
        query: str,
        chat_history: List[Dict[str, str]],
        enabled_sources: List[str]
    ) -> Dict[str, Any]:
        """
        Classify the query to determine search strategy

        Args:
            query: User's query
            chat_history: Conversation history
            enabled_sources: Available search sources

        Returns:
            Dictionary with classification results
        """
        llm = self.model_registry.get_llm()

        # Build classification prompt
        prompt = f"""You are a query classifier. Analyze the user's query and determine:
1. Whether web search is needed (some queries can be answered from general knowledge)
2. What search sources to use (web, academic, social)
3. Generate a standalone version of the query if it references previous context

Available sources: {', '.join(enabled_sources)}

<chat_history>
{self._format_history(chat_history[-3:])}
</chat_history>

User Query: {query}

Respond in JSON format:
{{
    "skip_search": false,
    "standalone_query": "rewritten query that stands alone",
    "reasoning": "brief explanation",
    "sources": ["web", "academic"],
    "query_type": "factual|conversational|computational|navigation"
}}

Rules:
- Set skip_search to true only for simple greetings, basic math, or common knowledge
- For queries referencing previous messages (e.g., "it", "that"), rewrite as standalone
- Use academic sources for research, scientific, or scholarly topics
- Use web sources for general information"""

        messages = [
            {"role": "system", "content": "You are a helpful assistant that responds only in valid JSON format."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await llm.generate(messages)
            content = response.get("content", "{}")

            # Extract JSON from response
            content = content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            classification = json.loads(content)

            # Ensure required fields
            if "skip_search" not in classification:
                classification["skip_search"] = False
            if "standalone_query" not in classification:
                classification["standalone_query"] = query
            if "sources" not in classification:
                classification["sources"] = enabled_sources

            # Filter sources to only enabled ones
            classification["sources"] = [
                s for s in classification["sources"] if s in enabled_sources
            ]

            return classification

        except (json.JSONDecodeError, Exception) as e:
            # Fallback classification
            return {
                "skip_search": False,
                "standalone_query": query,
                "reasoning": "Classification failed, using defaults",
                "sources": enabled_sources,
                "query_type": "factual"
            }

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format chat history for prompt"""
        if not history:
            return "No previous messages"

        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")

        return "\n".join(formatted)
