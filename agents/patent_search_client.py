"""
USPTO PatentsView API Client for Patent & Prior Art Search
Queries POST https://api.patentsview.org/patents/query to fetch granted US patents.
"""

import json
import re
import ssl
import urllib.request
import urllib.parse

PATENTSVIEW_API_URL = "https://api.patentsview.org/patents/query"

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our", "ours",
    "ourselves", "out", "over", "own", "same", "she", "should", "so", "some",
    "such", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where",
    "which", "while", "who", "whom", "why", "with", "would", "you", "your",
    "yours", "yourself", "yourselves", "app", "application", "system", "platform",
    "using", "used", "users", "user", "real-time", "based", "solution", "service"
}


def extract_search_keywords(idea_description: str, keywords: list = None) -> str:
    """
    Extracts concise, meaningful key terms from input keywords or idea description.
    Returns a space-separated string of 2-4 key words suited for API search.
    """
    if keywords and isinstance(keywords, list):
        valid_kw = [str(k).strip() for k in keywords if str(k).strip()]
        if valid_kw:
            # Take top key terms from the provided list
            combined = " ".join(valid_kw[:3])
            words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', combined)]
            filtered = [w for w in words if w not in STOP_WORDS]
            if filtered:
                # Deduplicate preserving order
                seen = set()
                dedup = [w for w in filtered if not (w in seen or seen.add(w))]
                return " ".join(dedup[:4])

    # Fallback to extracting from idea_description
    words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', idea_description)]
    filtered = [w for w in words if w not in STOP_WORDS]
    seen = set()
    dedup = [w for w in filtered if not (w in seen or seen.add(w))]
    
    if not dedup:
        return "patent"
        
    return " ".join(dedup[:4])


def trim_abstract(abstract: str, max_sentences: int = 2) -> str:
    """
    Trims a patent abstract to at most 1-2 sentences.
    """
    if not abstract:
        return ""
    
    sentences = re.split(r'(?<=[.!?])\s+', abstract.strip())
    trimmed = " ".join(sentences[:max_sentences]).strip()
    if len(trimmed) > 300:
        trimmed = trimmed[:297] + "..."
    return trimmed


try:
    from .search_utils import perform_web_search
except ImportError:
    from search_utils import perform_web_search


def query_patentsview(idea_description: str, keywords: list = None, per_page: int = 5) -> list:
    """
    Queries the USPTO PatentsView API (POST https://api.patentsview.org/patents/query)
    or fails over to Google Patents Search for real granted US/international patents.

    Returns a list of mapped patent dictionaries:
    [
      {
        "title": "<patent_title>",
        "summary": "<trimmed 1-2 sentence abstract>",
        "source_url": "https://patents.google.com/patent/<patent_number>"
      }
    ]
    """
    search_terms = extract_search_keywords(idea_description, keywords)
    print(f"[Patent Search] Querying USPTO / PatentsView API with terms: '{search_terms}'")

    payload = {
        "q": {
            "_text_any": {
                "patent_abstract": search_terms
            }
        },
        "f": [
            "patent_number",
            "patent_title",
            "patent_date",
            "assignee_organization",
            "patent_abstract"
        ],
        "o": {
            "per_page": per_page
        },
        "s": [
            {"patent_date": "desc"}
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LaunchPadAI/1.0"
    }

    mapped_patents = []

    try:
        data_bytes = json.dumps(payload).encode("utf-8")
        ctx = ssl._create_unverified_context()

        req = urllib.request.Request(
            PATENTSVIEW_API_URL,
            data=data_bytes,
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            raw_body = response.read().decode("utf-8", errors="ignore")
            
            # If PatentsView returns valid JSON
            if response.status == 200 and not raw_body.strip().startswith("<"):
                resp_json = json.loads(raw_body)
                raw_patents = resp_json.get("patents")
                
                if isinstance(raw_patents, list) and len(raw_patents) > 0:
                    for item in raw_patents:
                        p_num = str(item.get("patent_number") or item.get("patent_id") or "").strip()
                        p_title = item.get("patent_title") or "Untitled Patent"
                        p_abstract = item.get("patent_abstract") or ""
                        
                        summary = trim_abstract(p_abstract, max_sentences=2)
                        source_url = f"https://patents.google.com/patent/{p_num}" if p_num else "https://patents.google.com"

                        mapped_patents.append({
                            "title": p_title,
                            "summary": summary,
                            "source_url": source_url
                        })
                    print(f"[Patent Search] Retrieved {len(mapped_patents)} patents from PatentsView API.")
                    return mapped_patents
            else:
                print("[Patent Search] PatentsView API returned HTML redirect / transition page. Falling back to Google Patents Search...")
    except Exception as e:
        print(f"[Patent Search] PatentsView API request error ({e}). Falling back to Google Patents Search...")

    # Fallback: Perform targeted Google Patents web search
    try:
        gpatent_query = f"site:patents.google.com {search_terms}"
        print(f"[Patent Search] Executing Google Patents Search: '{gpatent_query}'")
        web_results = perform_web_search(gpatent_query, max_results=per_page)
        
        if web_results:
            for item in web_results:
                raw_title = item.get("title", "Patent Document")
                clean_title = re.sub(r'\s*-\s*Google Patents\s*$', '', raw_title, flags=re.IGNORECASE).strip()
                snippet = item.get("snippet", "")
                summary = trim_abstract(snippet, max_sentences=2)
                url = item.get("url", "https://patents.google.com")

                mapped_patents.append({
                    "title": clean_title,
                    "summary": summary if summary else "Prior art patent record indexed on Google Patents.",
                    "source_url": url
                })
            print(f"[Patent Search] Successfully retrieved {len(mapped_patents)} real prior art patents via Google Patents.")
            return mapped_patents
    except Exception as fallback_err:
        print(f"[Patent Search] Google Patents fallback search error: {fallback_err}")

    return []

