import asyncio
import json
import logging
from search_client import SearchClient

# Configure logging to see the warnings
logging.basicConfig(level=logging.WARNING)

async def main():
    client = SearchClient()
    
    print("Executing web search for: 'handloom market India'...")
    results = await client.web_search("handloom market India")
    
    print(f"\nFound {len(results)} results.")
    print(json.dumps(results, indent=2))
    
    if not results:
        print("\nNote: Results are empty because 'TAVILY_API_KEY' environment variable is missing or invalid.")
        print("Set it in your terminal (e.g. `$env:TAVILY_API_KEY='tvly-...'`) and run this script again to see live results!")

if __name__ == "__main__":
    asyncio.run(main())
