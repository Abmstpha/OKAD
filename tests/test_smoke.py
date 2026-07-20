"""Minimal smoke tests for OKAD skeleton + merge."""

from __future__ import annotations

from pathlib import Path

from okad.detect import detect
from okad.extract import extract_skeleton
from okad.merge import merge_story
from okad.report import generate_report
from okad.viz import render_html


def test_detect_and_skeleton(tmp_path: Path) -> None:
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "routes.py").write_text(
        '''
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/orders")
def create_order():
    return {"id": 1}
''',
        encoding="utf-8",
    )
    (tmp_path / "app" / "order_service.py").write_text(
        "class OrderService:\n    def create(self):\n        return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "app" / "order_model.py").write_text(
        "class Order:\n    pass\n",
        encoding="utf-8",
    )

    d = detect(tmp_path)
    assert d["total_files"] >= 3
    g = extract_skeleton(tmp_path, d)
    assert any(n.kind == "route" for n in g.nodes)
    assert g.system_name == tmp_path.name


def test_merge_and_render(tmp_path: Path) -> None:
    (tmp_path / "x.py").write_text("print('hi')\n", encoding="utf-8")
    d = detect(tmp_path)
    sk = extract_skeleton(tmp_path, d)
    story = {
        "system_name": "Demo",
        "summary": "A tiny demo system.",
        "nodes": [
            {
                "id": "screen:home",
                "label": "Home",
                "kind": "screen",
                "layer": "experience",
                "summary": "Landing",
            },
            {
                "id": "route:GET:/health",
                "label": "GET /health",
                "kind": "route",
                "layer": "interface",
                "summary": "Health check",
            },
        ],
        "edges": [
            {
                "id": "e1",
                "source": "screen:home",
                "target": "route:GET:/health",
                "kind": "triggers",
                "confidence": "inferred",
            }
        ],
        "journeys": [
            {
                "id": "j1",
                "name": "Health check",
                "summary": "User opens app",
                "steps": [{"node_id": "screen:home"}, {"node_id": "route:GET:/health"}],
            }
        ],
        "requests": [
            {
                "id": "r1",
                "name": "Health",
                "method": "GET",
                "route": "/health",
                "summary": "Liveness",
                "steps": ["route:GET:/health"],
            }
        ],
        "data_flows": [],
    }
    g = merge_story(sk, story)
    assert g.system_name == "Demo"
    assert len(g.journeys) == 1
    html = render_html(g, tmp_path / "story.html")
    assert html.exists()
    assert "OKAD" in html.read_text(encoding="utf-8")
    report = generate_report(g)
    assert "Health check" in report
