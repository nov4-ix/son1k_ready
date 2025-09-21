"""
Railway FastAPI app
"""
from fastapi import FastAPI
import os

app = FastAPI(title="Son1k Railway")

@app.get("/")
def root():
    port = os.environ.get("PORT", "unknown")
    return {
        "message": "Son1k Railway App", 
        "status": "online",
        "port": port,
        "env": "railway"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "son1k-railway"}

@app.get("/api/health")
def api_health():
    return {"status": "healthy", "service": "son1k-api"}