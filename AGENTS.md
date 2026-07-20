## OKAD

When the user runs `/okad` or asks for a system / architecture / data-flow / request-flow map,
follow the OKAD skill (`okad` skill / `skill/SKILL.md`). Prefer `okad query`, `okad path`,
and `okad explain` over grepping the whole repo once `okad-out/story.json` exists.

Install: `curl -fsSL https://raw.githubusercontent.com/Abmstpha/OKAD/main/install.sh | bash`  
(or `pipx install --backend pip "git+https://github.com/Abmstpha/OKAD.git" && okad install`)

## Local agent memory

If `memory/` exists (gitignored), read `memory/INDEX.md` first, then `PRODUCT.md`,
`ARCHITECTURE.md`, `CONVENTIONS.md`, and `SESSION.md` before changing the project.
Update `SESSION.md` when you finish meaningful work.

Do not narrate work as checklist theater (`Scaffold…`, `✔ Build…`). Prefer normal
engineering updates and conventional commit messages (see CONTRIBUTING.md).

## Git authorship

Commits must be **Abmstpha only** (`Abmstpha <21007@esp.mr>`).
Never add `Co-authored-by: Cursor` or any Cursor contributor trailer.
Use `commit-tree` with explicit `GIT_AUTHOR_*` / `GIT_COMMITTER_*` if the host would inject Cursor.
Hooks live in `.githooks/` (`prepare-commit-msg` strips Cursor trailers; `commit-msg` rejects them).

