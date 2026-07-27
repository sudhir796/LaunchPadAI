"""
Provider-agnostic LLM client for LaunchPad AI agents.

Set LLM_PROVIDER in your environment to one of: "gemini", "anthropic", "openai", "mock"
Set the matching API key env var:
  - GEMINI_API_KEY
  - ANTHROPIC_API_KEY
  - OPENAI_API_KEY

Every agent should import `call_llm` from this file rather than calling
any provider's SDK directly. This means switching providers later only
requires changing the LLM_PROVIDER env var, not touching agent code.
"""

import os
import json

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini").lower()


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
    """
    Sends a prompt to the configured LLM provider and returns the raw text response.
    Agents are responsible for parsing the response (usually as JSON).
    """
    provider = os.environ.get("LLM_PROVIDER", LLM_PROVIDER).lower()
    
    if provider == "mock":
        return _call_mock(system_prompt, user_prompt)
    elif provider == "gemini":
        return _call_gemini(system_prompt, user_prompt, max_tokens)
    elif provider == "anthropic":
        return _call_anthropic(system_prompt, user_prompt, max_tokens)
    elif provider == "openai":
        return _call_openai(system_prompt, user_prompt, max_tokens)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def _call_gemini(system_prompt, user_prompt, max_tokens):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Fallback to mock if API key is not configured
        print("[llm_client] Warning: GEMINI_API_KEY not set. Using mock response mode.")
        return _call_mock(system_prompt, user_prompt)
        
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_prompt,
    )
    response = model.generate_content(
        user_prompt,
        generation_config={"max_output_tokens": max_tokens},
    )
    return response.text


