"""
End-to-End Test Script for LaunchPad AI 7-Agent Pipeline (Async)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import json
from agents import (
    idea_validator,
    patent_search,
    market_research,
    competitor_analysis,
    business_model,
    pitch_deck,
    investor_matching,
)

async def test_full_pipeline():
    print("=== STARTING LAUNCHPAD AI PIPELINE TEST ===")
    
    # Raw User Input
    raw_idea = {
        "idea_id": "test-pipeline-100",
        "idea_title": "Campus Food Waste Redistribution App",
        "idea_description": (
            "An app that connects college canteens with surplus food at the end "
            "of the day to nearby students and local shelters, reducing food "
            "waste and food insecurity."
        ),
        "target_market": "College campuses and nearby low-income communities"
    }

    # Step 1: Idea Validator
    print("\n[1/7] Running Idea Validator...")
    val_out = await idea_validator.run(raw_idea)
    print(f"-> Validation Score: {val_out.get('validation_score')}/100")

    # Step 2: Patent & Prior Art Search
    print("\n[2/7] Running Patent Search...")
    pat_out = await patent_search.run({
        "idea_id": raw_idea["idea_id"],
        "idea_description": raw_idea["idea_description"],
        "keywords": ["food waste redistribution", "surplus food app", "campus food dispatch"]
    })
    print(f"-> Risk Level: {pat_out.get('risk_level')}")

    # Step 3: Market Research
    print("\n[3/7] Running Market Research...")
    mkt_out = await market_research.run({
        "idea_id": raw_idea["idea_id"],
        "idea_description": raw_idea["idea_description"],
        "target_market": raw_idea["target_market"],
        "region": "North America"
    })
    print(f"-> Market Size: {mkt_out.get('market_size_estimate')[:80]}...")

    # Step 4: Competitor Analysis
    print("\n[4/7] Running Competitor Analysis...")
    comp_out = await competitor_analysis.run({
        "idea_id": raw_idea["idea_id"],
        "idea_description": raw_idea["idea_description"],
        "market_research": mkt_out
    })
    print(f"-> Competitors Found: {len(comp_out.get('competitors', []))}")

    # Step 5: Business Model Generator
    print("\n[5/7] Running Business Model Generator...")
    bm_out = await business_model.run({
        "idea_id": raw_idea["idea_id"],
        "idea_description": raw_idea["idea_description"],
        "market_research": mkt_out,
        "competitor_analysis": comp_out
    })
    print(f"-> Value Proposition: {bm_out.get('value_proposition')[:80]}...")

    # Step 6: Pitch Deck Generator
    print("\n[6/7] Running Pitch Deck Generator...")
    pitch_out = await pitch_deck.run({
        "idea_id": raw_idea["idea_id"],
        "idea_validation": val_out,
        "market_research": mkt_out,
        "competitor_analysis": comp_out,
        "business_model": bm_out
    })
    print(f"-> Slides Generated: {len(pitch_out.get('slides', []))}")

    # Step 7: Investor Matching
    print("\n[7/7] Running Investor Matching...")
    inv_out = await investor_matching.run({
        "idea_id": raw_idea["idea_id"],
        "sector": "FoodTech & Campus Sustainability",
        "business_model": bm_out
    })
    print(f"-> Matched Investors: {len(inv_out.get('matched_investors', []))}")

    print("\n=== PIPELINE TEST COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
