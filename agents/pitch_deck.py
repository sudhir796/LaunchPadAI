"""
Agent 6 — Pitch Deck Generator Agent
Domain: NLP + Generative Content Creation

Input (dict):
{
  "idea_id": "string",
  "idea_validation": { output object from Agent 1 },
  "market_research": { output object from Agent 3 },
  "competitor_analysis": { output object from Agent 4 },
  "business_model": { output object from Agent 5 }
}

Output (dict):
{
  "idea_id": "string",
  "slides": [
    { "title": "string", "content": "string" }
  ]
}
"""

import json

try:
    from .llm_client import call_llm, extract_json
except ImportError:
    from llm_client import call_llm, extract_json

SYSTEM_PROMPT = """You are a Lead Startup Pitch Coach and Venture Content Specialist \
acting as the sixth stage in an automated startup accelerator pipeline. Your task is \
to synthesize all prior agent findings (validation, market size, competitors, business model) \
into a compelling, investor-grade 6-8 slide pitch deck outline.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "slides": [
    {
      "title": "<Slide Title e.g., Title & Mission, The Problem, The Solution, Market Size, Competitive Edge, Business Model, Go-To-Market>",
      "content": "<2-4 bullet points or concise 2-3 sentence slide body text delivering high-impact pitch content>"
    }
  ]
}
"""


def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    idea_validation = input_data.get("idea_validation", {})
    market_research = input_data.get("market_research", {})
    competitor_analysis = input_data.get("competitor_analysis", {})
    business_model = input_data.get("business_model", {})

    user_prompt = f"""idea_id: {idea_id}

Agent 1 Validation Output:
{json.dumps(idea_validation, indent=2) if idea_validation else "N/A"}

Agent 3 Market Research Output:
{json.dumps(market_research, indent=2) if market_research else "N/A"}

Agent 4 Competitor Analysis Output:
{json.dumps(competitor_analysis, indent=2) if competitor_analysis else "N/A"}

Agent 5 Business Model Output:
{json.dumps(business_model, indent=2) if business_model else "N/A"}

Synthesize this comprehensive startup intelligence into an investor-ready pitch deck and return the JSON object as instructed."""

    raw_response = call_llm(
        SYSTEM_PROMPT,
        user_prompt,
        max_tokens=1500,
        agent_name="pitch_deck",
        idea_id=idea_id,
    )
    result = extract_json(raw_response)

    # Safety nets
    result["idea_id"] = idea_id
    if "slides" not in result or not isinstance(result["slides"], list):
        result["slides"] = []

    return result


if __name__ == "__main__":
    # Quick manual test — run `python agents/pitch_deck.py` to try it locally
    sample_validation = {
        "idea_id": "test-001",
        "validation_score": 85,
        "strengths": ["Strong social impact", "High density market"],
        "weaknesses": ["Food safety liability"],
        "feasibility_notes": "Feasible mobile app with campus pilot.",
        "recommendation": "Proceed with pilot."
    }
    sample_market = {
        "idea_id": "test-001",
        "market_size_estimate": "$55.3B TAM growing at 7.6% CAGR.",
        "growth_trends": "ESG compliance mandates across university campuses.",
        "target_demographics": "College students aged 18-25 and campus dining managers.",
        "sources": ["https://www.toogoodtogo.com/en-us"]
    }
    sample_competitor = {
        "idea_id": "test-001",
        "competitors": [{"name": "Too Good To Go", "source_url": "https://www.toogoodtogo.com"}],
        "differentiation_opportunities": "Direct API integration with university dining halls and student ID systems."
    }
    sample_business = {
        "idea_id": "test-001",
        "revenue_streams": ["10-15% meal commission", "Dining SaaS subscription"],
        "cost_structure": ["Cloud hosting", "Campus marketing"],
        "value_proposition": "Monetizes campus surplus while cutting food waste by 40%.",
        "customer_segments": ["University dining managers", "Students"],
        "channels": ["Direct B2B campus sales", "Student ambassador network"]
    }

    test_input = {
        "idea_id": "test-001",
        "idea_validation": sample_validation,
        "market_research": sample_market,
        "competitor_analysis": sample_competitor,
        "business_model": sample_business,
    }
    output = run(test_input)
    print(json.dumps(output, indent=2))
