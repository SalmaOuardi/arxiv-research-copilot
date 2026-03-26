"""Vector store module using ChromaDB for persistent similarity search."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import chromadb

from src.retrieval.embedder import Embedder

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result from the vector store.

    Attributes:
        text: The document text content.
        metadata: Associated metadata dict.
        score: Similarity score (higher is more similar).
        doc_id: Unique document identifier in the store.
    """

    text: str
    metadata: dict[str, Any]
    score: float
    doc_id: str


class VectorStore:
    """Manages vector storage and similarity search using ChromaDB.

    Args:
        embedder: Embedder instance used to embed queries and documents.
        collection_name: Name of the ChromaDB collection.
        persist_directory: Directory to persist the database.
    """

    def __init__(
        self,
        embedder: Embedder,
        collection_name: str = "arxiv_papers",
        persist_directory: str | Path = "./data/embeddings",
    ) -> None:
        self.embedder = embedder
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        client = chromadb.PersistentClient(path=str(self.persist_directory))
        self._collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "VectorStore ready. Collection '%s' has %d documents.",
            collection_name,
            self._collection.count(),
        )

    def add_documents(
        self,
        texts: list[str],
        metadatas: Optional[list[dict[str, Any]]] = None,
        ids: Optional[list[str]] = None,
        embeddings: Optional[list[list[float]]] = None,
    ) -> list[str]:
        """Embed and store documents. Skips duplicates by ID (upsert).

        Args:
            texts: Document text strings.
            metadatas: Metadata dicts, one per document.
            ids: Unique IDs. Auto-generated if not provided.
            embeddings: Pre-computed embeddings. Computed if not provided.

        Returns:
            List of document IDs added.
        """
        if not texts:
            raise ValueError("Cannot add empty document list")

        ids = ids or [str(uuid.uuid4()) for _ in texts]
        metadatas = metadatas or [{} for _ in texts]

        if embeddings is None:
            embeddings = self.embedder.embed_documents(texts)

        self._collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info("Added %d documents to '%s'", len(texts), self.collection_name)
        return ids

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[dict[str, Any]] = None,
        similarity_threshold: Optional[float] = None,
    ) -> list[SearchResult]:
        """Search for documents similar to query.

        Args:
            query: Natural language search query.
            top_k: Maximum number of results to return.
            filter_metadata: ChromaDB where clause for metadata filtering.
            similarity_threshold: Minimum similarity score (0–1) to include.

        Returns:
            List of SearchResult sorted by relevance (best first).
        """
        query_embedding = self.embedder.embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._collection.count()),
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        for doc, meta, distance, doc_id in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
            results["ids"][0],
        ):
            score = 1.0 - distance  # cosine distance → similarity
            if similarity_threshold is not None and score < similarity_threshold:
                continue
            search_results.append(SearchResult(text=doc, metadata=meta, score=score, doc_id=doc_id))

        return search_results

    def get_collection_stats(self) -> dict[str, Any]:
        """Return basic stats about the collection."""
        return {"collection": self.collection_name, "count": self._collection.count()}
