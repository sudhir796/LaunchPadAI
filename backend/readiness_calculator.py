"""
Investor Readiness Score Calculator
Computes a 0-100 investor readiness score and 1-5 star rating from pipeline agent outputs.
"""

def calculate_investor_readiness_score(outputs: dict) -> dict:
    """
    Calculates investor_readiness_score (0-100) and star_rating (1-5) using:
    - 40% weight: idea_validator.validation_score
    - 20% weight: inverse of patent risk_level (low=100, medium=60, high=20)
    - 20% weight: market_research depth & quality
    - 20% weight: investor_matching matches count
    """
    # 1. Idea Validation Score (40% weight)
    val_output = outputs.get("idea_validator") or outputs.get("agent1") or {}
    raw_val_score = val_output.get("validation_score", 70)
    try:
        val_score = float(raw_val_score)
    except (ValueError, TypeError):
        val_score = 70.0
    val_score = max(0.0, min(100.0, val_score))
    c1 = val_score * 0.40

    # 2. Patent Risk Level Inverse (20% weight)
    pat_output = outputs.get("patent_search") or outputs.get("agent2") or {}
    raw_risk = str(pat_output.get("risk_level", "medium")).lower()
    if "low" in raw_risk:
        pat_score = 100.0
    elif "high" in raw_risk:
        pat_score = 20.0
    else:  # medium or default
        pat_score = 60.0
    c2 = pat_score * 0.20

    # 3. Market Research Quality (20% weight)
    mkt_output = outputs.get("market_research") or outputs.get("agent3") or {}
    mkt_size = str(mkt_output.get("market_size_estimate", "")).strip()
    growth = str(mkt_output.get("growth_trends", "")).strip()
    sources = mkt_output.get("sources", [])
    
    mkt_score = 40.0  # Base
    if mkt_size and len(mkt_size) > 10:
        mkt_score += 35.0
    if growth:
        mkt_score += 15.0
    if sources and isinstance(sources, list) and len(sources) > 0:
        mkt_score += 10.0
    mkt_score = min(100.0, mkt_score)
    c3 = mkt_score * 0.20

    # 4. Investor Matching Count/Quality (20% weight)
    inv_output = outputs.get("investor_matching") or outputs.get("agent7") or {}
    matched = inv_output.get("matched_investors", [])
    match_count = len(matched) if isinstance(matched, list) else 0

    if match_count >= 3:
        inv_score = 100.0
    elif match_count == 2:
        inv_score = 80.0
    elif match_count == 1:
        inv_score = 60.0
    else:
        inv_score = 40.0
    c4 = inv_score * 0.20

    # Total Score Calculation (0 - 100)
    total_score = round(c1 + c2 + c3 + c4, 1)
    total_score = max(0.0, min(100.0, total_score))

    # Star Rating (1 - 5 stars)
    if total_score >= 80.0:
        stars = 5
    elif total_score >= 65.0:
        stars = 4
    elif total_score >= 50.0:
        stars = 3
    elif total_score >= 35.0:
        stars = 2
    else:
        stars = 1

    return {
        "investor_readiness_score": total_score,
        "star_rating": stars
    }
