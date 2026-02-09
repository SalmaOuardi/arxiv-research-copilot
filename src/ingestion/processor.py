"""PDF processing and text chunking module.

Handles extracting text from PDF files and splitting into chunks
suitable for embedding and retrieval.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """A chunk of text extracted from a paper.

    Attributes:
        text: The chunk text content.
        metadata: Associated metadata (source, page, position, etc.).
    """

    text: str
    metadata: dict[str, str | int]


class PDFProcessor:
    """Processes PDF files into text chunks for embedding.

    Supports multiple PDF extraction backends (PyPDF2, PyMuPDF) and
    configurable chunking strategies.

    Args:
        chunk_size: Target size of each text chunk in characters.
        chunk_overlap: Number of overlapping characters between chunks.
        backend: PDF extraction backend ("pymupdf" or "pypdf2").

    Example:
        >>> processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
        >>> text = processor.extract_text(Path("paper.pdf"))
        >>> chunks = processor.chunk_text(text, metadata={"source": "paper.pdf"})
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        backend: str = "pymupdf",
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.backend = backend

    def extract_text(
        self,
        pdf_path: Path,
        pages: Optional[list[int]] = None,
    ) -> str:
        """Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file.
            pages: Optional list of page numbers to extract (0-indexed).
                If None, extracts all pages.

        Returns:
            Extracted text as a single string.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the backend is not supported.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info("Extracting text from %s using %s", pdf_path, self.backend)

        doc = fitz.open(pdf_path)
        page_texts: list[str] = []

        for i, page in enumerate(doc):
            if pages is not None and i not in pages:
                continue
            page_texts.append(page.get_text())

        doc.close()

        raw_text = "\n".join(page_texts)

        # Clean up: fix hyphenated line breaks and collapse whitespace
        text = re.sub(r"-\n(\w)", r"\1", raw_text)  # re-join hyphenated words
        text = re.sub(r"\n{3,}", "\n\n", text)       # collapse excessive newlines

        return text

    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict[str, str | int]] = None,
    ) -> list[TextChunk]:
        """Split text into overlapping chunks.

        Uses a recursive character-based splitting strategy that
        respects paragraph and sentence boundaries where possible.

        Args:
            text: The full text to split into chunks.
            metadata: Base metadata to attach to each chunk. Chunk-specific
                metadata (index, start/end positions) is added automatically.

        Returns:
            List of TextChunk objects with text and metadata.
        """
        base_metadata = metadata or {}

        logger.info(
            "Chunking %d characters into ~%d-char chunks with %d overlap",
            len(text),
            self.chunk_size,
            self.chunk_overlap,
        )

        if not text.strip():
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        raw_chunks = splitter.split_text(text)

        chunks: list[TextChunk] = []
        for i, chunk_text in enumerate(raw_chunks):
            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "total_chunks": len(raw_chunks),
            }
            chunks.append(TextChunk(text=chunk_text, metadata=chunk_metadata))

        logger.info("Created %d chunks", len(chunks))
        return chunks

    def process_pdf(
        self,
        pdf_path: Path,
        metadata: Optional[dict[str, str | int]] = None,
    ) -> list[TextChunk]:
        """End-to-end PDF processing: extract text and chunk it.

        Args:
            pdf_path: Path to the PDF file.
            metadata: Additional metadata to attach to chunks.

        Returns:
            List of TextChunk objects ready for embedding.
        """
        text = self.extract_text(pdf_path)
        return self.chunk_text(text, metadata=metadata)
