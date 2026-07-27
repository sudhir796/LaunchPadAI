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

import json

try:
    from .llm_client import call_llm, extract_json
    from .search_utils import perform_web_search
except ImportError:
    from llm_client import call_llm, extract_json
    from search_utils import perform_web_search

SYSTEM_PROMPT = """You are an Intellectual Property (IP) and Patent Research specialist \
acting as the second stage in an automated startup accelerator pipeline. Your job is \
to evaluate prior art and patent infringement risk for a startup idea using real web search results.

You must ground your findings strictly in the provided search results and IP analysis.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "similar_patents": [
    {
      "title": "<title of prior art, patent, or existing similar product/system>",
      "summary": "<1-2 sentence summary of what it is and how it overlaps with the idea>",
      "source_url": "<URL source from the search evidence>"
    }
  ],
  "risk_level": "<must be exactly one of: 'low', 'medium', or 'high'>",
  "notes": "<2-3 sentence overview of patentability, IP risks, and recommendations for freedom-to-operate>"
}
"""


def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    idea_description = input_data.get("idea_description", "")
    keywords = input_data.get("keywords", [])

    # Step 1: Perform real web search grounding
    kw_str = " ".join(keywords) if isinstance(keywords, list) else str(keywords)
    primary_query = f"patent prior art {kw_str}".strip()
    secondary_query = f"patent system {idea_description[:120]}".strip()

    search_results = perform_web_search(primary_query, max_results=4)
    if len(search_results) < 2:
        additional_results = perform_web_search(secondary_query, max_results=3)
        # Avoid duplicate URLs
        existing_urls = {r["url"] for r in search_results}
        for res in additional_results:
            if res["url"] not in existing_urls:
                search_results.append(res)

    # Format search evidence for LLM context
    evidence_lines = []
    for idx, item in enumerate(search_results, 1):
        evidence_lines.append(
            f"[{idx}] Title: {item.get('title')}\n"
            f"    URL: {item.get('url')}\n"
            f"    Snippet: {item.get('snippet')}\n"
        )
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "No web search results retrieved."

    user_prompt = f"""idea_id: {idea_id}
Idea Description: {idea_description}
Keywords: {kw_str}

Web Search Evidence (Real Prior Art & Patent References):
{evidence_text}

Analyze the patent/prior art landscape for this idea based on the search evidence provided and return the JSON object as instructed."""

    raw_response = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=1000)
    result = extract_json(raw_response)

    # Safety nets
    result["idea_id"] = idea_id
    
    # Ensure risk_level is standard ("low", "medium", "high")
    valid_risks = ["low", "medium", "high"]
    raw_risk = str(result.get("risk_level", "medium")).lower()
    if raw_risk not in valid_risks:
        for v in valid_risks:
            if v in raw_risk:
                result["risk_level"] = v
                break
        else:
            result["risk_level"] = "medium"
    else:
        result["risk_level"] = raw_risk

    if "similar_patents" not in result or not isinstance(result["similar_patents"], list):
        result["similar_patents"] = []

    return result


if __name__ == "__main__":
    # Quick manual test — run `python agents/patent_search.py` to try it locally
    test_input = {
        "idea_id": "test-001",
        "idea_description": (
            "An app that connects college canteens with surplus food at the end "
            "of the day to nearby students and local shelters, reducing food "
            "waste and food insecurity using real-time dynamic notification algorithms."
        ),
        "keywords": ["food waste redistribution", "surplus food app", "real-time food dispatch"],
    }
    output = run(test_input)
    print(json.dumps(output, indent=2))
