# Architecture (code tour)

```text
OKAD/
├── src/okad/           # installable package
│   ├── cli.py          # typer entrypoints
│   ├── detect.py       # corpus scan
│   ├── extract.py      # structural skeleton
│   ├── merge.py        # draft → StoryGraph + caps
│   ├── model.py        # dataclasses
│   ├── query.py        # query / path / explain
│   ├── report.py       # STORY_REPORT.md
│   ├── viz.py          # story.html
│   ├── install.py      # skill installers
│   └── _skill/         # packaged SKILL.md
├── skill/SKILL.md      # canonical /okad skill (edit here)
├── tests/              # pytest
├── examples/           # toy apps + sample stories
├── docs/               # human docs
└── .github/            # CI + templates
```

## Data flow inside OKAD itself

```text
okad skeleton
    detect.json
    skeleton.json / skeleton.md
         │
         │  (agent writes)
         ▼
    story.draft.json
         │
okad finalize
         ▼
    story.json ──► query/path/explain
    story.html
    STORY_REPORT.md
```

## Dependencies (kept small)

| Package | Why |
|---------|-----|
| `typer` | CLI |
| `rich` | terminal output |
| `networkx` | path / neighborhood queries |

No React build step. Viz is one HTML file with inline SVG/JS so `story.html` is emailable and openable offline.

## Testing

```bash
pytest -q
```

Smoke tests cover detect → skeleton → merge → HTML render on a tiny FastAPI-ish fixture.
