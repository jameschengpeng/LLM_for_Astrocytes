from pathlib import Path
from config import PROC_DIR
from index.vector_store import VectorStore

if __name__ == "__main__":
    vs = VectorStore()
    vs.build(PROC_DIR / "corpus.jsonl")
    print("Index built in data/index/")
