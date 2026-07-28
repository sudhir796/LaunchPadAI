"""
Agent 5 — Business Model Generator Agent
Domain: NLP / Strategic Reasoning

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
  },
  "competitor_analysis": {
    "idea_id": "string",
    "competitors": [...],
    "differentiation_opportunities": "string"
  }
}

Output (dict):
{
  "idea_id": "string",
  "revenue_streams": ["string"],
  "cost_structure": ["string"],
  "value_proposition": "string",
  "customer_segments": ["string"],
  "channels": ["string"]
}
"""

import json

try:
    from .llm_client import call_llm, extract_json
except ImportError:
    from llm_client import call_llm, extract_json

SYSTEM_PROMPT = """You are a Senior Startup Strategist and Business Model Architect \
acting as the fifth stage in an automated startup accelerator pipeline. Your task is \
to synthesize market research and competitive intelligence into a high-leverage Business Model Canvas \
tailored for early-stage investor evaluation.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "revenue_streams": [<2-4 specific monetization mechanisms, pricing models, or revenue streams>],
  "cost_structure": [<2-4 primary operational cost drivers, tech overheads, or marketing expenditures>],
  "value_proposition": "<2-3 sentence core value proposition summarizing primary customer benefits and ROI>",
  "customer_segments": [<2-4 specific target user/buyer segments>],
  "channels": [<2-4 acquisition, distribution, and go-to-market channels>]
}
"""


def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    idea_description = input_data.get("idea_description", "")
    market_research = input_data.get("market_research", {})
    competitor_analysis = input_data.get("competitor_analysis", {})

    market_research_context = json.dumps(market_research, indent=2) if market_research else "N/A"
    competitor_context = json.dumps(competitor_analysis, indent=2) if competitor_analysis else "N/A"

    user_prompt = f"""idea_id: {idea_id}
Idea Description: {idea_description}

Market Research (Agent 3 Output):
{market_research_context}

Competitor Analysis (Agent 4 Output):
{competitor_context}

Generate the strategic business model canvas and return the JSON object as instructed."""

    raw_response = call_llm(
        SYSTEM_PROMPT,
        user_prompt,
        max_tokens=1000,
        agent_name="business_model",
        idea_id=idea_id,
    )
    result = extract_json(raw_response)

    # Safety nets
    result["idea_id"] = idea_id
    for list_field in ["revenue_streams", "cost_structure", "customer_segments", "channels"]:
        if list_field not in result or not isinstance(result[list_field], list):
            result[list_field] = []

    return result


if __name__ == "__main__":
    # Quick manual test — run `python agents/business_model.py` to try it locally
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
    sample_competitor_analysis = {
        "idea_id": "test-001",
        "competitors": [
            {
                "name": "Too Good To Go",
                "description": "Surplus retail food marketplace.",
                "strengths": "Large consumer reach",
                "weaknesses": "No campus dining or student integration",
                "source_url": "https://www.toogoodtogo.com/en-us"
            }
        ],
        "differentiation_opportunities": "Direct API integration with university dining halls and student meal plans."
    }
    test_input = {
        "idea_id": "test-001",
        "idea_description": (
            "An app that connects college canteens with surplus food at the end "
            "of the day to nearby students and local shelters, reducing food "
            "waste and food insecurity."
        ),
        "market_research": sample_market_research,
        "competitor_analysis": sample_competitor_analysis,
    }
    output = run(test_input)
    print(json.dumps(output, indent=2))
