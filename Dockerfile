# Imagen base oficial de Python
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (mejor cache de capas)
COPY backend/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Crear directorios necesarios
RUN mkdir -p /data /app/storage /app/storage/uploads /app/storage/audio

# Exponer puerto para FastAPI (Railway usa variable PORT)
EXPOSE $PORT

# Comando de arranque usando Railway's PORT variable
CMD cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT

