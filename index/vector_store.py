import faiss, numpy as np, json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL, INDEX_DIR, PROC_DIR

class VectorStore:
    def __init__(self, model_name=EMBED_MODEL):
        self.embed = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
        self.metas = []

    def build(self, corpus_jsonl: Path):
        for line in corpus_jsonl.open():
            rec = json.loads(line)
            self.texts.append(rec["text"])
            self.metas.append(rec["meta"])
        X = self.embed.encode(self.texts, normalize_embeddings=True, convert_to_numpy=True)
        dim = X.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(X)
        np.save(INDEX_DIR / "embeddings.npy", X)
        (INDEX_DIR / "texts.jsonl").write_text("\n".join(self.texts), encoding="utf-8")
        with (INDEX_DIR / "metas.jsonl").open("w", encoding="utf-8") as f:
            for m in self.metas:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        faiss.write_index(self.index, str(INDEX_DIR / "faiss.index"))

    def load(self):
        X = np.load(INDEX_DIR / "embeddings.npy")
        self.index = faiss.IndexFlatIP(X.shape[1])
        self.index.add(X)
        self.texts = (INDEX_DIR / "texts.jsonl").read_text(encoding="utf-8").splitlines()
        self.metas = [json.loads(l) for l in (INDEX_DIR / "metas.jsonl").read_text(encoding="utf-8").splitlines()]

    def search(self, query_vec: np.ndarray, topk: int):
        D, I = self.index.search(query_vec, topk)
        results = []
        for j, i in enumerate(I[0]):
            results.append({
                "text": self.texts[i],
                "meta": self.metas[i],
                "score": float(D[0][j])
            })
        return results
