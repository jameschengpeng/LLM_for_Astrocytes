from sentence_transformers import CrossEncoder
from config import RERANK_MODEL, TOPK_FINAL

class Reranker:
    def __init__(self):
        self.model = CrossEncoder(RERANK_MODEL)

    def rerank(self, query: str, cands, k: int = TOPK_FINAL):
        pairs = [[query, c["text"]] for c in cands]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(cands, scores), key=lambda x: x[1], reverse=True)
        return [c for (c, _) in ranked[:k]]
