"""ArXiv paper downloader module.

Handles searching and downloading papers from the ArXiv API.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests
import arxiv
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Metadata for an ArXiv paper.

    Attributes:
        arxiv_id: The unique ArXiv identifier.
        title: Paper title.
        authors: List of author names.
        abstract: Paper abstract.
        categories: ArXiv categories the paper belongs to.
        published: Publication date as ISO string.
        pdf_url: URL to the PDF version.
    """

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: str
    pdf_url: str


class ArXivDownloader:
    """Downloads and manages ArXiv papers.

    Args:
        output_dir: Directory to store downloaded PDFs.
        max_results: Maximum number of results per search query.

    Example:
        >>> downloader = ArXivDownloader(output_dir="./data/raw")
        >>> papers = downloader.search_papers("transformer attention mechanism")
        >>> downloader.download_pdf(papers[0])
    """

    def __init__(
        self,
        output_dir: str | Path = "./data/raw",
        max_results: int = 100,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_results = max_results
        self.client = arxiv.Client()

    def search_papers(
        self,
        query: str,
        max_results: Optional[int] = None,
        categories: Optional[list[str]] = None,
    ) -> list[PaperMetadata]:
        """Search ArXiv for papers matching the query.

        Args:
            query: Search query string (supports ArXiv query syntax).
            max_results: Override default max results for this search.
            categories: Filter by ArXiv categories (e.g., ["cs.AI", "cs.LG"]).

        Returns:
            List of PaperMetadata objects for matching papers.

        Raises:
            arxiv.ArxivError: If the ArXiv API request fails.
        """
        # TODO: Implement category filtering by appending to query string
        # TODO: Add rate limiting to respect ArXiv API guidelines
        # TODO: Add caching to avoid redundant API calls
        # TODO: Implement pagination for large result sets

        effective_max = max_results or self.max_results

        search = arxiv.Search(
            query=query,
            max_results=effective_max,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers: list[PaperMetadata] = []
        for result in self.client.results(search):
            paper = PaperMetadata(
                arxiv_id=result.entry_id.split("/")[-1],
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                categories=result.categories,
                published=result.published.isoformat(),
                pdf_url=result.pdf_url,
            )
            papers.append(paper)

        logger.info("Found %d papers for query: %s", len(papers), query)
        return papers

    def download_pdf(
        self,
        paper: PaperMetadata,
        filename: Optional[str] = None,
    ) -> Path:
        """Download the PDF for a given paper.

        Args:
            paper: PaperMetadata object with the paper's info.
            filename: Optional custom filename. Defaults to {arxiv_id}.pdf.

        Returns:
            Path to the downloaded PDF file.

        Raises:
            requests.HTTPError: If the download request fails.
            IOError: If the file cannot be written to disk.
        """
        fname = filename or f"{paper.arxiv_id}.pdf"
        output_path = self.output_dir / fname

        if output_path.exists():
            logger.info("Already exists, skipping: %s", output_path)
            return output_path

        logger.info("Downloading paper %s to %s", paper.arxiv_id, output_path)

        response = requests.get(paper.pdf_url, stream=True, timeout=30)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info("Downloaded %s to %s", paper.arxiv_id, output_path)
        return output_path

    def batch_download(
        self,
        papers: list[PaperMetadata],
        skip_existing: bool = True,
    ) -> list[Path]:
        """Download PDFs for multiple papers.

        Args:
            papers: List of PaperMetadata objects to download.
            skip_existing: If True, skip papers already downloaded.

        Returns:
            List of paths to downloaded PDF files.
        """
        downloaded: list[Path] = []

        for paper in tqdm(papers, desc="Downloading papers"):
            pdf_path = self.output_dir / f"{paper.arxiv_id}.pdf"
            if skip_existing and pdf_path.exists():
                logger.info("Skipping existing: %s", paper.arxiv_id)
                downloaded.append(pdf_path)
                continue

            try:
                path = self.download_pdf(paper)
                downloaded.append(path)
            except requests.RequestException as e:
                logger.warning("Failed to download %s: %s", paper.arxiv_id, e)

        logger.info("Downloaded %d/%d papers", len(downloaded), len(papers))
        return downloaded
