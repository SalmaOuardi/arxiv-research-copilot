# ArXiv Research Copilot

Idea-evolution copilot for research concepts: fetch papers from ArXiv on demand, index them in ChromaDB, and generate a chronological narrative with citation grounding.

## What This Project Is Now

The project has shifted from a generic "RAG Q&A app" toward a focused **narrative engine**:

- Input: a concept (for example, `"attention mechanism"`).
- Pipeline: live ArXiv fetch -> PDF processing -> chunking -> embedding -> vector indexing.
- Output: an LLM-generated timeline narrative showing how the idea evolved, plus contradiction checks between adjacent claims.

## Current Implemented Scope

- `ArXivDownloader` with search, category filtering, caching, and PDF download.
- `PDFProcessor` with text extraction (PyMuPDF) and chunking.
- `Embedder` using Ollama's OpenAI-compatible API (`nomic-embed-text` by default).
- `VectorStore` on persistent ChromaDB with semantic search and metadata.
- `QueryPipeline.fetch_and_embed(concept)` for on-demand indexing with deduplication.
- `NarrativeEngine.generate(concept)` for claim extraction, chronological sorting, narrative generation, and contradiction detection.

Note: FastAPI and Streamlit entry points exist, but most endpoints and UI actions are still scaffolded (`501`/TODO).

## Tech Stack

- Python 3.11+
- Ollama (local)
- ChromaDB
- OpenAI-compatible client (`openai` package) targeting Ollama
- ArXiv API (`arxiv` package)
- PyMuPDF for PDF text extraction

## Quick Start

### 1) Install

```bash
git clone https://github.com/SalmaOuardi/arxiv-research-copilot.git
cd arxiv-research-copilot
uv sync
```

### 2) Start Ollama and pull models

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:7b
ollama serve
```

The code expects Ollama at `http://localhost:11434/v1`.

### 3) Run tests

```bash
make test
```

### 4) Run an ingestion script (optional)

```bash
uv run python scripts/run_ingestion.py
```

## Programmatic Usage (Narrative Engine)

```python
from src.generation.llm import LLMHandler
from src.generation.narrative import NarrativeEngine
from src.ingestion.pipeline import QueryPipeline
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore

embedder = Embedder(model="nomic-embed-text")
store = VectorStore(embedder=embedder)
pipeline = QueryPipeline(vector_store=store, max_results=8)
llm = LLMHandler(model="qwen2.5:7b")

engine = NarrativeEngine(
    pipeline=pipeline,
    vector_store=store,
    llm=llm,
    papers_per_concept=8,
    chunks_per_paper=3,
)

result = engine.generate("attention mechanism")
print(result.narrative)
```

## Project Structure

```text
src/
  ingestion/    # ArXiv search/download + PDF processing + on-demand pipeline
  retrieval/    # Embedding client + Chroma vector store
  generation/   # Prompts + LLM handler + narrative engine
  api/          # FastAPI scaffold (partially implemented)
  ui/           # Streamlit scaffold (partially implemented)
tests/          # Unit tests for ingestion/retrieval/generation modules
scripts/        # Utility scripts for download/process/full ingestion
```

## Development Commands

```bash
make install       # uv sync
make test          # pytest
make format        # black + ruff --fix
make lint          # black --check + ruff
make api           # run FastAPI app
make ui            # run Streamlit app
```

## License

MIT (see `LICENSE`).
