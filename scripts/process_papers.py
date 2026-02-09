"""Process already-downloaded PDFs: extract text and chunk."""

import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.processor import PDFProcessor


def main():
    raw_dir = Path("./data/raw")
    output_dir = Path("./data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)

    pdf_files = list(raw_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs to process")

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        chunks = processor.process_pdf(pdf_path, metadata={"source": pdf_path.name})

        # Save chunks as JSON for later use
        output_file = output_dir / f"{pdf_path.stem}.json"
        chunk_dicts = [{"text": c.text, "metadata": c.metadata} for c in chunks]
        output_file.write_text(json.dumps(chunk_dicts, indent=2))

        print(f"  -> {len(chunks)} chunks saved to {output_file.name}")

    print(f"\nDone! Processed {len(pdf_files)} papers into {output_dir}")


if __name__ == "__main__":
    main()
