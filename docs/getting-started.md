# Getting started

## 60-second version

```bash
git clone https://github.com/Abmstpha/OKAD.git
cd OKAD
uv venv && source .venv/bin/activate
uv pip install -e .
okad install
```

Open **your** project in Claude Code / Codex / Cursor and run:

```
/okad
```

Then open `okad-out/story.html`.

## What just happened?

1. `okad install` copied the OKAD **skill** into your agent config so `/okad` is understood.
2. `/okad` ran a **skeleton** pass (routes, screens, stores — capped).
3. Your **LLM session** authored journeys, request paths, and data flows.
4. `okad finalize` merged everything into a small, readable map.

No OKAD API key. The agent you already use *is* the model.

## Platform notes

### Claude Code

```bash
okad install --platform claude
cd ~/my-app && claude
# then: /okad
```

Creates `~/.claude/skills/okad/SKILL.md` and `~/.claude/commands/okad.md`.

### OpenAI Codex

```bash
okad install --platform codex
cd ~/my-app && codex
# then: /okad
```

### Cursor

```bash
okad install --platform cursor
```

Open the project → Agent chat → `/okad`.

### Terminal only (no story yet)

```bash
okad build .
open okad-out/story.html
```

This is a structural preview. For journeys/requests/data flows, use `/okad` in an agent.

## Verify install

```bash
okad version
okad detect .
which okad
```

## Next reading

- [Philosophy](PHILOSOPHY.md) — what “good” looks like  
- [Agent integration](agents.md) — deeper install details  
- [examples/](../examples/) — walk a tiny shop app  
