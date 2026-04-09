import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client: Optional[Client] = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            raise RuntimeError("Supabase is not configured (SUPABASE_URL / SUPABASE_KEY are empty).")
        _client = create_client(url, key)
    return _client


def save_result(agent: str, prompt: str, result: str, metadata: Optional[dict] = None) -> dict:
    """Insert an agent result into the `agent_results` table."""
    client = get_client()
    row = {
        "agent": agent,
        "prompt": prompt,
        "result": result,
        "metadata": metadata or {},
        "created_at": datetime.utcnow().isoformat(),
    }
    response = client.table("agent_results").insert(row).execute()
    return response.data[0] if response.data else row


def fetch_results(agent: Optional[str] = None, limit: int = 50) -> list:
    """Fetch agent results, optionally filtered by agent name."""
    client = get_client()
    query = client.table("agent_results").select("*").order("created_at", desc=True).limit(limit)
    if agent:
        query = query.eq("agent", agent)
    response = query.execute()
    return response.data or []
