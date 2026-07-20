"""Render an elegant multi-view story map (not a milky-way force graph)."""

from __future__ import annotations

import json
from pathlib import Path

from okad.model import StoryGraph

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>OKAD — __SYSTEM_NAME__</title>
<style>
  :root {
    --bg: #0f1412;
    --bg-elev: #171d1a;
    --ink: #e8efe9;
    --muted: #8a9a90;
    --line: #2a3530;
    --accent: #3dba8a;
    --accent-2: #e2b15c;
    --experience: #7ec8ff;
    --interface: #3dba8a;
    --application: #e2b15c;
    --data: #e87a6b;
    --infra: #c49bff;
    --danger: #e87a6b;
    --font-display: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
    --font-body: "IBM Plex Sans", "Segoe UI", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, monospace;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; background: var(--bg); color: var(--ink); font-family: var(--font-body); }
  body {
    background:
      radial-gradient(1200px 600px at 10% -10%, #1a2a24 0%, transparent 55%),
      radial-gradient(900px 500px at 100% 0%, #1c1a28 0%, transparent 50%),
      var(--bg);
  }
  header {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 1rem;
    align-items: end;
    padding: 1.25rem 1.5rem 1rem;
    border-bottom: 1px solid var(--line);
  }
  .brand {
    font-family: var(--font-display);
    font-size: clamp(1.8rem, 3vw, 2.6rem);
    letter-spacing: 0.04em;
    line-height: 1;
    margin: 0;
  }
  .brand span { color: var(--accent); }
  .tagline { color: var(--muted); margin: 0.4rem 0 0; max-width: 52ch; font-size: 0.95rem; }
  .tabs { display: flex; gap: 0.35rem; flex-wrap: wrap; justify-content: flex-end; }
  .tab {
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    padding: 0.45rem 0.85rem;
    font: inherit;
    cursor: pointer;
  }
  .tab[aria-selected="true"] {
    color: var(--bg);
    background: var(--accent);
    border-color: var(--accent);
  }
  main { display: grid; grid-template-columns: 280px 1fr; min-height: calc(100vh - 110px); }
  aside {
    border-right: 1px solid var(--line);
    padding: 1rem;
    overflow: auto;
    background: color-mix(in srgb, var(--bg-elev) 88%, transparent);
  }
  aside h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); margin: 0 0 0.75rem; }
  .list { display: flex; flex-direction: column; gap: 0.4rem; }
  .item {
    text-align: left;
    width: 100%;
    background: transparent;
    border: 1px solid transparent;
    color: var(--ink);
    padding: 0.55rem 0.65rem;
    cursor: pointer;
    font: inherit;
  }
  .item:hover, .item.active { border-color: var(--line); background: var(--bg-elev); }
  .item small { display: block; color: var(--muted); margin-top: 0.2rem; }
  .stage { position: relative; overflow: hidden; }
  svg { width: 100%; height: calc(100vh - 110px); display: block; }
  .layer-label { fill: var(--muted); font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; font-family: var(--font-body); }
  .node rect { stroke-width: 1; cursor: pointer; }
  .node text { fill: var(--ink); font-size: 12px; pointer-events: none; font-family: var(--font-body); }
  .node .sub { fill: var(--muted); font-size: 10px; }
  .edge { fill: none; stroke-opacity: 0.55; stroke-width: 1.4; }
  .edge.hot { stroke-opacity: 1; stroke-width: 2.2; }
  .node.dim { opacity: 0.18; }
  .edge.dim { stroke-opacity: 0.08; }
  .legend {
    position: absolute; left: 1rem; bottom: 1rem;
    display: flex; gap: 0.75rem; flex-wrap: wrap;
    background: color-mix(in srgb, var(--bg) 80%, transparent);
    border: 1px solid var(--line);
    padding: 0.55rem 0.75rem;
    font-size: 0.78rem; color: var(--muted);
  }
  .swatch { width: 0.65rem; height: 0.65rem; display: inline-block; margin-right: 0.3rem; }
  .inspector {
    position: absolute; right: 1rem; top: 1rem; width: min(320px, 90%);
    background: color-mix(in srgb, var(--bg-elev) 92%, transparent);
    border: 1px solid var(--line);
    padding: 1rem;
    display: none;
  }
  .inspector.open { display: block; }
  .inspector h3 { margin: 0 0 0.35rem; font-family: var(--font-display); font-weight: 500; }
  .inspector p { margin: 0; color: var(--muted); font-size: 0.9rem; line-height: 1.45; }
  .inspector .meta { margin-top: 0.75rem; font-family: var(--font-mono); font-size: 0.72rem; color: var(--muted); }
  .empty { padding: 3rem; color: var(--muted); }
  @media (max-width: 900px) {
    main { grid-template-columns: 1fr; }
    aside { border-right: 0; border-bottom: 1px solid var(--line); max-height: 220px; }
    svg { height: 70vh; }
  }
