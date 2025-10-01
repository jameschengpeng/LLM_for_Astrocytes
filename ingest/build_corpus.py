import argparse
from pathlib import Path
from ingest.parse_pdfs import run as parse
from ingest.chunk_text import run as chunk
from config import PDF_DIR

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf_dir", type=Path, default=PDF_DIR)
    args = ap.parse_args()
    parse(args.pdf_dir)   # parse from external folder
    chunk()               # build corpus.jsonl in PROC_DIR
