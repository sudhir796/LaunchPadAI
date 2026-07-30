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

SYSTEM_PROMPT = """You are a rigorous startup idea evaluation expert acting as the first stage \
in an automated startup accelerator pipeline. You assess a student's raw idea for \
viability, clarity, technical specificity, and execution potential.

CRITICAL SCORING DIRECTIVES:
- Do NOT give a high score just because an idea sounds plausible or uses trendy buzzwords like 'AI-powered', 'blockchain', or 'smart'.
- Vagueness itself is a primary failure mode. A vague or underspecified idea MUST score low even if it is not inherently flawed — lack of concrete mechanism or target user definition is a major weakness.
- Actively check for and penalize the ABSENCE of:
  1. A specific, named mechanism or technology approach (what does it actually DO concretely beyond 'uses AI' or 'helps with X'?).
  2. A clearly defined target user/customer segment (beyond generic categories like 'students' or 'businesses').
  3. A concrete problem definition (not vaguely implied or generic).
  4. Clear delivery/operational mechanism (how it actually functions or is delivered).

SCORING RUBRIC (0-100):
- 0-30 (Vague / Underspecified): Single vague sentence or headline with no specific mechanism, target user, or problem definition (e.g. "an app that helps students study better using AI").
- 31-50 (Generic Concept): Names a general direction or industry, but lacks a specific technical mechanism or clearly defined target user segment.
- 51-70 (Developing Concept): Has a clear problem and target user, but the technical mechanism or competitive differentiation is still generic or underdeveloped.
- 71-85 (Solid Venture): Has a specific mechanism, clear target user, and defined problem, with minor execution or feasibility questions remaining.
- 86-100 (Exceptional Venture): Highly specific, well-scoped, technically feasible, clearly differentiated from existing solutions, with clear operational mechanism.

WEAKNESSES GUIDANCE:
- You MUST actively inspect for vagueness, lack of specificity, and missing technical mechanisms.
- Include vagueness or underspecified details as explicit items in the "weaknesses" list whenever present.

CONCISENESS DIRECTIVE:
- Be concise in your reasoning — 1-2 sentences per field maximum unless more detail is explicitly requested.

You must respond with ONLY a valid JSON object, no other text, no markdown fences. \
The JSON object must have exactly these fields:
{
  "idea_id": "<same idea_id passed to you>",
  "validation_score": <integer 0-100 strictly conforming to the rubric above>,
  "strengths": [<2-4 short strings highlighting concrete strengths>],
  "weaknesses": [<2-4 short strings highlighting weaknesses, including vagueness/missing details if applicable>],
  "feasibility_notes": "<2-3 sentences on technical and practical feasibility>",
  "recommendation": "<1-2 sentences on strategic next steps or required specification before proceeding>"
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

Evaluate this idea strictly using the scoring rubric and directives provided, and return the JSON object as instructed."""

    raw_response = await asyncio.to_thread(
        call_llm,
        SYSTEM_PROMPT,
        user_prompt,
        max_tokens=1500,
        agent_name="idea_validator",
        idea_id=idea_id,
    )
    result = extract_json(raw_response)

    # Safety net: ensure idea_id always matches what was passed in
    result["idea_id"] = idea_id
    return result


if __name__ == "__main__":
    import json
    
    vague_idea = {
        "idea_id": "test-vague-001",
        "idea_title": "AI Study Helper",
        "idea_description": "An app that helps students study better using AI.",
        "target_market": "Students"
    }

    detailed_idea = {
        "idea_id": "test-detailed-002",
        "idea_title": "SolarGrid — Autonomous Solar Panel Cleaning Robot",
        "idea_description": (
            "An autonomous solar-powered robotic cleaning device for commercial high-altitude solar panel arrays. "
            "It uses real-time optical dust sensors, adaptive brush pressure control, and a tracks-based movement "
            "mechanism to clean panels without water, restoring energy efficiency by up to 30%."
        ),
        "target_market": "Commercial solar farm operators and utility companies in desert regions"
    }

    print("=== TESTING VAGUE IDEA ===")
    vague_output = asyncio.run(run(vague_idea))
    print(json.dumps(vague_output, indent=2))
    print(f"\n--> Vague Idea Score: {vague_output.get('validation_score')}/100\n")

    print("=== TESTING DETAILED IDEA ===")
    detailed_output = asyncio.run(run(detailed_idea))
    print(json.dumps(detailed_output, indent=2))
    print(f"\n--> Detailed Idea Score: {detailed_output.get('validation_score')}/100\n")

