# ingest/chunk_text.py
import json
from pathlib import Path
import tiktoken
from config import PROC_DIR, CHUNK_TOKENS, CHUNK_OVERLAP

enc = tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, tokens=CHUNK_TOKENS, overlap=CHUNK_OVERLAP):
    ids = enc.encode(text)
    chunks = []
    i = 0
    while i < len(ids):
        window = ids[i:i+tokens]
        chunks.append(enc.decode(window))
        i += max(1, tokens - overlap)
    return chunks

def run():
    inp = PROC_DIR / "parsed.jsonl"
    out = PROC_DIR / "corpus.jsonl"
    # ⬇️ specify UTF-8 for both read and write
    with inp.open("r", encoding="utf-8") as fin, out.open("w", encoding="utf-8") as fout:
        for line in fin:
            rec = json.loads(line)
            meta = rec["meta"]
            for idx, ch in enumerate(chunk_text(rec["text"])):
                item = {
                    "id": f"{meta['title']}::chunk{idx}",
                    "text": ch,
                    "meta": {**meta, "chunk_idx": idx}
                }
                fout.write(json.dumps(item, ensure_ascii=False) + "\n")
    print("Wrote", out)

if __name__ == "__main__":
    run()
