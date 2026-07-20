# Philosophy

## The problem

Modern agentic coding produces **too many files and too many links**.

Knowledge graphs that mirror every import look impressive and read like a milky way: bright, dense, and useless for onboarding. Naming nodes after filenames (`UserServiceImpl.ts`) teaches the file tree, not the system.

## The bet

A map should answer:

- What does a **user** do?
- Where does a **request** go?
- How does a piece of **data** move and change?

If a stranger can answer those from one HTML page, the map succeeded.

## Principles

### 1. Story over inventory

Prefer seven true journeys over seven hundred true edges.

### 2. Roles over paths

`Checkout` beats `src/pages/checkout/index.tsx`. Paths live in `source` metadata for citation — labels stay human.

### 3. Layers are a contract

Left → right:

**Experience → Interface → Application → Data → Infra**

If you cannot place a node in a layer, you do not understand it yet — do not draw it.

### 4. Elegance is a feature

Hard caps exist on purpose. When in doubt, **drop the node** or fold it into a layer hub.

### 5. Honesty over vibes

Every edge carries confidence: `extracted`, `inferred`, or `ambiguous`. Invented routes are a bug.

### 6. Local-first, agent-native

OKAD runs on your machine. The host LLM authors narrative. No SaaS, no telemetry, no required cloud key for the CLI.

## What we refuse

- Force-directed spaghetti as the default viz
- “Show everything” as a product goal
- Replacing Graphify — different job, different tool

## Aesthetic

The HTML viz should feel like a **diagram you’d pin on a wall**, not a physics simulation you’d apologize for.