</style>
</head>
<body>
<header>
  <div>
    <h1 class="brand">OKAD <span>__SYSTEM_NAME__</span></h1>
    <p class="tagline">__SUMMARY__</p>
  </div>
  <div class="tabs" role="tablist">
    <button class="tab" data-view="architecture" aria-selected="true">Architecture</button>
    <button class="tab" data-view="journeys">Journeys</button>
    <button class="tab" data-view="requests">Requests</button>
    <button class="tab" data-view="data">Data flow</button>
  </div>
</header>
<main>
  <aside>
    <h2 id="side-title">Stories</h2>
    <div class="list" id="side-list"></div>
  </aside>
  <section class="stage">
    <svg id="canvas"></svg>
    <div class="legend" id="legend"></div>
    <div class="inspector" id="inspector">
      <h3 id="ins-title"></h3>
      <p id="ins-body"></p>
      <div class="meta" id="ins-meta"></div>
    </div>
  </section>
</main>
<script>
const DATA = __DATA__;
const COLORS = {
  experience: getComputedStyle(document.documentElement).getPropertyValue('--experience').trim() || '#7ec8ff',
  interface: '#3dba8a',
  application: '#e2b15c',
  data: '#e87a6b',
  infra: '#c49bff',
};
const LAYER_ORDER = ['experience','interface','application','data','infra'];

let view = 'architecture';
let focusId = null;

const svg = document.getElementById('canvas');
const sideList = document.getElementById('side-list');
const sideTitle = document.getElementById('side-title');
const inspector = document.getElementById('inspector');
const legend = document.getElementById('legend');

document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(b => b.setAttribute('aria-selected', 'false'));
    btn.setAttribute('aria-selected', 'true');
    view = btn.dataset.view;
    focusId = null;
    render();
  });
});

function nodeMap() {
  const m = {};
  (DATA.nodes || []).forEach(n => m[n.id] = n);
  return m;
}

function render() {
  const W = svg.clientWidth || window.innerWidth - 280;
  const H = svg.clientHeight || window.innerHeight - 110;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = '';
  legend.innerHTML = LAYER_ORDER.map(l =>
    `<span><i class="swatch" style="background:${COLORS[l]}"></i>${l}</span>`
  ).join('');

  if (view === 'architecture') renderArchitecture(W, H);
  else if (view === 'journeys') renderPathView(W, H, 'journeys');
  else if (view === 'requests') renderPathView(W, H, 'requests');
  else renderPathView(W, H, 'data');
}

