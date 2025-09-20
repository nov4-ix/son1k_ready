#!/usr/bin/env python3
"""
🎵 Son1k Frontend Server
Servidor simple para el frontend integrado con sistema Suno
"""
import os
import http.server
import socketserver
from pathlib import Path

def start_frontend_server():
    """Iniciar servidor frontend en puerto 3000"""
    
    # Cambiar al directorio frontend
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    PORT = 3000
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Agregar headers para CORS
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def log_message(self, format, *args):
            # Logs más limpios
            print(f"📁 {self.address_string()} - {format % args}")
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("🎵 SON1K FRONTEND SERVER")
        print("=" * 40)
        print(f"🌐 Frontend corriendo en: http://localhost:{PORT}")
        print(f"📁 Directorio: {frontend_dir}")
        print("🔄 Sistema Suno integrado")
        print("")
        print("🔗 URLs importantes:")
        print(f"   👨‍💻 Frontend: http://localhost:{PORT}")
        print(f"   🛠️  Backend:  http://localhost:8000")
        print(f"   📚 API Docs: http://localhost:8000/docs")
        print("")
        print("✅ Listo para probar integración end-to-end!")
        print("Presiona Ctrl+C para detener")
        print("=" * 40)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Cerrando servidor frontend...")
            httpd.shutdown()

if __name__ == "__main__":
    start_frontend_server()