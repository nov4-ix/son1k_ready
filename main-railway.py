"""
Minimal Railway app - fixed
"""
from fastapi import FastAPI
import os

print("🚀 Starting app...")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Railway", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# This block should NOT run in Railway (uvicorn is started by Railway)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)