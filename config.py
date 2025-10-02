from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent

# Externalizable folders via env
PDF_DIR = Path(os.getenv("ASTRO_PDF_DIR", str(ROOT / "data" / "raw_pdfs"))).expanduser()
PROC_DIR = Path(os.getenv("ASTRO_PROC_DIR", str(ROOT / "data" / "processed"))).expanduser()
INDEX_DIR = Path(os.getenv("ASTRO_INDEX_DIR", str(ROOT / "data" / "index"))).expanduser()

PROC_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Chunking
CHUNK_TOKENS = int(os.getenv("CHUNK_TOKENS", 900))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 120))

# Models
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-base-en-v1.5")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
GEN_MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))

# Retrieval
TOPK_INITIAL = int(os.getenv("TOPK_INITIAL", 24))
TOPK_FINAL   = int(os.getenv("TOPK_FINAL", 10))

# ---------- OCR settings ----------
# Turn on OCR for scanned PDFs
OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() in ("1", "true", "yes", "on")
# "auto" tries ocrmypdf first (if available), then pytesseract; you can force one.
OCR_METHOD  = os.getenv("OCR_METHOD", "auto")  # "auto" | "ocrmypdf" | "pytesseract"
# Tesseract languages (install lang packs to use multiples, e.g., "eng+deu")
OCR_LANG    = os.getenv("OCR_LANG", "eng")
# If tesseract.exe is not on PATH (Windows), set absolute path here or via env
TESSERACT_EXE = os.getenv("TESSERACT_EXE", None)  # e.g., r"C:\Program Files\Tesseract-OCR\tesseract.exe"
