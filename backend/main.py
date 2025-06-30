from __future__ import annotations

import io
from typing import Dict, List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader

app = FastAPI(
    title="PDF Whisperer – Analyse de PDF",
    description="Micro-service FastAPI qui reçoit un fichier PDF et renvoie "
                "quelques métadonnées + le texte (extrait brut) pour des traitements ultérieurs.",
)

# Autorise tout domaine front (à restreindre en prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


def _extract_text(reader: PdfReader, max_chars: int = 20_000) -> str:
    """Concatène le texte des pages en se limitant à `max_chars` caractères."""
    chunks: List[str] = []
    total = 0
    for page in reader.pages:
        txt = page.extract_text() or ""
        total += len(txt)
        chunks.append(txt)
        if total >= max_chars:
            break
    return ("\n".join(chunks))[:max_chars]


@app.post("/analyze")
async def analyze(pdf: UploadFile = File(...)) -> Dict[str, str | int]:
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")

    try:
        # Charge le fichier en mémoire (pas d’écrasement sur disque)
        data = await pdf.read()
        reader = PdfReader(io.BytesIO(data))

        text = _extract_text(reader)
        num_pages = len(reader.pages)

        return {
            "filename": pdf.filename,
            "pages": num_pages,
            "chars_returned": len(text),
            "excerpt": text,
        }

    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"Erreur d’analyse : {exc}") from exc


@app.get("/")
def root() -> Dict[str, str]:
    """Endpoint de santé pour docker healthcheck."""
    return {"status": "ok"}
