"""OKAD CLI — story-driven architecture maps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from okad import __version__
from okad.detect import detect, summarize_detect, write_detect
from okad.extract import extract_skeleton, skeleton_brief, write_skeleton
from okad.merge import load_story, merge_story, save_story
from okad.query import explain as explain_node
from okad.query import path_between, query
from okad.report import write_report
from okad.viz import render_html

app = typer.Typer(
    name="okad",
    help="OKAD — story-driven architecture maps (journeys, requests, data flows).",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _out_dir(root: Path) -> Path:
    return root / "okad-out"


@app.callback()
def main() -> None:
    """OKAD command group."""


@app.command("version")
def version_cmd() -> None:
    """Print OKAD version."""
    console.print(__version__)


@app.command("detect")
def detect_cmd(
    path: Path = typer.Argument(Path("."), help="Codebase root"),
) -> None:
    """Scan a codebase and print a corpus summary."""
    root = path.resolve()
    result = detect(root)
    out = _out_dir(root)
    write_detect(result, out / "detect.json")
    console.print(summarize_detect(result))
    console.print(f"[dim]Wrote {out / 'detect.json'}[/dim]")


@app.command("skeleton")
def skeleton_cmd(
    path: Path = typer.Argument(Path("."), help="Codebase root"),
) -> None:
    """Build a structural skeleton (no LLM). Seeds for the story pass."""
    root = path.resolve()
    out = _out_dir(root)
    result = detect(root)
    write_detect(result, out / "detect.json")
    if result["total_files"] == 0:
        console.print("[red]No supported files found.[/red]")
        raise typer.Exit(1)
    graph = extract_skeleton(root, result)
    write_skeleton(graph, out / "skeleton.json")
    (out / "skeleton.md").write_text(skeleton_brief(graph), encoding="utf-8")
    console.print(summarize_detect(result))
    console.print(
        f"Skeleton: {len(graph.nodes)} nodes, {len(graph.edges)} edges → {out / 'skeleton.json'}"
    )
    console.print(
        "[dim]Next: host model authors story.json (see /okad skill), then `okad finalize`.[/dim]"
    )


@app.command("finalize")
def finalize_cmd(
    path: Path = typer.Argument(Path("."), help="Codebase root"),
    story: Optional[Path] = typer.Option(
        None, "--story", help="LLM story JSON (default okad-out/story.draft.json)"
    ),
) -> None:
    """Merge story draft onto skeleton and emit story.html + report."""
    root = path.resolve()
    out = _out_dir(root)
    skel_path = out / "skeleton.json"
    if not skel_path.exists():
        console.print("[red]Missing skeleton. Run `okad skeleton` first.[/red]")
        raise typer.Exit(1)
    draft_path = story or (out / "story.draft.json")
    if not draft_path.exists():
        console.print(f"[red]Missing story draft: {draft_path}[/red]")
        console.print("The /okad skill should write this after reading skeleton.md.")
        raise typer.Exit(1)

    skeleton = load_story(skel_path)
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    graph = merge_story(skeleton, draft)
    save_story(graph, out / "story.json")
    html = render_html(graph, out / "story.html")
    report = write_report(graph, out / "STORY_REPORT.md")
    console.print(
        f"[green]Story map ready[/green]: {len(graph.nodes)} nodes · "
        f"{len(graph.journeys)} journeys · {len(graph.requests)} requests · "
        f"{len(graph.data_flows)} data flows"
    )
    console.print(f"  {html}")
    console.print(f"  {report}")
    console.print(f"  {out / 'story.json'}")


@app.command("build")
def build_cmd(
    path: Path = typer.Argument(Path("."), help="Codebase root"),
) -> None:
    """Skeleton-only build + placeholder viz (no LLM story yet)."""
    root = path.resolve()
    out = _out_dir(root)
    result = detect(root)
    write_detect(result, out / "detect.json")
    if result["total_files"] == 0:
        console.print("[red]No supported files found.[/red]")
        raise typer.Exit(1)
    graph = extract_skeleton(root, result)
    write_skeleton(graph, out / "skeleton.json")
    (out / "skeleton.md").write_text(skeleton_brief(graph), encoding="utf-8")
    save_story(graph, out / "story.json")
    render_html(graph, out / "story.html")
    write_report(graph, out / "STORY_REPORT.md")
    console.print(summarize_detect(result))
    console.print(
        f"[yellow]Skeleton map[/yellow] written to {out}/ — "
        "run /okad in Claude Code or Codex for the full story pass."
    )


@app.command("query")
def query_cmd(
    question: str = typer.Argument(..., help="Natural-language question"),
    graph: Path = typer.Option(Path("okad-out/story.json"), "--graph"),
    budget: int = typer.Option(1800, "--budget"),
) -> None:
    """Answer a question from the story graph."""
    g = load_story(graph)
    console.print(Markdown(query(question, g, budget=budget)))


@app.command("path")
def path_cmd(
    a: str = typer.Argument(..., help="Start node label or id"),
    b: str = typer.Argument(..., help="End node label or id"),
    graph: Path = typer.Option(Path("okad-out/story.json"), "--graph"),
) -> None:
    """Shortest story path between two nodes."""
    g = load_story(graph)
    console.print(path_between(a, b, g))


@app.command("explain")
def explain_cmd(
    name: str = typer.Argument(..., help="Node or journey name"),
    graph: Path = typer.Option(Path("okad-out/story.json"), "--graph"),
) -> None:
    """Explain a node or journey in plain language."""
    g = load_story(graph)
    console.print(Markdown(explain_node(name, g)))


@app.command("install")
def install_cmd(
    platform: str = typer.Option(
        "auto",
        "--platform",
        help="claude|codex|cursor|agents|auto",
    ),
) -> None:
    """Install the /okad skill into your coding agent."""
    from okad.install import install

    targets = install(platform)
    if not targets:
        console.print("[red]No install targets found.[/red]")
        raise typer.Exit(1)
    for t in targets:
        console.print(f"[green]Installed[/green] → {t}")


@app.command("update")
def update_cmd(
    platform: str = typer.Option("auto", "--platform", help="claude|codex|cursor|agents|auto"),
) -> None:
    """Refresh installed /okad skill copies so they match this OKAD version."""
    from okad.install import install

    targets = install(platform)
    for t in targets:
        console.print(f"[green]Refreshed[/green] → {t}")
    console.print(f"okad {__version__} — skill copies now match the installed package.")
    console.print("[dim]Tip: `okad render <project>` re-renders story.html with the latest viewer.[/dim]")


@app.command("render")
def render_cmd(
    path: Path = typer.Argument(Path("."), help="Project root containing okad-out/story.json"),
) -> None:
    """Re-render story.html from an existing story.json (no LLM)."""
    root = path.resolve()
    out = _out_dir(root)
    story_path = out / "story.json"
    if not story_path.exists():
        console.print("[red]Missing okad-out/story.json. Run /okad or `okad finalize` first.[/red]")
        raise typer.Exit(1)
    graph = load_story(story_path)
    # Bump map schema version when re-rendering with a newer OKAD
    graph.version = max(int(graph.version or 1), 2)
    save_story(graph, story_path)
    html = render_html(graph, out / "story.html")
    console.print(f"[green]Re-rendered[/green] {html}  (okad {__version__}, story v{graph.version})")


@app.command("open")
def open_cmd(
    path: Path = typer.Argument(Path("."), help="Project root containing okad-out/"),
) -> None:
    """Print the path to story.html (open it in a browser)."""
    html = _out_dir(path.resolve()) / "story.html"
    if not html.exists():
        console.print("[red]No story.html yet. Run /okad or `okad build`.[/red]")
        raise typer.Exit(1)
    console.print(str(html))


if __name__ == "__main__":
    app()
