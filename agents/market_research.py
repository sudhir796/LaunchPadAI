"""
Agent 3 — Market Research Agent
Domain: Information Retrieval + Data Analytics

Input (dict):
{
  "idea_id": "string",
  "idea_description": "string",
  "target_market": "string",
  "region": "string (optional)"
}

Output (dict):
{
  "idea_id": "string",
  "market_size_estimate": "string",
  "growth_trends": "string",
  "target_demographics": "string",
  "sources": ["string (urls)"]
}
"""

import asyncio
import json

try:
    from .llm_client import call_llm, extract_json
    from .search_utils import perform_web_search
except ImportError:
    from llm_client import call_llm, extract_json
    from search_utils import perform_web_search

SYSTEM_PROMPT = """You are a Market Research and Strategic Data Analyst acting as the \
third stage in an automated startup accelerator pipeline. Your job is to analyze real \
web search data and evaluate market opportunity, TAM/SAM size, CAGR growth trends, target demographics, \
and reference sources for a startup idea.

You must ground your findings strictly in the provided web search results and market evidence.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "market_size_estimate": "<2-3 sentence market size estimation, TAM/SAM figures, or market valuation numbers>",
  "growth_trends": "<2-3 sentence overview of market drivers, CAGR, and industry growth trends>",
  "target_demographics": "<2-3 sentence description of core customer personas and target audience segments>",
  "sources": ["<array of unique source URLs retrieved from the search results>"]
}
"""


async def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    idea_description = input_data.get("idea_description", "")
    target_market = input_data.get("target_market", "")
    region = input_data.get("region", "Global")

    # Step 1: Perform real web search grounding
    query1 = f"{target_market} market size growth trends {region}".strip()
    query2 = f"{idea_description[:100]} industry report market trends".strip()

    search_results = await asyncio.to_thread(perform_web_search, query1, max_results=4)
    if len(search_results) < 2:
        additional_results = await asyncio.to_thread(perform_web_search, query2, max_results=3)
        existing_urls = {r["url"] for r in search_results}
        for res in additional_results:
            if res["url"] not in existing_urls:
                search_results.append(res)

    # Format search evidence and collect real URLs
    evidence_lines = []
    retrieved_urls = []
    for idx, item in enumerate(search_results, 1):
        url = item.get("url", "")
        if url:
            retrieved_urls.append(url)
        evidence_lines.append(
            f"[{idx}] Title: {item.get('title')}\n"
            f"    URL: {url}\n"
            f"    Snippet: {item.get('snippet')}\n"
        )
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "No web search results retrieved."

    user_prompt = f"""idea_id: {idea_id}
Idea Description: {idea_description}
Target Market: {target_market}
Region: {region}

Web Search Evidence (Real Market Reports & Data):
{evidence_text}

Analyze the market landscape for this idea based on the search evidence provided and return the JSON object as instructed."""

    raw_response = await asyncio.to_thread(
        call_llm,
        SYSTEM_PROMPT,
        user_prompt,
        max_tokens=1000,
        agent_name="market_research",
        idea_id=idea_id,
    )
    result = extract_json(raw_response)

    # Safety nets
    result["idea_id"] = idea_id

    # Guarantee sources is a list of string URLs
    if "sources" not in result or not isinstance(result["sources"], list):
        result["sources"] = list(set(retrieved_urls))
    else:
        # Merge retrieved URLs to ensure real source links exist
        all_sources = list(dict.fromkeys(result["sources"] + retrieved_urls))
        result["sources"] = all_sources

    return result


if __name__ == "__main__":
    # Quick manual test — run `python agents/market_research.py` to try it locally
    test_input = {
        "idea_id": "test-001",
        "idea_description": (
            "An app that connects college canteens with surplus food at the end "
            "of the day to nearby students and local shelters, reducing food "
            "waste and food insecurity."
        ),
        "target_market": "College campuses and nearby low-income communities",
        "region": "North America",
    }
    output = asyncio.run(run(test_input))
    print(json.dumps(output, indent=2))
