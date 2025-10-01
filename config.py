from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent

# external folders (outside repo) via env; fallback to repo paths if unset
PDF_DIR = Path(os.getenv("ASTRO_PDF_DIR", str(ROOT / "data" / "raw_pdfs"))).expanduser()
PROC_DIR = Path(os.getenv("ASTRO_PROC_DIR", str(ROOT / "data" / "processed"))).expanduser()
INDEX_DIR = Path(os.getenv("ASTRO_INDEX_DIR", str(ROOT / "data" / "index"))).expanduser()

PROC_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# chunking
CHUNK_TOKENS = int(os.getenv("CHUNK_TOKENS", 900))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 120))

# models
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
GEN_MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))

# retrieval
TOPK_INITIAL = int(os.getenv("TOPK_INITIAL", 24))
TOPK_FINAL   = int(os.getenv("TOPK_FINAL", 10))