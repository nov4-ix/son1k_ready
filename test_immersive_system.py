#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Script de Prueba del Sistema Inmersivo
Prueba el flujo completo: API + Frontend + Interfaz Inmersiva
"""

import asyncio
import requests
import time
import json
from pathlib import Path

class ImmersiveSystemTester:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8000"
        self.test_results = []
        
    async def run_all_tests(self):
        """Ejecutar todas las pruebas del sistema inmersivo"""
        print("🎵 SON1KVERS3 - Iniciando pruebas del sistema inmersivo...")
        print("=" * 60)
        
        # 1. Verificar API
        await self.test_api_health()
        
        # 2. Verificar generación musical
        await self.test_music_generation()
        
        # 3. Verificar endpoints de descarga
        await self.test_download_endpoints()
        
        # 4. Verificar archivos frontend
        await self.test_frontend_files()
        
        # 5. Mostrar resumen
        self.show_test_summary()
        
    async def test_api_health(self):
        """Probar salud de la API"""
        print("\n🔍 Probando salud de la API...")
        
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API saludable: {data}")
                self.test_results.append(("API Health", "PASS", data))
            else:
                print(f"❌ API no responde correctamente: {response.status_code}")
                self.test_results.append(("API Health", "FAIL", f"Status: {response.status_code}"))
        except Exception as e:
            print(f"❌ Error conectando a la API: {e}")
            self.test_results.append(("API Health", "FAIL", str(e)))
    
    async def test_music_generation(self):
        """Probar generación musical"""
        print("\n🎵 Probando generación musical...")
        
        try:
            # Generar música de prueba
            payload = {
                "prompt": "resistencia digital cyberpunk",
                "lyrics": "En las sombras digitales donde el código resuena",
                "style": "cyberpunk",
                "user_plan": "nexus"
            }
            
            response = requests.post(f"{self.api_url}/api/music/generate", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Generación iniciada: {data['job_id']}")
                
                # Monitorear progreso
                job_id = data['job_id']
                await self.monitor_generation(job_id)
                
                self.test_results.append(("Music Generation", "PASS", f"Job: {job_id}"))
            else:
                print(f"❌ Error en generación: {response.status_code}")
                self.test_results.append(("Music Generation", "FAIL", f"Status: {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Error en generación musical: {e}")
            self.test_results.append(("Music Generation", "FAIL", str(e)))
    
    async def monitor_generation(self, job_id):
        """Monitorear progreso de generación"""
        print(f"⏳ Monitoreando generación {job_id}...")
        
        for attempt in range(10):  # 10 intentos máximo
            try:
                response = requests.get(f"{self.api_url}/api/music/status/{job_id}", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    print(f"   Progreso: {status['progress']}% - {status['message']}")
                    
                    if status['status'] == 'completed':
                        print("✅ Generación completada!")
                        return True
                    elif status['status'] == 'failed':
                        print(f"❌ Generación falló: {status.get('error', 'Unknown error')}")
                        return False
                        
                await asyncio.sleep(2)  # Esperar 2 segundos
                
            except Exception as e:
                print(f"   Error monitoreando: {e}")
                await asyncio.sleep(2)
        
        print("⏰ Timeout en monitoreo")
        return False
    
    async def test_download_endpoints(self):
        """Probar endpoints de descarga"""
        print("\n📥 Probando endpoints de descarga...")
        
        try:
            # Obtener lista de tracks
            response = requests.get(f"{self.api_url}/api/music/tracks", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tracks disponibles: {data['total']}")
                
                if data['tracks']:
                    track = data['tracks'][0]
                    print(f"   Primera track: {track['title']}")
                    
                    # Probar descarga
                    download_url = f"{self.api_url}/api/audio/download/{track['filename']}"
                    download_response = requests.head(download_url, timeout=5)
                    
                    if download_response.status_code == 200:
                        print("✅ Endpoint de descarga funcional")
                        self.test_results.append(("Download Endpoints", "PASS", f"{data['total']} tracks"))
                    else:
                        print(f"❌ Error en descarga: {download_response.status_code}")
                        self.test_results.append(("Download Endpoints", "FAIL", f"Status: {download_response.status_code}"))
                else:
                    print("ℹ️  No hay tracks para probar descarga")
                    self.test_results.append(("Download Endpoints", "SKIP", "No tracks available"))
            else:
                print(f"❌ Error obteniendo tracks: {response.status_code}")
                self.test_results.append(("Download Endpoints", "FAIL", f"Status: {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Error probando descarga: {e}")
            self.test_results.append(("Download Endpoints", "FAIL", str(e)))
    
    async def test_frontend_files(self):
        """Probar archivos del frontend"""
        print("\n🎨 Probando archivos del frontend...")
        
        frontend_files = [
            "frontend/index.html",
            "frontend/immersive_interface.html",
            "frontend/immersive_integration.js"
        ]
        
        all_exist = True
        for file_path in frontend_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} existe")
            else:
                print(f"❌ {file_path} no encontrado")
                all_exist = False
        
        if all_exist:
            print("✅ Todos los archivos del frontend están presentes")
            self.test_results.append(("Frontend Files", "PASS", "All files present"))
        else:
            print("❌ Faltan archivos del frontend")
            self.test_results.append(("Frontend Files", "FAIL", "Missing files"))
    
    def show_test_summary(self):
        """Mostrar resumen de pruebas"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, status, details in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
            print(f"{status_icon} {test_name}: {status}")
            if details:
                print(f"   {details}")
            
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
            else:
                skipped += 1
        
        print(f"\n📈 Resultados: {passed} pasaron, {failed} fallaron, {skipped} omitidos")
        
        if failed == 0:
            print("\n🎉 ¡Todas las pruebas pasaron! El sistema inmersivo está listo.")
            print("\n🚀 Instrucciones de uso:")
            print("   1. Ejecuta: python son1k_optimized_system.py")
            print("   2. Abre: http://localhost:8000")
            print("   3. Presiona: Ctrl+Alt+H para activar interfaz inmersiva")
            print("   4. Explora los easter eggs y comandos NEXUS")
        else:
            print(f"\n⚠️  {failed} pruebas fallaron. Revisa los errores antes de continuar.")

async def main():
    """Función principal"""
    tester = ImmersiveSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
