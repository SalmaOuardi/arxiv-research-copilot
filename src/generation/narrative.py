"""NarrativeEngine: generates an idea evolution narrative from ArXiv papers."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.generation.llm import LLMHandler
from src.generation.prompts import (
    CLAIM_EXTRACTOR_TEMPLATE,
    CONTRADICTION_DETECTOR_TEMPLATE,
    NARRATIVE_GENERATOR_TEMPLATE,
)
from src.ingestion.pipeline import QueryPipeline
from src.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)


@dataclass
class PaperClaim:
    arxiv_id: str
    title: str
    authors: str
    published: str
    claim: str


@dataclass
class Contradiction:
    paper_a: str
    paper_b: str
    explanation: str


@dataclass
class NarrativeOutput:
    concept: str
    narrative: str
    timeline: list[PaperClaim]
    contradictions: list[Contradiction] = field(default_factory=list)


class NarrativeEngine:
    """Generates an idea evolution narrative for a given concept.

    Args:
        pipeline: QueryPipeline for fetching and indexing papers.
        vector_store: VectorStore for retrieving relevant chunks.
        llm: LLMHandler for text generation.
        papers_per_concept: How many papers to fetch from ArXiv.
        chunks_per_paper: How many chunks to retrieve per paper for claim extraction.
    """

    def __init__(
        self,
        pipeline: QueryPipeline,
        vector_store: VectorStore,
        llm: LLMHandler,
        papers_per_concept: int = 8,
        chunks_per_paper: int = 3,
    ) -> None:
        self.pipeline = pipeline
        self.store = vector_store
        self.llm = llm
        self.papers_per_concept = papers_per_concept
        self.chunks_per_paper = chunks_per_paper

    def generate(self, concept: str) -> NarrativeOutput:
        """Generate an idea evolution narrative for a concept."""
        # 1. Fetch papers on-demand
        self.pipeline.fetch_and_embed(concept)

        # 2. Retrieve top chunks across all papers
        results = self.store.search(
            concept,
            top_k=self.papers_per_concept * self.chunks_per_paper,
            context="research paper academic",
        )

        # 3. Group chunks by paper
        papers: dict[str, dict] = {}
        for r in results:
            aid = r.metadata.get("arxiv_id", "")
            if not aid:
                continue
            if aid not in papers:
                papers[aid] = {
                    "arxiv_id": aid,
                    "title": r.metadata.get("title", "Unknown"),
                    "authors": r.metadata.get("authors", ""),
                    "published": r.metadata.get("published", ""),
                    "chunks": [],
                }
            if len(papers[aid]["chunks"]) < self.chunks_per_paper:
                papers[aid]["chunks"].append(r.text)

        # 4. Extract one claim per paper
        claims: list[PaperClaim] = []
        for paper in papers.values():
            claim_text = self._extract_claim(paper, concept)
            claims.append(PaperClaim(
                arxiv_id=paper["arxiv_id"],
                title=paper["title"],
                authors=paper["authors"],
                published=paper["published"],
                claim=claim_text,
            ))

        # 5. Sort chronologically
        claims.sort(key=lambda c: c.published or "")

        # 6. Generate narrative
        narrative = self._generate_narrative(concept, claims)

        # 7. Detect contradictions
        contradictions = self._detect_contradictions(concept, claims)

        return NarrativeOutput(
            concept=concept,
            narrative=narrative,
            timeline=claims,
            contradictions=contradictions,
        )

    def _extract_claim(self, paper: dict, concept: str) -> str:
        prompt = CLAIM_EXTRACTOR_TEMPLATE.format(
            title=paper["title"],
            published=paper["published"][:10] if paper["published"] else "unknown",
            authors=paper["authors"],
            chunks="\n\n---\n\n".join(paper["chunks"]),
            concept=concept,
        )
        return self.llm.generate(prompt)

    def _generate_narrative(self, concept: str, claims: list[PaperClaim]) -> str:
        timeline_text = "\n\n".join([
            f"[{c.published[:4] if c.published else '????'}] {c.title} ({c.arxiv_id})\n{c.claim}"
            for c in claims
        ])
        prompt = NARRATIVE_GENERATOR_TEMPLATE.format(
            concept=concept,
            timeline=timeline_text,
        )
        return self.llm.generate(prompt, temperature=0.3)

    def _detect_contradictions(self, concept: str, claims: list[PaperClaim]) -> list[Contradiction]:
        contradictions = []
        for i in range(len(claims) - 1):
            a, b = claims[i], claims[i + 1]
            prompt = CONTRADICTION_DETECTOR_TEMPLATE.format(
                concept=concept,
                title_a=a.title,
                year_a=a.published[:4] if a.published else "????",
                claim_a=a.claim,
                title_b=b.title,
                year_b=b.published[:4] if b.published else "????",
                claim_b=b.claim,
            )
            response = self.llm.generate(prompt)
            if response.strip().upper().startswith("YES"):
                contradictions.append(Contradiction(
                    paper_a=a.arxiv_id,
                    paper_b=b.arxiv_id,
                    explanation=response,
                ))
        return contradictions
