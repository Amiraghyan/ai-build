FROM python:3.12-slim
WORKDIR /app

# chemins sans préfixe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
HEALTHCHECK CMD wget -qO- http://localhost:8000 || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
