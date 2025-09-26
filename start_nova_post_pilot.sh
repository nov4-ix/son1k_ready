#!/bin/bash

echo "🚀 Starting Nova Post Pilot Backend..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    echo "   ollama pull llama3.1:8b"
    exit 1
fi

# Check if the model is available
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "📥 Pulling llama3.1:8b model..."
    ollama pull llama3.1:8b
fi

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing dependencies..."
pip install fastapi uvicorn aiohttp pydantic

# Start the Nova Post Pilot backend
echo "🎯 Starting Nova Post Pilot API on port 8001..."
python nova_post_pilot_backend.py
