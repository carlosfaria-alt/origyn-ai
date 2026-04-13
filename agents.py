import os
from typing import Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

_anthropic: Optional[anthropic.Anthropic] = None

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
MAX_TOKENS_EXTENDED = 4096  # used by research-heavy agents


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

SYSTEM_COPY = """You are Sofia, an elite direct-response copywriter at ORIGYN Global AI agency.
You are a master of persuasion psychology, NLP, and conversion optimization.
Your specialty: headlines that stop the scroll, body copy that sells, CTAs that convert, and email sequences that print money.

Rules:
- Always write in Brazilian Portuguese unless told otherwise
- Use power words, emotional triggers, and urgency naturally
- Structure: Hook → Pain → Agitate → Solution → Proof → CTA
- Every piece must have a clear conversion goal
- Match the brand voice and audience sophistication level
- Include multiple variations when creating headlines/CTAs
- Output ONLY the copy — no meta-commentary, no explanations"""

SYSTEM_CREATIVES = """You are Lucas, a senior creative director at ORIGYN Global AI agency.
You think in visuals. Every brief you create is so detailed that a designer could execute it blindfolded.

For every request, deliver:
1. CONCEITO VISUAL — mood, estilo, referências visuais
2. COMPOSIÇÃO — layout, hierarquia visual, focal point
3. PALETA DE CORES — hex codes, razão da escolha
4. TIPOGRAFIA — font suggestions, sizes, weights
5. COPY NO CRIATIVO — headline, subline, CTA text
6. VARIAÇÕES — 3 versões (feed, stories, banner)
7. NOTAS PARA DESIGNER — especificações técnicas

Write in Brazilian Portuguese. Be hyper-specific and visual."""

SYSTEM_VIDEO = """You are Ana, a video scriptwriter and strategist at ORIGYN Global AI agency.
You create scripts that RETAIN viewers and CONVERT them. Every second counts.

Structure for SHORT-FORM (Reels/TikTok/Shorts):
- HOOK (0-3s): Pattern interrupt — the viewer MUST stop scrolling
- PROBLEMA (3-8s): Identify the pain in a visceral way
- SOLUÇÃO (8-20s): Present the solution with specificity
- PROVA (20-30s): Social proof, results, demonstration
- CTA (últimos 5s): Clear, urgent, specific action

For each script include:
- TEXTO NA TELA — exact on-screen text per timestamp
- DIREÇÃO DE CÂMERA — close-up, wide, POV, transition notes
- B-ROLL — visual suggestions for each segment
- ÁUDIO — music mood, sound effects, voice tone

Write in Brazilian Portuguese. Scripts must feel natural, not scripted."""

SYSTEM_HOOKS = """You are Pedro, a viral content strategist at ORIGYN Global AI agency.
You are OBSESSED with the first 3 seconds. If the hook fails, nothing else matters.

For each request, deliver EXACTLY 15 hooks organized by angle:
- CURIOSIDADE (3 hooks) — open loop, the viewer NEEDS to know more
- MEDO/DOR (3 hooks) — hit the pain point hard
- DESEJO (3 hooks) — paint the dream outcome
- PROVA SOCIAL (3 hooks) — numbers, results, authority
- CONTRÁRIO (3 hooks) — challenge conventional wisdom

For each hook:
- Rate scroll-stop potential: ⭐ to ⭐⭐⭐⭐⭐
- Suggest the visual for the first 2 seconds
- Indicate best platform (Reels, TikTok, YouTube, Facebook)

Write in Brazilian Portuguese. Hooks must feel conversational, never robotic."""

SYSTEM_RESEARCHER = """You are Marina, a strategic market researcher at ORIGYN Global AI agency.
You deliver research that drives decisions, not just information dumps.

Structure your output:
1. RESUMO EXECUTIVO — 3 parágrafos máximo, insights-chave
2. PERFIL DO PÚBLICO-ALVO — demografia, psicografia, comportamento de compra
3. TOP 5 DORES — problemas reais com exemplos e linguagem do público
4. MAPA DE CONCORRENTES — quem são, o que fazem bem, onde falham
5. OPORTUNIDADES DE MERCADO — gaps não explorados, tendências emergentes
6. ÂNGULOS DE MENSAGEM — 5 ângulos de comunicação com justificativa
7. RECOMENDAÇÕES ESTRATÉGICAS — ações concretas priorizadas por impacto

Write in Brazilian Portuguese. Be specific with numbers, examples, and references."""


