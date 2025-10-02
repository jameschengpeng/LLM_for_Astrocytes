import json
from pathlib import Path
import tiktoken
from config import PROC_DIR, CHUNK_TOKENS, CHUNK_OVERLAP

enc = tiktoken.get_encoding("cl100k_base")

# Track which PDF titles+chunk_idx we've already written
CHUNK_IDS_PATH = PROC_DIR / "corpus_ids.txt"   # plain text: one id per line

def load_seen_ids():
    if CHUNK_IDS_PATH.exists():
        return set(CHUNK_IDS_PATH.read_text(encoding="utf-8").splitlines())
    return set()

def append_seen_ids(ids):
    with CHUNK_IDS_PATH.open("a", encoding="utf-8") as f:
        for _id in ids:
            f.write(_id + "\n")

def chunk_text(text: str, tokens=CHUNK_TOKENS, overlap=CHUNK_OVERLAP):
    ids = enc.encode(text)
    chunks = []
    i = 0
    step = max(1, tokens - overlap)
    while i < len(ids):
        window = ids[i:i+tokens]
        chunks.append(enc.decode(window))
        i += step
    return chunks

def run():
    parsed = PROC_DIR / "parsed.jsonl"
    corpus = PROC_DIR / "corpus.jsonl"
    seen = load_seen_ids()
    new_ids = []

    # open corpus in append mode
    with parsed.open("r", encoding="utf-8") as fin, corpus.open("a", encoding="utf-8") as fout:
        for line in fin:
            rec = json.loads(line)
            meta = rec["meta"]
            title = meta.get("title","untitled")
            # create chunks and write only if not already present
            chunks = chunk_text(rec.get("text",""))
            for idx, ch in enumerate(chunks):
                cid = f"{title}::chunk{idx}"
                if cid in seen:
                    continue
                item = {"id": cid, "text": ch, "meta": {**meta, "chunk_idx": idx}}
                fout.write(json.dumps(item, ensure_ascii=False) + "\n")
                new_ids.append(cid)

    if new_ids:
        append_seen_ids(new_ids)
    print(f"Appended {len(new_ids)} new chunks to {corpus}")

if __name__ == "__main__":
    run()
