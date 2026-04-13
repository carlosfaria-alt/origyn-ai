"""
ORIGYN Global AI Agency — Backend API
"""
from contextlib import asynccontextmanager

from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict

from dashboard import DASHBOARD_HTML

from agents import (
    run_copy, run_creatives, run_video, run_hooks, run_researcher,
    run_researcher_stores, run_seo, run_email, run_sales,
    run_image, run_video_real, run_clone, check_video_status,
    route_command, AGENT_REGISTRY,
)
from database import save_result, fetch_results
from scheduler import create_scheduler, _run_all_agents_and_email

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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


class AuthRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    email: str
    name: str


# ---------------------------------------------------------------------------
# Hardcoded user store (extend via env or DB as needed)
# ---------------------------------------------------------------------------

_USERS: dict = {
    "admin@origyn.com": {"password": "origyn2024", "name": "Carlos"},
}


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


@app.post("/agents/researcher-stores", response_model=AgentResponse, tags=["Agents"])
def agent_researcher_stores(request: AgentRequest):
    """Discover and validate 5 high-revenue Shopify store opportunities in Brazil.
    Optionally enriched with real-time web search if SERPAPI_KEY or BRAVE_API_KEY is set."""
    return _handle_agent("researcher-stores", run_researcher_stores, request)


@app.post("/agents/seo", response_model=AgentResponse, tags=["Agents"])
def agent_seo(request: AgentRequest):
    """Rafael — SEO strategy: keywords, on-page, content calendar, link building."""
    return _handle_agent("seo", run_seo, request)


@app.post("/agents/email-marketing", response_model=AgentResponse, tags=["Agents"])
def agent_email(request: AgentRequest):
    """Camila — Email marketing: sequences, subject lines, segmentation, automation."""
    return _handle_agent("email-marketing", run_email, request)


@app.post("/agents/sales", response_model=AgentResponse, tags=["Agents"])
def agent_sales(request: AgentRequest):
    """Diego — Sales strategy: funnel analysis, objections, pricing, closing scripts."""
    return _handle_agent("sales", run_sales, request)


@app.post("/agents/image", response_model=AgentResponse, tags=["Agents"])
def agent_image(request: AgentRequest):
    """Generate real images with DALL-E 3."""
    return _handle_agent("image", run_image, request)


@app.post("/agents/video-real", response_model=AgentResponse, tags=["Agents"])
def agent_video_real(request: AgentRequest):
    """Generate real video with HeyGen avatar."""
    return _handle_agent("video-real", run_video_real, request)


@app.get("/agents/video-status", tags=["Agents"])
def agent_video_status(video_id: str = Query(..., description="HeyGen video ID")):
    """Check HeyGen video rendering status."""
    result = check_video_status(video_id)
    return {"video_id": video_id, "result": result}


@app.post("/agents/clone", response_model=AgentResponse, tags=["Agents"])
def agent_clone(request: AgentRequest):
    """Clone and optimize a landing page / Shopify store page."""
    return _handle_agent("clone", run_clone, request)


# ---------------------------------------------------------------------------
# Intelligent command router
# ---------------------------------------------------------------------------

class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    message: str


class CommandResponse(BaseModel):
    detected_agent: str
    prompt: str
    result: str
    saved: bool


@app.post("/command", response_model=CommandResponse, tags=["Router"])
def smart_command(request: CommandRequest):
    """Receive any message in Portuguese, detect intent, route to correct agent."""
    routing = route_command(request.message)
    agent_name = routing["agent"]

    agent_fn = AGENT_REGISTRY.get(agent_name)
    if not agent_fn:
        raise HTTPException(status_code=400, detail=f"Agente '{agent_name}' não encontrado.")

    try:
        result = agent_fn(request.message)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erro no agente {agent_name}: {exc}") from exc

    try:
        save_result(agent_name=agent_name, prompt=request.message, result=result)
        saved = True
    except Exception:
        saved = False

    return CommandResponse(
        detected_agent=agent_name,
        prompt=request.message,
        result=result,
        saved=saved,
    )


# ---------------------------------------------------------------------------
# WhatsApp webhook (Twilio)
# ---------------------------------------------------------------------------

@app.post("/webhook/whatsapp", tags=["WhatsApp"])
async def whatsapp_webhook(request: Request):
    """Receive WhatsApp messages via Twilio and respond using the intelligent router."""
    import os
    try:
        form = await request.form()
        incoming_msg = form.get("Body", "").strip()
        sender = form.get("From", "")

        if not incoming_msg:
            return {"status": "no message"}

        # Route to correct agent
        routing = route_command(incoming_msg)
        agent_name = routing["agent"]
        agent_fn = AGENT_REGISTRY.get(agent_name, AGENT_REGISTRY["copy"])

        # Execute agent
        result = agent_fn(incoming_msg)

        # Save to database
        try:
            save_result(agent_name=f"whatsapp-{agent_name}", prompt=incoming_msg, result=result)
        except Exception:
            pass

        # Send response via Twilio
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        twilio_number = os.environ.get("TWILIO_WHATSAPP_NUMBER", "")

        if account_sid and auth_token and twilio_number:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            # Truncate to WhatsApp limit (1600 chars)
            response_text = result[:1550] + "..." if len(result) > 1550 else result
            client.messages.create(
                body=f"🤖 *{agent_name.upper()}*\n\n{response_text}",
                from_=f"whatsapp:{twilio_number}",
                to=sender,
            )

        return {"status": "ok", "agent": agent_name, "sender": sender}

    except Exception as exc:
        print(f"[whatsapp] Error: {exc}")
        return {"status": "error", "detail": str(exc)}


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

# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@app.post("/login", response_model=AuthResponse, tags=["Auth"])
def login(request: AuthRequest):
    """Authenticate with email and password."""
    user = _USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    import secrets
    token = secrets.token_hex(24)
    return AuthResponse(token=token, email=request.email, name=user["name"])


@app.post("/register", tags=["Auth"])
def register(request: AuthRequest):
    """Request account registration (admin activation required)."""
    if "@" not in request.email or len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Email inválido ou senha muito curta (mín. 6 caracteres)")
    if request.email in _USERS:
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    return {"message": "Solicitação recebida. Um administrador irá ativar sua conta em breve."}


@app.post("/test-email", tags=["Health"])
def test_email():
    """Trigger the daily agent run + email immediately (for testing)."""
    import threading
    threading.Thread(target=_run_all_agents_and_email, daemon=True).start()
    return {"status": "triggered", "message": "Daily run started in background — check your inbox in ~2 minutes."}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "ORIGYN Global AI Agency API"}


# ---------------------------------------------------------------------------
# Frontend routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=FileResponse, tags=["Frontend"])
def serve_office():
    """Serve the ORIGYN office game at the root URL."""
    return FileResponse("origyn-workspace.html", media_type="text/html")


@app.get("/gather", response_class=FileResponse, tags=["Frontend"])
def serve_gather():
    """Serve the ORIGYN Gather office game."""
    return FileResponse("origyn-gather.html", media_type="text/html")


@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
def serve_dashboard():
    """Serve the agent results dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)
