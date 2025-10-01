import sys, json
from pipeline.qa_pipeline import QAPipeline

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]).strip()
    if not q:
        print("Usage: python cli/ask.py \"your question\""); sys.exit(1)
    pipe = QAPipeline()
    ans, passages = pipe.answer(q)
    print("\n=== ANSWER ===\n")
    print(ans)
    print("\n=== SOURCES ===\n")
    for i, p in enumerate(passages, 1):
        print(f"[{i}] {p['meta'].get('title','?')}  {p['meta'].get('source_path','')}")
