"""Download papers from ArXiv."""

import sys
import os

# Add the project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.downloader import ArXivDownloader


def main():
    downloader = ArXivDownloader(output_dir="./data/raw")
    papers = downloader.search_papers("transformer attention mechanism", max_results=50)
    print(f"Found {len(papers)} papers")
    paths = downloader.batch_download(papers)
    print(f"Downloaded {len(paths)} PDFs")


if __name__ == "__main__":
    main()
