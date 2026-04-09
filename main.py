"""
ORIGYN Global AI Agency — Backend API
"""
from contextlib import asynccontextmanager

from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from agents import run_copy, run_creatives, run_video, run_hooks, run_researcher
from database import save_result, fetch_results
from scheduler import create_scheduler

load_dotenv()


# ---------------------------------------------------------------------------
# Lifespan: start/stop the scheduler alongside the app
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    print("[origyn] Scheduler started — daily tasks at 08:00 UTC.")
    yield
    scheduler.shutdown(wait=False)
    print("[origyn] Scheduler stopped.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ORIGYN Global AI Agency API",
    description="AI agent endpoints for copy, creatives, video, hooks, and research.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str


class AgentResponse(BaseModel):
    agent: str
    prompt: str
    result: str
    saved: bool


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _handle_agent(agent_name: str, agent_fn, request: AgentRequest) -> AgentResponse:
    try:
        result = agent_fn(request.prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc

    try:
        save_result(agent_name=agent_name, prompt=request.prompt, result=result)
        saved = True
    except Exception as exc:
        print(f"[origyn] Warning: could not save result to Supabase — {exc}")
        saved = False

    return AgentResponse(agent=agent_name, prompt=request.prompt, result=result, saved=saved)


# ---------------------------------------------------------------------------
# Agent endpoints
# ---------------------------------------------------------------------------

@app.post("/agents/copy", response_model=AgentResponse, tags=["Agents"])
def agent_copy(request: AgentRequest):
    """Generate high-converting sales copy."""
    return _handle_agent("copy", run_copy, request)


@app.post("/agents/creatives", response_model=AgentResponse, tags=["Agents"])
def agent_creatives(request: AgentRequest):
    """Generate ad creative briefs and visual concepts."""
    return _handle_agent("creatives", run_creatives, request)


@app.post("/agents/video", response_model=AgentResponse, tags=["Agents"])
def agent_video(request: AgentRequest):
    """Generate short-form video scripts (Reels, TikTok, Shorts)."""
    return _handle_agent("video", run_video, request)


@app.post("/agents/hooks", response_model=AgentResponse, tags=["Agents"])
def agent_hooks(request: AgentRequest):
    """Generate 10 viral scroll-stopping hooks."""
    return _handle_agent("hooks", run_hooks, request)


@app.post("/agents/researcher", response_model=AgentResponse, tags=["Agents"])
def agent_researcher(request: AgentRequest):
    """Run strategic market research and audience analysis."""
    return _handle_agent("researcher", run_researcher, request)


# ---------------------------------------------------------------------------
# Results endpoint
# ---------------------------------------------------------------------------

@app.get("/results", tags=["Results"])
def get_results(
    agent: Optional[str] = Query(default=None, description="Filter by agent name"),
    limit: int = Query(default=50, ge=1, le=200, description="Max results to return"),
):
    """Fetch stored agent results from Supabase."""
    try:
        data = fetch_results(agent=agent, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Database error: {exc}") from exc
    return {"count": len(data), "results": data}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "ORIGYN Global AI Agency API"}
