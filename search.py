"""
Web search helpers for the researcher-stores agent.

Priority order:
  1. SerpAPI  (set SERPAPI_KEY)
  2. Brave Search API  (set BRAVE_API_KEY)
  3. No key → returns [] and the agent falls back to Claude's knowledge
"""
import os
import httpx

_TIMEOUT = 15


def _serpapi(query: str) -> list[dict]:
    key = os.environ.get("SERPAPI_KEY", "")
    if not key:
        return []
    try:
        r = httpx.get(
            "https://serpapi.com/search",
            params={"api_key": key, "q": query, "engine": "google",
                    "num": 6, "gl": "br", "hl": "pt"},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        items = r.json().get("organic_results", [])
        return [{"title": i.get("title", ""), "snippet": i.get("snippet", ""),
                 "link": i.get("link", "")} for i in items[:6]]
    except Exception:
        return []


def _brave(query: str) -> list[dict]:
    key = os.environ.get("BRAVE_API_KEY", "")
    if not key:
        return []
    try:
        r = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": key},
            params={"q": query, "count": 6},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        items = r.json().get("web", {}).get("results", [])
        return [{"title": i.get("title", ""), "snippet": i.get("description", ""),
                 "link": i.get("url", "")} for i in items[:6]]
    except Exception:
        return []


def web_search(query: str) -> list[dict]:
    """Try SerpAPI → Brave → empty list."""
    return _serpapi(query) or _brave(query)


def search_store_intelligence(niche_hint: str) -> str:
    """
    Run 4 targeted queries and return a single formatted context block
    ready to be injected into the Claude prompt. Returns empty string
    if no search key is configured.
    """
    queries = [
        f"melhores lojas shopify {niche_hint} brasil 2025 receita",
        f"nicho {niche_hint} e-commerce brasil lucrativo trending 2025",
        f"produtos mais vendidos shopify {niche_hint} alta conversão",
        f"dropshipping {niche_hint} brasil anúncio facebook ads 2025",
    ]

    all_results: list[dict] = []
    for q in queries:
        all_results.extend(web_search(q))

    if not all_results:
        return ""

    # Deduplicate by link
    seen: set[str] = set()
    unique = []
    for r in all_results:
        if r["link"] not in seen:
            seen.add(r["link"])
            unique.append(r)

    lines = []
    for r in unique[:16]:
        lines.append(f"• {r['title']}\n  {r['snippet']}\n  {r['link']}")

    return "\n\n".join(lines)
