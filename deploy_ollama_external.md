# Deployment Options for Ollama + Son1k

## Option 1: Railway + External Ollama Service

### Step 1: Deploy Ollama on DigitalOcean/AWS/Linode
```bash
# Create droplet with 4GB+ RAM
# SSH into server
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.1:8b

# Make it accessible
sudo ufw allow 11434
sudo systemctl enable ollama
```

### Step 2: Update Son1k Environment Variables
```env
OLLAMA_URL=http://your-ollama-server:11434
OLLAMA_EXTERNAL=true
```

### Step 3: Deploy Updated Code
Replace main.py with main_full.py and deploy to Railway

## Option 2: Single Railway Container with Ollama

### Requirements:
- Railway Pro plan (more resources)
- Docker deployment
- At least 4GB RAM allocated

### Files needed:
- Dockerfile.ollama
- .dockerignore
- Updated railway.toml

## Option 3: Local Development + Production External

### Development:
```bash
# Local machine
ollama serve
export OLLAMA_URL=http://localhost:11434
python main_full.py
```

### Production:
- External Ollama server
- Railway for main API
- Environment variables for connection

## Recommended: Option 1 (External Service)
- More stable
- Better resource allocation  
- Easier scaling
- Railway focuses on API only