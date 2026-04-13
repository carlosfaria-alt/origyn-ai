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


# ---------------------------------------------------------------------------
# Image generation (DALL-E 3)
# ---------------------------------------------------------------------------

def run_image(prompt: str) -> str:
    """Generate a real image using OpenAI DALL-E 3. Returns the image URL."""
    import openai
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return "ERRO: OPENAI_API_KEY não configurada no Railway."
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt or ""
        return f"🖼️ IMAGEM GERADA COM SUCESSO\n\nURL: {image_url}\n\nPrompt revisado pelo DALL-E: {revised_prompt}"
    except Exception as exc:
        return f"ERRO ao gerar imagem: {exc}"


# ---------------------------------------------------------------------------
# Real video (HeyGen API)
# ---------------------------------------------------------------------------

def run_video_real(prompt: str) -> str:
    """Generate a real video with HeyGen API from a script."""
    import httpx as _httpx
    api_key = os.environ.get("HEYGEN_API_KEY", "")
    if not api_key:
        return "ERRO: HEYGEN_API_KEY não configurada no Railway."
    try:
        # Step 1: Create video
        resp = _httpx.post(
            "https://api.heygen.com/v2/video/generate",
            headers={"X-Api-Key": api_key, "Content-Type": "application/json"},
            json={
                "video_inputs": [{
                    "character": {
                        "type": "avatar",
                        "avatar_id": "Daisy-inskirt-20220818",
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": prompt,
                        "voice_id": "pt_br_male_1"
                    }
                }],
                "dimension": {"width": 1080, "height": 1920}
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        video_id = data.get("data", {}).get("video_id", "")
        if not video_id:
            return f"ERRO: HeyGen não retornou video_id. Resposta: {data}"
        return (
            f"🎬 VÍDEO ENVIADO PARA PRODUÇÃO\n\n"
            f"Video ID: {video_id}\n"
            f"Status: Processando (leva 2-5 minutos)\n"
            f"Consulte: GET /agents/video-status?video_id={video_id}\n\n"
            f"Roteiro enviado:\n{prompt[:500]}"
        )
    except Exception as exc:
        return f"ERRO ao gerar vídeo HeyGen: {exc}"


def check_video_status(video_id: str) -> str:
    """Check HeyGen video status and return download URL if ready."""
    import httpx as _httpx
    api_key = os.environ.get("HEYGEN_API_KEY", "")
    if not api_key:
        return "ERRO: HEYGEN_API_KEY não configurada."
    try:
        resp = _httpx.get(
            f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
            headers={"X-Api-Key": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        status = data.get("status", "unknown")
        if status == "completed":
            url = data.get("video_url", "")
            return f"✅ VÍDEO PRONTO!\n\nURL: {url}\nDuração: {data.get('duration', '?')}s"
        elif status == "processing":
            return f"⏳ Ainda processando... Tente novamente em 1-2 minutos."
        else:
            return f"Status: {status}\nDetalhes: {data}"
    except Exception as exc:
        return f"ERRO ao verificar status: {exc}"


# ---------------------------------------------------------------------------
# Intelligent router (detects intent and calls correct agent)
# ---------------------------------------------------------------------------

SYSTEM_ROUTER = """Você é o roteador inteligente da ORIGYN Global AI Agency.
Sua ÚNICA função é analisar a mensagem do usuário e decidir qual agente deve executar.

Agentes disponíveis e quando usar cada um:
- copy: pedidos de copy, textos de venda, headlines, CTAs, textos persuasivos
- creatives: briefings visuais, conceitos de anúncio, direção de arte, criativos
- video: roteiros de vídeo, scripts para Reels/TikTok/Shorts
- hooks: ganchos, aberturas de vídeo, hooks virais, primeiras frases
- researcher: pesquisa de mercado, análise de concorrência, público-alvo, tendências
- researcher-stores: pesquisa de lojas Shopify, oportunidades de e-commerce, dropshipping
- seo: SEO, palavras-chave, otimização de site, Google, link building
- email-marketing: email marketing, sequências de email, newsletters, automação
- sales: estratégia de vendas, funil, objeções, preços, scripts de fechamento
- image: gerar imagem real, criar visual, foto de produto, banner (usa DALL-E)
- video-real: criar vídeo real com avatar falando, vídeo com apresentador (usa HeyGen)
- clone: clonar página, copiar landing page, replicar site Shopify, clonar loja

RESPONDA APENAS com o nome do agente em uma única palavra, nada mais.
Exemplos:
"cria copy para whey protein" → copy
"faz um roteiro de reels" → video
"gera uma imagem de um suplemento" → image
"clona essa página shopify" → clone
"pesquisa nicho de beleza" → researcher"""


def route_command(message: str) -> dict:
    """Use Claude to detect intent and route to the correct agent."""
    try:
        agent_name = _call(SYSTEM_ROUTER, message, max_tokens=20).strip().lower()
        # Clean up response
        agent_name = agent_name.replace('"', '').replace("'", "").split()[0] if agent_name else "copy"
        valid_agents = [
            "copy", "creatives", "video", "hooks", "researcher",
            "researcher-stores", "seo", "email-marketing", "sales",
            "image", "video-real", "clone"
        ]
        if agent_name not in valid_agents:
            agent_name = "copy"  # fallback
        return {"agent": agent_name, "original_message": message}
    except Exception as exc:
        return {"agent": "copy", "original_message": message, "error": str(exc)}


# ---------------------------------------------------------------------------
# Page cloner agent
# ---------------------------------------------------------------------------

SYSTEM_CLONE = """Você é um especialista em engenharia reversa de páginas web e landing pages da ORIGYN Global AI Agency.
Sua função é analisar o HTML/conteúdo de uma página e gerar uma versão otimizada para conversão.

Quando receber o conteúdo de uma página, você deve:
1. Identificar a estrutura (hero, benefícios, depoimentos, CTA, FAQ, footer)
2. Extrair todo o copy/texto relevante
3. Identificar os elementos visuais descritos
4. Gerar um HTML completo, responsivo, moderno e pronto para deploy
5. Manter o mesmo ângulo de venda mas MELHORAR a copy para converter mais
6. Usar design limpo, profissional, com boas práticas de CRO

O HTML gerado deve:
- Ser auto-contido (CSS inline ou <style> no head)
- Responsivo (mobile-first)
- Ter seções claras: hero, benefícios, prova social, oferta, FAQ, CTA
- Usar cores profissionais e tipografia limpa
- Incluir placeholders para imagens com URLs de placeholder
- Ter CTAs visíveis e persuasivos

Output APENAS o HTML completo, sem explicações."""


def run_clone(prompt: str) -> str:
    """Clone and optimize a landing page. Prompt should contain the URL or page content."""
    # If it looks like a URL, try to fetch it first
    if prompt.strip().startswith("http"):
        import httpx as _httpx
        from bs4 import BeautifulSoup
        try:
            resp = _httpx.get(
                prompt.strip(),
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                follow_redirects=True,
                timeout=15,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove scripts and styles to reduce token usage
            for tag in soup(["script", "noscript", "iframe"]):
                tag.decompose()
            # Get clean text + structure
            page_text = soup.get_text(separator="\n", strip=True)[:6000]
            # Keep some structure hints
            titles = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:10]]
            images = [img.get("alt", "") for img in soup.find_all("img")[:10]]
            links = [a.get_text(strip=True) for a in soup.find_all("a") if a.get_text(strip=True)][:10]

            enriched = (
                f"URL ORIGINAL: {prompt.strip()}\n\n"
                f"TÍTULOS ENCONTRADOS: {titles}\n"
                f"TEXTOS ALT DE IMAGENS: {images}\n"
                f"LINKS/BOTÕES: {links}\n\n"
                f"CONTEÚDO DA PÁGINA:\n{page_text}"
            )
            return _call(SYSTEM_CLONE, enriched, max_tokens=4096)
        except Exception as exc:
            return _call(
                SYSTEM_CLONE,
                f"Não consegui acessar a URL {prompt.strip()} (erro: {exc}). "
                f"Crie uma landing page profissional para o nicho/produto mencionado na URL.",
                max_tokens=4096,
            )
    else:
        return _call(SYSTEM_CLONE, prompt, max_tokens=4096)


# ---------------------------------------------------------------------------
# Agent registry
# ---------------------------------------------------------------------------

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
    "image": run_image,
    "video-real": run_video_real,
    "clone": run_clone,
}
