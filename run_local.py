#!/usr/bin/env python3
"""
Local development runner for Son1kVers3 - bypasses Docker issues
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Set up environment
project_root = Path(__file__).parent
os.chdir(project_root)

# Environment variables for local development
os.environ.update({
    'PYTHONPATH': str(project_root),
    'REDIS_URL': 'redis://localhost:6379/0',
    'POSTGRES_DSN': 'sqlite:///./son1k.db',  # Use SQLite for local dev
    'CORS_ORIGINS': '*'
})

def run_api():
    """Run the FastAPI application"""
    print("🚀 Starting Son1kVers3 API on http://localhost:8000")
    
    # Activate virtual environment and run
    venv_python = project_root / "son1k_env" / "bin" / "python"
    
    if not venv_python.exists():
        print("❌ Virtual environment not found. Please run:")
        print("   python3 -m venv son1k_env")
        print("   source son1k_env/bin/activate")
        print("   pip install -r backend/requirements.txt")
        return False
    
    cmd = [
        str(venv_python), 
        "-m", "uvicorn", 
        "backend.app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error running server: {e}")
        return False
    
    return True

def run_worker():
    """Run the Celery worker in background"""
    print("🔄 Starting Celery worker...")
    
    venv_python = project_root / "son1k_env" / "bin" / "python"
    
    cmd = [
        str(venv_python), 
        "-m", "celery", 
        "-A", "backend.app.queue.celery_app", 
        "worker", 
        "--loglevel=INFO"
    ]
    
    try:
        return subprocess.Popen(cmd)
    except Exception as e:
        print(f"❌ Error starting worker: {e}")
        return None

def main():
    print("🎵 Son1kVers3 Local Development Server")
    print("=" * 50)
    
    # Check Redis
    try:
        subprocess.run(["redis-cli", "ping"], check=True, capture_output=True)
        print("✅ Redis is running")
    except:
        print("❌ Redis not running. Starting with brew...")
        subprocess.run(["brew", "services", "start", "redis"])
        time.sleep(2)
    
    # Start worker in background
    worker_process = run_worker()
    if worker_process:
        print("✅ Celery worker started")
    
    try:
        # Start API server (blocking)
        print("\n🌐 Frontend will be available at: http://localhost:8000")
        print("📚 API docs at: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop\n")
        
        run_api()
        
    finally:
        # Clean up worker
        if worker_process:
            print("🧹 Stopping Celery worker...")
            worker_process.terminate()
            worker_process.wait()

if __name__ == "__main__":
    main()