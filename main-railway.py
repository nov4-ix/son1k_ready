"""
Railway-compatible main.py
Minimal version without Selenium dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create minimal app
app = FastAPI(
    title="Son1k Suno MVP - Railway",
    description="Railway-compatible version without Selenium"
)

# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Son1k Suno MVP - Railway Version",
        "status": "online",
        "version": "railway-minimal"
    }

@app.get("/api/health")
def health():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "service": "son1k-railway",
        "timestamp": os.environ.get("RAILWAY_DEPLOYMENT_ID", "unknown")
    }

@app.get("/health")
def health_alt():
    """Alternative health check"""
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)