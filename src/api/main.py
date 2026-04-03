"""FastAPI application for the ArXiv Research Copilot."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.generation.llm import LLMHandler
from src.generation.narrative import NarrativeEngine
from src.ingestion.pipeline import QueryPipeline
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore

# ---------------------------------------------------------------------------
# App state — initialized once on startup, shared across all requests
# ---------------------------------------------------------------------------

state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize heavy objects once on startup, clean up on shutdown."""
    embedder = Embedder()
    store = VectorStore(embedder)
    pipeline = QueryPipeline(store, max_results=8)
    llm = LLMHandler()
    engine = NarrativeEngine(pipeline, store, llm, papers_per_concept=8)

    state["store"] = store
    state["engine"] = engine
    yield
    state.clear()


app = FastAPI(
    title="ArXiv Research Copilot",
    description="Agentic RAG system for idea evolution narratives",
    version="0.2.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class NarrativeRequest(BaseModel):
    concept: str = Field(..., description="Research concept to trace (e.g. 'attention mechanism')")
    max_papers: int = Field(default=8, ge=1, le=20)


class PaperClaimOut(BaseModel):
    arxiv_id: str
    title: str
    authors: str
    published: str
    claim: str


class ContradictionOut(BaseModel):
    paper_a: str
    paper_b: str
    explanation: str


class NarrativeResponse(BaseModel):
    concept: str
    narrative: str
    timeline: list[PaperClaimOut]
    contradictions: list[ContradictionOut]


class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=50)
    context: str | None = Field(default=None, description="Extra terms to disambiguate the query")


class SearchResultOut(BaseModel):
    text: str
    score: float
    arxiv_id: str
    title: str
    published: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultOut]


class HealthResponse(BaseModel):
    status: str
    version: str
    indexed_documents: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    store: VectorStore = state.get("store")
    count = store.get_collection_stats()["count"] if store else 0
    return HealthResponse(status="healthy", version="0.2.0", indexed_documents=count)


@app.post("/narrative", response_model=NarrativeResponse)
async def generate_narrative(request: NarrativeRequest) -> NarrativeResponse:
    """Fetch ArXiv papers on-demand and generate an idea evolution narrative."""
    engine: NarrativeEngine = state.get("engine")
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    try:
        output = engine.generate(request.concept)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return NarrativeResponse(
        concept=output.concept,
        narrative=output.narrative,
        timeline=[PaperClaimOut(**c.__dict__) for c in output.timeline],
        contradictions=[ContradictionOut(**c.__dict__) for c in output.contradictions],
    )


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """Semantic search over indexed papers."""
    store: VectorStore = state.get("store")
    if not store:
        raise HTTPException(status_code=503, detail="Store not initialized")

    try:
        results = store.search(request.query, top_k=request.top_k, context=request.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return SearchResponse(
        query=request.query,
        results=[
            SearchResultOut(
                text=r.text,
                score=round(r.score, 4),
                arxiv_id=r.metadata.get("arxiv_id", ""),
                title=r.metadata.get("title", ""),
                published=r.metadata.get("published", ""),
            )
            for r in results
        ],
    )
