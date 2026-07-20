"""Structural skeleton extraction — routes, screens, handlers, stores.

Produces a thin skeleton the host LLM enriches into story flows.
Never dumps every import edge — only architecture-significant signals.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from okad.model import Edge, Node, StoryGraph


ROUTE_PATTERNS = [
    # Express / Fastify / Nest / Next route handlers
    re.compile(
        r"""(?:app|router|Router)\.(get|post|put|patch|delete|all)\s*\(\s*['"`]([^'"`]+)['"`]""",
        re.I,
    ),
    re.compile(
        r"""@(Get|Post|Put|Patch|Delete|All)\s*\(\s*['"`]?([^'"`)]*)['"`]?\s*\)""",
        re.I,
    ),
    # FastAPI / Flask
    re.compile(
        r"""@(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]""",
        re.I,
    ),
    re.compile(
        r"""@(?:get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]""",
        re.I,
    ),
    # Next.js app router path from file path handled separately
]

SCREEN_HINTS = re.compile(
    r"(page|screen|view|route|layout|index)\.(tsx|jsx|vue|svelte|ts|js)$",
    re.I,
)
SERVICE_HINTS = re.compile(
    r"(service|controller|handler|usecase|use-case|interactor|manager|provider)\.",
    re.I,
)
STORE_HINTS = re.compile(
    r"(model|schema|entity|repository|repo|dao|migration|prisma|drizzle|sql)",
    re.I,
)
API_DIR_HINTS = re.compile(r"(api|routes|controllers|handlers|endpoints)", re.I)


def extract_skeleton(root: Path, detect: dict[str, Any]) -> StoryGraph:
    root = root.resolve()
    name = root.name
    nodes: list[Node] = []
    edges: list[Edge] = []
    seen: set[str] = set()

    # Layer anchor nodes
    for layer in ("experience", "interface", "application", "data", "infra"):
        nid = f"layer:{layer}"
        nodes.append(
            Node(
                id=nid,
                label=layer.title(),
                kind="layer",
                layer=layer,  # type: ignore[arg-type]
                summary=f"{layer} layer",
            )
        )
        seen.add(nid)

    routes_found = 0
    screens_found = 0
    services_found = 0
    stores_found = 0

    for rel in detect.get("files", {}).get("code", []):
        path = root / rel
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        # Next.js / file-based routes
        if _is_app_route_file(rel):
            route = _file_to_route(rel)
            nid = _id("route", route)
            if nid not in seen:
                nodes.append(
                    Node(
                        id=nid,
                        label=route,
                        kind="route",
                        layer="interface",
                        summary=f"File-based route {route}",
                        source=rel,
                        meta={"method": "ALL", "path": route},
                    )
                )
                seen.add(nid)
                edges.append(
                    Edge(
                        id=_eid(nid, "layer:interface", "contains"),
                        source="layer:interface",
                        target=nid,
                        kind="contains",
                        label="exposes",
                    )
                )
                routes_found += 1
                if SCREEN_HINTS.search(path.name):
                    sid = _id("screen", route)
                    if sid not in seen:
                        nodes.append(
                            Node(
                                id=sid,
                                label=_humanize(route),
                                kind="screen",
                                layer="experience",
                                summary=f"UI for {route}",
                                source=rel,
                            )
                        )
                        seen.add(sid)
                        edges.append(
                            Edge(
                                id=_eid(sid, nid, "triggers"),
                                source=sid,
                                target=nid,
                                kind="triggers",
                                label="hits",
                            )
                        )
                        screens_found += 1

        # Explicit route registrations
        for pat in ROUTE_PATTERNS:
            for m in pat.finditer(text):
                groups = m.groups()
                if len(groups) == 2:
                    method, route_path = groups[0], groups[1] or "/"
                else:
                    method, route_path = "GET", groups[0] or "/"
                method = method.upper()
                if not route_path.startswith("/"):
                    route_path = "/" + route_path
                nid = _id("route", f"{method}:{route_path}")
                if nid in seen:
                    continue
                nodes.append(
                    Node(
                        id=nid,
                        label=f"{method} {route_path}",
                        kind="route",
                        layer="interface",
                        summary=f"{method} {route_path}",
                        source=rel,
                        meta={"method": method, "path": route_path},
                    )
                )
                seen.add(nid)
                edges.append(
                    Edge(
                        id=_eid("layer:interface", nid, "contains"),
                        source="layer:interface",
                        target=nid,
                        kind="contains",
                    )
                )
                routes_found += 1

        # Classify notable modules (not every file)
        if SERVICE_HINTS.search(rel) or API_DIR_HINTS.search(rel):
            label = _module_label(path)
            nid = _id("service", rel)
            if nid not in seen and _looks_like_logic(text):
                nodes.append(
                    Node(
                        id=nid,
                        label=label,
                        kind="service",
                        layer="application",
                        summary=f"Application module {label}",
                        source=rel,
                    )
                )
                seen.add(nid)
                edges.append(
                    Edge(
                        id=_eid("layer:application", nid, "contains"),
                        source="layer:application",
                        target=nid,
                        kind="contains",
                    )
                )
                services_found += 1

        if STORE_HINTS.search(rel):
            label = _module_label(path)
            nid = _id("store", rel)
            if nid not in seen:
                nodes.append(
                    Node(
                        id=nid,
                        label=label,
                        kind="store" if "repo" in rel.lower() or "dao" in rel.lower() else "entity",
                        layer="data",
                        summary=f"Data module {label}",
                        source=rel,
                    )
                )
                seen.add(nid)
                edges.append(
                    Edge(
                        id=_eid("layer:data", nid, "contains"),
                        source="layer:data",
                        target=nid,
                        kind="contains",
                    )
                )
                stores_found += 1

        # Screens from UI dirs
        if any(p in rel.lower() for p in ("/pages/", "/views/", "/screens/", "/components/")):
            if path.suffix.lower() in {".tsx", ".jsx", ".vue", ".svelte"} and path.stem[0].isupper():
                label = _humanize(path.stem)
                nid = _id("screen", rel)
                if nid not in seen and len(text) > 80:
                    nodes.append(
                        Node(
                            id=nid,
                            label=label,
                            kind="screen",
                            layer="experience",
                            summary=f"UI surface {label}",
                            source=rel,
                        )
                    )
                    seen.add(nid)
                    edges.append(
                        Edge(
                            id=_eid("layer:experience", nid, "contains"),
                            source="layer:experience",
                            target=nid,
                            kind="contains",
                        )
                    )
                    screens_found += 1

    # Cap skeleton size — elegance over exhaustiveness
    nodes, edges = _cap_skeleton(nodes, edges, max_per_layer=24)

    graph = StoryGraph(
        system_name=name,
        summary=(
            f"Structural skeleton for {name}: "
            f"{routes_found} routes, {screens_found} screens, "
            f"{services_found} services, {stores_found} data modules."
        ),
        nodes=nodes,
        edges=edges,
        meta={
            "phase": "skeleton",
            "routes": routes_found,
            "screens": screens_found,
            "services": services_found,
            "stores": stores_found,
            "root": str(root),
        },
    )
    graph.prune_orphan_edges()
    return graph


def skeleton_brief(graph: StoryGraph) -> str:
    """Compact brief for the host LLM — not a milky-way dump."""
    by_layer: dict[str, list[Node]] = {}
    for n in graph.nodes:
        if n.kind == "layer":
            continue
        by_layer.setdefault(n.layer, []).append(n)

    lines = [
        f"# Skeleton: {graph.system_name}",
        graph.summary,
        "",
        "Use these as seeds. Produce a STORY graph: journeys, request paths, data flows.",
        "Label nodes by role (Checkout, Auth gate), never by filename.",
        "Keep top-level under ~40 nodes. Aggregate noise into layer hubs.",
        "",
    ]
    for layer in ("experience", "interface", "application", "data", "infra"):
        items = by_layer.get(layer, [])
        if not items:
            continue
        lines.append(f"## {layer}")
        for n in items[:20]:
            src = f"  [{n.source}]" if n.source else ""
            lines.append(f"- {n.id} · {n.label} ({n.kind}){src}")
        if len(items) > 20:
            lines.append(f"- … +{len(items) - 20} more")
        lines.append("")
    return "\n".join(lines)


def write_skeleton(graph: StoryGraph, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph.to_dict(), indent=2), encoding="utf-8")


