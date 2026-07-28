"""
Local disk caching and API usage logging layer for LaunchPad AI agents.
"""

import os
import json
import datetime
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent / ".cache"


def is_cache_enabled() -> bool:
    """
    Checks if caching is enabled via the CACHE_ENABLED environment variable.
    Defaults to True unless set to 'false', '0', or 'no'.
    """
    val = os.environ.get("CACHE_ENABLED", "true").strip().lower()
    return val not in ("false", "0", "no", "off")


def get_cache_path(agent_name: str, idea_id: str) -> Path:
    """
    Returns the file path for a given agent and idea_id cache entry.
    """
    # Sanitize agent_name and idea_id for safe filenames
    safe_agent = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in agent_name)
    safe_idea = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in idea_id)
    return CACHE_DIR / f"{safe_agent}_{safe_idea}.json"


def get_cached(agent_name: str, idea_id: str) -> dict | None:
    """
    Looks up a cached result on disk under agents/.cache/{agent_name}_{idea_id}.json.
    Returns the parsed dict if it exists and is valid, otherwise None.
    """
    if not is_cache_enabled():
        return None

    cache_file = get_cache_path(agent_name, idea_id)
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[CACHE] Warning: Failed to read cache file {cache_file}: {e}")
            return None
    return None


def save_to_cache(agent_name: str, idea_id: str, result: dict) -> None:
    """
    Saves the result dict as JSON under agents/.cache/{agent_name}_{idea_id}.json.
    """
    if not is_cache_enabled():
        return

    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = get_cache_path(agent_name, idea_id)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"[CACHE] Warning: Failed to save to cache file for {agent_name}/{idea_id}: {e}")


def log_api_usage(agent_name: str, idea_id: str, provider: str) -> None:
    """
    Appends a timestamped log line to agents/.cache/usage_log.txt every time a real API call is made.
    """
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        log_file = CACHE_DIR / "usage_log.txt"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] PROVIDER: {provider} | AGENT: {agent_name} | IDEA_ID: {idea_id}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[CACHE] Warning: Failed to write to usage log: {e}")
