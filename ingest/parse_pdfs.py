import fitz
from pathlib import Path
import json, re, subprocess, shutil, tempfile, argparse, time
from config import PDF_DIR, PROC_DIR, OCR_ENABLED, OCR_LANG, OCR_METHOD, TESSERACT_EXE
from ingest.filehash import sha256_of_file

try:
    import pytesseract
    if TESSERACT_EXE:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
except Exception:
    pytesseract = None

REG_PATH = PROC_DIR / "registry.json"   # tracks PDFs we've parsed by hash

def load_registry():
    if REG_PATH.exists():
        return json.loads(REG_PATH.read_text(encoding="utf-8"))
    return {}  # {source_path: {"sha256":..., "mtime":..., "parsed": True}}

def save_registry(reg):
    REG_PATH.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")

def clean_text(s: str) -> str:
    s = re.sub(r"\s+\n", "\n", s)
    s = re.sub(r"\n{2,}", "\n\n", s)
    return s.strip()

def page_text_density(txt: str) -> float:
    alnum = sum(ch.isalnum() for ch in txt)
    return alnum / max(1, len(txt))

def pdf_has_enough_text(pdf_path: Path, min_chars_total=500, min_pages_with_text=2) -> bool:
    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return False
    pages_with_text = 0
    total_chars = 0
    sample_pages = min(6, len(doc))
    for i in range(sample_pages):
        txt = doc[i].get_text("text") or ""
        total_chars += len(txt)
        if page_text_density(txt) > 0.02 and len(txt) > 80:
            pages_with_text += 1
    return (total_chars >= min_chars_total) or (pages_with_text >= min_pages_with_text)

def ocrmypdf_available() -> bool:
    return shutil.which("ocrmypdf") is not None

def run_ocrmypdf(src: Path, dst: Path) -> bool:
    cmd = ["ocrmypdf","--skip-text","--language", OCR_LANG,"--output-type","pdfa","--optimize","0", str(src), str(dst)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return res.returncode == 0 and dst.exists()
    except Exception:
        return False

def ocr_page_with_pytesseract(page, dpi=200) -> str:
    mat = fitz.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    from io import BytesIO
    from PIL import Image
    img = Image.open(BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang=OCR_LANG, config="--psm 6")

def parse_pdf_plain(pdf_path: Path):
    doc = fitz.open(pdf_path)
    text_pages = [(page.get_text("text") or "") for page in doc]
    return clean_text("\n".join(text_pages))

def parse_pdf_with_pytesseract(pdf_path: Path):
    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        try:
            parts.append(ocr_page_with_pytesseract(page))
        except Exception:
            parts.append("")
    return clean_text("\n".join(parts))

def default_meta(pdf_path: Path):
    return {
        "title": pdf_path.stem,
        "source_path": str(pdf_path.resolve()),
        "doi": None, "pmid": None, "year": None, "journal": None
    }

def parse_pdf_with_optional_ocr(pdf_path: Path):
    # fast path
    if (not OCR_ENABLED) or pdf_has_enough_text(pdf_path):
        text = parse_pdf_plain(pdf_path)
        meta = default_meta(pdf_path)
        return {"meta": meta, "text": text}

    # try OCRmyPDF
    if (OCR_METHOD in ("auto", "ocrmypdf")) and ocrmypdf_available():
        with tempfile.TemporaryDirectory() as td:
            out_pdf = Path(td) / "ocr.pdf"
            if run_ocrmypdf(pdf_path, out_pdf):
                text = parse_pdf_plain(out_pdf)
                meta = default_meta(pdf_path)
                meta["ocr"] = "ocrmypdf"
                return {"meta": meta, "text": text}

    # fallback pytesseract
    if (OCR_METHOD in ("auto", "pytesseract")) and (pytesseract is not None):
        text = parse_pdf_with_pytesseract(pdf_path)
        meta = default_meta(pdf_path)
        meta["ocr"] = "pytesseract"
        return {"meta": meta, "text": text}

    # give up
    return {"meta": default_meta(pdf_path), "text": ""}

def run(pdf_dir: Path):
    reg = load_registry()
    out_path = PROC_DIR / "parsed.jsonl"
    # open for append; create if not exists
    fout = out_path.open("a", encoding="utf-8")
    n_new = 0
    for p in sorted(Path(pdf_dir).rglob("*.pdf")):
        spath = str(p.resolve())
        try:
            cur_hash = sha256_of_file(p)
            cur_mtime = int(p.stat().st_mtime)
        except Exception:
            continue

        entry = reg.get(spath)
        if entry and entry.get("sha256") == cur_hash and entry.get("mtime") == cur_mtime:
            # unchanged → skip
            continue

        rec = parse_pdf_with_optional_ocr(p)
        fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
        reg[spath] = {"sha256": cur_hash, "mtime": cur_mtime, "parsed": True, "ts": int(time.time())}
        n_new += 1

    fout.close()
    save_registry(reg)
    print(f"Parsed {n_new} new/updated PDFs. Appended to {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf_dir", type=Path, default=PDF_DIR, help="Folder containing PDFs (recurses)")
    args = ap.parse_args()
    run(args.pdf_dir)
