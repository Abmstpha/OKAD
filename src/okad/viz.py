"""Render an elegant multi-view story map (not a milky-way force graph)."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from okad import __version__
from okad.model import StoryGraph


def _load_template() -> str:
    try:
        return resources.files("okad").joinpath("templates/story.html").read_text(encoding="utf-8")
    except Exception:
        # Editable / source-tree fallback
        return (Path(__file__).parent / "templates" / "story.html").read_text(encoding="utf-8")


def render_html(graph: StoryGraph, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(graph.to_dict(), ensure_ascii=False)
    # Escape </script> breakouts in JSON embedded in HTML
    data = data.replace("<", "\\u003c").replace(">", "\\u003e")
    story_version = str(graph.to_dict().get("version", 1))
    html = (
        _load_template()
        .replace("__SYSTEM_NAME__", _esc(graph.system_name))
        .replace("__SUMMARY__", _esc(graph.summary or "Story-driven architecture map"))
        .replace("__OKAD_VERSION__", _esc(__version__))
        .replace("__STORY_VERSION__", _esc(story_version))
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
