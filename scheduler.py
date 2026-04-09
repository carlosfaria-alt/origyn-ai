"""
APScheduler daily tasks — all 5 agents run at 08:00 UTC, results saved to
Supabase, then a formatted HTML email summary is sent via SMTP.

Required env vars for email:
  SMTP_HOST   e.g. smtp.gmail.com
  SMTP_PORT   e.g. 587
  SMTP_USER   sender address
  SMTP_PASS   app password (Gmail) or SMTP password
  EMAIL_TO    recipient address (comma-separated for multiple)
"""
import os
import smtplib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from agents import AGENT_REGISTRY
from database import save_result

# ---------------------------------------------------------------------------
# Default daily prompts
# ---------------------------------------------------------------------------

DAILY_PROMPTS: dict[str, str] = {
    "copy":               "Crie 3 variações de copy para e-commerce de suplementos",
    "creatives":          "Crie briefing visual para anúncio de suplementos no Instagram",
    "video":              "Crie script de 30 segundos para expert de emagrecimento",
    "hooks":              "Crie 10 hooks para anúncios de suplementos",
    "researcher":         "Pesquise os nichos de e-commerce mais lucrativos no Brasil agora",
    "researcher-stores":  "Encontre 5 oportunidades de lojas Shopify com alto potencial de vendas no Brasil agora",
}

# Agent display metadata for the email
AGENT_META: dict[str, dict] = {
    "copy":       {"name": "Sofia",  "role": "Especialista em Copy",        "color": "#7c3aed"},
    "creatives":  {"name": "Lucas",  "role": "Diretor de Criativos",        "color": "#d97706"},
    "video":      {"name": "Ana",    "role": "Roteirista de Vídeo",         "color": "#dc2626"},
    "hooks":      {"name": "Pedro",  "role": "Especialista em Hooks",       "color": "#059669"},
    "researcher":         {"name": "Marina",  "role": "Pesquisadora de Mercado",      "color": "#0284c7"},
    "researcher-stores":  {"name": "Isabela", "role": "Analista de Lojas Shopify",    "color": "#0f766e"},
}

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run_agent(agent_name: str) -> tuple[str, str]:
    """Run a single agent and save to Supabase. Returns (agent_name, result|error)."""
    prompt = DAILY_PROMPTS[agent_name]
    print(f"[scheduler] ▶ Starting {agent_name}...")
    try:
        result = AGENT_REGISTRY[agent_name](prompt)
        save_result(agent_name=agent_name, prompt=prompt, result=result)
        print(f"[scheduler] ✓ {agent_name} done.")
        return agent_name, result
    except Exception as exc:
        error = f"ERROR: {exc}"
        print(f"[scheduler] ✗ {agent_name} failed: {exc}")
        return agent_name, error


