# Story JSON schema

Version `2` documents produced by OKAD (version `1` lacked `agents`).

## Top level

```json
{
  "version": 2,
  "system_name": "string",
  "summary": "string",
  "layers": [{ "id": "experience", "label": "Experience", "blurb": "..." }],
  "nodes": [],
  "edges": [],
  "journeys": [],
  "requests": [],
  "data_flows": [],
  "agents": [],
  "meta": {}
}
```

## Agent

```json
{
  "id": "agent:seller-engine",
  "name": "Seller Deal Engine",
  "summary": "What this agent does",
  "role": "LangGraph orchestrator",
  "level": "orchestrator",
  "parent_id": "agent:pipeline",
  "node_id": "service:seller-graph",
  "flow": ["agent:verify", "agent:value"],
  "relations": [{ "target": "agent:buyer", "kind": "feeds", "label": "deal package" }],
  "tools": [{ "id": "t1", "name": "estimate_value", "summary": "", "source": null }]
}
```

`level` is `system | orchestrator | subagent`. `flow` orders child agents;
the viewer shows it as numbered badges. `node_id` links the agent to an
architecture node.

## Validation

`okad finalize` validates draft values against the schema enums: unknown
`kind` / `layer` / `confidence` values are close-match corrected (e.g.
`"aplication"` → `"application"`) or fall back to defaults, and every
correction is recorded in `meta.warnings`.

## Node

```json
{
  "id": "screen:checkout",
  "label": "Checkout",
  "kind": "screen",
  "layer": "experience",
  "summary": "User reviews cart and pays",
  "source": "apps/web/app/checkout/page.tsx",
  "meta": {}
}
```

`id` should be stable and readable. Prefer `kind:slug` patterns.

## Edge

```json
{
  "id": "e1",
  "source": "screen:checkout",
  "target": "route:POST:/api/orders",
  "kind": "triggers",
  "label": "submit order",
  "confidence": "extracted",
  "meta": {}
}
```

## Journey

```json
{
  "id": "j-checkout",
  "name": "Checkout",
  "summary": "Guest buys a product",
  "actor": "user",
  "steps": [
    { "node_id": "screen:catalog", "note": "browse" },
    { "node_id": "screen:checkout", "note": "pay" }
  ]
}
```

## Request path

```json
{
  "id": "req-create-order",
  "name": "Create order",
  "method": "POST",
  "route": "/api/orders",
  "summary": "Persists order and charges payment",
  "steps": ["route:POST:/api/orders", "service:orders", "store:orders"],
  "status": ["201", "400", "401"]
}
```

## Data flow

```json
{
  "id": "df-order",
  "name": "Order payload",
  "summary": "Cart becomes a persisted order",
  "origin": "screen:checkout",
  "through": ["route:POST:/api/orders", "service:orders"],
  "destination": "store:orders",
  "shape": "Order { items[], total, currency }"
}
```

## Draft vs final

- Agents write **`okad-out/story.draft.json`** (same shape, may omit `version` / `layers`).
- `okad finalize` merges onto the skeleton and writes **`okad-out/story.json`**.

See [examples/mini-shop/story.draft.json](../examples/mini-shop/story.draft.json).
