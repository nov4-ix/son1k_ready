# Setup para usar Ollama externo en Railway

## Opción 1: Tu Mac como servidor Ollama

### 1. Exponer Ollama al exterior
```bash
# En tu Mac, cambiar configuración de Ollama
export OLLAMA_HOST=0.0.0.0:11434
ollama serve

# O usar ngrok para tunnel público
brew install ngrok
ngrok http 11434
```

### 2. Configurar variables en Railway
```
OLLAMA_URL=https://tu-ngrok-url.ngrok.io
# O tu IP pública: http://tu-ip-publica:11434
```

## Opción 2: Servidor en la nube (Recomendado)

### DigitalOcean Droplet (4GB RAM)
```bash
# SSH al droplet
ssh root@tu-ip

# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Configurar servicio
systemctl enable ollama
systemctl start ollama

# Abrir puerto
ufw allow 11434

# Instalar modelo
ollama pull llama3.1:8b

# Configurar para escuchar en todas las interfaces
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

### Variables Railway:
```
OLLAMA_URL=http://tu-ip-droplet:11434
```

## Opción 3: Usar Ollama local para desarrollo

### Variables Railway para desarrollo:
```
OLLAMA_URL=http://tu-ip-local:11434
# Ejemplo: http://192.168.1.100:11434
```

## Verificar conexión:
```bash
curl http://tu-ollama-url/api/tags
```