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

INVESTOR_DATASET = [
    {
        "name": "Peak XV Partners",
        "focus_area": "Early-mid stage, broad sectors"
    },
    {
        "name": "Blume Ventures",
        "focus_area": "Early stage, consumer tech, SaaS"
    },
    {
        "name": "Accel",
        "focus_area": "Early-growth stage, technology"
    },
    {
        "name": "Y Combinator",
        "focus_area": "Very early stage, all sectors"
    },
    {
        "name": "100X.VC",
        "focus_area": "Pre-seed, India-focused"
    },
    {
        "name": "Titan Capital",
        "focus_area": "Early stage, consumer/tech"
    },
    {
        "name": "Kalaari Capital",
        "focus_area": "Early stage, tech-enabled businesses"
    },
    {
        "name": "Chiratae Ventures",
        "focus_area": "Early-growth, tech/consumer"
    }
]

SYSTEM_PROMPT = """You are a Venture Capital Matching & Investment Syndicate Lead acting as \
the seventh stage in an automated startup accelerator pipeline. Your job is to analyze \
a startup idea and select the best matching investors strictly from our curated dataset of real \
India-focused venture capital funds:

Real Investor Dataset Pool:
- Peak XV Partners — focus: early-mid stage, broad sectors
- Blume Ventures — focus: early stage, consumer tech, SaaS
- Accel — focus: early-growth stage, technology
- Y Combinator — focus: very early stage, all sectors
- 100X.VC — focus: pre-seed, India-focused
- Titan Capital — focus: early stage, consumer/tech
- Kalaari Capital — focus: early stage, tech-enabled businesses
- Chiratae Ventures — focus: early-growth, tech/consumer

You must select 2-4 investors from this dataset that best match the startup's sector, stage, and business model, \
and provide a strategic thesis rationale for each.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "matched_investors": [
    {
      "name": "<exact VC firm name from dataset above>",
      "focus_area": "<exact focus area from dataset above>",
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

    # Step 1: Perform web search grounding for sector context
    query1 = f"venture capital firms investing in {sector}".strip()
    query2 = f"top seed investors funds {sector} {value_proposition[:60]}".strip()

    search_results = await asyncio.to_thread(perform_web_search, query1, max_results=4)
    if len(search_results) < 2:
        additional_results = await asyncio.to_thread(perform_web_search, query2, max_results=3)
        existing_urls = {r["url"] for r in search_results}
        for res in additional_results:
            if res["url"] not in existing_urls:
                search_results.append(res)

    evidence_lines = []
    for idx, item in enumerate(search_results, 1):
        evidence_lines.append(
            f"[{idx}] Title: {item.get('title')}\n"
            f"    URL: {item.get('url')}\n"
            f"    Snippet: {item.get('snippet')}\n"
        )
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "No web search results retrieved."

    bm_context = json.dumps(business_model, indent=2) if business_model else "N/A"

    dataset_summary = "\n".join(f"- {inv['name']}: {inv['focus_area']}" for inv in INVESTOR_DATASET)

    user_prompt = f"""idea_id: {idea_id}
Sector: {sector}

Business Model (Agent 5 Output):
{bm_context}

Available Real Investor Dataset Pool:
{dataset_summary}

Web Search Intelligence Context:
{evidence_text}

Match the 2-4 best target investors from the dataset for this startup and return the JSON object as instructed."""

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
    if "matched_investors" not in result or not isinstance(result["matched_investors"], list) or len(result["matched_investors"]) == 0:
        # Fallback to top matches from dataset
        result["matched_investors"] = [
            {
                "name": "Peak XV Partners",
                "focus_area": "Early-mid stage, broad sectors",
                "reason": f"Strong thesis match for {sector} ventures looking for scalable growth and market expansion."
            },
            {
                "name": "Blume Ventures",
                "focus_area": "Early stage, consumer tech, SaaS",
                "reason": "Ideal early-stage investor for tech-enabled business models with high user engagement."
            },
            {
                "name": "100X.VC",
                "focus_area": "Pre-seed, India-focused",
                "reason": "Provides early-stage iSAFE seed capital and incubation support for campus and student-led startups."
            }
        ]

    retrieved_urls = [r["url"] for r in search_results if isinstance(r, dict) and r.get("url")]
    if "sources" not in result or not isinstance(result["sources"], list):
        result["sources"] = retrieved_urls
    else:
        all_sources = list(dict.fromkeys(result["sources"] + retrieved_urls))
        result["sources"] = all_sources

    # Compute investor readiness score & star rating
    try:
        from backend.readiness_calculator import calculate_investor_readiness_score
        readiness_data = calculate_investor_readiness_score(input_data.get("outputs", input_data))
    except ImportError:
        # Fallback calculation if backend import is unavailable
        num_matches = len(result.get("matched_investors", []))
        score = 75.0 if num_matches >= 3 else 65.0 if num_matches == 2 else 55.0
        stars = 4 if score >= 65 else 3
        readiness_data = {"investor_readiness_score": score, "star_rating": stars}

    result["investor_readiness_score"] = readiness_data["investor_readiness_score"]
    result["star_rating"] = readiness_data["star_rating"]

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
