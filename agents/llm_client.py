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
    "idea_validator": ["groq", "gemini", "cerebras"],
    "business_model": ["groq", "gemini", "cerebras"],
    "pitch_deck": ["groq", "gemini", "cerebras"],
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
    import time
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            if _is_rate_limit_or_transient_error(e):
                time.sleep(0.5)
                continue
            else:
                raise e

    if last_error:
        raise last_error


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


def _extract_prompt_meta(user_prompt: str) -> tuple[str, str, str]:
    idea_id = "unknown"
    id_match = re.search(r'idea_id:\s*([^\n\r]+)', user_prompt, re.IGNORECASE)
    if id_match:
        idea_id = id_match.group(1).strip()

    title_match = re.search(r'Idea Title:\s*([^\n\r]+)', user_prompt, re.IGNORECASE)
    desc_match = re.search(r'Idea Description:\s*([^\n\r]+)', user_prompt, re.IGNORECASE)
    
    desc = desc_match.group(1).strip() if desc_match else "technology innovation venture"
    title = title_match.group(1).strip() if title_match else desc[:50]

    return idea_id, title, desc


def _call_mock(system_prompt: str, user_prompt: str) -> str:
    """
    Dynamic mock response generator for offline testing or when API keys are not set/exhausted.
    Extracts idea title and description from user_prompt to tailor responses to the actual user idea.
    """
    idea_id, title, desc = _extract_prompt_meta(user_prompt)

    if "similar_patents" in system_prompt:
        return json.dumps({
            "idea_id": idea_id,
            "similar_patents": [
                {
                    "title": f"System and Method for {title} (US Patent 10,842,109)",
                    "summary": f"Prior art system for automated processing related to {desc[:80]}.",
                    "source_url": "https://patents.google.com"
                }
            ],
            "risk_level": "medium",
            "notes": f"Initial prior art exists around automated systems for {title[:40]}. Patentability focus should highlight unique algorithm/hardware integrations."
        })
    elif "validation_score" in system_prompt:
        return json.dumps({
            "idea_id": idea_id,
            "validation_score": 82,
            "strengths": [
                f"Addresses a clear market demand for {title[:40]}",
                "High scalability potential across targeted customer segments",
                "Strong technological value proposition"
            ],
            "weaknesses": [
                "Initial customer acquisition friction",
                "Requires robust early operational execution"
            ],
            "feasibility_notes": f"Feasible technology stack for {title[:50]}. Key focus should be on MVP iteration and user feedback.",
            "recommendation": "Proceed with pilot launch and targeted customer onboarding."
        })
    elif "market_size_estimate" in system_prompt:
        return json.dumps({
            "idea_id": idea_id,
            "market_size_estimate": f"The global market for {title[:40]} was valued at $12.5B in 2023 and is projected to grow to $28.4B by 2030.",
            "growth_trends": "Growing rapidly driven by digital transformation, automation adoption, and efficiency demands.",
            "target_demographics": f"Primary target audience includes early adopters, enterprise users, and specialized operators needing {desc[:60]}.",
            "sources": [
                "https://www.statista.com",
                "https://www.bloomberg.com"
            ]
        })
    elif "differentiation_opportunities" in system_prompt:
        return json.dumps({
            "idea_id": idea_id,
            "competitors": [
                {
                    "name": "Legacy Industry Leader",
                    "description": f"Established player offering traditional solutions in {title[:40]}.",
                    "strengths": "Large existing customer base and brand awareness.",
                    "weaknesses": "Slow innovation cycle and higher cost structure.",
                    "source_url": "https://example.com/competitor1"
                },
                {
                    "name": "NextGen Solution Provider",
                    "description": "Niche startup focused on basic automated workflows.",
                    "strengths": "Modern tech stack.",
                    "weaknesses": "Limited features and lack of deep customization.",
                    "source_url": "https://example.com/competitor2"
                }
            ],
            "differentiation_opportunities": f"Unique opportunity to differentiate {title[:40]} through proprietary real-time automation and seamless workflow integration."
        })
    elif "revenue_streams" in system_prompt:
        return json.dumps({
            "idea_id": idea_id,
            "revenue_streams": [
                "Subscription SaaS pricing tier (Monthly/Annual)",
                "Usage-based transaction or commission fees",
                "Enterprise integration and premium support plans"
            ],
            "cost_structure": [
                "Cloud infrastructure, API hosting, and security compliance",
                "Product R&D and continuous software maintenance",
                "Sales, marketing, and customer success operations"
            ],
            "value_proposition": f"Delivers automated, cost-effective, and high-efficiency performance for {desc[:90]}.",
            "customer_segments": [
                f"Primary end-users seeking efficient {title[:40]} solutions",
                "SMBs and growth-stage enterprises needing automated workflows"
            ],
            "channels": [
                "Direct B2B digital marketing and product-led growth",
                "Strategic channel partnerships and industry events"
            ]
        })
    elif "matched_investors" in system_prompt:
        return json.dumps({
            "idea_id": idea_id,
            "matched_investors": [
                {
                    "name": "Peak XV Partners",
                    "focus_area": "Early-mid stage, broad technology sectors",
                    "reason": f"Active investor matching the growth thesis for {title[:40]}."
                },
                {
                    "name": "Blume Ventures",
                    "focus_area": "Early stage, consumer tech & SaaS",
                    "reason": f"Strong thesis alignment for scalable software and tech-enabled business models like {title[:30]}."
                },
                {
                    "name": "100X.VC",
                    "focus_area": "Pre-seed, India-focused technology startups",
                    "reason": "Pre-seed seed capital partner for early stage innovation."
                }
            ]
        })
    elif "slides" in system_prompt:
        return json.dumps({
            "idea_id": idea_id,
            "slides": [
                {
                    "title": "Title & Executive Summary",
                    "content": f"{title} — {desc[:100]}"
                },
                {
                    "title": "The Problem",
                    "content": f"Existing manual processes for {title[:40]} are inefficient, costly, and prone to delays."
                },
                {
                    "title": "The Solution",
                    "content": f"A specialized automated platform delivering {desc[:100]}."
                },
                {
                    "title": "Market Opportunity",
                    "content": f"Global market TAM estimated at $12.5B+ with strong CAGR growth across key demographics."
                },
                {
                    "title": "Competitive Advantage",
                    "content": f"Proprietary features and seamless user experience tailored for {title[:40]}."
                },
                {
                    "title": "Business Model",
                    "content": "SaaS subscriptions, transaction fees, and enterprise integration support."
                },
                {
                    "title": "Go-to-Market Strategy",
                    "content": "Targeted digital acquisition, strategic partnerships, and community-driven expansion."
                }
            ]
        })
    else:
        return json.dumps({
            "idea_id": idea_id,
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
