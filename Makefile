.PHONY: help install test lint example clean

help:
	@echo "OKAD make targets:"
	@echo "  make install   - editable install with dev deps"
	@echo "  make test      - pytest"
	@echo "  make lint      - ruff"
	@echo "  make example   - skeleton+finalize mini-shop"
	@echo "  make clean     - remove caches and example okad-out"

install:
	uv pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src tests

example:
	okad skeleton examples/mini-shop
	cp examples/mini-shop/story.draft.json examples/mini-shop/okad-out/story.draft.json
	okad finalize examples/mini-shop
	@echo "Open examples/mini-shop/okad-out/story.html"

clean:
	rm -rf .pytest_cache .ruff_cache src/okad.egg-info okad.egg-info
	rm -rf examples/mini-shop/okad-out
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true
