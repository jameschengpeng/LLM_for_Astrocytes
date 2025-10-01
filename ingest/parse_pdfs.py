import fitz
from pathlib import Path
import json, re, argparse
from config import PDF_DIR, PROC_DIR

def clean_text(s: str) -> str:
    s = re.sub(r"\s+\n", "\n", s)
    s = re.sub(r"\n{2,}", "\n\n", s)
    return s.strip()

def parse_pdf(pdf_path: Path):
    doc = fitz.open(pdf_path)
    text = []
    for page in doc:
        text.append(page.get_text("text"))
    full = clean_text("\n".join(text))
    meta = {
        "title": pdf_path.stem,
        "source_path": str(pdf_path.resolve()),
        "doi": None, "pmid": None, "year": None, "journal": None
    }
    return {"meta": meta, "text": full}

def run(pdf_dir: Path):
    out_path = PROC_DIR / "parsed.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for p in sorted(Path(pdf_dir).glob("*.pdf")):
            rec = parse_pdf(p)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("Wrote", out_path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf_dir", type=Path, default=PDF_DIR,
                    help="Folder containing PDFs (can be outside the repo)")
    args = ap.parse_args()
    run(args.pdf_dir)
