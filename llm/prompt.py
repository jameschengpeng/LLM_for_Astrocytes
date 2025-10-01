def build_prompt(question: str, passages: list[dict]) -> str:
    ctx = "\n\n".join([f"({i+1}) {p['text']}" for i, p in enumerate(passages)])
    refs = "\n".join([
        f"[{i+1}] {p['meta'].get('title','?')} ({p['meta'].get('year','?')})  DOI:{p['meta'].get('doi','N/A')}"
        for i, p in enumerate(passages)
    ])
    return f"""You are a careful neuroscience assistant.

Answer the question **using only the Context** and **cite with [#]** after each claim.
If information is not available, say "insufficient evidence in corpus."

Question: {question}

Context:
{ctx}

Answer Requirements:
- Start with a bullet list of pathways → mechanisms → key molecules.
- Then add a short "Evidence" paragraph with citations.
- End with a "References" list.

References:
{refs}
"""
