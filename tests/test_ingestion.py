"""Tests for the ingestion module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.downloader import ArXivDownloader, PaperMetadata
from src.ingestion.processor import PDFProcessor, TextChunk


class TestArXivDownloader:
    """Tests for ArXivDownloader class."""

    def test_init_creates_output_dir(self, tmp_path: Path) -> None:
        """Test that the downloader creates the output directory."""
        output_dir = tmp_path / "papers"
        downloader = ArXivDownloader(output_dir=output_dir)
        assert output_dir.exists()

    def test_init_default_max_results(self) -> None:
        """Test default max_results value."""
        downloader = ArXivDownloader()
        assert downloader.max_results == 100

    # TODO: Add test for search_papers with mocked ArXiv API
    # TODO: Add test for download_pdf with mocked HTTP response
    # TODO: Add test for batch_download
    # TODO: Add test for handling API errors
    # TODO: Add test for category filtering


class TestPDFProcessor:
    """Tests for PDFProcessor class."""

    def test_init_default_values(self) -> None:
        """Test default initialization values."""
        processor = PDFProcessor()
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200
        assert processor.backend == "pymupdf"

    def test_extract_text_file_not_found(self) -> None:
        """Test that FileNotFoundError is raised for missing files."""
        processor = PDFProcessor()
        with pytest.raises(FileNotFoundError):
            processor.extract_text(Path("/nonexistent/paper.pdf"))

    # TODO: Add test for extract_text with a sample PDF
    # TODO: Add test for chunk_text with known text
    # TODO: Add test for chunk overlap correctness
    # TODO: Add test for process_pdf end-to-end
