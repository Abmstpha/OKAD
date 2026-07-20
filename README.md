# OKAD

**Story-driven architecture maps for any codebase.**

OKAD turns a repo into a readable map of **user journeys**, **request paths**, and **data flows** — layered trees and graphs a stranger can understand.

It is inspired by tools like [Graphify](https://github.com/graphify-labs/graphify), but it is intentionally different:

| | Graphify | OKAD |
|---|---|---|
| Goal | Exhaustive knowledge graph | Narrative system map |
| Nodes | Many symbols / files | Curated roles (`Checkout`, `Auth gate`) |
| Edges | Dense connections | Story-significant only |
| Viz feel | Milky-way / force graph | Layered columns + journey trees |
| Primary question | “What connects to X?” | “How does a user / request / datum move?” |

Open `okad-out/story.html` after a run. If someone cannot understand the system from that page, the map failed — not the reader.

## Install

```bash
# from this repo
pip install -e .
# or
uv pip install -e .

okad install          # Claude Code / Codex / Cursor skill + /okad command
okad version
```

Requires Python 3.10+.

## Quick start

Inside Claude Code, Codex, or Cursor:

```
/okad
```

Or from a terminal (skeleton only — no LLM story yet):

```bash
okad build .
open okad-out/story.html   # macOS
```

Full story maps are authored by the **host model** (the agent running `/okad`), then finalized:

```bash
okad skeleton .
# agent writes okad-out/story.draft.json
okad finalize .
```

## CLI

```
okad detect [path]              # corpus summary
okad skeleton [path]            # structural seeds (routes, screens, stores)
okad finalize [path]            # merge story draft → html + report + json
okad build [path]               # skeleton map without LLM story
okad query "How does checkout work?"
okad path "Checkout" "Order store"
okad explain "Auth gate"
okad install [--platform claude|codex|cursor|auto]
okad open [path]                # print story.html path
```

## Outputs (`okad-out/`)

- `story.html` — interactive views: Architecture · Journeys · Requests · Data flow
- `STORY_REPORT.md` — plain-language narrative
- `story.json` — queryable story graph
- `skeleton.md` / `skeleton.json` — structural seeds for the story pass

## How it works

1. **Detect** source files (skips `node_modules`, secrets, etc.).
2. **Skeleton** extracts architecture-significant signals only (routes, screens, services, stores) — capped per layer.
3. **Story pass** (host LLM via `/okad` skill) authors journeys, request sequences, and data pipelines with human labels.
4. **Finalize** merges, enforces an elegance cap (~60 nodes), and renders the viz.

No API key is required for the CLI. The agent session *is* the model.

## Philosophy

Most AI coding sessions explode into too many files and links. OKAD exists to **compress** a system into a story you can hand to anyone:

- left-to-right layers: Experience → Interface → Application → Data → Infra
- drill into one journey or one request at a time
- refuse the milky-way

## License

MIT © Abmstpha

## Repo

https://github.com/Abmstpha/OKAD