def _run_all_agents_and_email() -> None:
    """Run all 5 agents in parallel, then send the daily email summary."""
    print(f"[scheduler] === Daily run started at {datetime.now(timezone.utc).isoformat()} ===")

    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(_run_agent, name): name for name in DAILY_PROMPTS}
        for future in as_completed(futures):
            agent_name, result = future.result()
            results[agent_name] = result

    print("[scheduler] All agents complete. Sending email summary...")
    _send_daily_email(results)
    print("[scheduler] === Daily run finished ===")


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def _build_html_email(results: dict[str, str], date_str: str) -> str:
    agent_blocks = ""
    for agent_id, result in results.items():
        meta = AGENT_META.get(agent_id, {"name": agent_id, "role": "", "color": "#2563eb"})
        is_error = result.startswith("ERROR:")
        status_badge = (
            '<span style="background:#fee2e2;color:#dc2626;padding:2px 8px;border-radius:12px;font-size:11px">✗ Falhou</span>'
            if is_error else
            '<span style="background:#d1fae5;color:#059669;padding:2px 8px;border-radius:12px;font-size:11px">✓ Concluído</span>'
        )
        # Truncate result for email readability
        preview = result[:800] + ("…" if len(result) > 800 else "")
        preview_html = preview.replace("\n", "<br>").replace("**", "").replace("##", "")

        agent_blocks += f"""
        <div style="margin-bottom:28px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden">
          <div style="background:{meta['color']}11;padding:14px 18px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:space-between">
            <div>
              <span style="font-weight:600;font-size:15px;color:{meta['color']}">{meta['name']}</span>
              <span style="color:#6b7280;font-size:12px;margin-left:8px">{meta['role']}</span>
            </div>
            {status_badge}
          </div>
          <div style="padding:16px 18px;font-size:13px;line-height:1.65;color:#374151;background:#fff">
            {preview_html}
          </div>
        </div>
        """

    success_count = sum(1 for r in results.values() if not r.startswith("ERROR:"))
    total = len(results)

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Inter',Arial,sans-serif">
  <div style="max-width:680px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08)">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1a1a2e 0%,#2563eb 100%);padding:32px 36px">
      <div style="color:#fff;font-size:22px;font-weight:700;letter-spacing:-0.3px">ORIGYN Global AI</div>
      <div style="color:rgba(255,255,255,0.65);font-size:13px;margin-top:4px">Relatório Diário dos Agentes</div>
      <div style="margin-top:20px;background:rgba(255,255,255,0.12);border-radius:10px;padding:14px 18px;display:inline-block">
        <div style="color:rgba(255,255,255,0.7);font-size:11px;text-transform:uppercase;letter-spacing:0.08em">Data</div>
        <div style="color:#fff;font-size:16px;font-weight:600;margin-top:2px">{date_str}</div>
      </div>
      <div style="display:inline-block;margin-left:16px;background:rgba(255,255,255,0.12);border-radius:10px;padding:14px 18px">
        <div style="color:rgba(255,255,255,0.7);font-size:11px;text-transform:uppercase;letter-spacing:0.08em">Status</div>
        <div style="color:#34d399;font-size:16px;font-weight:600;margin-top:2px">{success_count}/{total} agentes ✓</div>
      </div>
    </div>

    <!-- Body -->
    <div style="padding:28px 32px">
      <p style="color:#6b7280;font-size:13px;margin:0 0 24px">
        Abaixo estão os outputs gerados automaticamente pelos seus 5 agentes de IA às 08:00 UTC de hoje.
        Os resultados completos estão salvos no Supabase.
      </p>

      {agent_blocks}

      <!-- Footer -->
      <div style="border-top:1px solid #e5e7eb;padding-top:20px;margin-top:8px;text-align:center">
        <p style="color:#9ca3af;font-size:11px;margin:0">
          Gerado automaticamente pela ORIGYN Global AI Agency
          &nbsp;·&nbsp; <a href="https://web-production-9b425.up.railway.app/results" style="color:#2563eb">Ver todos os resultados</a>
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""


def _send_daily_email(results: dict[str, str]) -> None:
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    email_to  = os.environ.get("EMAIL_TO", "")

    if not all([smtp_host, smtp_user, smtp_pass, email_to]):
        print("[scheduler] Email env vars not set — skipping email.")
        return

    date_str = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    recipients = [addr.strip() for addr in email_to.split(",")]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🤖 ORIGYN AI — Relatório Diário {date_str}"
    msg["From"]    = smtp_user
    msg["To"]      = ", ".join(recipients)

    html_body = _build_html_email(results, date_str)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipients, msg.as_string())
        print(f"[scheduler] ✉ Email sent to {recipients}")
    except Exception as exc:
        print(f"[scheduler] ✗ Email failed: {exc}")


# ---------------------------------------------------------------------------
# Scheduler factory
# ---------------------------------------------------------------------------

def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        func=_run_all_agents_and_email,
        trigger=CronTrigger(hour=8, minute=0, timezone="America/Sao_Paulo"),
        id="daily_all_agents",
        name="Daily — all agents + email (08:00 BRT)",
        replace_existing=True,
    )
    return scheduler
