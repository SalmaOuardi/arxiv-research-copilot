.PHONY: install install-dev test format lint clean api ui

install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

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
