# ----------- Stage 1: Build Frontend -----------
FROM node:20 AS frontend-builder

# Diretório de trabalho para o frontend
WORKDIR /app/frontend

# Ignora scripts pós-instalação (ex: postinstall)
ENV npm_config_ignore_scripts=true

# Copia os arquivos do frontend
COPY frontend/package.json ./
RUN npm install --legacy-peer-deps
COPY frontend/ ./

# Build do frontend
RUN npm run build

# ----------- Stage 2: Backend + Final Image -----------
FROM python:3.10-slim AS backend

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho para o backend
WORKDIR /app/services/virtual-tryon

# Copia o backend
COPY services/virtual-tryon/ ./

# Copia o build do frontend para a pasta estática do Flask
COPY --from=frontend-builder /app/frontend/dist/ ./static/react-app/

# Copia o pyproject.toml
COPY pyproject.toml ./

# Instala dependências do backend
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

# Expõe a porta padrão do Flask
EXPOSE 5000

# Comando para rodar o Flask
CMD ["python", "flasktry.py"] 