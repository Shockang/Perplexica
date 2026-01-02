"""
Query classifier for determining search strategy
"""

import json
import logging
from typing import Dict, List, Any

from .models.base import BaseLLM
from .prompts.classifier import CLASSIFIER_PROMPT


logger = logging.getLogger(__name__)


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

        # Build classification prompt using the official prompt template
        prompt = f"""{CLASSIFIER_PROMPT}

<chat_history>
{self._format_history(chat_history[-3:])}
</chat_history>

User Query: {query}

Available sources: {', '.join(enabled_sources)}

Note: For the "sources" field in classification, map:
- "web" search sources to general web search
- "academic" to academic search
- "discussion" to social/discussion search
"""

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

            result = json.loads(content)

            # Map from the official classifier format to our internal format
            classification_data = result.get("classification", {})

            # Map search sources based on classification
            sources = []
            if classification_data.get("academicSearch", False):
                sources.append("academic")
            if classification_data.get("discussionSearch", False):
                sources.append("social")
            # Default to web if no specific sources selected
            if not sources and not classification_data.get("skipSearch", False):
                sources.append("web")

            # Filter to only enabled sources
            sources = [s for s in sources if s in enabled_sources]

            # Build our internal classification format
            classification = {
                "skip_search": classification_data.get("skipSearch", False),
                "standalone_query": result.get("standaloneFollowUp", query),
                "sources": sources if sources else enabled_sources,
                "reasoning": "Query classified using official classifier",
                # Store original classification for reference
                "original_classification": classification_data
            }

            return classification

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Classification parsing failed: {e}, using fallback")
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
