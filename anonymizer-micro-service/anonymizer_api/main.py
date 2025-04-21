# ────────────────────────────────────────────────────────────────
# File: anonymizer_api/main.py
# Description: API FastAPI qui expose le service d’anonymisation
# ────────────────────────────────────────────────────────────────

import os
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, conlist

from .anonymizer import anonymize_all, anonymize_all_many

app = FastAPI(title="Anonymizer API", version="1.0.0")

MAX_PAYLOAD = int(os.getenv("MAX_PAYLOAD_SIZE", "51200"))  # 50 kB par défaut


# ---------- Modèles Pydantic ----------


class SingleIn(BaseModel):
    text: str = Field(..., max_length=MAX_PAYLOAD)


class BatchIn(BaseModel):
    # Pydantic v2 : min_length remplace min_items
    texts: conlist(str, min_length=1)  # type: ignore


class SingleOut(BaseModel):
    anonymized_text: str


class BatchOut(BaseModel):
    anonymized_text: List[str]


# ---------- Endpoints ----------


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.post("/anonymize", response_model=SingleOut, tags=["anonymize"])
def anonymize(payload: SingleIn):
    if len(payload.text.encode()) > MAX_PAYLOAD:
        raise HTTPException(status_code=413, detail="Payload too large")
    return {"anonymized_text": anonymize_all(payload.text)}


@app.post("/anonymize_batch", response_model=BatchOut, tags=["anonymize"])
def anonymize_batch(payload: BatchIn):
    total = sum(len(t.encode()) for t in payload.texts)
    if total > MAX_PAYLOAD:
        raise HTTPException(status_code=413, detail="Batch payload too large")
    return {"anonymized_text": anonymize_all_many(payload.texts)}


# ---------- Exécution locale ----------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
