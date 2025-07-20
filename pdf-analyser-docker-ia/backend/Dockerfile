# backend/Dockerfile
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ───── réglages Python ─────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ───── utilitaires système ─────
# wget est requis par le HEALTHCHECK
RUN apt-get update \
 && apt-get install -y --no-install-recommends wget ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ───── dépendances Python ─────
COPY requirements.txt .
# mise en cache du dossier pip pour accélérer les builds répétés
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# ───── code de l’application ─────
COPY . .

# ───── variables par défaut (écrasables par compose/K8s) ─────
ENV OLLAMA_HOST=http://ollama:11434 \
    OLLAMA_MODEL=llama3:8b \
    OLLAMA_MAX_CHARS=15000

# ───── réseau & supervision ─────
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=5 --start-period=60s \
  CMD wget -qO- http://localhost:8000/ || exit 1

# ───── lancement ─────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
