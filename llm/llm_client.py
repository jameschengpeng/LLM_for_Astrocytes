import os, requests
from config import GEN_MAX_TOKENS

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")

def generate(prompt: str) -> str:
    # Ollama non-streaming
    r = requests.post(f"{OLLAMA_URL}/api/generate",
                      json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                            "options": {"num_ctx": 8192, "num_predict": GEN_MAX_TOKENS}})
    r.raise_for_status()
    return r.json()["response"]
