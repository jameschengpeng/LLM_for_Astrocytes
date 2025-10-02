# LLM for Astrocytes – Literature Q&A System

This project lets you **ask natural language questions** against your personal corpus of neuroscience papers (e.g., calcium signaling in astrocytes).  
It combines:

- **Document ingestion**: PDFs → clean text (with optional OCR for scanned papers)  
- **Chunking**: text split into manageable segments  
- **Vector index**: semantic embeddings stored in FAISS for fast retrieval  
- **Retrieval + Reranking**: top chunks selected and re-ranked by relevance  
- **LLM generation**: context and your query fed into a local language model (via Ollama)  
- **Cited answers**: outputs concise answers with inline citations and reference list  

---

## Features

- 📚 Supports **PDF libraries** (Zotero export, lab folder, etc.)  
- 🔍 **Incremental indexing**: only new/updated PDFs are processed on reruns  
- 🧾 **OCR fallback**: scanned PDFs are recognized using `ocrmypdf` or `pytesseract`  
- 🖥️ **Runs locally** on your GPU (RTX 4070, V100, etc.) — no API costs  
- 🔗 **Cited answers** with references back to the source PDFs  
- ⚡ **Fast updates**: just re-run two commands after adding new PDFs  

---

## Installation

```cmd
:: clone the repo
git clone https://github.com/<your-org>/LLM_for_Astrocytes.git
cd LLM_for_Astrocytes

:: create venv and install deps
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

:: install Ollama and pull a model (one-time)
ollama pull llama3.1:8b-instruct-q4_K_M
```

(Windows users: also install **Tesseract OCR** and **Ghostscript** for OCR support)

---

## Usage Workflow

1. **Export PDFs**  
   Export your library from Zotero (or collect PDFs in a folder).  
   Example: `D:\Literature_corpus`

2. **Set environment variables (cmd.exe)**

   ```cmd
   set ASTRO_PDF_DIR=D:\Literature_corpus
   set ASTRO_PROC_DIR=D:\Literature_corpus\processed
   set ASTRO_INDEX_DIR=D:\Literature_corpus\index
   set OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
   set OLLAMA_URL=http://localhost:11434
   ```

3. **Build or update corpus & index**

   ```cmd
   python -m ingest.build_corpus --pdf_dir %ASTRO_PDF_DIR%
   python -m index.build_index
   ```

   - First run: processes all PDFs, builds index  
   - Later runs: only processes **new or changed PDFs**

4. **Ask questions (CLI)**

   ```cmd
   python -m cli.ask "Summarize pathways that modulate astrocyte Ca2+ signaling"
   ```

   Example output:

   ```
   === ANSWER ===
   • IP3R2-mediated Ca2+ release … [1]
   • Store-operated Ca2+ entry … [2]

   === SOURCES ===
   [1] Paukert_2014.pdf  D:\Literature_corpus\Paukert_2014.pdf
   [2] Bazargani_2016.pdf  D:\Literature_corpus\Bazargani_2016.pdf
   ```

5. **Run API server (optional)**

   ```cmd
   uvicorn api.server:app --reload --port 8000
   ```

   Query with:

   ```cmd
   curl -Method POST -Uri http://127.0.0.1:8000/ask -Body "{\"question\":\"What triggers SOCE in astrocytes?\"}" -ContentType "application/json"
   ```

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `ASTRO_PDF_DIR`  | Where PDFs live | `D:\Literature_corpus` |
| `ASTRO_PROC_DIR` | Processed JSON + chunks | `D:\Literature_corpus\processed` |
| `ASTRO_INDEX_DIR`| FAISS index + embeddings | `D:\Literature_corpus\index` |
| `OLLAMA_MODEL`   | Which model Ollama should run | `llama3.1:8b-instruct-q4_K_M` |
| `OLLAMA_URL`     | Ollama server URL | `http://localhost:11434` |
| `OCR_ENABLED`    | Enable OCR (true/false) | `true` |
| `OCR_METHOD`     | `auto`, `ocrmypdf`, or `pytesseract` | `auto` |
| `OCR_LANG`       | Tesseract language codes | `eng` |
| `TESSERACT_EXE`  | Path to tesseract.exe (if not in PATH) | `C:\Program Files\Tesseract-OCR\tesseract.exe` |

---

## OCR Support

- If a PDF already has text, it’s used directly  
- If not:  
  - Tries `ocrmypdf` (best quality, requires Ghostscript + Tesseract)  
  - Falls back to `pytesseract` page-by-page OCR  
- Marked in metadata (`ocr: "ocrmypdf"` or `"pytesseract"`)  
- Use `OCR_LANG` for non-English texts (`eng+chi_sim`, `eng+deu`, etc.)

---

## Incremental Updates

The pipeline maintains:

- `registry.json` (tracks PDFs by SHA256 + mtime)  
- `corpus_ids.txt` (chunk IDs already processed)  
- `index_state.json` (how many chunks embedded)  

So:
- Re-run `build_corpus` + `build_index` anytime  
- Only **new/changed PDFs** are parsed and added  
- Old chunks/index remain untouched  
- If you delete PDFs and want them removed → do a clean rebuild (delete `processed/` + `index/` once)

---

## FAQ

**Q: Is the model free?**  
A: Yes — running with Ollama and open-weight models is free, local, and private. No API costs.

**Q: Can I use GPT-4 instead?**  
A: Yes — swap `llm_client.py` to call OpenAI API (requires API key + billing).

**Q: How fast is OCR?**  
A: OCRmyPDF is slower, but only runs on scanned files. Most modern PDFs skip OCR.

**Q: What if I update an existing PDF (replace with a new version)?**  
A: The SHA256/mtime check will detect changes and re-parse it.

---

## Roadmap

- [ ] Add progress bar + logging for long ingests  
- [ ] Add hybrid retrieval (BM25 + embeddings)  
- [ ] Add evaluation tools (RAGAS)  
- [ ] Prebuilt Docker image for easy deployment  

---

## License

MIT