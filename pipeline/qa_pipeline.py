from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from llm.prompt import build_prompt
from llm.llm_client import generate

class QAPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.reranker = Reranker()

    def answer(self, question: str):
        cands = self.retriever.retrieve(question)
        top = self.reranker.rerank(question, cands)
        prompt = build_prompt(question, top)
        return generate(prompt), top
