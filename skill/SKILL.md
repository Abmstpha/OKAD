---
name: okad
description: "Build a story-driven architecture map of any codebase — UX journeys, request paths, and data flows as readable trees and layered graphs. Use when the user runs /okad, or asks how the system flows, where requests go, or how data moves. Prefer okad-out/story.json over raw grep once it exists."
---

# /okad

Turn any codebase into a **story map**: layered architecture, user journeys, request paths, and data flows.

OKAD curates a small narrative graph — role-labeled journeys, request paths, and data flows — so a stranger can understand the system from the viz alone. It refuses milky-way dumps of every file link.

## Usage

```
/okad                         # full story pipeline on current directory
/okad <path>                  # full pipeline on a path
/okad --skeleton-only         # structural pass only (no LLM story)
/okad query "<question>"      # answer from okad-out/story.json
/okad path "A" "B"            # shortest story path
/okad explain "Checkout"      # explain a node or journey
```

## Design rules (non-negotiable)

1. **Label by role, never by filename.** Prefer `Checkout`, `Auth gate`, `Order store` — not `checkout_controller.ts`.
2. **Cap the graph.** Top-level story ≤ ~40–60 nodes. Aggregate noise into layer hubs.
3. **Edges must tell a story.** Only navigates / triggers / calls / reads / writes / transforms / returns. No import spaghetti.
4. **Four views matter:** Architecture (columns), Journeys (trees), Requests (sequences), Data flow (pipelines).
5. **Honesty:** mark confidence `extracted` | `inferred` | `ambiguous`. Never invent a route that is not evidenced.

Layers (left → right in the viz):

| Layer | Meaning |
|-------|---------|
| experience | Screens, actions, user-visible steps |
| interface | HTTP routes, events, CLI entrypoints |
| application | Services, use-cases, orchestration |
| data | Stores, entities, databases |
| infra | Queues, caches, third-party APIs |

---

## What You Must Do When Invoked

If the user invoked `/okad --help` or `/okad -h`, print the Usage section above and stop.

### Fast path — existing story

If `okad-out/story.json` exists **and** the user asked a natural-language question (not a rebuild), run:

```bash
okad query "<question>"
```

Do not rebuild. Answer from the story graph. Offer one follow-up path to explore.

If they asked `path` or `explain`, run the matching CLI.

---

### Step 0 — Ensure OKAD is installed

```bash
if ! command -v okad >/dev/null 2>&1 || ! python3 -c "import okad" 2>/dev/null; then
  if command -v uv >/dev/null 2>&1; then
    uv pip install -e . 2>/dev/null || uv tool install okad 2>/dev/null || python3 -m pip install -e .
  else
    python3 -m pip install -e . 2>/dev/null || python3 -m pip install okad
  fi
fi
okad version
```

If installing from this repo, prefer editable install from the project root.

---

### Step 1 — Detect + structural skeleton

If no path was given, use `.`

```bash
okad skeleton INPUT_PATH
```

Read `okad-out/skeleton.md` (brief) and optionally `okad-out/skeleton.json`.
Present the detect summary to the user (file counts only). Do **not** dump the whole skeleton into chat.

If `--skeleton-only` was given: run `okad build INPUT_PATH`, point at `okad-out/story.html`, and stop.

---

### Step 2 — Author the story (YOU are the model)

You write `okad-out/story.draft.json`. This is the product differentiator.

Read enough of the codebase to understand **real** flows — but stay surgical:

1. Read `okad-out/skeleton.md`.
2. Open the highest-signal entrypoints only (routers, `app/` pages, main services, schema files). Use the skeleton `source` paths.
3. Infer **3–7 user journeys**, **5–15 request paths**, **3–8 data flows**, and **agents with tools** (LangGraph / AI workers).
4. Keep total nodes ≤ 60.

Write JSON with this schema:

```json
{
  "system_name": "Short product name",
  "summary": "One paragraph a new engineer would need.",
  "nodes": [
    {
      "id": "screen:checkout",
      "label": "Checkout",
      "kind": "screen",
      "layer": "experience",
      "summary": "User reviews cart and pays",
      "source": "optional/relative/path",
      "meta": {}
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "screen:checkout",
      "target": "route:POST:/api/orders",
      "kind": "triggers",
      "label": "submit order",
      "confidence": "extracted"
    }
  ],
  "journeys": [
    {
      "id": "j-checkout",
      "name": "Checkout",
      "summary": "Guest buys a product",
      "actor": "user",
      "steps": [
        {"node_id": "screen:catalog", "note": "browse"},
        {"node_id": "screen:checkout", "note": "pay"},
        {"node_id": "route:POST:/api/orders", "note": "create order"}
      ]
    }
  ],
  "requests": [
    {
      "id": "req-create-order",
      "name": "Create order",
      "method": "POST",
      "route": "/api/orders",
      "summary": "Persists order and charges payment",
      "steps": ["route:POST:/api/orders", "service:orders", "store:orders", "infra:stripe"],
      "status": ["201", "400", "401"]
    }
  ],
  "data_flows": [
    {
      "id": "df-order",
      "name": "Order payload",
      "summary": "Cart line items become a persisted order",
      "origin": "screen:checkout",
      "through": ["route:POST:/api/orders", "service:orders"],
      "destination": "store:orders",
      "shape": "Order { items[], total, currency }"
    }
  ],
  "agents": [
    {
      "id": "agent:seller-engine",
      "name": "Seller Deal Engine",
      "summary": "LangGraph that builds a deal package from an address",
      "node_id": "service:seller-graph",
      "tools": [
        {"id": "tool:verify-address", "name": "Verify address", "summary": "Normalizes and validates the property"},
        {"id": "tool:valuation", "name": "Valuation", "summary": "Comps + estimate"},
        {"id": "tool:str-roi", "name": "STR ROI", "summary": "Airbnb revenue model"}
      ]
    }
  ]
}
```

Allowed `kind`: `journey|screen|action|route|handler|service|store|entity|external|layer|system|agent|tool`  
Allowed edge `kind`: `navigates|triggers|calls|reads|writes|transforms|returns|contains|depends_on`  
Allowed `layer`: `experience|interface|application|data|infra`

**Always author `agents` when the codebase has LangGraph / LLM workers** — each agent lists its tools (graph nodes, retrieval, externals). The Agents & tools view depends on this.

**Reuse skeleton node ids when they match.** Add new story ids when the skeleton is incomplete.

Write the file with the Write tool:

`okad-out/story.draft.json`

---

### Step 3 — Finalize outputs

```bash
okad finalize INPUT_PATH
```

This merges draft + skeleton and writes:

```
okad-out/story.html       # interactive story map (open in browser)
okad-out/STORY_REPORT.md  # plain-language report
okad-out/story.json       # queryable graph
```

---

### Step 4 — Report to the user

Tell them:

```
Story map ready → PATH/okad-out/

  story.html        interactive architecture / journeys / requests / data
  STORY_REPORT.md   plain-language narrative
  story.json        queryable story graph
```

Paste only:

- system summary (1 short paragraph)
- list of journey names
- 3 most important request paths

Then ask one sharp follow-up, e.g.  
> Want me to trace **Checkout** end-to-end with `okad path`?

---

## For /okad query · path · explain

```bash
okad query "<question>"
okad path "Auth gate" "Order store"
okad explain "Checkout"
```

Answer using only graph output. Cite `source` paths when present.

---

## Anti-patterns

- Do **not** emit thousands of file-to-file import edges.
- Do **not** name nodes after filenames or class names unless that name is the user-facing concept.
- Do **not** skip the elegance cap — if unsure, drop the node.
- Do **not** ask for an API key. You (the host model) author the story.
