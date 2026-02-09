"""Full ingestion pipeline: search -> download -> extract -> chunk."""

import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.downloader import ArXivDownloader
from src.ingestion.processor import PDFProcessor


def main():
    query = "transformer attention mechanism"
    max_results = 50

    # Step 1: Search and download
    print(f"Searching ArXiv for: '{query}'")
    downloader = ArXivDownloader(output_dir="./data/raw")
    papers = downloader.search_papers(query, max_results=max_results)
    print(f"Found {len(papers)} papers")

    paths = downloader.batch_download(papers)
    print(f"Downloaded {len(paths)} PDFs")

    # Step 2: Process PDFs into chunks
    output_dir = Path("./data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)

    for pdf_path in paths:
        print(f"Processing: {pdf_path.name}")
        chunks = processor.process_pdf(pdf_path, metadata={"source": pdf_path.name})

        output_file = output_dir / f"{pdf_path.stem}.json"
        chunk_dicts = [{"text": c.text, "metadata": c.metadata} for c in chunks]
        output_file.write_text(json.dumps(chunk_dicts, indent=2))

        print(f"  -> {len(chunks)} chunks")

    print(f"\nDone! Full pipeline complete.")


if __name__ == "__main__":
    main()
