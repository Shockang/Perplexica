"""
Search integration with SearXNG
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode


class SearxngSearch:
    """SearXNG search client"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        engines: Optional[List[str]] = None,
        language: str = "en",
        page: int = 1,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform a search query

        Args:
            query: Search query string
            categories: Optional list of categories to search
            engines: Optional list of engines to use
            language: Language code
            page: Page number
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, url, content, etc.
        """
        params = {
            "q": query,
            "format": "json",
            "language": language,
            "pageno": page
        }

        if categories:
            params["categories"] = ",".join(categories)
        if engines:
            params["engines"] = ",".join(engines)

        url = f"{self.base_url}/search?{urlencode(params)}"

        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                data = await response.json()

                results = data.get("results", [])
                suggestions = data.get("suggestions", [])

                # Limit results
                results = results[:max_results]

                # Standardize result format
                standardized_results = []
                for result in results:
                    standardized_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "img_src": result.get("img_src", ""),
                        "thumbnail": result.get("thumbnail_src", ""),
                        "author": result.get("author", ""),
                        "engine": result.get("engine", ""),
                    })

                return {
                    "results": standardized_results,
                    "suggestions": suggestions
                }

    async def academic_search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform academic search"""
        return await self.search(
            query=query,
            categories=["science"],
            max_results=max_results
        )

    async def social_search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform social search"""
        return await self.search(
            query=query,
            categories=["social"],
            max_results=max_results
        )
