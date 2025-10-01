import numpy as np
from sentence_transformers import SentenceTransformer
from index.vector_store import VectorStore
from config import EMBED_MODEL, TOPK_INITIAL

class Retriever:
    def __init__(self):
        self.embed = SentenceTransformer(EMBED_MODEL)
        self.vs = VectorStore()
        self.vs.load()

    def retrieve(self, query: str, k: int = TOPK_INITIAL):
        qv = self.embed.encode([query], normalize_embeddings=True, convert_to_numpy=True)
        return self.vs.search(qv, k)