function renderArchitecture(W, H) {
  sideTitle.textContent = 'Layers & hubs';
  const nodes = (DATA.nodes || []).filter(n => n.kind !== 'layer');
  const byLayer = {};
  LAYER_ORDER.forEach(l => byLayer[l] = []);
  nodes.forEach(n => {
    const layer = byLayer[n.layer] ? n.layer : 'application';
    byLayer[layer].push(n);
  });

  sideList.innerHTML = LAYER_ORDER.map(l => {
    const count = byLayer[l].length;
    return `<button class="item" data-id="layer:${l}"><strong>${l}</strong><small>${count} nodes · ${(DATA.layers||[]).find(x=>x.id===l)?.blurb||''}</small></button>`;
  }).join('');
  bindSide();

  const padX = 40, padY = 48;
  const colW = (W - padX * 2) / LAYER_ORDER.length;

  // column bands
  LAYER_ORDER.forEach((l, i) => {
    const x = padX + i * colW;
    const g = el('g');
    const rect = el('rect', {
      x, y: padY - 28, width: colW - 16, height: H - padY - 20,
      fill: 'transparent', stroke: '#2a3530', 'stroke-dasharray': '3 6', opacity: 0.7
    });
    const label = el('text', { x: x + 8, y: 28, class: 'layer-label' });
    label.textContent = l;
    g.appendChild(rect); g.appendChild(label); svg.appendChild(g);
  });

  const positions = {};
  LAYER_ORDER.forEach((l, i) => {
    const items = byLayer[l].slice(0, 14);
    const x = padX + i * colW + (colW - 16) / 2;
    const gap = Math.min(56, (H - padY - 40) / Math.max(items.length, 1));
    items.forEach((n, idx) => {
      positions[n.id] = { x, y: padY + 20 + idx * gap, n };
    });
  });

  const edges = (DATA.edges || []).filter(e =>
    positions[e.source] && positions[e.target] && e.kind !== 'contains'
  );
  edges.forEach(e => drawEdge(positions[e.source], positions[e.target], e));
  Object.values(positions).forEach(p => drawNode(p));
}

function renderPathView(W, H, mode) {
  const nm = nodeMap();
  let items = [];
  if (mode === 'journeys') {
    sideTitle.textContent = 'User journeys';
    items = DATA.journeys || [];
  } else if (mode === 'requests') {
    sideTitle.textContent = 'Request paths';
    items = DATA.requests || [];
  } else {
    sideTitle.textContent = 'Data flows';
    items = DATA.data_flows || [];
  }

  if (!items.length) {
    sideList.innerHTML = `<div class="empty">No ${mode} yet. Re-run /okad so the model can author them.</div>`;
    svg.innerHTML = `<text x="40" y="80" fill="#8a9a90" font-size="16">No ${mode} in this map.</text>`;
    return;
  }

  if (!focusId) focusId = items[0].id;
  sideList.innerHTML = items.map(it => {
    const sub = it.summary || it.route || it.shape || '';
    return `<button class="item ${it.id===focusId?'active':''}" data-id="${it.id}"><strong>${esc(it.name)}</strong><small>${esc(sub)}</small></button>`;
  }).join('');
  bindSide();

  const current = items.find(i => i.id === focusId) || items[0];
  let stepIds = [];
  if (mode === 'journeys') stepIds = (current.steps || []).map(s => s.node_id || s);
  else if (mode === 'requests') stepIds = current.steps || [];
  else stepIds = [current.origin, ...(current.through||[]), current.destination].filter(Boolean);

  // tree / sequence layout left → right
  const unique = [];
  stepIds.forEach(id => { if (id && !unique.includes(id)) unique.push(id); });
  if (!unique.length) {
    svg.innerHTML = `<text x="40" y="80" fill="#8a9a90">This story has no steps yet.</text>`;
    return;
  }

  const padX = 80, padY = H / 2;
  const gap = Math.min(180, (W - padX * 2) / Math.max(unique.length - 1, 1));
  const positions = {};
  unique.forEach((id, i) => {
    const n = nm[id] || { id, label: id, layer: 'application', kind: 'service', summary: '' };
    positions[id] = { x: padX + i * gap, y: padY + (i % 2 === 0 ? -40 : 40), n };
  });

  for (let i = 0; i < unique.length - 1; i++) {
    drawEdge(positions[unique[i]], positions[unique[i+1]], { kind: 'calls', label: '' }, true);
  }
  Object.values(positions).forEach(p => drawNode(p, true));

  // title
  const t = el('text', { x: 40, y: 40, fill: '#e8efe9', 'font-size': 18, 'font-family': 'Georgia, serif' });
  t.textContent = current.name;
  svg.appendChild(t);
  const s = el('text', { x: 40, y: 62, fill: '#8a9a90', 'font-size': 12 });
  s.textContent = current.summary || `${current.method || ''} ${current.route || ''}`.trim();
  svg.appendChild(s);
}

