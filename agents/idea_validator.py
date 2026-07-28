"""
Agent 1 — Idea Validator Agent
Domain: NLP / Reasoning & Evaluation

Input (dict):
{
  "idea_id": "string",
  "idea_title": "string",
  "idea_description": "string",
  "target_market": "string (optional)"
}

Output (dict):
{
  "idea_id": "string",
  "validation_score": number (0-100),
  "strengths": [string],
  "weaknesses": [string],
  "feasibility_notes": "string",
  "recommendation": "string"
}
"""

import asyncio

try:
    from .llm_client import call_llm, extract_json
except ImportError:
    from llm_client import call_llm, extract_json

SYSTEM_PROMPT = """You are a startup idea evaluation expert acting as the first stage \
in an automated startup accelerator pipeline. You assess a student's raw idea for \
viability, clarity, and potential — not to discourage, but to give an honest, \
constructive first read that later agents (market research, business modeling, \
pitch generation) will build on.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "validation_score": <integer 0-100>,
  "strengths": [<2-4 short strings>],
  "weaknesses": [<2-4 short strings>],
  "feasibility_notes": "<2-3 sentences on technical/practical feasibility>",
  "recommendation": "<1-2 sentences on whether/how to proceed>"
}
"""


async def run(input_data: dict) -> dict:
    idea_id = input_data.get("idea_id", "unknown")
    idea_title = input_data.get("idea_title", "")
    idea_description = input_data.get("idea_description", "")
    target_market = input_data.get("target_market", "not specified")

    user_prompt = f"""idea_id: {idea_id}
Idea title: {idea_title}
Idea description: {idea_description}
Target market: {target_market}

Evaluate this idea and return the JSON object as instructed."""

    raw_response = await asyncio.to_thread(
        call_llm,
        SYSTEM_PROMPT,
        user_prompt,
        max_tokens=800,
        agent_name="idea_validator",
        idea_id=idea_id,
    )
    result = extract_json(raw_response)

    # Safety net: ensure idea_id always matches what was passed in,
    # even if the model forgets to echo it back correctly.
    result["idea_id"] = idea_id
    return result


if __name__ == "__main__":
    # Quick manual test — run `python agents/idea_validator.py` to try it locally
    test_input = {
        "idea_id": "test-001",
        "idea_title": "Campus Food Waste Redistribution App",
        "idea_description": (
            "An app that connects college canteens with surplus food at the end "
            "of the day to nearby students and local shelters, reducing food "
            "waste and food insecurity."
        ),
        "target_market": "College campuses and nearby low-income communities",
    }
    import json
    output = asyncio.run(run(test_input))
    print(json.dumps(output, indent=2))
