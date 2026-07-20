"""Core data model for OKAD story graphs.

Unlike milky-way dependency graphs, OKAD stores curated narrative structure:
layers, journeys, request paths, and data flows — labeled by role, not filename.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any, Literal


LayerId = Literal["experience", "interface", "application", "data", "infra"]
NodeKind = Literal[
    "journey",
    "screen",
    "action",
    "route",
    "handler",
    "service",
    "store",
    "entity",
    "external",
    "layer",
    "system",
    "agent",
    "tool",
]
EdgeKind = Literal[
    "navigates",
    "triggers",
    "calls",
    "reads",
    "writes",
    "transforms",
    "returns",
    "contains",
    "depends_on",
]
Confidence = Literal["extracted", "inferred", "ambiguous"]


LAYERS: list[dict[str, str]] = [
    {"id": "experience", "label": "Experience", "blurb": "What the user sees and does"},
    {"id": "interface", "label": "Interface", "blurb": "Routes, APIs, events that enter the system"},
    {"id": "application", "label": "Application", "blurb": "Business logic and orchestration"},
    {"id": "data", "label": "Data", "blurb": "Stores, entities, and persistence"},
    {"id": "infra", "label": "Infra", "blurb": "Queues, caches, third-party services"},
]


@dataclass
class Node:
    id: str
    label: str
    kind: NodeKind
    layer: LayerId
    summary: str = ""
    source: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Edge:
    id: str
    source: str
    target: str
    kind: EdgeKind
    label: str = ""
    confidence: Confidence = "extracted"
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JourneyStep:
    node_id: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Journey:
    id: str
    name: str
    summary: str
    steps: list[JourneyStep] = field(default_factory=list)
    actor: str = "user"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "summary": self.summary,
            "actor": self.actor,
            "steps": [s.to_dict() for s in self.steps],
        }


@dataclass
class RequestPath:
    id: str
    name: str
    method: str
    route: str
    summary: str
    steps: list[str] = field(default_factory=list)  # node ids in order
    status: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DataFlow:
    id: str
    name: str
    summary: str
    origin: str
    destination: str
    through: list[str] = field(default_factory=list)
    shape: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentTool:
    id: str
    name: str
    summary: str = ""
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Agent:
    """An orchestration agent and the tools it can call."""

    id: str
    name: str
    summary: str = ""
    tools: list[AgentTool] = field(default_factory=list)
    node_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "summary": self.summary,
            "node_id": self.node_id,
            "tools": [t.to_dict() for t in self.tools],
        }


@dataclass
class StoryGraph:
    """The OKAD story graph — curated, layered, narrative."""

    system_name: str
    summary: str
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    journeys: list[Journey] = field(default_factory=list)
    requests: list[RequestPath] = field(default_factory=list)
    data_flows: list[DataFlow] = field(default_factory=list)
    agents: list[Agent] = field(default_factory=list)
    layers: list[dict[str, str]] = field(default_factory=lambda: list(LAYERS))
    meta: dict[str, Any] = field(default_factory=dict)
    version: int = 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "system_name": self.system_name,
            "summary": self.summary,
            "layers": self.layers,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "journeys": [j.to_dict() for j in self.journeys],
            "requests": [r.to_dict() for r in self.requests],
            "data_flows": [d.to_dict() for d in self.data_flows],
            "agents": [a.to_dict() for a in self.agents],
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryGraph:
        nodes = []
        allowed = {f.name for f in fields(Node)}
        for n in data.get("nodes", []):
            payload = {k: v for k, v in dict(n).items() if k in allowed}
            nodes.append(Node(**payload))
        edge_allowed = {f.name for f in fields(Edge)}
        edges = []
        for e in data.get("edges", []):
            payload = {k: v for k, v in dict(e).items() if k in edge_allowed}
            edges.append(Edge(**payload))
        journeys = []
        for j in data.get("journeys", []):
            steps = [JourneyStep(**s) for s in j.get("steps", [])]
            journeys.append(
                Journey(
                    id=j["id"],
                    name=j["name"],
                    summary=j.get("summary", ""),
                    actor=j.get("actor", "user"),
                    steps=steps,
                )
            )
        requests = [RequestPath(**r) for r in data.get("requests", [])]
        data_flows = [DataFlow(**d) for d in data.get("data_flows", [])]
        agents: list[Agent] = []
        for a in data.get("agents", []) or []:
            tools = [AgentTool(**t) if isinstance(t, dict) else AgentTool(id=str(t), name=str(t)) for t in a.get("tools", [])]
            agents.append(
                Agent(
                    id=str(a.get("id") or a.get("name") or "agent"),
                    name=str(a.get("name") or "Agent"),
                    summary=str(a.get("summary") or ""),
                    node_id=a.get("node_id"),
                    tools=tools,
                )
            )
        return cls(
            system_name=data.get("system_name", "System"),
            summary=data.get("summary", ""),
            nodes=nodes,
            edges=edges,
            journeys=journeys,
            requests=requests,
            data_flows=data_flows,
            agents=agents,
            layers=data.get("layers", list(LAYERS)),
            meta=data.get("meta", {}),
            version=int(data.get("version") or 2),
        )

    def node_map(self) -> dict[str, Node]:
        return {n.id: n for n in self.nodes}

    def prune_orphan_edges(self) -> None:
        ids = {n.id for n in self.nodes}
        self.edges = [e for e in self.edges if e.source in ids and e.target in ids]
