# Analyse PDF, IA local, déployable via docker

Développé par Growthsystemes Tech

Analyse et résumez instantanément n’importe quel PDF en local grâce à un modèle Llama 3 open‑source exécuté par Ollama. Aucune donnée ne quitte vos serveurs : déployez l’application on‑premise ou sur votre propre cloud en un simple `docker compose up`.

---

## Fonctionnalités

* **Drag‑and‑drop de PDF** : déposez un ou plusieurs fichiers, l’IA extrait le texte et génère un résumé ou des insights personnalisés.  
* **Analyse multilingue** : fonctionne sur des documents français et anglais.  
* **Modèle IA open‑source** : Llama 3 (ou tout autre modèle compatible Ollama) – aucun service SaaS propriétaire.  
* **Déploiement 100 % conteneurisé** : frontend React/TypeScript + backend FastAPI + moteur Ollama, orchestrés par docker‑compose.  
* **Scalabilité horizontale** : services sans état, prêts pour Kubernetes.  
* **Conformité RGPD** : aucune dépendance externe, vos PDF restent dans votre infrastructure.

---

## Architecture technique

```
Frontend (React/Vite) --HTTP--> Backend (FastAPI) --REST--> Ollama (Llama 3)
            |                                |
         NGINX                       réseau interne
```

* **Frontend** : React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui  
* **Backend** : Python 3.12, FastAPI, PyPDF2  
* **IA** : Ollama + modèle Llama 3 (par défaut `llama3.2:3b`)  
* **Conteneurs** : deux images custom (frontend, backend) + image officielle `ollama/ollama`

---

## Démarrage rapide

Prérequis : Docker 24+ et Docker Compose v2 installés sur la machine cible.

```bash
# 1. Récupérer le code
git clone https://github.com/votre-org/pdf-whisperer-ai-lab.git
cd pdf-whisperer-ai-lab

# 2. (Optionnel) personnaliser les variables d'environnement
cp .env.example .env    # voir la section Configuration

# 3. Builder et lancer
docker compose up --build -d
```

| Service      | Port hôte               | Description        |
|--------------|-------------------------|--------------------|
| Frontend     | http://localhost:8080   | Interface web      |
| Backend API  | http://localhost:8000   | Endpoints FastAPI  |
| Ollama API   | http://localhost:11434  | Moteur de génération |

Arrêter l’application :

```bash
docker compose down
```

---

## Configuration

Variables surchargées via `docker-compose.yml` :

| Variable            | Par défaut     | Impact                                           |
|---------------------|----------------|--------------------------------------------------|
| `OLLAMA_MODEL`      | `llama3.2:3b`  | Modèle utilisé pour l’analyse                    |
| `OLLAMA_MAX_CHARS`  | `15000`        | Longueur maximale de texte envoyé à l’IA         |
| `VITE_API_BASE_URL` | `http://backend:8000` | URL de l’API pour le frontend           |

Changer de modèle :

```bash
docker exec -it ollama ollama pull mistral:7b
docker compose restart backend
```

---

## Développement local sans Docker

### Backend API

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

Lancer un daemon Ollama localement (`ollama serve`) puis ajustez les URLs dans `.env`.

---

## Tests

```bash
# backend
pytest

# frontend (Vitest)
npm run test
```

---

## Déploiement en production

* **Docker Swarm ou Kubernetes** : adaptez le fichier `docker-compose.yml` ou fournissez un chart Helm.  
* **CI/CD** : exemple de pipeline GitHub Actions dans `.github/workflows/`.  
* **Observabilité** : endpoints de healthcheck exposés pour Prometheus ou Grafana.

---

## Licence

Code sous licence MIT.  
Les modèles IA appartiennent à leurs auteurs respectifs (consultez leurs licences).

---

## Contribuer

Les merge requests / pull requests sont bienvenues. Ouvrez une issue ou participez aux discussions GitHub.

---

## Remerciements

* Ollama pour l’intégration simple des modèles open‑source  
* Meta AI pour Llama 3  
* Les mainteneurs de FastAPI, React, Tailwind CSS et autres dépendances
