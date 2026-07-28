"""
Agent 2 — Patent & Prior Art Search Agent
Domain: Information Retrieval / IP Research

Input (dict):
{
  "idea_id": "string",
  "idea_description": "string",
  "keywords": ["string"]
}

Output (dict):
{
  "idea_id": "string",
  "similar_patents": [
    { "title": "string", "summary": "string", "source_url": "string" }
  ],
  "risk_level": "string (low/medium/high)",
  "notes": "string"
}
"""

import asyncio
import json

try:
    from .llm_client import call_llm, extract_json
    from .patent_search_client import query_patentsview
except ImportError:
    from llm_client import call_llm, extract_json
    from patent_search_client import query_patentsview

SYSTEM_PROMPT = """You are an Intellectual Property (IP) and Patent Research specialist \
acting as the second stage in an automated startup accelerator pipeline. Your job is \
to evaluate prior art and patent infringement risk for a startup idea using real \
USPTO PatentsView patent search results.

You must ground your findings strictly in the provided USPTO patent evidence and IP analysis.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "similar_patents": [
    {
      "title": "<title of prior art patent>",
      "summary": "<1-2 sentence summary of what it is and how it overlaps with the idea>",
      "source_url": "<Google Patents URL>"
    }
  ],
  "risk_level": "<must be exactly one of: 'low', 'medium', or 'high'>",
  "notes": "<2-3 sentence overview of patentability, IP risks, and recommendations for freedom-to-operate>"
}
"""


async def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    idea_description = input_data.get("idea_description", "")
    keywords = input_data.get("keywords", [])

    # Step 1: Query real USPTO PatentsView API
    patentsview_results = await asyncio.to_thread(
        query_patentsview, idea_description, keywords
    )

    # Format retrieved real patents as evidence for LLM reasoning
    if patentsview_results:
        evidence_lines = []
        for idx, item in enumerate(patentsview_results, 1):
            evidence_lines.append(
                f"[{idx}] Title: {item.get('title')}\n"
                f"    Google Patent URL: {item.get('source_url')}\n"
                f"    Summary: {item.get('summary')}\n"
            )
        evidence_text = "\n".join(evidence_lines)
    else:
        evidence_text = (
            "No direct USPTO granted patent matches were returned for these keywords. "
            "This indicates low prior art density in the USPTO database for this specific query."
        )

    kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)

    user_prompt = f"""idea_id: {idea_id}
Idea Description: {idea_description}
Keywords: {kw_str}

USPTO PatentsView Real Patent Search Evidence:
{evidence_text}

Analyze the patent/prior art landscape for this idea based strictly on the USPTO evidence provided and return the JSON object as instructed."""

    # Step 2: Call LLM to interpret search evidence and assess IP risk level
    raw_response = await asyncio.to_thread(
        call_llm,
        SYSTEM_PROMPT,
        user_prompt,
        max_tokens=1000,
        agent_name="patent_search",
        idea_id=idea_id,
    )
    result = extract_json(raw_response)

    # Step 3: Enforce strict contract mapping and safety nets
    result["idea_id"] = idea_id

    # Always use the real mapped PatentsView search results for similar_patents
    result["similar_patents"] = patentsview_results

    # Ensure risk_level is standard ("low", "medium", "high")
    valid_risks = ["low", "medium", "high"]
    raw_risk = str(result.get("risk_level", "medium")).lower()
    if raw_risk not in valid_risks:
        for v in valid_risks:
            if v in raw_risk:
                result["risk_level"] = v
                break
        else:
            result["risk_level"] = "low" if not patentsview_results else "medium"
    else:
        result["risk_level"] = raw_risk

    # If zero patent matches were found, ensure notes reflect low prior art
    if not patentsview_results and "no direct" not in str(result.get("notes", "")).lower():
        if not result.get("notes"):
            result["notes"] = (
                "No direct USPTO patent matches were found for the idea keywords, suggesting low prior art risk. "
                "A broader freedom-to-operate search across international databases is recommended."
            )

    return result


if __name__ == "__main__":
    # Test Agent 2 standalone with a realistic startup idea
    test_input = {
        "idea_id": "test-patent-002",
        "idea_description": (
            "An autonomous solar-powered robotic cleaning device for high-altitude solar panels "
            "using real-time dust sensors and adaptive brush pressure control."
        ),
        "keywords": ["solar panel cleaning robot", "autonomous solar panel cleaner", "dust sensor brush control"],
    }
    
    print("=== STANDALONE TEST: Agent 2 — Patent Search ===")
    print(f"Input Idea: {test_input['idea_description']}")
    print(f"Keywords: {test_input['keywords']}\n")

    output = asyncio.run(run(test_input))

    print("\n=== FINAL AGENT OUTPUT ===")
    print(json.dumps(output, indent=2))
