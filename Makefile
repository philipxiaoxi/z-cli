.PHONY: install dev lint test clean

VENV = .venv/bin/
PYTHON = $(VENV)python
PIP = $(VENV)pip

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

dev:
	PYTHONPATH=src $(PYTHON) -m zspace

lint:
	$(PYTHON) -m ruff check src/ tests/
	$(PYTHON) -m mypy src/

test:
	$(PYTHON) -m pytest tests/ -v

typecheck:
	$(PYTHON) -m mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/