function drawNode(p, hot=false) {
  const n = p.n;
  const g = el('g', { class: `node ${focusRelated(n.id) ? '' : (focusId && view==='architecture' ? '' : '')}`, transform: `translate(${p.x},${p.y})` });
  const label = (n.label || n.id).slice(0, 28);
  const w = Math.max(110, Math.min(160, label.length * 7.2 + 24));
  const h = 44;
  const color = COLORS[n.layer] || '#8a9a90';
  const rect = el('rect', {
    x: -w/2, y: -h/2, width: w, height: h,
    rx: 2, fill: '#171d1a', stroke: color, opacity: hot ? 1 : 0.95
  });
  const t = el('text', { x: 0, y: -2, 'text-anchor': 'middle' });
  t.textContent = label;
  const sub = el('text', { x: 0, y: 14, 'text-anchor': 'middle', class: 'sub' });
  sub.textContent = n.kind;
  g.appendChild(rect); g.appendChild(t); g.appendChild(sub);
  g.addEventListener('click', () => showInspector(n));
  svg.appendChild(g);
}

function drawEdge(a, b, e, hot=false) {
  const path = el('path', {
    class: `edge ${hot ? 'hot' : ''}`,
    d: `M ${a.x} ${a.y} C ${(a.x+b.x)/2} ${a.y}, ${(a.x+b.x)/2} ${b.y}, ${b.x} ${b.y}`,
    stroke: COLORS[a.n.layer] || '#8a9a90'
  });
  svg.appendChild(path);
}

function focusRelated(id) {
  return !focusId || focusId === id || String(focusId).endsWith(id);
}

function bindSide() {
  sideList.querySelectorAll('.item').forEach(btn => {
    btn.addEventListener('click', () => {
      focusId = btn.dataset.id;
      if (view === 'architecture' && focusId.startsWith('layer:')) {
        const layer = focusId.split(':')[1];
        const first = (DATA.nodes||[]).find(n => n.layer === layer && n.kind !== 'layer');
        if (first) showInspector(first);
      } else if (view !== 'architecture') {
        render();
        return;
      }
      sideList.querySelectorAll('.item').forEach(b => b.classList.toggle('active', b.dataset.id === focusId));
    });
  });
}

function showInspector(n) {
  inspector.classList.add('open');
  document.getElementById('ins-title').textContent = n.label || n.id;
  document.getElementById('ins-body').textContent = n.summary || 'No summary.';
  document.getElementById('ins-meta').textContent = [
    n.kind && `kind: ${n.kind}`,
    n.layer && `layer: ${n.layer}`,
    n.source && `source: ${n.source}`,
  ].filter(Boolean).join('\n');
}

function el(name, attrs={}) {
  const node = document.createElementNS('http://www.w3.org/2000/svg', name);
  Object.entries(attrs).forEach(([k,v]) => node.setAttribute(k, v));
  return node;
}
function esc(s) {
  return String(s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

window.addEventListener('resize', render);
render();
</script>
</body>
</html>
"""


def render_html(graph: StoryGraph, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(graph.to_dict(), ensure_ascii=False)
    # Escape </script> in JSON
    data = data.replace("<", "\\u003c").replace(">", "\\u003e")
    html = (
        TEMPLATE.replace("__SYSTEM_NAME__", _esc(graph.system_name))
        .replace("__SUMMARY__", _esc(graph.summary or "Story-driven architecture map"))
        .replace("__DATA__", data)
    )
    out.write_text(html, encoding="utf-8")
    return out


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
