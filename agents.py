import os
from typing import Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

_anthropic: Optional[anthropic.Anthropic] = None

MODEL = "claude-opus-4-6"
MAX_TOKENS = 1024


def get_anthropic() -> anthropic.Anthropic:
    global _anthropic
    if _anthropic is None:
        _anthropic = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _anthropic


def _call(system: str, user_prompt: str) -> str:
    client = get_anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Specialized agents
# ---------------------------------------------------------------------------

SYSTEM_COPY = """You are an elite direct-response copywriter for ORIGYN Global AI agency.
Your specialty is writing high-converting sales copy: headlines, body copy, CTAs, and email sequences.
Always write in a persuasive, clear, and benefit-driven tone. Match the brand voice requested.
Output only the requested copy — no commentary or meta-text."""

SYSTEM_CREATIVES = """You are a senior creative director at ORIGYN Global AI agency.
Your job is to conceptualize visual ad creatives: describe the image/video concept, color palette,
typography direction, and the hook the creative must land. Be specific, visual, and practical —
your briefs go directly to designers and motion artists."""

SYSTEM_VIDEO = """You are a video scriptwriter and strategist at ORIGYN Global AI agency.
You write short-form video scripts (Reels, TikToks, YouTube Shorts) optimized for retention and conversion.
Structure every script with: Hook (0–3s), Problem (3–8s), Solution (8–20s), Proof (20–30s), CTA (last 5s).
Include on-screen text suggestions and B-roll notes."""

SYSTEM_HOOKS = """You are a viral content strategist at ORIGYN Global AI agency specialized in hooks.
You write scroll-stopping opening lines for ads, videos, and social posts.
For each request, deliver 10 hook variations across different angles:
curiosity, fear, desire, social proof, contrarian, and story-based.
Rank them by estimated scroll-stop potential."""

SYSTEM_RESEARCHER = """You are a strategic market researcher at ORIGYN Global AI agency.
Your job is to analyze markets, audiences, competitors, and trends to produce actionable insights.
Structure your research output as: Executive Summary, Target Audience Profile, Key Pain Points,
Competitor Positioning, Market Opportunities, and Recommended Messaging Angles.
Be data-driven, specific, and strategic."""


def run_copy(prompt: str) -> str:
    return _call(SYSTEM_COPY, prompt)


def run_creatives(prompt: str) -> str:
    return _call(SYSTEM_CREATIVES, prompt)


def run_video(prompt: str) -> str:
    return _call(SYSTEM_VIDEO, prompt)


def run_hooks(prompt: str) -> str:
    return _call(SYSTEM_HOOKS, prompt)


def run_researcher(prompt: str) -> str:
    return _call(SYSTEM_RESEARCHER, prompt)


AGENT_REGISTRY: dict = {
    "copy": run_copy,
    "creatives": run_creatives,
    "video": run_video,
    "hooks": run_hooks,
    "researcher": run_researcher,
}
