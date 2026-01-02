"""
Mock search implementation for testing when SearXNG is not available
"""

import logging
from typing import Dict, List, Any
from perplexica.search import SearxngSearch


logger = logging.getLogger(__name__)


class MockSearch(SearxngSearch):
    """Mock search client for testing"""

    def __init__(self, base_url: str = "mock://", timeout: int = 30, verify_ssl: bool = True):
        # Skip parent init to avoid connection attempts
        self.base_url = base_url
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        logger.warning("Using mock search - results will be simulated")

    async def search(
        self,
        query: str,
        categories: List[str] = None,
        engines: List[str] = None,
        language: str = "en",
        page: int = 1,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Simulate search results"""
        logger.info(f"Mock search for: {query}")

        # Generate mock results based on query
        mock_results = [
            {
                "title": f"Mock Result 1 for '{query}'",
                "url": "https://example.com/mock1",
                "content": f"This is a simulated search result for the query '{query}'. "
                          f"In production, this would be actual content from SearXNG search.",
                "img_src": "",
                "thumbnail": "",
                "author": "Mock Author",
                "engine": "mock_engine"
            },
            {
                "title": f"Mock Result 2 for '{query}'",
                "url": "https://example.com/mock2",
                "content": f"Another simulated result. This demonstrates that the search pipeline "
                          f"is working, even without a real SearXNG instance.",
                "img_src": "",
                "thumbnail": "",
                "author": "Mock Author 2",
                "engine": "mock_engine"
            },
            {
                "title": "Python Official Documentation",
                "url": "https://docs.python.org/",
                "content": "Python is a programming language that lets you work quickly "
                          "and integrate systems more effectively.",
                "img_src": "",
                "thumbnail": "",
                "author": "",
                "engine": "wiki"
            }
        ]

        # Limit results as requested
        mock_results = mock_results[:max_results]

        return {
            "results": mock_results,
            "suggestions": [f"{query} tutorial", f"{query} examples", f"how to {query}"]
        }

    async def academic_search(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Simulate academic search"""
        logger.info(f"Mock academic search for: {query}")
        return await self.search(
            query=query,
            categories=["science"],
            max_results=max_results
        )

    async def social_search(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Simulate social search"""
        logger.info(f"Mock social search for: {query}")
        return await self.search(
            query=query,
            categories=["social"],
            max_results=max_results
        )
