"""QueryPipeline: on-demand ArXiv fetch → process → embed → store."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

from src.ingestion.downloader import ArXivDownloader, PaperMetadata
from src.ingestion.processor import PDFProcessor
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Stats returned after running the pipeline for a concept.

    Attributes:
        concept: The concept that was queried.
        fetched: Number of new papers downloaded and indexed.
        skipped: Number of papers already in the store (deduped).
        total_chunks: Total new chunks added to the vector store.
        elapsed_seconds: Wall time for the full run.
    """

    concept: str
    fetched: int
    skipped: int
    total_chunks: int
    elapsed_seconds: float


class QueryPipeline:
    """Fetches ArXiv papers on-demand and indexes them into the vector store.

    Given a concept (e.g. "attention mechanism"), this pipeline:
      1. Searches ArXiv for relevant papers.
      2. Skips papers already indexed (deduplication by arxiv_id).
      3. Downloads, processes, and embeds new papers.
      4. Stores chunks in ChromaDB with full metadata.

    Args:
        vector_store: Initialized VectorStore to index papers into.
        raw_dir: Directory to save downloaded PDFs.
        max_results: Max papers to fetch from ArXiv per query.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        raw_dir: str | Path = "./data/raw",
        max_results: int = 10,
    ) -> None:
        self.store = vector_store
        self.downloader = ArXivDownloader(output_dir=raw_dir)
        self.processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
        self.max_results = max_results

    def fetch_and_embed(self, concept: str) -> PipelineResult:
        """Search ArXiv for concept, index any new papers found.

        Args:
            concept: Research concept to search for (e.g. "attention mechanism").

        Returns:
            PipelineResult with stats about what was fetched vs skipped.
        """
        start = time.time()
        logger.info("Pipeline started for concept: '%s'", concept)

        # 1. Search ArXiv
        papers = self.downloader.search_papers(concept, max_results=self.max_results)
        logger.info("Found %d papers on ArXiv", len(papers))

        # 2. Deduplicate: find which arxiv_ids are already in the store
        known_ids = self._get_known_ids([p.arxiv_id for p in papers])
        new_papers = [p for p in papers if p.arxiv_id not in known_ids]
        skipped = len(papers) - len(new_papers)
        logger.info("%d new papers, %d already indexed", len(new_papers), skipped)

        # 3. Download + process + embed new papers
        total_chunks = 0
        fetched = 0

        for paper in new_papers:
            try:
                pdf_path = self.downloader.download_pdf(paper)
                if pdf_path is None:
                    continue

                chunks = self.processor.process_pdf(pdf_path, paper=paper)
                if not chunks:
                    continue

                texts = [c.text for c in chunks]
                metadatas = [
                    {**c.metadata, "categories": ", ".join(paper.categories), "concept": concept}
                    for c in chunks
                ]
                ids = [f"{paper.arxiv_id}-{i}" for i in range(len(chunks))]

                self.store.add_documents(texts=texts, metadatas=metadatas, ids=ids)
                total_chunks += len(chunks)
                fetched += 1
                logger.info("Indexed '%s' (%d chunks)", paper.title[:60], len(chunks))

            except Exception as e:
                logger.warning("Failed to process %s: %s", paper.arxiv_id, e)
                continue

        elapsed = round(time.time() - start, 1)
        result = PipelineResult(
            concept=concept,
            fetched=fetched,
            skipped=skipped,
            total_chunks=total_chunks,
            elapsed_seconds=elapsed,
        )
        logger.info("Pipeline done: %s", result)
        return result

    def _get_known_ids(self, arxiv_ids: list[str]) -> set[str]:
        """Return the subset of arxiv_ids already present in the store."""
        if not arxiv_ids:
            return set()
        try:
            results = self.store._collection.get(
                where={"arxiv_id": {"$in": arxiv_ids}},
                include=["metadatas"],
            )
            return {m["arxiv_id"] for m in results["metadatas"]}
        except Exception:
            return set()
