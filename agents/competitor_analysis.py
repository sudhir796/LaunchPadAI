"""
Agent 4 — Competitor Analysis Agent
Domain: Information Retrieval + Comparative NLP Analysis

Input (dict):
{
  "idea_id": "string",
  "idea_description": "string",
  "market_research": {
    "idea_id": "string",
    "market_size_estimate": "string",
    "growth_trends": "string",
    "target_demographics": "string",
    "sources": ["string"]
  }
}

Output (dict):
{
  "idea_id": "string",
  "competitors": [
    { "name": "string", "description": "string", "strengths": "string", "weaknesses": "string", "source_url": "string" }
  ],
  "differentiation_opportunities": "string"
}
"""

import json

try:
    from .llm_client import call_llm, extract_json
    from .search_utils import perform_web_search
except ImportError:
    from llm_client import call_llm, extract_json
    from search_utils import perform_web_search

SYSTEM_PROMPT = """You are a Strategic Competitive Intelligence Analyst acting as the \
fourth stage in an automated startup accelerator pipeline. Your task is to analyze real \
web search data and market research to identify key direct and indirect competitors, evaluate their \
strengths and weaknesses, and pinpoint strategic differentiation opportunities for a startup idea.

You must ground your competitor analysis in real companies/apps found in the web search evidence.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "competitors": [
    {
      "name": "<name of existing competitor company or product>",
      "description": "<1-2 sentence overview of what the competitor offers>",
      "strengths": "<key competitive strengths or market advantage>",
      "weaknesses": "<key limitations or gaps in their offering>",
      "source_url": "<URL source from the search evidence>"
    }
  ],
  "differentiation_opportunities": "<2-3 sentences highlighting unique moat, positioning, and white space opportunities for this startup>"
}
"""


def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    idea_description = input_data.get("idea_description", "")
    market_research = input_data.get("market_research", {})

    target_demographics = ""
    if isinstance(market_research, dict):
        target_demographics = market_research.get("target_demographics", "")

    # Step 1: Perform real web search grounding for competitors
    query1 = f"top competitors apps for {idea_description[:80]}".strip()
    query2 = f"alternatives to market leaders {target_demographics[:80]}".strip()

    search_results = perform_web_search(query1, max_results=4)
    if len(search_results) < 2:
        additional_results = perform_web_search(query2, max_results=3)
        existing_urls = {r["url"] for r in search_results}
        for res in additional_results:
            if res["url"] not in existing_urls:
                search_results.append(res)

    # Format web search evidence
    evidence_lines = []
    for idx, item in enumerate(search_results, 1):
        evidence_lines.append(
            f"[{idx}] Name/Title: {item.get('title')}\n"
            f"    URL: {item.get('url')}\n"
            f"    Snippet: {item.get('snippet')}\n"
        )
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "No web search results retrieved."

    market_research_context = json.dumps(market_research, indent=2) if market_research else "N/A"

    user_prompt = f"""idea_id: {idea_id}
Idea Description: {idea_description}

Market Research (from Agent 3):
{market_research_context}

Web Search Evidence (Real Competitor & Product References):
{evidence_text}

Analyze the competitive landscape and return the JSON object as instructed."""

    raw_response = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=1000)
    result = extract_json(raw_response)

    # Safety nets
    result["idea_id"] = idea_id
    if "competitors" not in result or not isinstance(result["competitors"], list):
        result["competitors"] = []

    return result


if __name__ == "__main__":
    # Quick manual test — run `python agents/competitor_analysis.py` to try it locally
    sample_market_research = {
        "idea_id": "test-001",
        "market_size_estimate": "The global surplus food management market was valued at $55.3B in 2023.",
        "growth_trends": "Growing at CAGR 7.6% driven by campus sustainability mandates.",
        "target_demographics": "College students aged 18-25 and university dining hall managers.",
        "sources": [
            "https://www.sciencedirect.com/science/article/pii/S1877050925026791",
            "https://www.toogoodtogo.com/en-us"
        ]
    }
    test_input = {
        "idea_id": "test-001",
        "idea_description": (
            "An app that connects college canteens with surplus food at the end "
            "of the day to nearby students and local shelters, reducing food "
            "waste and food insecurity."
        ),
        "market_research": sample_market_research,
    }
    output = run(test_input)
    print(json.dumps(output, indent=2))
