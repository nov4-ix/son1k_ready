# Imagen base oficial de Python
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
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

# Crear directorios necesarios
RUN mkdir -p /data /app/storage

# Exponer puerto para FastAPI
EXPOSE 8000

# Comando de arranque por defecto (puede ser sobrescrito por docker-compose)
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

