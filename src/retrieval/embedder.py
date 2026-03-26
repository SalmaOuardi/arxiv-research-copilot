"""Embedding module for converting text to vector representations using Ollama."""

from __future__ import annotations

import logging
import time
from openai import OpenAI

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434/v1"


class Embedder:
    """Generates embeddings via Ollama's OpenAI-compatible API.

    Args:
        model: Ollama embedding model name.
        batch_size: Number of texts per API call.
        request_delay: Seconds to wait between batches.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        batch_size: int = 32,
        request_delay: float = 0.1,
    ) -> None:
        self.model = model
        self.batch_size = batch_size
        self.request_delay = request_delay
        self._client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents. Returns one vector per text."""
        if not texts:
            raise ValueError("Cannot embed empty text list")

        logger.info("Embedding %d documents with %s", len(texts), self.model)
        embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            response = self._client.embeddings.create(model=self.model, input=batch)
            embeddings.extend([item.embedding for item in response.data])
            if i + self.batch_size < len(texts):
                time.sleep(self.request_delay)

        return embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        if not text.strip():
            raise ValueError("Cannot embed empty query")

        response = self._client.embeddings.create(model=self.model, input=[text])
        return response.data[0].embedding
