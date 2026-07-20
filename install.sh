#!/usr/bin/env bash
# OKAD one-shot installer for macOS / Linux.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Abmstpha/OKAD/main/install.sh | bash
# Or:
#   ./install.sh
set -euo pipefail

REPO_URL="git+https://github.com/Abmstpha/OKAD.git"
export PATH="${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:${PATH}"

die() {
  printf '%s\n' "error: $*" >&2
  exit 1
}

have() { command -v "$1" >/dev/null 2>&1; }

install_with_uv() {
  echo "→ installing okad with uv tool…"
  uv tool install --force "${REPO_URL}"
}

install_with_pipx() {
  echo "→ installing okad with pipx (pip backend)…"
  # --backend pip avoids pipx requiring a brand-new uv (common Homebrew trap)
  pipx install --force --backend pip "${REPO_URL}"
}

ensure_pipx() {
  if have pipx; then
    return 0
  fi
  if have brew; then
    echo "→ installing pipx via Homebrew…"
    brew install pipx
  else
    die "need pipx or uv. Install one of:
  brew install pipx
  # or https://docs.astral.sh/uv/"
  fi
  pipx ensurepath --force >/dev/null 2>&1 || true
  export PATH="${HOME}/.local/bin:${PATH}"
}

main() {
  if have uv; then
    install_with_uv
  else
    ensure_pipx
    install_with_pipx
  fi

  export PATH="${HOME}/.local/bin:${PATH}"
  have okad || die "okad binary not on PATH. Open a new terminal, then run: okad install
  (expected location: ${HOME}/.local/bin/okad)"

  echo "→ okad $(okad version)"
  echo "→ wiring /okad skill into Claude / Codex / Cursor…"
  okad install

  cat <<'EOF'

OKAD is ready.

  cd /path/to/your-project
  # open Cursor / Claude Code / Codex and run:
  /okad

Then open okad-out/story.html
EOF
}

main "$@"
