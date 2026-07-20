"""Detect supported source files in a codebase."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CODE_EXT = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".vue",
    ".svelte",
}
DOC_EXT = {".md", ".mdx", ".txt", ".rst"}
SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
    ".tox",
    "coverage",
    ".okad",
    "okad-out",
    "graphify-out",
    ".turbo",
    "vendor",
    "target",
    ".idea",
    ".vscode",
}
SENSITIVE_NAMES = {".env", ".env.local", "credentials.json", "secrets.yaml", "id_rsa"}


def detect(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files: dict[str, list[str]] = {"code": [], "docs": []}
    skipped_sensitive: list[str] = []
    by_ext: dict[str, int] = defaultdict(int)
    words = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SENSITIVE_NAMES or path.name.startswith(".env"):
            skipped_sensitive.append(str(path))
            continue

        ext = path.suffix.lower()
        rel = str(path.relative_to(root))
        if ext in CODE_EXT:
            files["code"].append(rel)
            by_ext[ext] += 1
            words += _rough_words(path)
        elif ext in DOC_EXT:
            files["docs"].append(rel)
            by_ext[ext] += 1
            words += _rough_words(path)

    return {
        "scan_root": str(root),
        "total_files": len(files["code"]) + len(files["docs"]),
        "total_words": words,
        "files": files,
        "by_ext": dict(sorted(by_ext.items(), key=lambda x: -x[1])),
        "skipped_sensitive": len(skipped_sensitive),
    }


def _rough_words(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    return max(1, len(text.split()))


def summarize_detect(result: dict[str, Any]) -> str:
    lines = [
        f"Corpus: {result['total_files']} files · ~{result['total_words']:,} words",
        f"  code:  {len(result['files']['code'])} files",
        f"  docs:  {len(result['files']['docs'])} files",
    ]
    if result.get("by_ext"):
        top = ", ".join(f"{k}×{v}" for k, v in list(result["by_ext"].items())[:8])
        lines.append(f"  top:   {top}")
    if result.get("skipped_sensitive"):
        lines.append(f"  skipped sensitive: {result['skipped_sensitive']}")
    return "\n".join(lines)


def write_detect(result: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
