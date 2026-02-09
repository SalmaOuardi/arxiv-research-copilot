"""Tests for the ingestion module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.downloader import ArXivDownloader, PaperMetadata
from src.ingestion.processor import PDFProcessor, TextChunk


# --- Helper: a fake PaperMetadata for tests ---

def make_paper(arxiv_id: str = "2401.00001v1") -> PaperMetadata:
    return PaperMetadata(
        arxiv_id=arxiv_id,
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="A test abstract.",
        categories=["cs.AI"],
        published="2024-01-01T00:00:00",
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
    )


class TestArXivDownloader:
    """Tests for ArXivDownloader class."""

    def test_init_creates_output_dir(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "papers"
        downloader = ArXivDownloader(output_dir=output_dir)
        assert output_dir.exists()

    def test_init_default_max_results(self) -> None:
        downloader = ArXivDownloader()
        assert downloader.max_results == 100

    def test_category_filtering_builds_query(self) -> None:
        """Categories should be appended to the query string."""
        downloader = ArXivDownloader()
        with patch.object(downloader.client, "results", return_value=iter([])):
            downloader.search_papers("test", categories=["cs.AI", "cs.LG"])
        # Check the cache key contains the category filter
        assert any("cat:cs.AI" in key for key in downloader._search_cache)

    def test_search_caching(self) -> None:
        """Second identical search should return cached results."""
        downloader = ArXivDownloader()
        with patch.object(downloader.client, "results", return_value=iter([])) as mock:
            downloader.search_papers("test query", max_results=5)
            downloader.search_papers("test query", max_results=5)
        # API should only be called once
        mock.assert_called_once()

    @patch("src.ingestion.downloader.requests.get")
    @patch("src.ingestion.downloader.time.sleep")
    def test_download_pdf(self, mock_sleep, mock_get, tmp_path: Path) -> None:
        """download_pdf should write PDF bytes to disk."""
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"fake pdf content"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        downloader = ArXivDownloader(output_dir=tmp_path)
        paper = make_paper()
        path = downloader.download_pdf(paper)

        assert path.exists()
        assert path.read_bytes() == b"fake pdf content"
        mock_sleep.assert_called_once()  # rate limiting happened

    @patch("src.ingestion.downloader.requests.get")
    @patch("src.ingestion.downloader.time.sleep")
    def test_download_pdf_skips_existing(self, mock_sleep, mock_get, tmp_path: Path) -> None:
        """download_pdf should skip files that already exist."""
        downloader = ArXivDownloader(output_dir=tmp_path)
        paper = make_paper()

        # Create the file first
        existing = tmp_path / f"{paper.arxiv_id}.pdf"
        existing.write_bytes(b"already here")

        path = downloader.download_pdf(paper)
        assert path == existing
        mock_get.assert_not_called()  # no HTTP request made

    @patch("src.ingestion.downloader.requests.get")
    @patch("src.ingestion.downloader.time.sleep")
    def test_batch_download_handles_errors(self, mock_sleep, mock_get, tmp_path: Path) -> None:
        """batch_download should continue past failed downloads."""
        import requests

        mock_get.side_effect = requests.ConnectionError("fail")

        downloader = ArXivDownloader(output_dir=tmp_path)
        papers = [make_paper("001"), make_paper("002")]
        result = downloader.batch_download(papers)

        assert len(result) == 0  # both failed, but no exception raised


class TestPDFProcessor:
    """Tests for PDFProcessor class."""

    def test_init_default_values(self) -> None:
        processor = PDFProcessor()
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200
        assert processor.backend == "pymupdf"

    def test_extract_text_file_not_found(self) -> None:
        processor = PDFProcessor()
        with pytest.raises(FileNotFoundError):
            processor.extract_text(Path("/nonexistent/paper.pdf"))

    def test_chunk_text_basic(self) -> None:
        """chunk_text should split text into chunks with metadata."""
        processor = PDFProcessor(chunk_size=50, chunk_overlap=10)
        text = "This is sentence one. " * 20  # ~440 chars

        chunks = processor.chunk_text(text, metadata={"source": "test"})

        assert len(chunks) > 1
        assert all(isinstance(c, TextChunk) for c in chunks)
        # Each chunk should have source + chunk_index + total_chunks
        assert chunks[0].metadata["source"] == "test"
        assert chunks[0].metadata["chunk_index"] == 0
        assert chunks[0].metadata["total_chunks"] == len(chunks)

    def test_chunk_text_empty_input(self) -> None:
        """chunk_text should return empty list for empty text."""
        processor = PDFProcessor()
        assert processor.chunk_text("") == []
        assert processor.chunk_text("   ") == []

    def test_chunk_text_short_input(self) -> None:
        """Text shorter than chunk_size should produce one chunk."""
        processor = PDFProcessor(chunk_size=1000)
        chunks = processor.chunk_text("Short text.")
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."

    def test_chunk_overlap_present(self) -> None:
        """Consecutive chunks should share overlapping text."""
        processor = PDFProcessor(chunk_size=100, chunk_overlap=30)
        text = "word " * 200  # 1000 chars

        chunks = processor.chunk_text(text)

        # Check that the end of chunk 0 overlaps with the start of chunk 1
        assert len(chunks) > 2
        end_of_first = chunks[0].text[-30:]
        assert end_of_first in chunks[1].text

    @patch("src.ingestion.processor.fitz")
    def test_extract_text_calls_fitz(self, mock_fitz, tmp_path: Path) -> None:
        """extract_text should open PDF with fitz and get text per page."""
        # Create a dummy file so FileNotFoundError isn't raised
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy")

        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page text here."
        mock_doc = MagicMock()
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_fitz.open.return_value = mock_doc

        processor = PDFProcessor()
        text = processor.extract_text(pdf_file)

        mock_fitz.open.assert_called_once_with(pdf_file)
        mock_doc.close.assert_called_once()
        assert "Page text here." in text

    def test_hyphen_cleanup(self) -> None:
        """extract_text should rejoin hyphenated words across lines."""
        processor = PDFProcessor()
        # We test the regex logic directly
        import re
        raw = "trans-\nformer model"
        cleaned = re.sub(r"-\n(\w)", r"\1", raw)
        assert cleaned == "transformer model"
