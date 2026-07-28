import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SearchClient:
    def __init__(self):
        self.api_key = os.environ.get("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"

    async def web_search(self, query: str, num_results: int = 5) -> list[dict]:
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not set. Returning empty search results.")
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": num_results,
            "search_depth": "basic"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            logger.warning(f"Web search failed for query '{query}': {e}")
            return []

    async def patent_search(self, query: str) -> list[dict]:
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not set. Returning empty patent search results.")
            return []

        # Focus the search on patents by restricting domains
        payload = {
            "api_key": self.api_key,
            "query": f"{query} patent",
            "max_results": 5,
            "search_depth": "advanced",
            "include_domains": ["patents.google.com", "uspto.gov"]
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            logger.warning(f"Patent search failed for query '{query}': {e}")
            return []