def _cap_skeleton(
    nodes: list[Node], edges: list[Edge], max_per_layer: int = 24
) -> tuple[list[Node], list[Edge]]:
    kept: list[Node] = []
    counts: dict[str, int] = {}
    kept_ids: set[str] = set()
    for n in nodes:
        if n.kind == "layer":
            kept.append(n)
            kept_ids.add(n.id)
            continue
        c = counts.get(n.layer, 0)
        if c >= max_per_layer:
            continue
        counts[n.layer] = c + 1
        kept.append(n)
        kept_ids.add(n.id)
    kept_edges = [e for e in edges if e.source in kept_ids and e.target in kept_ids]
    return kept, kept_edges


def _is_app_route_file(rel: str) -> bool:
    p = rel.replace("\\", "/").lower()
    return bool(
        re.search(r"(^|/)(app|pages)/.+\.(tsx?|jsx?|vue|svelte)$", p)
        or re.search(r"(^|/)routes?/.+\.(tsx?|jsx?|py|go|rs)$", p)
    )


def _file_to_route(rel: str) -> str:
    p = rel.replace("\\", "/")
    p = re.sub(r"^.*?/(app|pages)/", "/", p)
    p = re.sub(r"\.(tsx?|jsx?|vue|svelte)$", "", p)
    p = re.sub(r"/page$", "", p)
    p = re.sub(r"/index$", "", p)
    p = re.sub(r"/layout$", "", p)
    p = re.sub(r"/route$", "", p)
    p = re.sub(r"\[([^\]]+)\]", r":\1", p)
    if not p.startswith("/"):
        p = "/" + p
    if p == "/":
        return "/"
    return p.rstrip("/") or "/"


def _module_label(path: Path) -> str:
    stem = path.stem
    for suffix in (
        "Service",
        "Controller",
        "Handler",
        "Repository",
        "Repo",
        "Model",
        "Schema",
        "Entity",
    ):
        if stem.endswith(suffix) and len(stem) > len(suffix):
            stem = stem[: -len(suffix)]
            break
    return _humanize(stem)


def _humanize(value: str) -> str:
    value = value.strip("/").replace("-", " ").replace("_", " ").replace(".", " ")
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", value)
    parts = [p for p in value.split() if p]
    if not parts:
        return "Home"
    return " ".join(p[:1].upper() + p[1:] for p in parts)


def _looks_like_logic(text: str) -> bool:
    return len(text) > 120 and (
        "def " in text
        or "function " in text
        or "class " in text
        or "export " in text
        or "async " in text
    )


def _id(kind: str, raw: str) -> str:
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    safe = re.sub(r"[^a-zA-Z0-9:_/-]+", "-", raw)[:48].strip("-")
    return f"{kind}:{safe}:{digest}"


def _eid(a: str, b: str, kind: str) -> str:
    digest = hashlib.sha1(f"{a}|{b}|{kind}".encode()).hexdigest()[:12]
    return f"e:{digest}"
