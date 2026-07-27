import urllib.request
import urllib.parse
import ssl
import re
import json
import html

def perform_web_search(query: str, max_results: int = 5) -> list:
    """
    Performs a real web search for the query and returns a list of results:
    [{"title": str, "snippet": str, "url": str}]
    """
    # 1. Try DuckDuckGo HTML search
    results = _search_duckduckgo(query, max_results)
    if results:
        return results

    # 2. Fallback: DDG Lite
    return _search_duckduckgo_lite(query, max_results)


def _search_duckduckgo(query: str, max_results: int = 5) -> list:
    ctx = ssl._create_unverified_context()
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            raw_html = resp.read().decode("utf-8", errors="ignore")
            results = []

            # Extract result blocks
            # Look for result__body or individual result blocks
            matches = re.findall(
                r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?(?:<a[^>]*class="result__snippet"[^>]*>(.*?)</a>|<td[^>]*class="result-snippet"[^>]*>(.*?)</td>)',
                raw_html,
                re.DOTALL
            )
            
            if not matches:
                # Separate extraction fallback
                titles_urls = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', raw_html, re.DOTALL)
                snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', raw_html, re.DOTALL)
                
                for i in range(min(len(titles_urls), max_results)):
                    raw_url, raw_title = titles_urls[i]
                    raw_snippet = snippets[i] if i < len(snippets) else ""
                    
                    results.append({
                        "title": _clean_html_text(raw_title),
                        "snippet": _clean_html_text(raw_snippet),
                        "url": _clean_ddg_url(raw_url)
                    })
            else:
                for match in matches[:max_results]:
                    raw_url, raw_title, snip1, snip2 = match
                    raw_snippet = snip1 or snip2 or ""
                    results.append({
                        "title": _clean_html_text(raw_title),
                        "snippet": _clean_html_text(raw_snippet),
                        "url": _clean_ddg_url(raw_url)
                    })
                        
            return results[:max_results]
    except Exception as e:
        print(f"[Search Debug] DDG HTML search error: {e}")
        return []


def _search_duckduckgo_lite(query: str, max_results: int = 5) -> list:
    ctx = ssl._create_unverified_context()
    url = "https://lite.duckduckgo.com/lite/"
    data = urllib.parse.urlencode({"q": query}).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            raw_html = resp.read().decode("utf-8", errors="ignore")
            results = []
            links = re.findall(r'<a[^>]*class="result-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', raw_html, re.DOTALL)
            snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', raw_html, re.DOTALL)
            
            for i in range(min(len(links), max_results)):
                raw_url, raw_title = links[i]
                raw_snippet = snippets[i] if i < len(snippets) else ""
                results.append({
                    "title": _clean_html_text(raw_title),
                    "snippet": _clean_html_text(raw_snippet),
                    "url": _clean_ddg_url(raw_url)
                })
            return results[:max_results]
    except Exception as e:
        print(f"[Search Debug] DDG Lite search error: {e}")
        return []


def _clean_ddg_url(url: str) -> str:
    url = html.unescape(url)
    if "uddg=" in url:
        match = re.search(r'uddg=([^&]+)', url)
        if match:
            return urllib.parse.unquote(match.group(1))
    return url


def _clean_html_text(raw_html: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


if __name__ == "__main__":
    res = perform_web_search("patent food waste redistribution app", max_results=3)
    print(json.dumps(res, indent=2))
