"""Merge host-LLM story JSON into a validated StoryGraph."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from okad.model import (
    Agent,
    AgentRelation,
    AgentTool,
    DataFlow,
    Edge,
    Journey,
    JourneyStep,
    Node,
    RequestPath,
    StoryGraph,
)


def load_story(path: Path) -> StoryGraph:
    data = json.loads(path.read_text(encoding="utf-8"))
    return StoryGraph.from_dict(data)


def save_story(graph: StoryGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph.to_dict(), indent=2), encoding="utf-8")


def merge_story(skeleton: StoryGraph, story: dict[str, Any]) -> StoryGraph:
    """Validate and merge LLM story output onto the structural skeleton."""
    nodes: dict[str, Node] = {n.id: n for n in skeleton.nodes}
    edges: dict[str, Edge] = {e.id: e for e in skeleton.edges}

    for raw in story.get("nodes", []):
        nid = str(raw.get("id") or "").strip()
        if not nid:
            continue
        node = Node(
            id=nid,
            label=str(raw.get("label") or nid),
            kind=raw.get("kind") or "service",  # type: ignore[arg-type]
            layer=raw.get("layer") or "application",  # type: ignore[arg-type]
            summary=str(raw.get("summary") or ""),
            source=raw.get("source"),
            meta=dict(raw.get("meta") or {}),
        )
        nodes[nid] = node

    for raw in story.get("edges", []):
        src, tgt = raw.get("source"), raw.get("target")
        if not src or not tgt:
            continue
        eid = str(raw.get("id") or f"e:{src}->{tgt}:{raw.get('kind', 'calls')}")
        edges[eid] = Edge(
            id=eid,
            source=str(src),
            target=str(tgt),
            kind=raw.get("kind") or "calls",  # type: ignore[arg-type]
            label=str(raw.get("label") or ""),
            confidence=raw.get("confidence") or "inferred",  # type: ignore[arg-type]
            meta=dict(raw.get("meta") or {}),
        )

    journeys: list[Journey] = []
    for raw in story.get("journeys", []):
        steps = [
            JourneyStep(node_id=str(s.get("node_id") or s), note=str(s.get("note") or ""))
            if isinstance(s, dict)
            else JourneyStep(node_id=str(s))
            for s in raw.get("steps", [])
        ]
        journeys.append(
            Journey(
                id=str(raw.get("id") or _slug(raw.get("name", "journey"))),
                name=str(raw.get("name") or "Journey"),
                summary=str(raw.get("summary") or ""),
                actor=str(raw.get("actor") or "user"),
                steps=steps,
            )
        )

    requests: list[RequestPath] = []
    for raw in story.get("requests", []):
        requests.append(
            RequestPath(
                id=str(raw.get("id") or _slug(raw.get("name", "request"))),
                name=str(raw.get("name") or "Request"),
                method=str(raw.get("method") or "GET").upper(),
                route=str(raw.get("route") or "/"),
                summary=str(raw.get("summary") or ""),
                steps=[str(s) for s in raw.get("steps", [])],
                status=[str(s) for s in raw.get("status", [])],
            )
        )

    data_flows: list[DataFlow] = []
    for raw in story.get("data_flows", []):
        data_flows.append(
            DataFlow(
                id=str(raw.get("id") or _slug(raw.get("name", "flow"))),
                name=str(raw.get("name") or "Data flow"),
                summary=str(raw.get("summary") or ""),
                origin=str(raw.get("origin") or ""),
                destination=str(raw.get("destination") or ""),
                through=[str(s) for s in raw.get("through", [])],
                shape=str(raw.get("shape") or ""),
            )
        )

    agents: list[Agent] = []
    for raw in story.get("agents", []) or []:
        tools: list[AgentTool] = []
        for t in raw.get("tools", []) or []:
            if isinstance(t, dict):
                tools.append(
                    AgentTool(
                        id=str(t.get("id") or t.get("name") or "tool"),
                        name=str(t.get("name") or t.get("id") or "Tool"),
                        summary=str(t.get("summary") or ""),
                        source=t.get("source"),
                    )
                )
            else:
                tools.append(AgentTool(id=str(t), name=_human(str(t))))
        relations = [
            AgentRelation(
                target=str(r.get("target") or ""),
                kind=str(r.get("kind") or "calls"),
                label=str(r.get("label") or ""),
            )
            for r in (raw.get("relations") or [])
            if isinstance(r, dict) and r.get("target")
        ]
        agents.append(
            Agent(
                id=str(raw.get("id") or _slug(raw.get("name", "agent"))),
                name=str(raw.get("name") or "Agent"),
                summary=str(raw.get("summary") or ""),
                role=str(raw.get("role") or ""),
                level=str(raw.get("level") or "orchestrator"),
                parent_id=raw.get("parent_id"),
                node_id=raw.get("node_id"),
                flow=[str(x) for x in (raw.get("flow") or [])],
                relations=relations,
                tools=tools,
            )
        )

    # Ensure journey/request/data nodes exist as references when missing
    for j in journeys:
        for step in j.steps:
            if step.node_id not in nodes:
                nodes[step.node_id] = Node(
                    id=step.node_id,
                    label=_human(step.node_id),
                    kind="action",
                    layer="experience",
                    summary=step.note or "Journey step",
                )

    graph = StoryGraph(
        system_name=str(story.get("system_name") or skeleton.system_name),
        summary=str(story.get("summary") or skeleton.summary),
        nodes=list(nodes.values()),
        edges=list(edges.values()),
        journeys=journeys,
        requests=requests,
        data_flows=data_flows,
        agents=agents,
        version=2,
        meta={
            **skeleton.meta,
            "phase": "story",
            "journey_count": len(journeys),
            "request_count": len(requests),
            "data_flow_count": len(data_flows),
            "agent_count": len(agents),
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
    )
    graph.prune_orphan_edges()
    return _elegance_cap(graph)


def _elegance_cap(graph: StoryGraph, max_nodes: int = 60) -> StoryGraph:
    """Hard cap so viz stays readable — keep journeys/requests/data hubs first."""
    if len(graph.nodes) <= max_nodes:
        return graph

    priority: dict[str, int] = {}
    for n in graph.nodes:
        score = 0
        if n.kind == "layer":
            score = 1000
        elif n.kind in {"journey", "screen", "route"}:
            score = 100
        elif n.kind in {"handler", "service"}:
            score = 80
        elif n.kind in {"store", "entity"}:
            score = 70
        else:
            score = 40
        # Boost if referenced by journeys/requests/flows
        for j in graph.journeys:
            if any(s.node_id == n.id for s in j.steps):
                score += 50
        for r in graph.requests:
            if n.id in r.steps or n.label in (r.name, r.route):
                score += 40
        for d in graph.data_flows:
            if n.id in {d.origin, d.destination, *d.through}:
                score += 40
        priority[n.id] = score

    ranked = sorted(graph.nodes, key=lambda n: (-priority.get(n.id, 0), n.label))
    keep = {n.id for n in ranked[:max_nodes]}
    graph.nodes = [n for n in graph.nodes if n.id in keep]
    graph.edges = [e for e in graph.edges if e.source in keep and e.target in keep]
    for j in graph.journeys:
        j.steps = [s for s in j.steps if s.node_id in keep]
    for r in graph.requests:
        r.steps = [s for s in r.steps if s in keep]
    for d in graph.data_flows:
        d.through = [s for s in d.through if s in keep]
    graph.meta["capped"] = True
    graph.meta["node_count"] = len(graph.nodes)
    graph.meta["edge_count"] = len(graph.edges)
    return graph


def _slug(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", str(name).lower()).strip("-")
    return s or "item"


def _human(nid: str) -> str:
    tail = nid.split(":")[-1] if ":" in nid else nid
    return tail.replace("-", " ").replace("_", " ").title()