def _call_anthropic(system_prompt, user_prompt, max_tokens):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[llm_client] Warning: ANTHROPIC_API_KEY not set. Using mock response mode.")
        return _call_mock(system_prompt, user_prompt)

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _call_openai(system_prompt, user_prompt, max_tokens):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[llm_client] Warning: OPENAI_API_KEY not set. Using mock response mode.")
        return _call_mock(system_prompt, user_prompt)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _call_mock(system_prompt, user_prompt):
    """
    Intelligent mock response generator for offline testing or when API keys are not set.
    """
    # Detect expected schema from system prompt or user prompt
    if "similar_patents" in system_prompt:
        return json.dumps({
            "idea_id": "test-001",
            "similar_patents": [
                {
                    "title": "Surplus Food Redistribution System and Method (US Patent 10,984,392)",
                    "summary": "Automated matching and dispatch system for connecting commercial kitchens with surplus food to local receivers.",
                    "source_url": "https://patents.google.com/patent/US10984392B2/en"
                },
                {
                    "title": "Dynamic Mobile Notification for Perishable Goods Distribution",
                    "summary": "Real-time geolocation-based push alert system for time-sensitive inventory dispatch.",
                    "source_url": "https://patents.google.com/patent/US20210042812A1/en"
                }
            ],
            "risk_level": "medium",
            "notes": "Prior art exists around real-time food dispatch algorithms. However, focusing on campus-specific micro-logistics and student authentication provides clear patentability and differentiation space."
        })
    elif "validation_score" in system_prompt:
        return json.dumps({
            "idea_id": "test-001",
            "validation_score": 85,
            "strengths": [
                "Strong social impact and sustainability focus",
                "Clear high-density target market in university campuses",
                "High availability of surplus food"
            ],
            "weaknesses": [
                "Logistical challenges with short food expiry windows",
                "Food safety liability concerns"
            ],
            "feasibility_notes": "Technically straightforward mobile app with geolocation and push notifications. Main barrier is operational partner onboarding.",
            "recommendation": "Proceed with pilot test at a single campus location with signed food safety liability waivers."
        })
    elif "market_size_estimate" in system_prompt:
        return json.dumps({
            "idea_id": "test-001",
            "market_size_estimate": "The global surplus food management and food waste reduction market was valued at $55.3 billion in 2023 and is projected to reach $92.6 billion by 2030, representing a TAM of over $90B globally.",
            "growth_trends": "Growing at a CAGR of 7.6% driven by ESG compliance mandates, rising food prices, and institutional sustainability initiatives across university campuses.",
            "target_demographics": "College students aged 18-25 seeking affordable meal options, university dining hall managers, and local community food redistribution shelters.",
            "sources": [
                "https://www.sciencedirect.com/science/article/pii/S1877050925026791",
                "https://www.toogoodtogo.com/en-us"
            ]
        })
    elif "differentiation_opportunities" in system_prompt:
        return json.dumps({
            "idea_id": "test-001",
            "competitors": [
                {
                    "name": "Too Good To Go",
                    "description": "Global marketplace connecting consumers with restaurants and bakeries for surplus surprise bags.",
                    "strengths": "Massive brand recognition, large user base, established vendor partnerships.",
                    "weaknesses": "Generic retail focus, lack of real-time university dining integration, no student financial aid meal plans.",
                    "source_url": "https://www.toogoodtogo.com/en-us"
                },
                {
                    "name": "Olio",
                    "description": "Peer-to-peer neighborhood sharing app for surplus food and household items.",
                    "strengths": "Community-driven hyper-local sharing model with zero cost options.",
                    "weaknesses": "Inconsistent availability, dependent on volunteer pickups, lacks institutional campus integration.",
                    "source_url": "https://olioapp.com/"
                }
            ],
            "differentiation_opportunities": "Focusing specifically on university dining halls and campus micro-logistics allows direct API integration with student ID card balances and automated end-of-day kitchen surplus dispatch, which generic commercial apps do not support."
        })
    elif "revenue_streams" in system_prompt:
        return json.dumps({
            "idea_id": "test-001",
            "revenue_streams": [
                "Micro-transaction commissions (10-15%) per discounted surplus meal sold to students",
                "SaaS subscription fee for university dining services providing analytics & ESG compliance reporting",
                "Sponsored sustainability partnerships with campus eco-organizations and brands"
            ],
            "cost_structure": [
                "Cloud infrastructure, API hosting, and real-time notification push services",
                "Mobile app maintenance, UI updates, and technical support",
                "Campus ambassador marketing, onboarding kits, and operational coordination"
            ],
            "value_proposition": "Empowers university canteens to monetize surplus meals while cutting campus food waste by up to 40% and offering students high-quality, ultra-affordable food options.",
            "customer_segments": [
                "University & College Dining Service Managers seeking waste reduction and ESG reporting",
                "Budget-conscious college students and university staff looking for discounted fresh meals",
                "Local community food pantries receiving subsidized surplus food donations"
            ],
            "channels": [
                "Direct B2B university dining administration sales & campus partnerships",
                "Student campus ambassador network & orientation week promotional events",
                "Push notifications, university student portal integrations, and social media campaigns"
            ]
        })
    elif "matched_investors" in system_prompt:
        return json.dumps({
            "idea_id": "test-001",
            "matched_investors": [
                {
                    "name": "S2G Ventures",
                    "focus_area": "FoodTech, AgriTech & Sustainable Supply Chain",
                    "reason": "Active seed/series A investor specializing in food waste reduction platforms, sustainable agriculture, and circular economy startups."
                },
                {
                    "name": "Closed Loop Partners",
                    "focus_area": "Circular Economy & Resource Efficiency",
                    "reason": "Impact venture firm funding solutions that reduce municipal and institutional food waste with strong ESG returns."
                },
                {
                    "name": "Better Food Ventures",
                    "focus_area": "Food Tech & Food Service Innovation",
                    "reason": "Focuses specifically on technology platforms transforming food service operations, institutional catering, and surplus management."
                }
            ]
        })
    elif "slides" in system_prompt:
        return json.dumps({
            "idea_id": "test-001",
            "slides": [
                {
                    "title": "Title & Executive Summary",
                    "content": "Campus Food Waste Redistribution App — Transforming university food surplus into affordable student meals and zero campus waste."
                },
                {
                    "title": "The Problem",
                    "content": "Over 35% of cooked food in university canteens is discarded daily due to inefficient demand forecasting, while 30%+ of college students experience food insecurity."
                },
                {
                    "title": "The Solution",
                    "content": "A real-time hyper-local marketplace app connecting university dining halls with surplus meals directly to students at 50-70% discount during end-of-day flash sales."
                },
                {
                    "title": "Market Opportunity",
                    "content": "Global food surplus management TAM is $55.3B growing at 7.6% CAGR. Target SAM: 4,000+ higher education institutions in North America."
                },
                {
                    "title": "Competitive Advantage",
                    "content": "Direct API integration with campus student ID card systems and university dining services, enabling automated operational dispatch impossible for generic commercial apps."
                },
                {
                    "title": "Business Model & Monetization",
                    "content": "10-15% micro-commission per meal order plus SaaS subscription tier for university dining services providing ESG compliance & sustainability reporting."
                },
                {
                    "title": "Go-to-Market & Execution",
                    "content": "Launch pilot with 3 major university campuses via student ambassador networks and orientation week campaigns, scaling to 50 campuses in Year 1."
                }
            ]
        })
    else:
        return json.dumps({
            "status": "success",
            "message": "Mock response generated for offline testing."
        })


def extract_json(text: str) -> dict:
    """
    Helper to safely pull JSON out of an LLM response, even if the model
    wraps it in markdown code fences or adds stray text around it.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in LLM response: {text[:200]}")
    return json.loads(text[start:end + 1])
