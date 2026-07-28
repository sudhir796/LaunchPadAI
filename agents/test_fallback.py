"""
Unit test script for Provider Fallback, Agent Provider Routing, and extract_json Repairs.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from agents.llm_client import extract_json, call_llm, AGENT_PROVIDER_MAP


def test_extract_json_repairs():
    print("--- Testing extract_json() Repairs ---")
    
    # 1. Surrounding text and markdown fences
    text1 = "Here is the result:\n```json\n{\n  \"idea_id\": \"test-1\",\n  \"score\": 90\n}\n```\nHope this helps!"
    res1 = extract_json(text1, provider="test_provider")
    assert res1["score"] == 90, f"Expected 90, got {res1}"
    print("[PASS] Markdown & surrounding text extraction")

    # 2. Trailing commas
    text2 = '{\n  "idea_id": "test-2",\n  "items": ["a", "b",],\n}'
    res2 = extract_json(text2, provider="test_provider")
    assert res2["idea_id"] == "test-2", f"Expected test-2, got {res2}"
    print("[PASS] Trailing comma repair")

    # 3. Single quotes
    text3 = "{'idea_id': 'test-3', 'score': 85}"
    res3 = extract_json(text3, provider="test_provider")
    assert res3["score"] == 85, f"Expected 85, got {res3}"
    print("[PASS] Single quote repair")


def test_simulated_fallback():
    print("\n--- Testing Agent Provider Routing & Rate Limit Fallback ---")
    print("Agent Provider Map configured:")
    for agent, providers in AGENT_PROVIDER_MAP.items():
        print(f"  - {agent}: {providers}")

    # Test call for reasoning agent (idea_validator: Gemini primary -> Groq fallback)
    # Gemini API key in .env has 0 free quota (429), so calling idea_validator with CACHE_ENABLED=false
    # will simulate a rate-limit on Gemini and automatically trigger [FALLBACK] to Groq!
    import os
    os.environ["CACHE_ENABLED"] = "false"
    
    print("\nExecuting idea_validator with simulated rate limit on Gemini...")
    from agents import idea_validator
    res = idea_validator.run({
        "idea_id": "fallback-test-999",
        "idea_title": "Automated Campus Recycling",
        "idea_description": "Smart bin system using computer vision to sort campus recycling."
    })
    print("\nResult received from fallback provider:")
    print(json.dumps(res, indent=2))
    assert res["idea_id"] == "fallback-test-999"
    print("\n[PASS] Rate-limit fallback test completed successfully!")


if __name__ == "__main__":
    test_extract_json_repairs()
    test_simulated_fallback()
