import asyncio
import json
import logging
import sys
sys.path.insert(0, ".")

logging.basicConfig(level=logging.WARNING)

from agents.market_research import run

async def main():
    test_input = {
        "idea_id": "test-market-001",
        "idea_description": "An AI-powered platform that connects handloom weavers directly with global buyers, eliminating middlemen",
        "target_market": "Handloom textiles",
        "region": "India"
    }

    print("Running Market Research Agent...")
    print(f"Idea: {test_input['idea_description']}")
    print(f"Target Market: {test_input['target_market']}")
    print(f"Region: {test_input['region']}")
    print("-" * 60)

    result = await run(test_input)

    print("\nAgent Output:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
