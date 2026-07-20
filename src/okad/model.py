"""Core data model for OKAD story graphs.

Unlike milky-way dependency graphs, OKAD stores curated narrative structure:
layers, journeys, request paths, and data flows — labeled by role, not filename.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
class StoryGraph:
    """The OKAD story graph — curated, layered, narrative."""

    system_name: str
    summary: str
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    journeys: list[Journey] = field(default_factory=list)
    requests: list[RequestPath] = field(default_factory=list)
    data_flows: list[DataFlow] = field(default_factory=list)
    layers: list[dict[str, str]] = field(default_factory=lambda: list(LAYERS))
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": 1,
            "system_name": self.system_name,
            "summary": self.summary,
            "layers": self.layers,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "journeys": [j.to_dict() for j in self.journeys],
            "requests": [r.to_dict() for r in self.requests],
            "data_flows": [d.to_dict() for d in self.data_flows],
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryGraph:
        nodes = [Node(**n) for n in data.get("nodes", [])]
        edges = [Edge(**e) for e in data.get("edges", [])]
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
        return cls(
            system_name=data.get("system_name", "System"),
            summary=data.get("summary", ""),
            nodes=nodes,
            edges=edges,
            journeys=journeys,
            requests=requests,
            data_flows=data_flows,
            layers=data.get("layers", list(LAYERS)),
            meta=data.get("meta", {}),
        )

    def node_map(self) -> dict[str, Node]:
        return {n.id: n for n in self.nodes}

    def prune_orphan_edges(self) -> None:
        ids = {n.id for n in self.nodes}
        self.edges = [e for e in self.edges if e.source in ids and e.target in ids]
