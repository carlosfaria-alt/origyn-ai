import os
from typing import Optional
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

TABLE = "agent_results"


def _headers() -> dict:
    key = os.environ.get("SUPABASE_KEY", "")
    if not key:
        raise RuntimeError("SUPABASE_KEY is not set.")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _base_url() -> str:
    url = os.environ.get("SUPABASE_URL", "")
    if not url:
        raise RuntimeError("SUPABASE_URL is not set.")
    return f"{url.rstrip('/')}/rest/v1/{TABLE}"


def save_result(agent_name: str, prompt: str, result: str, metadata: Optional[dict] = None) -> dict:
    """Insert an agent result into the agent_results table."""
    row = {
        "agent_name": agent_name,
        "prompt": prompt,
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    response = httpx.post(
        _base_url(),
        headers={**_headers(), "Prefer": "return=representation"},
        json=row,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data[0] if data else row


def fetch_results(agent: Optional[str] = None, limit: int = 50) -> list:
    """Fetch agent results, optionally filtered by agent name."""
    params: dict = {"order": "created_at.desc", "limit": str(limit)}
    if agent:
        params["agent_name"] = f"eq.{agent}"
    response = httpx.get(
        _base_url(),
        headers={**_headers(), "Prefer": "return=representation"},
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
