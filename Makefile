.PHONY: install install-dev test format lint clean api ui

install:
	uv sync

install-dev:
	uv sync
	uv run pre-commit install

test:
	uv run pytest tests/ -v

format:
	uv run black src/ tests/
	uv run ruff check src/ tests/ --fix

lint:
	uv run black src/ tests/ --check
	uv run ruff check src/ tests/

api:
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

ui:
	uv run streamlit run src/ui/app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/

test:
	pytest tests/ -v

format:
	black src/ tests/
	ruff check src/ tests/ --fix

lint:
	black src/ tests/ --check
	ruff check src/ tests/

api:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

ui:
	streamlit run src/ui/app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
