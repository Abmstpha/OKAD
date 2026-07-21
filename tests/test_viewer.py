"""Viewer template tests — the rendered story.html is the product.

Static checks always run; a DOM-level render check runs when a headless
Chrome/Chromium binary is available (skipped otherwise, e.g. bare CI).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from okad.merge import merge_story
from okad.model import StoryGraph
from okad.viz import render_html

FIXTURE_STORY = {
    "system_name": "Fixture Shop",
    "summary": "A tiny shop used to smoke-test the viewer.",
    "nodes": [
        {"id": "screen:home", "label": "Home", "kind": "screen", "layer": "experience"},
        {"id": "route:GET:/items", "label": "GET /items", "kind": "route", "layer": "interface"},
        {"id": "service:catalog", "label": "Catalog", "kind": "service", "layer": "application"},
        {"id": "store:items", "label": "Items store", "kind": "store", "layer": "data"},
    ],
    "edges": [
        {"source": "screen:home", "target": "route:GET:/items", "kind": "triggers", "label": "browse"},
        {"source": "route:GET:/items", "target": "service:catalog", "kind": "calls", "label": "list"},
        {"source": "service:catalog", "target": "store:items", "kind": "reads", "label": "query"},
    ],
    "journeys": [
        {
            "id": "j-browse",
            "name": "Browse items",
            "summary": "User opens the shop and sees items.",
            "actor": "shopper",
            "steps": [
                {"node_id": "screen:home", "note": "land"},
                {"node_id": "route:GET:/items", "note": "fetch"},
                {"node_id": "service:catalog", "note": "list"},
            ],
        }
    ],
    "requests": [
        {
            "id": "req-items",
            "name": "List items",
            "method": "GET",
            "route": "/items",
            "summary": "Fetch the catalog.",
            "steps": ["route:GET:/items", "service:catalog", "store:items"],
            "status": ["200"],
        }
    ],
    "data_flows": [
        {
            "id": "df-items",
            "name": "Store → screen",
            "summary": "Items flow to the home screen.",
            "origin": "store:items",
            "destination": "screen:home",
            "through": ["service:catalog", "route:GET:/items"],
            "shape": "Item { id, name }",
        }
    ],
    "agents": [
        {
            "id": "agent:orch",
            "name": "Shop Orchestrator",
            "level": "orchestrator",
            "role": "Coordinates the fixture.",
            "flow": ["agent:worker"],
            "tools": [],
        },
        {
            "id": "agent:worker",
            "name": "Worker",
            "level": "subagent",
            "parent_id": "agent:orch",
            "summary": "Does the fixture work.",
            "tools": [{"id": "t1", "name": "list_items"}],
        },
    ],
}


def _fixture_graph() -> StoryGraph:
    skeleton = StoryGraph(system_name="Fixture Shop", summary="skeleton")
    return merge_story(skeleton, FIXTURE_STORY)


def _render(tmp_path: Path) -> tuple[Path, str]:
    out = tmp_path / "story.html"
    render_html(_fixture_graph(), out)
    return out, out.read_text(encoding="utf-8")


def test_rendered_html_embeds_full_story(tmp_path: Path) -> None:
    _, html = _render(tmp_path)
    m = re.search(r"const DATA = (\{.*?\});\n", html, re.S)
    assert m, "embedded DATA payload missing"
    data = json.loads(m.group(1).replace("\\u003c", "<").replace("\\u003e", ">"))
    assert {n["id"] for n in data["nodes"]} >= {"screen:home", "store:items"}
    assert len(data["journeys"]) == 1 and data["journeys"][0]["steps"][0]["note"] == "land"
    assert data["agents"][1]["tools"][0]["name"] == "list_items"
    assert data["requests"][0]["status"] == ["200"]


def test_rendered_html_is_self_contained_and_has_views(tmp_path: Path) -> None:
    _, html = _render(tmp_path)
    for marker in (
        'data-view="agents"', 'data-view="architecture"', 'data-view="journeys"',
        'data-view="requests"', 'data-view="data"',
        "drawLayeredGraph", "renderSequenceGraph", "Fixture Shop",
    ):
        assert marker in html, f"missing marker: {marker}"
    # No graph-library CDNs — the engine must stay zero-dependency
    for banned in ("cytoscape", "mermaid", "dagre", "d3js", "unpkg.com", "jsdelivr"):
        assert banned not in html.lower(), f"unexpected dependency: {banned}"


def _chrome() -> str | None:
    for c in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "google-chrome", "chromium", "chromium-browser",
    ):
        found = shutil.which(c) or (c if Path(c).exists() else None)
        if found:
            return found
    return None


@pytest.mark.skipif(_chrome() is None, reason="no headless Chrome available")
@pytest.mark.parametrize("view,expect", [
    ("agents", "Shop Orchestrator"),
    ("architecture/j-browse", "GET /items"),
    ("journeys/j-browse", "Browse items"),
    ("requests/req-items", "Items store"),
    ("data/df-items", "Catalog"),
])
def test_views_render_nodes_in_dom(tmp_path: Path, view: str, expect: str) -> None:
    out, _ = _render(tmp_path)
    dom = subprocess.run(
        [_chrome(), "--headless", "--disable-gpu", "--dump-dom",
         "--virtual-time-budget=3000", f"file://{out}#{view}"],
        capture_output=True, text=True, timeout=60,
    ).stdout
    assert 'class="gnode' in dom, f"{view}: no graph nodes rendered"
    assert expect in dom, f"{view}: expected {expect!r} in DOM"


def test_merge_coerces_bad_layer_and_kind() -> None:
    story = dict(FIXTURE_STORY)
    story = json.loads(json.dumps(story))
    story["nodes"].append(
        {"id": "svc:x", "label": "X", "kind": "servcie", "layer": "aplication"}
    )
    story["edges"].append(
        {"source": "svc:x", "target": "store:items", "kind": "raeds", "confidence": "guessed"}
    )
    graph = merge_story(StoryGraph(system_name="s", summary=""), story)
    node = next(n for n in graph.nodes if n.id == "svc:x")
    assert node.kind == "service" and node.layer == "application"
    edge = next(e for e in graph.edges if e.source == "svc:x")
    assert edge.kind == "reads" and edge.confidence == "inferred"
    assert any("corrected" in w for w in graph.meta["warnings"])