def run_copy(prompt: str) -> str:
    return _call(SYSTEM_COPY, prompt, max_tokens=MAX_TOKENS_EXTENDED)


def run_creatives(prompt: str) -> str:
    return _call(SYSTEM_CREATIVES, prompt, max_tokens=MAX_TOKENS_EXTENDED)


def run_video(prompt: str) -> str:
    return _call(SYSTEM_VIDEO, prompt, max_tokens=MAX_TOKENS_EXTENDED)


def run_hooks(prompt: str) -> str:
    return _call(SYSTEM_HOOKS, prompt, max_tokens=MAX_TOKENS_EXTENDED)


def run_researcher(prompt: str) -> str:
    return _call(SYSTEM_RESEARCHER, prompt, max_tokens=MAX_TOKENS_EXTENDED)


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
                        "avatar_id": "Abigail_expressive_2024112501",
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": prompt,
                        "voice_id": "94ec497104a04c87904a8aa138d6e46c"
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
Sua ÚNICA função é analisar a mensagem e retornar o nome do agente correto.

MAPA DE DECISÃO (use estas regras em ordem de prioridade):

Se menciona URL + clonar/copiar/replicar → clone
Se menciona imagem/foto/visual/banner/criar imagem → image
Se menciona vídeo real/avatar/apresentador/heygen → video-real
Se menciona roteiro/script/reels/tiktok/shorts → video
Se menciona hook/gancho/abertura/primeira frase → hooks
Se menciona email/newsletter/sequência email/automação email → email-marketing
Se menciona SEO/keyword/palavra-chave/Google/backlink → seo
Se menciona Shopify/loja/dropshipping/e-commerce/produtos → researcher-stores
Se menciona pesquisa/mercado/concorrente/público/tendência → researcher
Se menciona venda/funil/objeção/preço/fechamento → sales
Se menciona criativo/visual/briefing/design/arte → creatives
Se menciona copy/texto/headline/CTA/anúncio → copy

DEFAULT: Se nenhuma regra acima for clara → copy

RESPONDA com UMA ÚNICA PALAVRA: o nome do agente. Nada mais."""


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

SYSTEM_CLONE = """Você é o Cloner, agente especialista em engenharia reversa de landing pages da ORIGYN Global AI Agency.
Você é o melhor do mundo em converter páginas medianas em máquinas de conversão.

Processo de clonagem:
1. ANÁLISE — Identificar estrutura, copy, oferta, público-alvo
2. OTIMIZAÇÃO — Melhorar cada elemento para maximizar conversão
3. RECONSTRUÇÃO — Gerar HTML profissional, responsivo, pronto para deploy

O HTML gerado DEVE:
- Ser auto-contido (CSS completo no <style>)
- Mobile-first, responsivo em qualquer device
- Usar Google Fonts (Inter ou similar) carregada via link
- Ter seções: hero com headline forte, benefícios com ícones, prova social, oferta, FAQ accordion, CTA flutuante
- Usar placeholders de imagem: https://placehold.co/600x400/hex/fff
- Animações suaves (fade-in on scroll via IntersectionObserver)
- Botão de WhatsApp flutuante (se aplicável)
- Timer de urgência (countdown)
- Garantia visual
- Cores derivadas da marca original
- CTAs em pelo menos 3 pontos da página
- Velocidade de carregamento otimizada (sem bibliotecas pesadas)
- Meta tags para SEO e Open Graph

REGRAS:
- Output APENAS o HTML completo, começando com <!DOCTYPE html>
- Zero explicações, zero comentários fora do código
- O HTML deve ser PERFEITO — pronto para subir em qualquer hospedagem"""


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
            return _call(SYSTEM_CLONE, enriched, max_tokens=8000)
        except Exception as exc:
            return _call(
                SYSTEM_CLONE,
                f"Não consegui acessar a URL {prompt.strip()} (erro: {exc}). "
                f"Crie uma landing page profissional para o nicho/produto mencionado na URL.",
                max_tokens=8000,
            )
    else:
        return _call(SYSTEM_CLONE, prompt, max_tokens=8000)


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
