# Changelog

All notable changes to OKAD are documented here.

Format inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
OKAD follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned

- Richer multi-language extractors (Go, Rails, Nest deeper)
- SVG / GraphML export
- PyPI publish (`okad`)

## [0.2.0] — 2026-07-20

### Added

- Story map v2 viz: pan/zoom fit-to-laptop, animated node cards, flowing edges
- **Agents & tools** tab (+ `agents` in story draft / `story.json`)
- Mermaid sequence panel for journeys, requests, agents
- `okad render` to rebuild `story.html` from existing `story.json`
- Version chips in the HTML header (`okad X.Y.Z` · `story vN`)

### Changed

- Install path documents `pipx --backend pip` / `curl | bash` for Homebrew Macs

## [0.1.0] — 2026-07-20

### Added

- Initial public release
- CLI: `detect`, `skeleton`, `finalize`, `build`, `query`, `path`, `explain`, `install`, `open`
- Story model: layers, journeys, request paths, data flows
- Elegance caps so maps stay readable (~60 nodes)
- Interactive `story.html` (Architecture / Journeys / Requests / Data flow)
- `/okad` skill for Claude Code, Codex, Cursor, AGENTS.md hosts
- Smoke tests and MIT license

[Unreleased]: https://github.com/Abmstpha/OKAD/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Abmstpha/OKAD/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Abmstpha/OKAD/releases/tag/v0.1.0
