########################
# 1. Étape de build
########################
FROM node:20-alpine AS builder
WORKDIR /app

# Dépendances – on garde aussi les devDeps pour que vite soit présent
COPY package*.json ./
RUN npm ci                # <-- suppression de --omit=dev

# Copie du code source
COPY . .

# Variable d’API injectée au build
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8000}

# Build React
RUN npm run build
# (Optionnel) nettoyage des deps dev : RUN npm prune --omit=dev

########################
# 2. Image finale Nginx
########################
FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
HEALTHCHECK CMD wget -qO- http://localhost || exit 1
CMD ["nginx", "-g", "daemon off;"]
