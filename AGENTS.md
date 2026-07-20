## OKAD

When the user runs `/okad` or asks for a system / architecture / data-flow / request-flow map,
follow the OKAD skill (`okad` skill / `skill/SKILL.md`). Prefer `okad query`, `okad path`,
and `okad explain` over grepping the whole repo once `okad-out/story.json` exists.

Install: `pipx install "git+https://github.com/Abmstpha/OKAD.git" && okad install` (or `uv tool install …`)

## Local agent memory

If `memory/` exists (gitignored), read `memory/INDEX.md` first, then `PRODUCT.md`,
`ARCHITECTURE.md`, `CONVENTIONS.md`, and `SESSION.md` before changing the project.
Update `SESSION.md` when you finish meaningful work.

Do not narrate work as checklist theater (`Scaffold…`, `✔ Build…`). Prefer normal
engineering updates and conventional commit messages (see CONTRIBUTING.md).

