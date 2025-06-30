from __future__ import annotations

import io
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader

# ────────────────── Configuration ──────────────────
load_dotenv()  # charge le .env

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
MAX_CHARS    = int(os.getenv("OLLAMA_MAX_CHARS", "15000"))

app = FastAPI(
    title="PDF Whisperer – Analyse de PDF via Llama",
    description="Micro-service : extrait le texte d’un PDF puis interroge un modèle Llama "
                "géré par Ollama pour renvoyer une réponse.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────── Fonctions utilitaires ──────────────────
def _extract_text(reader: PdfReader, max_chars: int = MAX_CHARS) -> str:
    """Concatène le texte des pages – limité à `max_chars` caractères."""
    chunks: List[str] = []
    total = 0
    for page in reader.pages:
        txt = page.extract_text() or ""
        total += len(txt)
        chunks.append(txt)
        if total >= max_chars:
            break
    return ("\n".join(chunks))[:max_chars]


def _query_ollama(prompt: str) -> str:
    """Envoie `prompt` à Ollama, renvoie la réponse brute (mode non-stream)."""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["response"]
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc


# ────────────────── Routes ──────────────────
@app.post("/analyze")
async def analyze(pdf: UploadFile = File(...)) -> Dict[str, str | int]:
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")

    try:
        data = await pdf.read()
        reader = PdfReader(io.BytesIO(data))

        raw_text = _extract_text(reader)
        num_pages = len(reader.pages)

        # Prompt minimal : résumé
        prompt = (
            "Tu es un assistant spécialisé dans la lecture de documents PDF. "
            "Voici le contenu extrait :\n\n"
            f"{raw_text}\n\n"
            "Fournis un résumé détaillé (max 300 mots) en français :"
        )
        llama_response = _query_ollama(prompt)

        return {
            "filename": pdf.filename,
            "pages": num_pages,
            "chars_sent": len(raw_text),
            "summary": llama_response.strip(),
        }

    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"Erreur d’analyse : {exc}") from exc


@app.get("/")
def root() -> Dict[str, str]:
    """Endpoint de santé pour docker healthcheck."""
    return {"status": "ok"}
