# Agent integration

OKAD is built to be invoked **inside** coding agents via a skill and `/okad` command.

## Install targets

`okad install` (default `--platform auto`) writes:

| Platform | Paths |
|----------|-------|
| Claude Code | `~/.claude/skills/okad/SKILL.md`, `~/.claude/commands/okad.md`, `~/.claude/commands/okad-delete.md` |
| Codex | `~/.codex/skills/okad/SKILL.md`, AGENTS.md snippet |
| Cursor | `~/.cursor/skills/okad/SKILL.md` |
| Generic | `~/.agents/skills/okad/SKILL.md`, project `AGENTS.md` |
| Project-local | `.claude/skills/okad/`, `.claude/commands/okad.md`, `.claude/commands/okad-delete.md` |

`/okad-delete` is agent-side only: it lists `okad-out/` contents, asks the user
to confirm, then removes the directory. There is deliberately no CLI equivalent.

## What the skill does

See [`skill/SKILL.md`](../skill/SKILL.md). In short:

1. Fast-path: if `okad-out/story.json` exists and the user asked a question → `okad query`  
2. Else: `okad skeleton` → author `story.draft.json` → `okad finalize`  
3. Report journeys + key requests; offer a follow-up trace  

The skill **forbids** milky-way dumps and filename labels.

## No API key

The CLI never asks for `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`.  
Semantic authorship is the host agent’s job.

## Manual invoke (debugging)

```bash
okad skeleton .
# write okad-out/story.draft.json yourself or via agent
okad finalize .
okad query "How does X work?"
```

## Updating the skill

1. Edit `skill/SKILL.md`  
2. Copy to `src/okad/_skill/SKILL.md`  
3. Run `okad install` again on your machine  
4. Mention skill changes in the PR

## Staying current

`okad update` self-updates the installed package to the latest published
version (pipx / uv / pip aware; source of truth is the GitHub repo), then
refreshes every installed skill copy via the freshly installed binary.
Editable dev checkouts skip the package step. Use `--skill-only` to only
re-sync skill files.  
