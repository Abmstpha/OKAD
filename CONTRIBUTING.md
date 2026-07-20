# Contributing to OKAD

Thanks for helping. OKAD stays useful only if maps stay **readable** — elegance over exhaustiveness.

## Quick start for contributors

```bash
git clone https://github.com/Abmstpha/OKAD.git
cd OKAD
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
okad version
pytest -q
ruff check src tests
```

## Ways to contribute

| Kind | Examples |
|------|----------|
| **Bugs** | Broken route detection, bad HTML, install path issues |
| **Extractors** | Better FastAPI / Next.js / Go / Rails signals (still capped!) |
| **Viz** | Clearer layouts, accessibility, export SVG |
| **Skills** | Better `/okad` prompts for Claude / Codex / Cursor |
| **Docs** | Tutorials, language guides, screenshots |
| **Examples** | Tiny sample apps + expected `story.draft.json` |

## Design guardrails (please read)

1. **Keep maps readable.** No milky-way of every import edge.
2. **Label by role**, not filename (`Checkout`, not `checkout_controller.ts`).
3. **Cap the graph** — top-level story stays around ≤60 nodes.
4. **Honesty** — mark edges `extracted` | `inferred` | `ambiguous`.

More in [docs/DESIGN.md](docs/DESIGN.md) and [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md).

## Pull request checklist

- [ ] `pytest -q` passes
- [ ] `ruff check src tests` clean (or justified)
- [ ] Docs / skill updated if behavior changed
- [ ] Keep diffs focused — one idea per PR
- [ ] No secrets, no huge generated `okad-out/` dumps unless under `examples/`

## Commit style

Imperative subject, optional body for why. Write like a normal open-source project — not agent checklists or vibe-coding status lines.

**Author is always Abmstpha only.** Never add `Co-authored-by: Cursor` (or any Cursor bot). Enable the repo hooks:

```bash
git config core.hooksPath .githooks   # once per clone
```

Good:

```
fix skeleton: detect NestJS @Get routes

Nest handlers were missed because the decorator regex
required a quoted path; optional path is now accepted.
```

Bad (never):

```
Scaffold Python package: CLI, extractors, viz, skill
✔ Build flow extraction + elegant HTML viz
✔ Add /okad skill for Claude Code & Codex
```

## Code of conduct

Be kind. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Do not file public issues for vulnerabilities. See [SECURITY.md](SECURITY.md).

## License

By contributing you agree your work is released under the MIT License (same as the project).
