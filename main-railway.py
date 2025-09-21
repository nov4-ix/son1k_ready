"""
Debug Railway app with logging
"""
from fastapi import FastAPI
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 Starting Railway app...")
logger.info("🚀 Starting Railway app...")

app = FastAPI(title="Son1k Railway Debug")

@app.get("/")
def root():
    logger.info("🏠 Root endpoint called")
    return {"status": "ok", "message": "Railway app running", "port": os.environ.get("PORT", "unknown")}

@app.get("/health")
def health():
    logger.info("🩺 Health check called")
    return {"status": "healthy", "service": "railway-debug"}

@app.get("/api/health") 
def api_health():
    logger.info("🩺 API Health check called")
    return {"status": "healthy", "service": "railway-debug-api"}

@app.on_event("startup")
async def startup_event():
    logger.info("🎉 App startup complete")
    print("🎉 App startup complete")

if __name__ == "__main__":
    print("🔧 Starting uvicorn server...")
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")