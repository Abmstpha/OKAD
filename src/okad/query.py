"""Query helpers over an OKAD story graph."""

from __future__ import annotations

import json
import re
from pathlib import Path

import networkx as nx

from okad.merge import load_story
from okad.model import StoryGraph


def load_graph(path: Path | None = None) -> StoryGraph:
    path = path or Path("okad-out/story.json")
    if not path.exists():
        raise FileNotFoundError(f"No story graph at {path}. Run /okad first.")
    return load_story(path)


def to_nx(graph: StoryGraph) -> nx.DiGraph:
    G = nx.DiGraph()
    for n in graph.nodes:
        G.add_node(n.id, **n.to_dict())
    for e in graph.edges:
        G.add_edge(e.source, e.target, **e.to_dict())
    # Journey / request / data soft edges for traversal
    for j in graph.journeys:
        ids = [s.node_id for s in j.steps]
        for a, b in zip(ids, ids[1:]):
            if a in G and b in G:
                G.add_edge(a, b, kind="navigates", label=j.name)
    for r in graph.requests:
        for a, b in zip(r.steps, r.steps[1:]):
            if a in G and b in G:
                G.add_edge(a, b, kind="calls", label=r.name)
    for d in graph.data_flows:
        chain = [d.origin, *d.through, d.destination]
        chain = [c for c in chain if c]
        for a, b in zip(chain, chain[1:]):
            if a in G and b in G:
                G.add_edge(a, b, kind="transforms", label=d.name)
    return G


def query(question: str, graph: StoryGraph | None = None, budget: int = 1800) -> str:
    graph = graph or load_graph()
    G = to_nx(graph)
    tokens = _tokens(question)
    scored: list[tuple[int, str]] = []
    for nid, data in G.nodes(data=True):
        blob = " ".join(
            str(data.get(k, "")) for k in ("label", "summary", "kind", "layer", "source", "id")
        ).lower()
        score = sum(1 for t in tokens if t in blob)
        if score:
            scored.append((score, nid))
    scored.sort(reverse=True)
    seeds = [nid for _, nid in scored[:5]]
    if not seeds:
        # fall back to journeys matching words
        for j in graph.journeys:
            if any(t in j.name.lower() or t in j.summary.lower() for t in tokens):
                seeds.extend(s.node_id for s in j.steps[:3])
        seeds = seeds[:5]

    lines = [f"# OKAD query", f"Q: {question}", ""]
    if graph.journeys:
        hits = [
            j
            for j in graph.journeys
            if any(t in (j.name + " " + j.summary).lower() for t in tokens) or not tokens
        ][:3]
        if hits:
            lines.append("## Matching journeys")
            for j in hits:
                chain = " → ".join(s.node_id for s in j.steps)
                lines.append(f"- **{j.name}**: {j.summary} `{chain}`")
            lines.append("")

    if graph.requests:
        hits = [
            r
            for r in graph.requests
            if any(t in (r.name + " " + r.route + " " + r.summary).lower() for t in tokens)
        ][:5]
        if hits:
            lines.append("## Matching request paths")
            for r in hits:
                chain = " → ".join(r.steps)
                lines.append(f"- **{r.method} {r.route}** ({r.name}): {r.summary} `{chain}`")
            lines.append("")

    if not seeds:
        lines.append("No strong node matches. Try `okad explain` on a layer or journey name.")
        return _trim("\n".join(lines), budget)

    lines.append("## Neighborhood")
    seen: set[str] = set()
    for seed in seeds:
        data = G.nodes[seed]
        lines.append(f"### {data.get('label', seed)} (`{seed}`)")
        lines.append(f"- layer: {data.get('layer')} · kind: {data.get('kind')}")
        if data.get("summary"):
            lines.append(f"- {data['summary']}")
        if data.get("source"):
            lines.append(f"- source: `{data['source']}`")
        for _, tgt, edata in G.out_edges(seed, data=True):
            key = f"{seed}->{tgt}"
            if key in seen:
                continue
            seen.add(key)
            tlabel = G.nodes[tgt].get("label", tgt)
            lines.append(f"- → {tlabel} [{edata.get('kind', 'rel')}]")
        for src, _, edata in G.in_edges(seed, data=True):
            key = f"{src}->{seed}"
            if key in seen:
                continue
            seen.add(key)
            slabel = G.nodes[src].get("label", src)
            lines.append(f"- ← {slabel} [{edata.get('kind', 'rel')}]")
        lines.append("")

    return _trim("\n".join(lines), budget)


def path_between(a: str, b: str, graph: StoryGraph | None = None) -> str:
    graph = graph or load_graph()
    G = to_nx(graph)
    src = _resolve(G, a)
    dst = _resolve(G, b)
    if not src or not dst:
        return f"Could not resolve endpoints: {a!r} → {b!r}"
    try:
        nodes = nx.shortest_path(G, src, dst)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        try:
            nodes = nx.shortest_path(G.to_undirected(), src, dst)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return f"No path between {a} and {b}."
    parts = []
    for nid in nodes:
        n = G.nodes[nid]
        parts.append(f"{n.get('label', nid)} [{n.get('layer')}/{n.get('kind')}]")
    return " → ".join(parts)


def explain(name: str, graph: StoryGraph | None = None) -> str:
    graph = graph or load_graph()
    G = to_nx(graph)
    nid = _resolve(G, name)
    if not nid:
        # try journeys
        for j in graph.journeys:
            if name.lower() in j.name.lower():
                steps = " → ".join(s.node_id for s in j.steps)
                return f"# {j.name}\n{j.summary}\n\nSteps: `{steps}`\n"
        return f"Nothing named like {name!r} in the story map."
    n = G.nodes[nid]
    lines = [
        f"# {n.get('label', nid)}",
        n.get("summary") or "",
        "",
        f"- id: `{nid}`",
        f"- kind: {n.get('kind')} · layer: {n.get('layer')}",
    ]
    if n.get("source"):
        lines.append(f"- source: `{n['source']}`")
    outs = list(G.out_edges(nid, data=True))[:12]
    inns = list(G.in_edges(nid, data=True))[:12]
    if outs:
        lines.append("\n## Out")
        for _, t, e in outs:
            lines.append(f"- → {G.nodes[t].get('label', t)} ({e.get('kind')})")
    if inns:
        lines.append("\n## In")
        for s, _, e in inns:
            lines.append(f"- ← {G.nodes[s].get('label', s)} ({e.get('kind')})")
    # related journeys
    related = [
        j.name
        for j in graph.journeys
        if any(s.node_id == nid for s in j.steps)
    ]
    if related:
        lines.append("\n## Journeys")
        for name_ in related:
            lines.append(f"- {name_}")
    return "\n".join(lines).rstrip() + "\n"


def _resolve(G: nx.DiGraph, needle: str) -> str | None:
    needle_l = needle.lower()
    if needle in G:
        return needle
    for nid, data in G.nodes(data=True):
        if data.get("label", "").lower() == needle_l:
            return nid
    for nid, data in G.nodes(data=True):
        if needle_l in data.get("label", "").lower() or needle_l in nid.lower():
            return nid
    return None


def _tokens(q: str) -> list[str]:
    stop = {"the", "a", "an", "of", "to", "and", "or", "how", "what", "where", "does", "is", "in"}
    return [t for t in re.findall(r"[a-z0-9_/-]+", q.lower()) if t not in stop and len(t) > 1]


def _trim(text: str, budget: int) -> str:
    # rough token budget ~ chars/4
    max_chars = budget * 4
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20] + "\n\n…truncated\n"
