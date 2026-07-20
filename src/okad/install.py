"""Install OKAD skill into Claude Code, Codex, Cursor, and AGENTS.md hosts."""

from __future__ import annotations

import shutil
from pathlib import Path


def skill_source() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        here.parent / "_skill" / "SKILL.md",  # installed package
        here.parents[2] / "skill" / "SKILL.md",  # repo layout
        Path.cwd() / "skill" / "SKILL.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("Could not locate skill/SKILL.md")


def install(platform: str = "auto") -> list[Path]:
    src = skill_source()
    home = Path.home()
    written: list[Path] = []

    targets: list[Path] = []
    p = platform.lower()
    if p in ("auto", "claude"):
        targets.append(home / ".claude" / "skills" / "okad" / "SKILL.md")
        # Claude Code slash commands
        targets.append(home / ".claude" / "commands" / "okad.md")
        targets.append(home / ".claude" / "commands" / "okad-delete.md")
    if p in ("auto", "codex", "agents"):
        targets.append(home / ".codex" / "skills" / "okad" / "SKILL.md")
        targets.append(home / ".agents" / "skills" / "okad" / "SKILL.md")
    if p in ("auto", "cursor"):
        targets.append(home / ".cursor" / "skills" / "okad" / "SKILL.md")

    # Also drop a project-local copy when cwd looks like a project
    if p == "auto":
        local = Path.cwd() / ".claude" / "skills" / "okad" / "SKILL.md"
        targets.append(local)
        targets.append(Path.cwd() / ".claude" / "commands" / "okad.md")
        targets.append(Path.cwd() / ".claude" / "commands" / "okad-delete.md")

    text = src.read_text(encoding="utf-8")
    # Slash command wrappers for Claude Code
    command_body = (
        "---\n"
        "description: Build a story-driven architecture map (UX / requests / data flows)\n"
        "---\n\n"
        "Follow the OKAD skill at skills/okad/SKILL.md (or ~/.claude/skills/okad/SKILL.md).\n"
        "User args: $ARGUMENTS\n"
    )
    delete_body = (
        "---\n"
        "description: Delete this project's OKAD story (okad-out/)\n"
        "---\n\n"
        "Delete the generated OKAD story for the current project, if it exists.\n\n"
        "1. Look for an `okad-out/` directory at the project root.\n"
        "2. If it does not exist, tell the user there is nothing to delete and stop.\n"
        "3. If it exists, list what it contains (file names / count), ask the user to\n"
        "   confirm, then remove the directory (`rm -rf okad-out`).\n"
        "User args: $ARGUMENTS\n"
    )

    for dest in targets:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.parent.name == "commands" and dest.name == "okad.md":
            dest.write_text(command_body, encoding="utf-8")
        elif dest.parent.name == "commands" and dest.name == "okad-delete.md":
            dest.write_text(delete_body, encoding="utf-8")
        else:
            dest.write_text(text, encoding="utf-8")
        written.append(dest)

    # AGENTS.md snippet for Codex / OpenCode style hosts
    if p in ("auto", "codex", "agents"):
        for agents in (Path.cwd() / "AGENTS.md", home / ".codex" / "AGENTS.md"):
            _ensure_agents_snippet(agents)
            if agents.exists():
                written.append(agents)

    return written


def _ensure_agents_snippet(path: Path) -> None:
    marker = "## OKAD"
    snippet = """## OKAD

When the user runs `/okad` or asks for a system / architecture / data-flow / request-flow map,
follow the OKAD skill (`okad` skill / `skill/SKILL.md`). Prefer `okad query`, `okad path`,
and `okad explain` over grepping the whole repo once `okad-out/story.json` exists.

Install: `pip install okad && okad install`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(snippet + "\n", encoding="utf-8")
        return
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + snippet + "\n", encoding="utf-8")


def uninstall() -> list[Path]:
    home = Path.home()
    removed: list[Path] = []
    paths = [
        home / ".claude" / "skills" / "okad",
        home / ".claude" / "commands" / "okad.md",
        home / ".claude" / "commands" / "okad-delete.md",
        home / ".codex" / "skills" / "okad",
        home / ".agents" / "skills" / "okad",
        home / ".cursor" / "skills" / "okad",
        Path.cwd() / ".claude" / "skills" / "okad",
        Path.cwd() / ".claude" / "commands" / "okad.md",
        Path.cwd() / ".claude" / "commands" / "okad-delete.md",
    ]
    for p in paths:
        if p.is_file():
            p.unlink()
            removed.append(p)
        elif p.is_dir():
            shutil.rmtree(p)
            removed.append(p)
    return removed
