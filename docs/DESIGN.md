# Design

## Pipeline

```text
 codebase
    │
    ▼
 detect  ──►  corpus summary (code/docs counts)
    │
    ▼
 skeleton ──►  capped structural seeds (routes, screens, services, stores)
    │
    ▼
 story draft (host LLM via /okad skill)
    │         journeys · requests · data_flows · role-labeled nodes
    ▼
 finalize ──►  merge + elegance cap
    │
    ├── story.json
    ├── story.html
    └── STORY_REPORT.md
```

## Core types

Defined in `src/okad/model.py`:

| Type | Role |
|------|------|
| `Node` | A thing with `kind`, `layer`, human `label`, optional `source` |
| `Edge` | Story-significant relation + `confidence` |
| `Journey` | Ordered UX steps |
| `RequestPath` | Method + route + ordered internal steps |
| `DataFlow` | Origin → through → destination (+ optional shape) |
| `StoryGraph` | The whole map |

### Node kinds

`journey | screen | action | route | handler | service | store | entity | external | layer | system`

### Edge kinds

`navigates | triggers | calls | reads | writes | transforms | returns | contains | depends_on`

### Layers

`experience | interface | application | data | infra`

## Caps (non-negotiable)

| Stage | Cap | Why |
|-------|-----|-----|
| Skeleton per layer | ~24 | Avoid milky-way seeds |
| Final story nodes | ~60 | Viz stays readable |
| Journeys | aim 3–7 | Narrative focus |
| Request paths | aim 5–15 | Cover the real API surface |
| Data flows | aim 3–8 | Show movement, not schema dump |

Priority when capping: nodes referenced by journeys / requests / data flows win.

## Confidence

| Value | Meaning |
|-------|---------|
| `extracted` | Evidenced in code (route decorator, file-based route, …) |
| `inferred` | Strongly suggested by structure / naming / call patterns |
| `ambiguous` | Plausible but unsure — still useful, marked honestly |

## Viz views

1. **Architecture** — columns by layer, pan/zoom, animated cards  
2. **Agents & tools** — each agent and the tools it calls (from `agents` or inferred)  
3. **Journeys** — one sequence at a time  
4. **Requests** — handler chain left → right  
5. **Data flow** — payload movement pipeline  
6. **Mermaid** — toggle panel for sequence / flowchart of the current focus  

Story schema `version` is `2` when agents are supported. 

## Extension points

- `extract.py` — add framework signals **without** removing caps  
- `viz.py` — new view tabs, keep self-contained HTML  
- `skill/SKILL.md` — improve agent authoring instructions  
- `merge.py` — validation / normalization of drafts  

See also [schema.md](schema.md).
