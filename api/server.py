from fastapi import FastAPI
from pydantic import BaseModel
from pipeline.qa_pipeline import QAPipeline

app = FastAPI(title="AstroCa2 RAG")
pipe = QAPipeline()

class AskReq(BaseModel):
    question: str

@app.post("/ask")
def ask(req: AskReq):
    answer, passages = pipe.answer(req.question)
    return {"answer": answer, "passages": passages}
