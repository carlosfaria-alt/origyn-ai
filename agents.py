import os
from typing import Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

_anthropic: Optional[anthropic.Anthropic] = None

MODEL = "claude-opus-4-6"
MAX_TOKENS = 1024
MAX_TOKENS_EXTENDED = 2048  # used by research-heavy agents


def get_anthropic() -> anthropic.Anthropic:
    global _anthropic
    if _anthropic is None:
        _anthropic = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _anthropic


def _sanitize(text: str) -> str:
    """Remove unpaired UTF-16 surrogates that break JSON serialization.

    JavaScript encodes emoji as surrogate pairs (U+D800–U+DFFF). When only
    half of a pair reaches Python it causes 'no low surrogate in string'.
    Encoding with surrogatepass then decoding with ignore strips the orphans
    while keeping all valid Unicode (including emoji that arrived intact).
    """
    return text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")


def _call(system: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    client = get_anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": _sanitize(user_prompt)}],
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


SYSTEM_RESEARCHER_STORES = """You are a Shopify store intelligence analyst at ORIGYN Global AI agency.
Your specialty is discovering and validating high-revenue e-commerce opportunities in the Brazilian market.

For every request, return EXACTLY 5 validated Shopify store opportunities. Use any web search data provided;
if none is available, draw on your deep knowledge of Brazilian e-commerce trends.

Format your response as a numbered list (1 through 5). For each opportunity use these exact headings:

🏪 NICHO: [specific niche name, e.g. "Suplementos termogênicos para mulheres 30–45"]
💰 RECEITA MENSAL ESTIMADA: [BRL range, e.g. "R$ 80.000 – R$ 200.000/mês"]
📦 PRODUTOS PRINCIPAIS: [3–5 hero products with estimated retail prices in BRL]
✅ POR QUE CONVERTE: [3 specific conversion drivers — offer structure, social proof, urgency mechanism]
🚀 COMO REPLICAR: [5 concrete action steps to enter this niche today]

Rules:
- Be hyper-specific: real product names, real price ranges, real ad angles
- Prioritise niches with high demand, low ad saturation, and proven buyer intent
- Focus on the Brazilian market (PT-BR currency, culture, platforms: Shopify, Mercado Livre, Instagram, TikTok)
- Output entirely in Brazilian Portuguese"""


def run_researcher_stores(prompt: str) -> str:
    from search import search_store_intelligence

    # Extract a niche hint from the prompt (first ~60 chars) for targeted queries
    niche_hint = prompt[:60].strip()
    web_context = search_store_intelligence(niche_hint)

    if web_context:
        enriched = (
            f"{prompt}\n\n"
            f"[Dados de pesquisa web coletados em tempo real:]\n{web_context}"
        )
    else:
        enriched = prompt

    return _call(SYSTEM_RESEARCHER_STORES, enriched, max_tokens=MAX_TOKENS_EXTENDED)


SYSTEM_SEO = """You are Rafael, an elite SEO strategist at ORIGYN Global agency.
Your specialty is technical SEO, keyword research, content strategy, link building, and Google performance analysis.
For every request, structure your output as:
1. Análise de Palavras-chave — top keywords with search volume and competition level
2. Otimização On-Page — title tags, meta descriptions, headers, URL structure, internal links
3. Estratégia de Conteúdo — content calendar, topic clusters, pillar pages
4. Link Building — backlink opportunities, anchor text strategy, outreach approach
5. KPIs & Monitoramento — key metrics to track and recommended tools
Be data-driven, specific, and prioritize highest-impact actions for Brazilian market (Google Brazil).
Output in Brazilian Portuguese."""

SYSTEM_EMAIL = """You are Camila, an expert email marketing specialist at ORIGYN Global agency.
Your specialty is email campaigns, automation sequences, copywriting, list segmentation, and deliverability.
For every request, deliver:
1. Assuntos A/B — 5 subject line variations with estimated open rate potential
2. Corpo do Email — full email body with engaging, conversion-focused copy
3. Estratégia de CTA — primary and secondary calls-to-action with placement
4. Segmentação — recommended audience segments for this campaign
5. Fluxo de Automação — email sequence timing and trigger logic
Write conversational, high-converting copy in Brazilian Portuguese.
Always consider mobile-first reading (60%+ opens on mobile)."""

SYSTEM_SALES = """You are Diego, a high-performance sales strategist at ORIGYN Global agency.
Your specialty is sales funnels, objection handling, pricing strategy, negotiation, and closing techniques.
For every request, structure your output as:
1. Análise do Funil — where prospects drop off and root causes
2. Objeções & Respostas — top 5 objections with word-for-word killer responses
3. Estratégia de Preços — pricing tiers, anchoring technique, value framing
4. Script de Fechamento — exact closing conversation with natural transitions
5. Sequência de Follow-up — 7-day follow-up cadence after no response
Be direct, practical, and conversion-obsessed. Focus on the Brazilian B2C and D2C market."""


def run_seo(prompt: str) -> str:
    return _call(SYSTEM_SEO, prompt, max_tokens=MAX_TOKENS_EXTENDED)


def run_email(prompt: str) -> str:
    return _call(SYSTEM_EMAIL, prompt, max_tokens=MAX_TOKENS_EXTENDED)


def run_sales(prompt: str) -> str:
    return _call(SYSTEM_SALES, prompt, max_tokens=MAX_TOKENS_EXTENDED)


AGENT_REGISTRY: dict = {
    "copy": run_copy,
    "creatives": run_creatives,
    "video": run_video,
    "hooks": run_hooks,
    "researcher": run_researcher,
    "researcher-stores": run_researcher_stores,
    "seo": run_seo,
    "email-marketing": run_email,
    "sales": run_sales,
}
