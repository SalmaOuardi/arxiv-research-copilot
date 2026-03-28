"""Tests for the retrieval module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import SearchResult, VectorStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_embedder(vector: list[float] | None = None) -> Embedder:
    """Return an Embedder whose API calls are mocked."""
    vec = vector or [0.1, 0.2, 0.3]
    embedder = MagicMock(spec=Embedder)
    embedder.embed_query.return_value = vec
    embedder.embed_documents.return_value = [vec]
    return embedder


# ---------------------------------------------------------------------------
# Embedder
# ---------------------------------------------------------------------------

class TestEmbedder:

    def test_init_default_model(self) -> None:
        with patch("src.retrieval.embedder.OpenAI"):
            embedder = Embedder()
        assert embedder.model == "nomic-embed-text"
        assert embedder.batch_size == 32

    def test_embed_documents_empty_raises(self) -> None:
        with patch("src.retrieval.embedder.OpenAI"):
            embedder = Embedder()
        with pytest.raises(ValueError, match="Cannot embed empty"):
            embedder.embed_documents([])

    def test_embed_query_empty_raises(self) -> None:
        with patch("src.retrieval.embedder.OpenAI"):
            embedder = Embedder()
        with pytest.raises(ValueError, match="Cannot embed empty"):
            embedder.embed_query("   ")

    def test_embed_documents_batches_and_returns_vectors(self) -> None:
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=[0.1, 0.2, 0.3])]
        )
        with patch("src.retrieval.embedder.OpenAI", return_value=mock_client):
            embedder = Embedder(batch_size=2)
        result = embedder.embed_documents(["hello"])
        assert result == [[0.1, 0.2, 0.3]]
        mock_client.embeddings.create.assert_called_once()

    def test_embed_query_returns_vector(self) -> None:
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=[0.5, 0.6, 0.7])]
        )
        with patch("src.retrieval.embedder.OpenAI", return_value=mock_client):
            embedder = Embedder()
        result = embedder.embed_query("attention mechanism")
        assert result == [0.5, 0.6, 0.7]


# ---------------------------------------------------------------------------
# VectorStore
# ---------------------------------------------------------------------------

class TestVectorStore:

    def test_init_creates_directory(self, tmp_path) -> None:
        persist_dir = tmp_path / "embeddings"
        with patch("src.retrieval.vector_store.chromadb.PersistentClient"):
            store = VectorStore(_mock_embedder(), persist_directory=persist_dir)
        assert persist_dir.exists()

    def test_add_documents_empty_raises(self, tmp_path) -> None:
        with patch("src.retrieval.vector_store.chromadb.PersistentClient"):
            store = VectorStore(_mock_embedder(), persist_directory=tmp_path)
        with pytest.raises(ValueError, match="Cannot add empty"):
            store.add_documents([])

    def test_add_documents_calls_upsert(self, tmp_path) -> None:
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection

        with patch("src.retrieval.vector_store.chromadb.PersistentClient", return_value=mock_client):
            store = VectorStore(_mock_embedder(), persist_directory=tmp_path)

        store.add_documents(texts=["hello world"], ids=["doc-1"])
        mock_collection.upsert.assert_called_once()

    def test_search_applies_context(self, tmp_path) -> None:
        mock_collection = MagicMock()
        mock_collection.count.return_value = 1
        mock_collection.query.return_value = {
            "documents": [["some text"]],
            "metadatas": [[{"arxiv_id": "1234"}]],
            "distances": [[0.2]],
            "ids": [["doc-1"]],
        }
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection

        embedder = _mock_embedder()
        with patch("src.retrieval.vector_store.chromadb.PersistentClient", return_value=mock_client):
            store = VectorStore(embedder, persist_directory=tmp_path)

        store.search("transformer", context="neural network")
        embedder.embed_query.assert_called_once_with("transformer neural network")

    def test_search_no_context(self, tmp_path) -> None:
        mock_collection = MagicMock()
        mock_collection.count.return_value = 1
        mock_collection.query.return_value = {
            "documents": [["text"]],
            "metadatas": [[{}]],
            "distances": [[0.1]],
            "ids": [["id-1"]],
        }
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection

        embedder = _mock_embedder()
        with patch("src.retrieval.vector_store.chromadb.PersistentClient", return_value=mock_client):
            store = VectorStore(embedder, persist_directory=tmp_path)

        store.search("transformer")
        embedder.embed_query.assert_called_once_with("transformer")

    def test_search_score_is_one_minus_distance(self, tmp_path) -> None:
        mock_collection = MagicMock()
        mock_collection.count.return_value = 1
        mock_collection.query.return_value = {
            "documents": [["text"]],
            "metadatas": [[{}]],
            "distances": [[0.3]],
            "ids": [["id-1"]],
        }
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection

        with patch("src.retrieval.vector_store.chromadb.PersistentClient", return_value=mock_client):
            store = VectorStore(_mock_embedder(), persist_directory=tmp_path)

        results = store.search("query")
        assert abs(results[0].score - 0.7) < 1e-6
