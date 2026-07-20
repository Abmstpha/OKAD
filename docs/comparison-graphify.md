# OKAD vs Graphify

Both help agents understand codebases. They optimize for different questions.

| Dimension | Graphify | OKAD |
|-----------|----------|------|
| Primary artifact | Dense knowledge graph | Story map |
| Default viz | Force / community graph | Layered columns + trees |
| Node naming | Often file/symbol oriented | Role / product language |
| Edge density | High (many connections) | Low (story-significant) |
| Best question | “What connects to X?” | “How does X flow?” |
| Agent command | `/graphify` | `/okad` |
| Typical size | Thousands of nodes OK | Tens of nodes preferred |
| Structural pass | tree-sitter AST | Heuristic skeleton (capped) |
| Semantic pass | Docs/papers/images + agent | Journeys/requests/data via agent |

## Use Graphify when

- You need exhaustive symbol/community structure
- You want `query` / `path` / `explain` over a huge corpus
- You are auditing surprising cross-module links

## Use OKAD when

- You are onboarding a human (or agent) to **how the product works**
- You want a diagram for a PR, design review, or README
- File-link spaghetti would confuse more than it helps

## Can they coexist?

Yes. Many repos can keep both:

- `graphify-out/` — deep inventory  
- `okad-out/` — narrative map  

Rule of thumb for agents: flow / UX / request questions → OKAD first; broad “what exists” → Graphify.

OKAD is **inspired by** Graphify’s agent-skill distribution model, not a fork. Different product, MIT, independent.
