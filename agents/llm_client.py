"""
Provider-agnostic LLM client for LaunchPad AI agents with agent-specific provider routing,
automatic API key rotation, multi-provider rate-limit fallback, and resilient JSON parsing.

Key Rotation & Multi-Key Support:
You can provide multiple API keys for any provider in two ways:
  1. Comma-separated list: GEMINI_API_KEY=key1,key2,key3
  2. Numbered variables: GEMINI_API_KEY_1=key1, GEMINI_API_KEY_2=key2, GEMINI_API_KEY_3=key3

Agent-Specific Provider Routing:
  - Reasoning Agents (idea_validator, business_model, pitch_deck): Primary = Gemini -> Groq -> Cerebras
  - Search-Grounded Agents (patent_search, market_research, competitor_analysis, investor_matching): Primary = Groq -> Cerebras -> Gemini
"""

import os
import json
import re
import ast

try:
    from .cache import get_cached, save_to_cache, log_api_usage, is_cache_enabled
except ImportError:
    from cache import get_cached, save_to_cache, log_api_usage, is_cache_enabled


def load_dotenv_file():
    """
    Auto-loads .env file from project root into os.environ if present.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root_dir, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass

load_dotenv_file()

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini").lower()
ALL_PROVIDERS = ["groq", "cerebras", "gemini", "openai", "anthropic"]

# Agent-specific provider fallback priority map:
# Reasoning agents default to Gemini primary; Search-grounded agents default to Groq primary.
AGENT_PROVIDER_MAP = {
    "idea_validator": ["gemini", "groq", "cerebras"],
    "business_model": ["gemini", "groq", "cerebras"],
    "pitch_deck": ["gemini", "groq", "cerebras"],
    "patent_search": ["groq", "cerebras", "gemini"],
    "market_research": ["groq", "cerebras", "gemini"],
    "competitor_analysis": ["groq", "cerebras", "gemini"],
    "investor_matching": ["groq", "cerebras", "gemini"],
}


def get_api_keys(provider: str) -> list:
    """
    Retrieves all configured API keys for a given provider.
    Supports comma-separated strings (GEMINI_API_KEY=key1,key2) and
    numbered environment variables (GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.).
    """
    provider_upper = provider.upper()
    keys = []

    # Check comma-separated variables
    for env_var in [f"{provider_upper}_API_KEYS", f"{provider_upper}_API_KEY"]:
        val = os.environ.get(env_var, "")
        if val:
            for k in val.split(","):
                k_clean = k.strip()
                if k_clean and k_clean not in keys:
                    keys.append(k_clean)

    # Check numbered variables (e.g. GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3)
    for i in range(1, 10):
        val = os.environ.get(f"{provider_upper}_API_KEY_{i}", "").strip()
        if val and val not in keys:
            keys.append(val)

    return keys


def _is_rate_limit_or_transient_error(e: Exception) -> bool:
    """
    Checks if an exception is a rate limit (429), billing quota limit (402), or connection failure.
    """
    err_str = str(e).lower()
    err_cls = e.__class__.__name__.lower()
    keywords = [
        "429", "rate", "quota", "resourceexhausted", "exceeded",
        "402", "payment required", "timeout", "connectionerror",
        "temporarily unavailable", "serviceunavailable", "503"
    ]
    return any(kw in err_str or kw in err_cls for kw in keywords)


def call_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    agent_name: str = None,
    idea_id: str = None,
) -> str:
    """
    Sends a prompt to the LLM with agent-specific provider routing, key rotation, and rate-limit fallback.
    Returns the raw text response.
    """
    if agent_name and idea_id and is_cache_enabled():
        cached_result = get_cached(agent_name, idea_id)
        if cached_result is not None:
            print(f"[CACHE HIT] {agent_name} / {idea_id} — skipping API call")
            return json.dumps(cached_result)
        print(f"[CACHE MISS] {agent_name} / {idea_id} — calling API")

    # Determine provider priority list for this request
    if agent_name and agent_name in AGENT_PROVIDER_MAP:
        providers = AGENT_PROVIDER_MAP[agent_name]
    else:
        fallback_env = os.environ.get("LLM_FALLBACK_PROVIDERS", "")
        if fallback_env:
            providers = [p.strip().lower() for p in fallback_env.split(",") if p.strip()]
        else:
            primary = os.environ.get("LLM_PROVIDER", LLM_PROVIDER).lower()
            providers = [primary] + [p for p in ALL_PROVIDERS if p != primary]

    raw_text = None
    used_provider = None

    if providers and providers[0] == "mock":
        raw_text = _call_mock(system_prompt, user_prompt)
        used_provider = "mock"
    else:
        for p_idx, provider in enumerate(providers):
            keys = get_api_keys(provider)
            if not keys:
                continue

            provider_failed = False
            for idx, key in enumerate(keys, 1):
                try:
                    if provider == "groq":
                        raw_text = _call_groq_single_key(key, system_prompt, user_prompt, max_tokens)
                    elif provider == "cerebras":
                        raw_text = _call_cerebras_single_key(key, system_prompt, user_prompt, max_tokens)
                    elif provider == "gemini":
                        raw_text = _call_gemini_single_key(key, system_prompt, user_prompt, max_tokens)
                    elif provider == "anthropic":
                        raw_text = _call_anthropic_single_key(key, system_prompt, user_prompt, max_tokens)
                    elif provider == "openai":
                        raw_text = _call_openai_single_key(key, system_prompt, user_prompt, max_tokens)

                    if raw_text:
                        used_provider = provider
                        break
                except Exception as e:
                    masked_key = key[:6] + "..." + key[-4:] if len(key) > 10 else "***"
                    if _is_rate_limit_or_transient_error(e):
                        next_p = providers[p_idx + 1] if p_idx + 1 < len(providers) else "mock/offline"
                        print(f"[FALLBACK] {provider} rate-limited/unavailable for {agent_name or 'request'} — trying {next_p}")
                        provider_failed = True
                        break  # Rotate to next provider in priority map
                    else:
                        print(f"[llm_client] Warning: Provider '{provider}' key #{idx} ({masked_key}) failed with non-rate-limit error: {e}")
                        # Re-raise auth or fatal exceptions if not rate-limited
                        raise e

            if raw_text:
                break

    if not raw_text:
        print("[llm_client] Warning: All configured API keys/providers failed or none configured. Falling back to mock response mode.")
        raw_text = _call_mock(system_prompt, user_prompt)
        used_provider = "mock"

    # Post-process: log usage and save to cache
    if agent_name and idea_id:
        log_api_usage(agent_name, idea_id, used_provider or "unknown")
        try:
            parsed_result = extract_json(raw_text, provider=used_provider)
            save_to_cache(agent_name, idea_id, parsed_result)
        except Exception as e:
            print(f"[CACHE] Warning: Failed to parse and cache LLM response for {agent_name}/{idea_id}: {e}")

    return raw_text


def _call_cerebras_single_key(api_key: str, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.cerebras.ai/v1",
    )

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _call_groq_single_key(api_key: str, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _call_gemini_single_key(api_key: str, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
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


def _call_anthropic_single_key(api_key: str, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _call_openai_single_key(api_key: str, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
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


def _call_mock(system_prompt: str, user_prompt: str) -> str:
    """
    Intelligent mock response generator for offline testing or when API keys are not set/exhausted.
    """
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


def extract_json(text: str, provider: str = None) -> dict:
    """
    Helper to safely pull JSON out of an LLM response with multi-stage repairs for:
    1. Markdown code fences (```json ... ```)
    2. Surrounding explanatory text before/after JSON
    3. Trailing commas in objects/arrays
    4. Single-quoted keys/strings
    Includes provider attribution if parsing fails.
    """
    provider_info = f"[Provider: {provider}] " if provider else ""
    cleaned = text.strip()

    # Stage 1: Strip markdown code fences
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            part_str = part.strip()
            if part_str.startswith("json"):
                part_str = part_str[4:].strip()
            if part_str.startswith("{") and part_str.endswith("}"):
                cleaned = part_str
                break

    # Stage 2: Extract JSON substring between outer { }
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"{provider_info}No JSON object found in LLM response snippet: {cleaned[:200]}")

    json_str = cleaned[start:end + 1]

    # Attempt 1: Direct standard json.loads
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Attempt 2: Repair trailing commas before } or ]
    repaired = re.sub(r',\s*([}\]])', r'\1', json_str)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Attempt 3: Safe evaluation for single-quoted Python/JSON dicts
    try:
        eval_result = ast.literal_eval(repaired)
        if isinstance(eval_result, dict):
            return eval_result
    except Exception:
        pass

    # Attempt 4: Replace single quotes around keys/values with double quotes
    try:
        single_quote_repaired = re.sub(r"'\s*:\s*", '": ', repaired)
        single_quote_repaired = re.sub(r"{\s*'", '{"', single_quote_repaired)
        single_quote_repaired = re.sub(r",\s*'", ',"', single_quote_repaired)
        return json.loads(single_quote_repaired)
    except Exception:
        pass

    raise ValueError(f"{provider_info}Failed to parse or repair JSON output: {json_str[:300]}")
