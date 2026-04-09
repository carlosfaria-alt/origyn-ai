"""Dashboard HTML — served at GET /dashboard"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ORIGYN AI — Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f172a;--surface:#1e293b;--surface2:#263348;--border:#334155;
  --text:#f1f5f9;--muted:#94a3b8;--accent:#2563eb;
  --radius:12px;--font:'Inter',system-ui,sans-serif;
}
html{background:var(--bg);color:var(--text);font-family:var(--font);font-size:14px}
body{min-height:100vh;padding:0 0 48px}
a{color:var(--accent);text-decoration:none}

/* TOP BAR */
.topbar{
  background:#0b1222;border-bottom:1px solid var(--border);
  padding:0 28px;height:56px;display:flex;align-items:center;
  justify-content:space-between;position:sticky;top:0;z-index:100;
}
.brand{display:flex;align-items:center;gap:10px}
.logo{width:32px;height:32px;border-radius:8px;background:var(--accent);
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:13px;letter-spacing:-.5px}
.brand-name{font-weight:700;font-size:15px;letter-spacing:-.3px}
.brand-sub{font-size:11px;color:var(--muted);margin-top:1px}
.topbar-right{display:flex;align-items:center;gap:12px}
.badge{display:flex;align-items:center;gap:5px;padding:4px 10px;border-radius:20px;
  font-size:11px;font-weight:500}
.badge-green{background:rgba(5,150,105,.15);color:#34d399;border:1px solid rgba(52,211,153,.2)}
.badge-blue{background:rgba(37,99,235,.15);color:#60a5fa;border:1px solid rgba(96,165,250,.2)}
.refresh-btn{padding:6px 14px;border-radius:8px;border:1px solid var(--border);
  background:transparent;color:var(--text);font-size:12px;cursor:pointer;
  transition:all .15s;display:flex;align-items:center;gap:5px}
.refresh-btn:hover{background:var(--surface2);border-color:var(--accent)}
.office-link{padding:6px 14px;border-radius:8px;border:none;
  background:var(--accent);color:#fff;font-size:12px;font-weight:600;cursor:pointer;
  text-decoration:none;display:flex;align-items:center;gap:5px}
.office-link:hover{opacity:.88}

/* LAYOUT */
.page{max-width:1280px;margin:0 auto;padding:28px 28px 0}

/* STATS ROW */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:18px 20px}
.stat-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
.stat-value{font-size:28px;font-weight:700;letter-spacing:-1px}
.stat-sub{font-size:11px;color:var(--muted);margin-top:4px}

/* SECTION TITLE */
.section-title{font-size:13px;font-weight:600;color:var(--muted);
  text-transform:uppercase;letter-spacing:.07em;margin-bottom:14px}

/* AGENT CARDS */
.agents-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:32px}
.agent-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  overflow:hidden;display:flex;flex-direction:column;transition:border-color .2s}
.agent-card:hover{border-color:var(--card-color,var(--accent))}
.agent-card-header{padding:14px 16px;display:flex;align-items:center;gap:10px;
  border-bottom:1px solid var(--border);
  background:color-mix(in srgb,var(--card-color,var(--accent)) 8%,transparent)}
.agent-av{width:38px;height:38px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;
  background:color-mix(in srgb,var(--card-color,var(--accent)) 20%,transparent);
  color:var(--card-color,var(--accent))}
.agent-name{font-weight:600;font-size:14px}
.agent-role{font-size:11px;color:var(--muted);margin-top:1px}
.agent-meta{margin-left:auto;text-align:right}
.agent-count{font-size:20px;font-weight:700;color:var(--card-color,var(--accent))}
.agent-count-label{font-size:10px;color:var(--muted)}

.agent-card-body{padding:14px 16px;flex:1;display:flex;flex-direction:column;gap:10px}
.result-preview{font-size:12px;color:var(--muted);line-height:1.6;
  flex:1;overflow:hidden;display:-webkit-box;-webkit-line-clamp:4;
  -webkit-box-orient:vertical;min-height:72px}
.result-time{font-size:10px;color:#475569}

.agent-card-footer{padding:10px 16px;border-top:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;gap:8px}
.run-btn{flex:1;padding:7px 12px;border-radius:8px;border:none;cursor:pointer;
  font-size:12px;font-weight:600;color:#fff;
  background:var(--card-color,var(--accent));transition:opacity .15s}
.run-btn:hover{opacity:.82}
.run-btn:disabled{opacity:.4;cursor:not-allowed}
.view-btn{padding:7px 10px;border-radius:8px;border:1px solid var(--border);
  background:transparent;color:var(--muted);font-size:12px;cursor:pointer;
  transition:all .15s;white-space:nowrap}
.view-btn:hover{border-color:var(--card-color,var(--accent));color:var(--text)}

/* CHART */
.chart-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:22px 24px;margin-bottom:32px}
.chart-wrap{position:relative;height:220px}

/* RESULTS TABLE */
.table-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  overflow:hidden;margin-bottom:32px}
.table-header{padding:14px 20px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between}
.table-header h3{font-size:14px;font-weight:600}
table{width:100%;border-collapse:collapse}
th{padding:10px 16px;text-align:left;font-size:11px;color:var(--muted);
   text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border);
   background:var(--surface2)}
td{padding:12px 16px;border-bottom:1px solid rgba(51,65,85,.5);font-size:12px;
   vertical-align:top;max-width:0}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--surface2)}
.agent-badge{display:inline-flex;align-items:center;gap:5px;
  padding:3px 9px;border-radius:20px;font-size:11px;font-weight:500;
  white-space:nowrap}
.td-prompt{width:28%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--muted)}
.td-result{width:42%;color:#cbd5e1}
.td-result-inner{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.td-time{width:13%;color:var(--muted);white-space:nowrap}

/* RESULT DRAWER */
.drawer-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:200;
  display:none;align-items:center;justify-content:center}
.drawer-overlay.open{display:flex}
.drawer{background:var(--surface);border:1px solid var(--border);border-radius:16px;
  width:680px;max-width:95vw;max-height:80vh;display:flex;flex-direction:column}
.drawer-head{padding:18px 22px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between}
.drawer-head h3{font-size:15px;font-weight:600}
.drawer-close{width:28px;height:28px;border-radius:7px;border:1px solid var(--border);
  background:transparent;color:var(--muted);font-size:18px;cursor:pointer;
  display:flex;align-items:center;justify-content:center}
.drawer-close:hover{background:var(--surface2);color:var(--text)}
.drawer-body{padding:20px 22px;overflow-y:auto;font-size:13px;line-height:1.75;
  color:#cbd5e1;white-space:pre-wrap;flex:1}
.drawer-prompt{padding:12px 22px;background:var(--surface2);border-bottom:1px solid var(--border);
  font-size:11px;color:var(--muted)}
.drawer-prompt strong{color:var(--text)}

/* RUN MODAL */
.run-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:300;
  display:none;align-items:center;justify-content:center}
.run-modal-overlay.open{display:flex}
.run-modal{background:var(--surface);border:1px solid var(--border);border-radius:16px;
  width:560px;max-width:95vw;padding:24px}
.run-modal h3{font-size:16px;font-weight:600;margin-bottom:6px}
.run-modal p{font-size:12px;color:var(--muted);margin-bottom:16px}
.run-modal textarea{width:100%;background:var(--surface2);border:1px solid var(--border);
  border-radius:8px;padding:10px 12px;color:var(--text);font-size:13px;
  font-family:var(--font);resize:vertical;min-height:80px;outline:none}
.run-modal textarea:focus{border-color:var(--accent)}
.run-modal-btns{display:flex;gap:8px;justify-content:flex-end;margin-top:14px}
.btn-cancel2{padding:8px 16px;border:1px solid var(--border);border-radius:8px;
  background:transparent;color:var(--muted);font-size:13px;cursor:pointer}
.btn-cancel2:hover{border-color:var(--text);color:var(--text)}
.btn-run{padding:8px 20px;border:none;border-radius:8px;
  font-size:13px;font-weight:600;color:#fff;cursor:pointer;transition:opacity .15s}
.btn-run:hover{opacity:.85}
.btn-run:disabled{opacity:.4;cursor:not-allowed}
.run-result{margin-top:14px;padding:12px;background:var(--surface2);border-radius:8px;
  font-size:12px;line-height:1.7;color:#cbd5e1;white-space:pre-wrap;
  max-height:240px;overflow-y:auto;display:none}

/* LOADING */
.spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.3);
  border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.skeleton{background:linear-gradient(90deg,var(--surface2) 25%,var(--border) 50%,var(--surface2) 75%);
  background-size:200% 100%;animation:shimmer 1.4s infinite;border-radius:4px;height:14px}
@keyframes shimmer{0%{background-position:200%}100%{background-position:-200%}}

/* EMPTY */
.empty{text-align:center;padding:48px 24px;color:var(--muted)}
.empty-icon{font-size:36px;margin-bottom:10px}

@media(max-width:900px){
  .agents-grid{grid-template-columns:repeat(2,1fr)}
  .stats{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:600px){
  .agents-grid{grid-template-columns:1fr}
  .stats{grid-template-columns:repeat(2,1fr)}
  .page{padding:16px}
}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="brand">
    <div class="logo">OG</div>
    <div>
      <div class="brand-name">ORIGYN Global AI</div>
      <div class="brand-sub">Dashboard de Agentes</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="badge badge-green">
      <div style="width:6px;height:6px;border-radius:50%;background:#34d399;animation:pulse2 2s infinite"></div>
      <span id="online-count">6 agentes online</span>
    </div>
    <div class="badge badge-blue" id="last-updated">Carregando...</div>
    <button class="refresh-btn" onclick="loadDashboard()">
      <span id="refresh-icon">↻</span> Atualizar
    </button>
    <a class="office-link" href="/">🏢 Escritório</a>
  </div>
</div>

<div class="page">

  <!-- STATS -->
  <div class="stats" id="stats-row">
    <div class="stat-card"><div class="stat-label">Total de Execuções</div>
      <div class="stat-value" id="stat-total"><div class="skeleton" style="width:60px;height:32px"></div></div>
      <div class="stat-sub">todos os agentes</div></div>
    <div class="stat-card"><div class="stat-label">Agentes Ativos</div>
      <div class="stat-value" id="stat-agents"><div class="skeleton" style="width:40px;height:32px"></div></div>
      <div class="stat-sub">com resultados salvos</div></div>
    <div class="stat-card"><div class="stat-label">Execuções Hoje</div>
      <div class="stat-value" id="stat-today"><div class="skeleton" style="width:40px;height:32px"></div></div>
      <div class="stat-sub" id="stat-today-date">—</div></div>
    <div class="stat-card"><div class="stat-label">Última Execução</div>
      <div class="stat-value" style="font-size:18px" id="stat-last"><div class="skeleton" style="width:100px;height:24px"></div></div>
      <div class="stat-sub" id="stat-last-agent">—</div></div>
  </div>

  <!-- AGENT CARDS -->
  <div class="section-title">Agentes</div>
  <div class="agents-grid" id="agents-grid">
    <!-- populated by JS -->
  </div>

  <!-- CHART -->
  <div class="chart-card">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px">
      <div>
        <div class="section-title" style="margin:0">Atividade — Últimos 7 dias</div>
        <div style="font-size:11px;color:var(--muted);margin-top:2px">Execuções por agente</div>
      </div>
      <div id="chart-legend" style="display:flex;gap:14px;flex-wrap:wrap;justify-content:flex-end"></div>
    </div>
    <div class="chart-wrap"><canvas id="activity-chart"></canvas></div>
  </div>

  <!-- RESULTS TABLE -->
  <div class="table-card">
    <div class="table-header">
      <h3>Resultados Recentes</h3>
      <div style="font-size:11px;color:var(--muted)" id="table-count"></div>
    </div>
    <div style="overflow-x:auto">
      <table>
        <thead><tr>
          <th style="width:14%">Agente</th>
          <th class="td-prompt" style="width:28%">Prompt</th>
          <th class="td-result" style="width:40%">Resultado</th>
          <th class="td-time">Data</th>
          <th style="width:7%"></th>
        </tr></thead>
        <tbody id="results-tbody">
          <tr><td colspan="5" style="text-align:center;padding:32px;color:var(--muted)">
            <div class="spinner" style="margin:0 auto"></div>
          </td></tr>
        </tbody>
      </table>
    </div>
  </div>

</div><!-- /page -->

<!-- RESULT DRAWER -->
<div class="drawer-overlay" id="drawer" onclick="if(event.target===this)closeDrawer()">
  <div class="drawer">
    <div class="drawer-head">
      <h3 id="drawer-title">Resultado</h3>
      <button class="drawer-close" onclick="closeDrawer()">✕</button>
    </div>
    <div class="drawer-prompt" id="drawer-prompt"></div>
    <div class="drawer-body" id="drawer-body"></div>
  </div>
</div>

<!-- RUN MODAL -->
<div class="run-modal-overlay" id="run-modal" onclick="if(event.target===this&&!_running)closeRunModal()">
  <div class="run-modal">
    <h3 id="run-modal-title">Executar Agente</h3>
    <p id="run-modal-subtitle">O resultado será salvo no Supabase automaticamente.</p>
    <textarea id="run-prompt" rows="3"></textarea>
    <div class="run-result" id="run-result"></div>
    <div class="run-modal-btns">
      <button class="btn-cancel2" id="run-cancel-btn" onclick="closeRunModal()">Cancelar</button>
      <button class="btn-run" id="run-submit-btn" onclick="submitRun()">▶ Executar</button>
    </div>
  </div>
</div>

<style>
@keyframes pulse2{0%,100%{opacity:1}50%{opacity:.4}}
</style>

<script>
const BASE = '';  // same-origin — works both on Railway and locally

const AGENTS = [
  {id:'copy',              name:'Sofia',   role:'Especialista em Copy',     color:'#7c3aed', emoji:'✍️',
   endpoint:'/agents/copy',
   defaultPrompt:'Crie 3 variações de copy para e-commerce de suplementos'},
  {id:'creatives',         name:'Lucas',   role:'Diretor de Criativos',     color:'#d97706', emoji:'🎨',
   endpoint:'/agents/creatives',
   defaultPrompt:'Crie briefing visual para anúncio de suplementos no Instagram'},
  {id:'video',             name:'Ana',     role:'Roteirista de Vídeo',      color:'#dc2626', emoji:'🎬',
   endpoint:'/agents/video',
   defaultPrompt:'Crie script de 30 segundos para expert de emagrecimento'},
  {id:'hooks',             name:'Pedro',   role:'Especialista em Hooks',    color:'#059669', emoji:'🪝',
   endpoint:'/agents/hooks',
   defaultPrompt:'Crie 10 hooks para anúncios de suplementos'},
  {id:'researcher',        name:'Marina',  role:'Pesquisadora de Mercado',  color:'#0284c7', emoji:'🔬',
   endpoint:'/agents/researcher',
   defaultPrompt:'Pesquise os nichos de e-commerce mais lucrativos no Brasil agora'},
  {id:'researcher-stores', name:'Isabela', role:'Analista de Lojas Shopify',color:'#0f766e', emoji:'🏪',
   endpoint:'/agents/researcher-stores',
   defaultPrompt:'Encontre 5 oportunidades de lojas Shopify com alto potencial de vendas no Brasil agora'},
];

let _allResults = [];
let _chart = null;
let _running = false;
let _runAgentId = null;

// ── LOAD ──────────────────────────────────────────────────────────────────────
async function loadDashboard() {
  document.getElementById('refresh-icon').innerHTML = '<span class="spinner" style="border-top-color:var(--text)"></span>';
  try {
    const res = await fetch(BASE + '/results?limit=200');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    _allResults = data.results || [];
    renderAll(_allResults);
    const now = new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
    document.getElementById('last-updated').textContent = 'Atualizado às ' + now;
  } catch(e) {
    document.getElementById('last-updated').textContent = 'Erro ao carregar';
    console.error(e);
  }
  document.getElementById('refresh-icon').textContent = '↻';
}

function renderAll(results) {
  renderStats(results);
  renderAgentCards(results);
  renderChart(results);
  renderTable(results);
}

// ── STATS ─────────────────────────────────────────────────────────────────────
function renderStats(results) {
  const today = new Date().toISOString().slice(0,10);
  const todayCount = results.filter(r => r.created_at?.startsWith(today)).length;
  const activeAgents = new Set(results.map(r => r.agent_name)).size;
  const latest = results[0];

  document.getElementById('stat-total').textContent = results.length;
  document.getElementById('stat-agents').textContent = activeAgents;
  document.getElementById('stat-today').textContent = todayCount;
  document.getElementById('stat-today-date').textContent = new Date().toLocaleDateString('pt-BR',{weekday:'short',day:'numeric',month:'short'});
  if (latest) {
    const ago = timeAgo(latest.created_at);
    document.getElementById('stat-last').textContent = ago;
    const a = AGENTS.find(a => a.id === latest.agent_name);
    document.getElementById('stat-last-agent').textContent = a ? a.name + ' — ' + a.role : latest.agent_name;
  } else {
    document.getElementById('stat-last').textContent = '—';
    document.getElementById('stat-last-agent').textContent = 'Nenhuma execução ainda';
  }
}

// ── AGENT CARDS ───────────────────────────────────────────────────────────────
function renderAgentCards(results) {
  const grid = document.getElementById('agents-grid');
  grid.innerHTML = '';
  AGENTS.forEach(agent => {
    const agentResults = results.filter(r => r.agent_name === agent.id);
    const latest = agentResults[0];
    const count = agentResults.length;

    const card = document.createElement('div');
    card.className = 'agent-card';
    card.style.setProperty('--card-color', agent.color);

    card.innerHTML = `
      <div class="agent-card-header">
        <div class="agent-av">${agent.emoji}</div>
        <div>
          <div class="agent-name">${agent.name}</div>
          <div class="agent-role">${agent.role}</div>
        </div>
        <div class="agent-meta">
          <div class="agent-count">${count}</div>
          <div class="agent-count-label">execuções</div>
        </div>
      </div>
      <div class="agent-card-body">
        ${latest
          ? `<div class="result-preview">${escHtml(latest.result).slice(0,280)}${latest.result.length>280?'…':''}</div>
             <div class="result-time">${formatDate(latest.created_at)}</div>`
          : `<div class="empty"><div class="empty-icon">💤</div><div>Nenhum resultado ainda</div></div>`
        }
      </div>
      <div class="agent-card-footer">
        <button class="run-btn" onclick="openRunModal('${agent.id}')">▶ Run Now</button>
        ${latest
          ? `<button class="view-btn" onclick="openDrawer('${agent.id}')">Ver último</button>`
          : ''
        }
      </div>
    `;
    grid.appendChild(card);
  });
}

// ── CHART ─────────────────────────────────────────────────────────────────────
function renderChart(results) {
  // Build last 7 days labels
  const days = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    days.push(d.toISOString().slice(0,10));
  }
  const labels = days.map(d => {
    const dt = new Date(d + 'T12:00:00');
    return dt.toLocaleDateString('pt-BR',{day:'numeric',month:'short'});
  });

  const datasets = AGENTS.map(agent => {
    const data = days.map(day =>
      results.filter(r => r.agent_name === agent.id && r.created_at?.startsWith(day)).length
    );
    return {
      label: agent.name,
      data,
      borderColor: agent.color,
      backgroundColor: agent.color + '22',
      borderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
      tension: 0.4,
      fill: false,
    };
  });

  // Legend
  const legend = document.getElementById('chart-legend');
  legend.innerHTML = AGENTS.map(a =>
    `<div style="display:flex;align-items:center;gap:5px;font-size:11px;color:var(--muted)">
      <div style="width:10px;height:10px;border-radius:50%;background:${a.color}"></div>${a.name}
    </div>`
  ).join('');

  if (_chart) _chart.destroy();
  const ctx = document.getElementById('activity-chart').getContext('2d');
  _chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1e293b',
          borderColor: '#334155',
          borderWidth: 1,
          titleColor: '#f1f5f9',
          bodyColor: '#94a3b8',
          padding: 10,
        }
      },
      scales: {
        x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { size: 11 } } },
        y: {
          grid: { color: '#1e293b' },
          ticks: { color: '#64748b', font: { size: 11 }, stepSize: 1, precision: 0 },
          beginAtZero: true,
        }
      }
    }
  });
}

// ── TABLE ─────────────────────────────────────────────────────────────────────
function renderTable(results) {
  const tbody = document.getElementById('results-tbody');
  document.getElementById('table-count').textContent = results.length + ' resultados';

  if (!results.length) {
    tbody.innerHTML = `<tr><td colspan="5">
      <div class="empty"><div class="empty-icon">📭</div><div>Nenhum resultado ainda. Execute um agente!</div></div>
    </td></tr>`;
    return;
  }

  tbody.innerHTML = results.slice(0, 50).map((r, i) => {
    const agent = AGENTS.find(a => a.id === r.agent_name);
    const color = agent?.color || '#64748b';
    const name  = agent?.name  || r.agent_name;
    return `<tr>
      <td><span class="agent-badge" style="background:${color}22;color:${color}">${agent?.emoji||'🤖'} ${name}</span></td>
      <td class="td-prompt" title="${escHtml(r.prompt)}">${escHtml(r.prompt)}</td>
      <td class="td-result"><div class="td-result-inner">${escHtml(r.result)}</div></td>
      <td class="td-time">${formatDate(r.created_at)}</td>
      <td><button class="view-btn" style="font-size:11px;padding:4px 8px"
          onclick='showDrawer(${JSON.stringify(escHtml(name))},${JSON.stringify(escHtml(r.prompt))},${JSON.stringify(escHtml(r.result))})'>
        Ver
      </button></td>
    </tr>`;
  }).join('');
}

// ── DRAWER ────────────────────────────────────────────────────────────────────
function openDrawer(agentId) {
  const latest = _allResults.find(r => r.agent_name === agentId);
  if (!latest) return;
  const agent = AGENTS.find(a => a.id === agentId);
  showDrawer(agent?.name || agentId, latest.prompt, latest.result);
}

function showDrawer(name, prompt, result) {
  document.getElementById('drawer-title').textContent = name + ' — Último Resultado';
  document.getElementById('drawer-prompt').innerHTML = '<strong>Prompt:</strong> ' + prompt;
  document.getElementById('drawer-body').textContent = result;
  document.getElementById('drawer').classList.add('open');
}

function closeDrawer() {
  document.getElementById('drawer').classList.remove('open');
}

// ── RUN MODAL ─────────────────────────────────────────────────────────────────
function openRunModal(agentId) {
  _runAgentId = agentId;
  _running = false;
  const agent = AGENTS.find(a => a.id === agentId);
  document.getElementById('run-modal-title').textContent = agent.emoji + ' ' + agent.name + ' — Run Now';
  document.getElementById('run-modal-subtitle').textContent = agent.role + ' · resultado salvo no Supabase automaticamente';
  document.getElementById('run-prompt').value = agent.defaultPrompt;
  document.getElementById('run-result').style.display = 'none';
  document.getElementById('run-result').textContent = '';
  document.getElementById('run-submit-btn').disabled = false;
  document.getElementById('run-submit-btn').innerHTML = '▶ Executar';
  document.getElementById('run-submit-btn').style.background = agent.color;
  document.getElementById('run-cancel-btn').textContent = 'Cancelar';
  document.getElementById('run-modal').classList.add('open');
  setTimeout(()=>document.getElementById('run-prompt').focus(), 80);
}

function closeRunModal() {
  if (_running) return;
  document.getElementById('run-modal').classList.remove('open');
  _runAgentId = null;
}

async function submitRun() {
  const prompt = document.getElementById('run-prompt').value.trim();
  if (!prompt || !_runAgentId) return;

  const agent = AGENTS.find(a => a.id === _runAgentId);
  _running = true;
  document.getElementById('run-submit-btn').disabled = true;
  document.getElementById('run-submit-btn').innerHTML = '<span class="spinner"></span> Executando...';
  document.getElementById('run-cancel-btn').textContent = 'Aguarde...';

  try {
    const res = await fetch(BASE + agent.endpoint, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({prompt}),
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({}));
      throw new Error(err.detail || 'HTTP ' + res.status);
    }
    const data = await res.json();
    const resultEl = document.getElementById('run-result');
    resultEl.textContent = data.result;
    resultEl.style.display = 'block';
    document.getElementById('run-submit-btn').innerHTML = '✓ Concluído';
    document.getElementById('run-cancel-btn').textContent = 'Fechar';
    // Refresh data silently
    setTimeout(loadDashboard, 1000);
  } catch(e) {
    const resultEl = document.getElementById('run-result');
    resultEl.textContent = '❌ Erro: ' + e.message;
    resultEl.style.display = 'block';
    document.getElementById('run-submit-btn').innerHTML = '↻ Tentar novamente';
    document.getElementById('run-submit-btn').disabled = false;
  }
  _running = false;
  document.getElementById('run-cancel-btn').textContent = 'Fechar';
}

// ── UTILS ─────────────────────────────────────────────────────────────────────
function escHtml(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'short'}) + ' ' +
         d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
}

function timeAgo(iso) {
  if (!iso) return '—';
  const diff = Math.floor((Date.now() - new Date(iso)) / 1000);
  if (diff < 60)  return diff + 's atrás';
  if (diff < 3600) return Math.floor(diff/60) + 'min atrás';
  if (diff < 86400) return Math.floor(diff/3600) + 'h atrás';
  return Math.floor(diff/86400) + 'd atrás';
}

// Keyboard close
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeDrawer(); if (!_running) closeRunModal(); }
});

// Boot
loadDashboard();
// Auto-refresh every 60s
setInterval(loadDashboard, 60000);
</script>
</body>
</html>"""
