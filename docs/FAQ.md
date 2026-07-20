# FAQ

## Do I need an API key?

No. The CLI is local. The story is authored by whatever LLM app you’re already using (`/okad`).

## Is OKAD a Graphify fork?

No. Inspired by the *distribution idea* (CLI + agent skill), different product goals. See [comparison-graphify.md](comparison-graphify.md).

## Why so few nodes?

That’s the point. Dense graphs look smart and teach nothing. Caps are intentional — see [PHILOSOPHY.md](PHILOSOPHY.md).

## Can I run without Claude / Codex / Cursor?

Yes — `okad build .` gives a structural skeleton map. Journeys/requests/data flows need a story draft (`/okad` or hand-written JSON).

## Which languages are supported?

Any text codebase can be scanned. Route/screen heuristics currently favor JS/TS (Next, Express, Nest), Python (FastAPI/Flask), and common `service` / `model` naming. More extractors welcome — keep the caps.

## Where do outputs go?

Always `okad-out/` under the project you scanned. Gitignore it unless you intentionally commit a snapshot.

## Can I commit `story.html`?

Yes, if you want the team to browse a frozen map. Prefer committing `story.json` + regenerating HTML, or committing both for convenience.

## Windows?

Python 3.10+ works. Activate venv with `.venv\Scripts\activate`. Open HTML with `start okad-out\story.html`.

## How do I uninstall the skill?

Remove the skill directories listed in [agents.md](agents.md), or delete `~/.claude/skills/okad`, `~/.codex/skills/okad`, `~/.cursor/skills/okad`.

## Who maintains this?

[Abmstpha](https://github.com/Abmstpha) — MIT licensed, contributions welcome.
