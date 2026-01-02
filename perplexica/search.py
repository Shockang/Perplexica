"""
Search integration with SearXNG
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode


logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Base exception for search errors"""
    pass


class SearxngConnectionError(SearchError):
    """Exception raised when connection to SearXNG fails"""
    pass


class SearxngSearch:
    """SearXNG search client"""

    def __init__(self, base_url: str, timeout: int = 30, verify_ssl: bool = True):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    async def search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        engines: Optional[List[str]] = None,
        language: str = "en",
        page: int = 1,
        max_results: int = 10
    ) -> Dict[str, Any]:
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
            Dictionary with results and suggestions

        Raises:
            SearxngConnectionError: If connection to SearXNG fails
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

        # Create connector with SSL verification control
        import ssl
        ssl_context = None if self.verify_ssl else False
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        # Add headers to avoid bot detection
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"SearXNG returned status {response.status}: {error_text}")
                        raise SearxngConnectionError(
                            f"SearXNG returned status {response.status}: {error_text}"
                        )

                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        error_text = await response.text()
                        logger.error(f"SearXNG returned non-JSON response: {error_text}")
                        raise SearxngConnectionError(
                            f"SearXNG returned non-JSON response: {error_text}"
                        )

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

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Failed to connect to SearXNG at {self.base_url}: {e}")
            raise SearxngConnectionError(
                f"Failed to connect to SearXNG at {self.base_url}. "
                f"Make sure SearXNG is running and accessible."
            ) from e
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout while searching SearXNG: {e}")
            raise SearxngConnectionError(
                f"Search request timed out after {self.timeout} seconds"
            ) from e
        except SearxngConnectionError:
            # Re-raise SearXNG connection errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise SearchError(f"Unexpected error during search: {e}") from e

    async def academic_search(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
        """Perform social search"""
        return await self.search(
            query=query,
            categories=["social"],
            max_results=max_results
        )
