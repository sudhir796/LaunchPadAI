"""
Agent 7 — Investor Matching Agent
Domain: Information Retrieval + Recommendation Systems

Input (dict):
{
  "idea_id": "string",
  "sector": "string",
  "business_model": {
    "idea_id": "string",
    "revenue_streams": ["string"],
    "cost_structure": ["string"],
    "value_proposition": "string",
    "customer_segments": ["string"],
    "channels": ["string"]
  }
}

Output (dict):
{
  "idea_id": "string",
  "matched_investors": [
    { "name": "string", "focus_area": "string", "reason": "string" }
  ]
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

SYSTEM_PROMPT = """You are a Venture Capital Matching & Investment Syndicate Lead acting as \
the seventh stage in an automated startup accelerator pipeline. Your job is to analyze real \
web search data and evaluate venture capital firms, angel networks, and impact investors \
that actively invest in the startup's sector and business model.

You must ground your investor recommendations in real VC firms and active investors found in the web search evidence.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "matched_investors": [
    {
      "name": "<real VC firm name, accelerator, or investor group>",
      "focus_area": "<primary investment focus, sector thesis, or stage preference>",
      "reason": "<2-3 sentence strategic rationale explaining why this fund is a strong thesis match for the business model>"
    }
  ]
}
"""


async def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    sector = input_data.get("sector", "Technology")
    business_model = input_data.get("business_model", {})

    value_proposition = ""
    if isinstance(business_model, dict):
        value_proposition = business_model.get("value_proposition", "")

    # Step 1: Perform real web search grounding for investors
    query1 = f"venture capital firms investing in {sector}".strip()
    query2 = f"top seed investors funds {sector} {value_proposition[:60]}".strip()

    search_results = await asyncio.to_thread(perform_web_search, query1, max_results=4)
    if len(search_results) < 2:
        additional_results = await asyncio.to_thread(perform_web_search, query2, max_results=3)
        existing_urls = {r["url"] for r in search_results}
        for res in additional_results:
            if res["url"] not in existing_urls:
                search_results.append(res)

    # Format web search evidence
    evidence_lines = []
    for idx, item in enumerate(search_results, 1):
        evidence_lines.append(
            f"[{idx}] Investor/Article Title: {item.get('title')}\n"
            f"    URL: {item.get('url')}\n"
            f"    Snippet: {item.get('snippet')}\n"
        )
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "No web search results retrieved."

    bm_context = json.dumps(business_model, indent=2) if business_model else "N/A"

    user_prompt = f"""idea_id: {idea_id}
Sector: {sector}

Business Model (Agent 5 Output):
{bm_context}

Web Search Evidence (Real Venture Capital & Investor References):
{evidence_text}

Match the best target investors for this startup and return the JSON object as instructed."""

    raw_response = await asyncio.to_thread(
        call_llm,
        SYSTEM_PROMPT,
        user_prompt,
        max_tokens=1000,
        agent_name="investor_matching",
        idea_id=idea_id,
    )
    result = extract_json(raw_response)

    # Safety nets
    result["idea_id"] = idea_id
    if "matched_investors" not in result or not isinstance(result["matched_investors"], list):
        result["matched_investors"] = []

    return result


if __name__ == "__main__":
    # Quick manual test — run `python agents/investor_matching.py` to try it locally
    sample_business_model = {
        "idea_id": "test-001",
        "revenue_streams": [
            "Micro-transaction commissions (10-15%) per discounted meal sold",
            "SaaS subscription fee for campus dining analytics & ESG reporting"
        ],
        "cost_structure": [
            "Cloud infrastructure and real-time push notification API hosting",
            "Campus ambassador marketing and operational support"
        ],
        "value_proposition": "Monetizes campus dining surplus meals while reducing food waste by up to 40%.",
        "customer_segments": [
            "University dining hall managers",
            "Budget-conscious college students"
        ],
        "channels": [
            "Direct B2B university administration sales",
            "Student ambassador networks"
        ]
    }
    test_input = {
        "idea_id": "test-001",
        "sector": "FoodTech & EdTech / Campus Sustainability",
        "business_model": sample_business_model,
    }
    output = asyncio.run(run(test_input))
    print(json.dumps(output, indent=2))
