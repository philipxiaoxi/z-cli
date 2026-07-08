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

# 修复 __editable__.pth 被 macOS UF_HIDDEN 标志导致 Python 跳过的问题
# Python 3.8+ 安全修复：跳过带隐藏标志的 .pth 文件
# macOS 的 com.apple.provenance 扩展属性会触发 UF_HIDDEN
fix-pth:
	@echo "Creating fallback zspace.pth to work around macOS UF_HIDDEN issue..."
	@SITE_PKG=$$($(PYTHON) -c "import sysconfig; print(sysconfig.get_path('purelib'))"); \
	echo "$(CURDIR)/src" > "$$SITE_PKG/zspace.pth"; \
	xattr -c "$$SITE_PKG/zspace.pth"; \
	chflags 0 "$$SITE_PKG/zspace.pth"
	@echo "Done."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/
