# index/vector_store.py
import faiss, numpy as np, json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL, INDEX_DIR, PROC_DIR

STATE_PATH = INDEX_DIR / "index_state.json"  # tracks how many corpus lines embedded

class VectorStore:
    def __init__(self, model_name=EMBED_MODEL):
        # We keep an embedder here so retriever can pass query vectors OR we can encode ad-hoc.
        self.embed = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
        self.metas = []

    # ---------- Incremental build/update ----------

    def _load_corpus_lines(self):
        corpus = (PROC_DIR / "corpus.jsonl")
        with corpus.open("r", encoding="utf-8") as f:
            return corpus, f.readlines()

    def _load_state(self):
        if STATE_PATH.exists():
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return {"count": 0}

    def _save_state(self, count: int):
        STATE_PATH.write_text(json.dumps({"count": count}, indent=2), encoding="utf-8")

    def _load_or_init_index(self, dim: int):
        idx_path = INDEX_DIR / "faiss.index"
        if idx_path.exists():
            self.index = faiss.read_index(str(idx_path))
        else:
            self.index = faiss.IndexFlatIP(dim)

    def _append_artifacts(self, texts, metas):
        with (INDEX_DIR / "texts.jsonl").open("a", encoding="utf-8") as ft:
            for t in texts:
                ft.write(t + "\n")
        with (INDEX_DIR / "metas.jsonl").open("a", encoding="utf-8") as fm:
            for m in metas:
                fm.write(json.dumps(m, ensure_ascii=False) + "\n")

    def build_or_update(self):
        _, lines = self._load_corpus_lines()
        state = self._load_state()
        done = state.get("count", 0)
        total = len(lines)

        if done >= total:
            print(f"No new chunks. Embedded {done}/{total}.")
            return

        new_texts, new_metas = [], []
        for line in lines[done:]:
            rec = json.loads(line)
            new_texts.append(rec["text"])
            new_metas.append(rec["meta"])

        X = self.embed.encode(new_texts, normalize_embeddings=True, convert_to_numpy=True)
        dim = X.shape[1]

        self._load_or_init_index(dim)
        self.index.add(X)
        faiss.write_index(self.index, str(INDEX_DIR / "faiss.index"))

        self._append_artifacts(new_texts, new_metas)

        emb_path = INDEX_DIR / "embeddings.npy"
        if emb_path.exists():
            old = np.load(emb_path)
            np.save(emb_path, np.vstack([old, X]))
        else:
            np.save(emb_path, X)

        self._save_state(total)
        print(f"Indexed {len(new_texts)} new chunks. Total = {total}.")

    # ---------- Load for inference ----------

    def load(self):
        """Load FAISS + artifacts into memory for retrieval."""
        idx_path = INDEX_DIR / "faiss.index"
        texts_path = INDEX_DIR / "texts.jsonl"
        metas_path = INDEX_DIR / "metas.jsonl"

        if not (idx_path.exists() and texts_path.exists() and metas_path.exists()):
            raise FileNotFoundError(
                "Index or artifacts not found. Run `python -m index.build_index` first."
            )

        self.index = faiss.read_index(str(idx_path))
        self.texts = texts_path.read_text(encoding="utf-8").splitlines()
        self.metas = [json.loads(l) for l in metas_path.read_text(encoding="utf-8").splitlines()]

    # ---------- Search ----------

    def search(self, query_vec: np.ndarray, topk: int):
        """
        Expect a shape (1, dim) normalized query vector. Returns list of {text, meta, score}.
        """
        if self.index is None or not self.texts:
            self.load()

        D, I = self.index.search(query_vec, topk)
        results = []
        for j, i in enumerate(I[0]):
            # Guard against rare index/texts mismatch
            if i < 0 or i >= len(self.texts):
                continue
            results.append({
                "text": self.texts[i],
                "meta": self.metas[i],
                "score": float(D[0][j])
            })
        return results
