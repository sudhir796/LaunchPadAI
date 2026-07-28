# Agent 3 — Market Research Agent (REAL implementation)
# See AGENTS.md section 4 for contract
# Uses Tavily for web search + Google Gemini for synthesis
import os
import json
import logging
from google import genai
from search_client import SearchClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a market research analyst. You will be given web search results about a startup idea's target market.

Your job is to synthesize these search results into a structured market research report. You MUST:
1. Only use data, numbers, and facts that appear in the provided search results
2. Never invent or fabricate market sizes, growth rates, or statistics
3. Include real URLs from the search results as sources
4. If the search results don't contain specific data points, say "Data not available from current sources" rather than making up numbers

Respond with ONLY a valid JSON object (no markdown, no code fences) matching this exact schema:
{
  "market_size_estimate": "string — dollar figure with timeframe, from search results",
  "growth_trends": "string — CAGR or growth description from search results",
  "target_demographics": "string — who the target customers are based on idea and research",
  "sources": ["array of real URLs from the search results used"]
}"""

async def run(input: dict) -> dict:
    idea_id = input.get("idea_id", "unknown")
    idea_description = input.get("idea_description", "")
    target_market = input.get("target_market", "General")
    region = input.get("region", "")

    # Step 1: Run multiple targeted web searches
    search_client = SearchClient()

    queries = [
        f"{target_market} market size {region}".strip(),
        f"{idea_description} industry growth trends",
        f"{target_market} target demographics customers",
    ]

    all_results = []
    all_urls = []
    for query in queries:
        results = await search_client.web_search(query, num_results=3)
        for r in results:
            all_results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", "")
            })
            if r.get("url"):
                all_urls.append(r["url"])

    # Step 2: Synthesize with Google Gemini
    search_context = json.dumps(all_results, indent=2) if all_results else "No search results found."

    user_prompt = f"""Startup Idea: {idea_description}
Target Market: {target_market}
Region: {region or "Global"}

Here are the web search results to base your analysis on:

{search_context}

Synthesize these into the JSON market research report. Only cite URLs that appear above."""

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        response = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=user_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,
                        max_output_tokens=1024,
                    ),
                )
                break  # success
            except Exception as retry_err:
                if "429" in str(retry_err) and attempt < 2:
                    import asyncio
                    wait_time = 30 * (attempt + 1)
                    logger.warning(f"Rate limited, retrying in {wait_time}s (attempt {attempt + 1}/3)")
                    await asyncio.sleep(wait_time)
                else:
                    raise retry_err

        response_text = response.text.strip()
        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0].strip()

        parsed = json.loads(response_text)

        # Ensure sources only contain real URLs from search results
        valid_sources = [url for url in parsed.get("sources", []) if url in all_urls]
        if not valid_sources and all_urls:
            valid_sources = list(set(all_urls))[:5]

        return {
            "idea_id": idea_id,
            "market_size_estimate": parsed.get("market_size_estimate", "Data not available from current sources"),
            "growth_trends": parsed.get("growth_trends", "Data not available from current sources"),
            "target_demographics": parsed.get("target_demographics", "Data not available from current sources"),
            "sources": valid_sources
        }

    except Exception as e:
        logger.warning(f"LLM synthesis failed for market research: {e}")
        # Fallback: return raw search data in a structured format
        fallback_sources = list(set(all_urls))[:5]
        return {
            "idea_id": idea_id,
            "market_size_estimate": "Data not available -- LLM synthesis failed",
            "growth_trends": f"Search returned {len(all_results)} results but synthesis failed: {str(e)}",
            "target_demographics": target_market,
            "sources": fallback_sources
        }
