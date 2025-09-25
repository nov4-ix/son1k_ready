#!/usr/bin/env python3
"""
Son1kVers3 - Servidor Principal para Railway
Sistema híbrido que combina FastAPI backend con Node.js wrapper
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

# Configuración
PORT = int(os.environ.get("PORT", 8000))
NODE_SERVER_PORT = 3001
PYTHON_SERVER_PORT = 8000

class Son1kServer:
    def __init__(self):
        self.node_process = None
        self.python_process = None
        self.running = True
        
    def start_node_server(self):
        """Iniciar servidor Node.js (suno_wrapper_server.js)"""
        try:
            print("🚀 Iniciando servidor Node.js...")
            self.node_process = subprocess.Popen([
                "node", "suno_wrapper_server.js"
            ], env={**os.environ, "PORT": str(NODE_SERVER_PORT)})
            print(f"✅ Servidor Node.js iniciado en puerto {NODE_SERVER_PORT}")
        except Exception as e:
            print(f"❌ Error iniciando servidor Node.js: {e}")
    
    def start_python_server(self):
        """Iniciar servidor Python (FastAPI)"""
        try:
            print("🐍 Iniciando servidor Python...")
            # Cambiar al directorio backend
            backend_dir = Path("backend")
            if backend_dir.exists():
                os.chdir(backend_dir)
            
            # Activar entorno virtual si existe
            venv_python = Path("../.venv/bin/python")
            if venv_python.exists():
                python_cmd = str(venv_python)
            else:
                python_cmd = "python3"
            
            self.python_process = subprocess.Popen([
                python_cmd, "-m", "uvicorn", "app.main:app",
                "--host", "0.0.0.0", "--port", str(PYTHON_SERVER_PORT)
            ])
            print(f"✅ Servidor Python iniciado en puerto {PYTHON_SERVER_PORT}")
        except Exception as e:
            print(f"❌ Error iniciando servidor Python: {e}")
    
    def start_hybrid_server(self):
        """Iniciar servidor híbrido simple con FastAPI"""
        try:
            from fastapi import FastAPI
            from fastapi.middleware.cors import CORSMiddleware
            from fastapi.responses import JSONResponse
            import uvicorn
            
            app = FastAPI(title="Son1kVers3 Hybrid Server")
            
            # CORS
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
                    "message": "Son1kVers3 Hybrid Server",
                    "status": "running",
                    "version": "3.0.0",
                    "endpoints": {
                        "health": "/health",
                        "generate": "/generate-music",
                        "stats": "/stats"
                    }
                }
            
            @app.get("/health")
            def health():
                return {
                    "status": "healthy",
                    "service": "Son1kVers3",
                    "timestamp": time.time()
                }
            
            @app.post("/generate-music")
            def generate_music(request: dict):
                # Proxy al servidor Node.js si está disponible
                try:
                    import requests
                    response = requests.post(
                        f"http://localhost:{NODE_SERVER_PORT}/generate-music",
                        json=request,
                        timeout=30
                    )
                    return response.json()
                except:
                    return {
                        "success": False,
                        "error": "Servicio de generación no disponible",
                        "fallback": True
                    }
            
            @app.get("/stats")
            def stats():
                return {
                    "status": "running",
                    "uptime": time.time(),
                    "hybrid_mode": True
                }
            
            print(f"🚀 Iniciando servidor híbrido en puerto {PORT}")
            uvicorn.run(app, host="0.0.0.0", port=PORT)
            
        except Exception as e:
            print(f"❌ Error iniciando servidor híbrido: {e}")
            # Fallback a servidor simple
            self.start_simple_server()
    
    def start_simple_server(self):
        """Servidor simple de fallback"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import json
            
            class SimpleHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == "/health":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "status": "healthy",
                            "service": "Son1kVers3 Simple"
                        }).encode())
                    else:
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "message": "Son1kVers3 Simple Server",
                            "status": "running"
                        }).encode())
                
                def do_POST(self):
                    if self.path == "/generate-music":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "success": False,
                            "error": "Servicio en modo simple",
                            "message": "Use el servidor completo para generación"
                        }).encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
            
            print(f"🚀 Iniciando servidor simple en puerto {PORT}")
            server = HTTPServer(("0.0.0.0", PORT), SimpleHandler)
            server.serve_forever()
            
        except Exception as e:
            print(f"❌ Error iniciando servidor simple: {e}")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Manejar señales de terminación"""
        print(f"\n🛑 Recibida señal {signum}, cerrando servidores...")
        self.running = False
        
        if self.node_process:
            self.node_process.terminate()
        if self.python_process:
            self.python_process.terminate()
        
        sys.exit(0)
    
    def run(self):
        """Ejecutar servidor principal"""
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🎵 Son1kVers3 - Servidor Principal")
        print("=" * 40)
        print(f"Puerto principal: {PORT}")
        print(f"Puerto Node.js: {NODE_SERVER_PORT}")
        print(f"Puerto Python: {PYTHON_SERVER_PORT}")
        print("=" * 40)
        
        # Verificar si estamos en Railway
        if os.environ.get("RAILWAY_ENVIRONMENT"):
            print("🚂 Detectado entorno Railway")
            # En Railway, usar servidor híbrido
            self.start_hybrid_server()
        else:
            print("💻 Entorno local detectado")
            # En local, intentar servidor híbrido
            self.start_hybrid_server()

if __name__ == "__main__":
    server = Son1kServer()
    server.run()

