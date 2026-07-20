# Roadmap

OKAD is young on purpose. The north star stays fixed: **a stranger can understand your system from `story.html`.**

## Now (0.1.x)

- [x] Skeleton + story finalize pipeline
- [x] Layered HTML viz + CLI query/path/explain
- [x] Agent skill `/okad` for Claude / Codex / Cursor
- [ ] CI green on every PR
- [ ] First language cookbooks (Next.js, FastAPI, Express)

## Next

- [ ] Publish to PyPI so `pip install okad` / `uv tool install okad` Just Works™
- [ ] Deeper extractors without raising node count (aggregate smarter)
- [ ] `okad watch` — refresh skeleton on file change
- [ ] Export: SVG for docs, Mermaid for PRs
- [ ] Diff two story maps across git commits (“what flow changed?”)

## Later / maybe

- [ ] Shared story packs for popular frameworks (templates, not milky-ways)
- [ ] MCP server that exposes `query` / `path` / `explain`
- [ ] Browser extension to open `story.html` from GitHub

## Explicit non-goals

- Replacing Graphify’s exhaustive symbol graph
- Embedding / vector RAG
- SaaS lock-in or telemetry

Ideas welcome in [Discussions](https://github.com/Abmstpha/OKAD/discussions) or issues labeled `idea`.
