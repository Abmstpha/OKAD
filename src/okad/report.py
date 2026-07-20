"""Plain-language story report."""

from __future__ import annotations

from pathlib import Path

from okad.model import StoryGraph


def generate_report(graph: StoryGraph) -> str:
    lines = [
        f"# OKAD — {graph.system_name}",
        "",
        graph.summary or "_No summary._",
        "",
        "## How to read this map",
        "",
        "OKAD is a **story map**, not a milky-way of every file link.",
        "Read layers top-down: Experience → Interface → Application → Data.",
        "Open `story.html` and switch views: Architecture, Journeys, Requests, Data flow.",
        "",
        "## Stats",
        "",
        f"- Nodes: **{len(graph.nodes)}** (capped for readability)",
        f"- Edges: **{len(graph.edges)}** (story-significant only)",
        f"- Journeys: **{len(graph.journeys)}**",
        f"- Request paths: **{len(graph.requests)}**",
        f"- Data flows: **{len(graph.data_flows)}**",
        "",
    ]

    if graph.journeys:
        lines += ["## User journeys", ""]
        for j in graph.journeys:
            steps = " → ".join(s.node_id for s in j.steps) or "_no steps_"
            lines += [
                f"### {j.name}",
                j.summary or "",
                f"- Actor: `{j.actor}`",
                f"- Path: `{steps}`",
                "",
            ]

    if graph.requests:
        lines += ["## Request paths", ""]
        for r in graph.requests:
            chain = " → ".join(r.steps) or "_no steps_"
            lines += [
                f"### {r.method} {r.route} — {r.name}",
                r.summary or "",
                f"- Chain: `{chain}`",
                "",
            ]

    if graph.data_flows:
        lines += ["## Data flows", ""]
        for d in graph.data_flows:
            thru = " → ".join(d.through) if d.through else "…"
            lines += [
                f"### {d.name}",
                d.summary or "",
                f"- `{d.origin}` → {thru} → `{d.destination}`",
                (f"- Shape: `{d.shape}`" if d.shape else ""),
                "",
            ]

    # Layer rollup
    lines += ["## Layer rollup", ""]
    by_layer: dict[str, list[str]] = {}
    for n in graph.nodes:
        if n.kind == "layer":
            continue
        by_layer.setdefault(n.layer, []).append(n.label)
    for layer in ("experience", "interface", "application", "data", "infra"):
        labels = by_layer.get(layer, [])
        if not labels:
            continue
        preview = ", ".join(labels[:12])
        more = f" (+{len(labels) - 12})" if len(labels) > 12 else ""
        lines.append(f"- **{layer}**: {preview}{more}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_report(graph: StoryGraph, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    text = generate_report(graph)
    out.write_text(text, encoding="utf-8")
    return out
