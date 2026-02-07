"""Tests for the retrieval module."""

from __future__ import annotations

import numpy as np
import pytest

from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import SearchResult, VectorStore


class TestEmbedder:
    """Tests for Embedder class."""

    def test_init_default_values(self) -> None:
        """Test default initialization values."""
        embedder = Embedder()
        assert embedder.provider == "openai"
        assert embedder.model == "text-embedding-3-small"
        assert embedder.dimensions == 1536

    def test_embed_documents_empty_list(self) -> None:
        """Test that ValueError is raised for empty input."""
        embedder = Embedder()
        with pytest.raises(ValueError, match="Cannot embed empty"):
            embedder.embed_documents([])

    def test_embed_query_empty_string(self) -> None:
        """Test that ValueError is raised for empty query."""
        embedder = Embedder()
        with pytest.raises(ValueError, match="Cannot embed empty"):
            embedder.embed_query("")

    def test_compute_similarity_identical(self) -> None:
        """Test cosine similarity of identical vectors is 1.0."""
        embedder = Embedder()
        vec = [1.0, 2.0, 3.0]
        similarity = embedder.compute_similarity(vec, vec)
        assert abs(similarity - 1.0) < 1e-6

    def test_compute_similarity_orthogonal(self) -> None:
        """Test cosine similarity of orthogonal vectors is 0.0."""
        embedder = Embedder()
        vec_a = [1.0, 0.0]
        vec_b = [0.0, 1.0]
        similarity = embedder.compute_similarity(vec_a, vec_b)
        assert abs(similarity) < 1e-6

    # TODO: Add test for embed_documents with mocked API
    # TODO: Add test for embed_query with mocked API
    # TODO: Add test for batch processing behavior


class TestVectorStore:
    """Tests for VectorStore class."""

    def test_init_creates_directory(self, tmp_path: str) -> None:
        """Test that the persist directory is created."""
        persist_dir = tmp_path / "embeddings"
        store = VectorStore(persist_directory=persist_dir)
        assert persist_dir.exists()

    def test_add_documents_empty_list(self) -> None:
        """Test that ValueError is raised for empty document list."""
        store = VectorStore()
        with pytest.raises(ValueError, match="Cannot add empty"):
            store.add_documents([])

    # TODO: Add test for add_documents with mocked ChromaDB
    # TODO: Add test for search with mocked ChromaDB
    # TODO: Add test for delete_documents
    # TODO: Add test for metadata filtering
