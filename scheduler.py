"""
APScheduler daily tasks — each agent runs at 08:00 UTC with a default prompt.
Results are saved to Supabase automatically.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from agents import AGENT_REGISTRY
from database import save_result

# Default daily prompts for each agent
DAILY_PROMPTS: dict[str, str] = {
    "copy": (
        "Write 3 high-converting Facebook ad copy variations for a premium AI agency "
        "targeting e-commerce brands doing $50k–$500k/month in revenue."
    ),
    "creatives": (
        "Conceptualize 3 ad creative briefs for an AI agency targeting DTC brands. "
        "Focus on before/after transformations and ROI-driven visuals."
    ),
    "video": (
        "Write a 30-second Reels/TikTok script for an AI agency showing how AI "
        "saves businesses 20+ hours per week."
    ),
    "hooks": (
        "Generate 10 viral hooks for an AI marketing agency targeting business owners "
        "who are frustrated with their current marketing results."
    ),
    "researcher": (
        "Research the AI agency market in 2025: key players, pricing models, "
        "client pain points, and the biggest opportunities for a new entrant."
    ),
}


def _run_agent_task(agent_name: str) -> None:
    prompt = DAILY_PROMPTS[agent_name]
    print(f"[scheduler] Running daily task for agent: {agent_name}")
    try:
        result = AGENT_REGISTRY[agent_name](prompt)
        save_result(agent=agent_name, prompt=prompt, result=result, metadata={"source": "scheduler"})
        print(f"[scheduler] ✓ {agent_name} task completed and saved.")
    except Exception as exc:
        print(f"[scheduler] ✗ {agent_name} task failed: {exc}")


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")

    for agent_name in AGENT_REGISTRY:
        scheduler.add_job(
            func=_run_agent_task,
            trigger=CronTrigger(hour=8, minute=0),
            args=[agent_name],
            id=f"daily_{agent_name}",
            name=f"Daily {agent_name} agent",
            replace_existing=True,
        )

    return scheduler
