#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Test de Integración Suno Real
Prueba la integración completa con Suno AI
"""

import asyncio
import requests
import json
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SunoIntegrationTester:
    """Tester para la integración con Suno"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000"
        
    async def run_all_tests(self):
        """Ejecutar todas las pruebas de integración"""
        print("🎵 SON1KVERS3 - Test de Integración Suno Real")
        print("=" * 50)
        
        # 1. Verificar API
        await self.test_api_health()
        
        # 2. Verificar estado de Suno
        await self.test_suno_status()
        
        # 3. Probar generación con Suno real
        await self.test_suno_generation()
        
        # 4. Mostrar resumen
        self.show_test_summary()
    
    async def test_api_health(self):
        """Probar salud de la API"""
        print("\n🔍 Probando salud de la API...")
        
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API saludable: {data['status']}")
                return True
            else:
                print(f"❌ API no responde: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando a la API: {e}")
            return False
    
    async def test_suno_status(self):
        """Probar estado de Suno"""
        print("\n🎵 Probando estado de Suno...")
        
        try:
            response = requests.get(f"{self.api_url}/api/suno/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("connected"):
                    print("✅ Suno conectado y funcionando")
                    return True
                else:
                    print(f"⚠️ Suno no conectado: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Error verificando Suno: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error verificando Suno: {e}")
            return False
    
    async def test_suno_generation(self):
        """Probar generación con Suno"""
        print("\n🎵 Probando generación con Suno...")
        
        try:
            # Generar música de prueba
            payload = {
                "prompt": "resistencia digital cyberpunk",
                "lyrics": "En las sombras digitales donde el código resuena",
                "style": "cyberpunk",
                "user_plan": "nexus"
            }
            
            print("📤 Enviando request de generación...")
            response = requests.post(f"{self.api_url}/api/music/generate", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                job_id = data['job_id']
                print(f"✅ Generación iniciada: {job_id}")
                
                # Monitorear progreso
                await self.monitor_generation(job_id)
                return True
            else:
                print(f"❌ Error en generación: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en generación: {e}")
            return False
    
    async def monitor_generation(self, job_id: str):
        """Monitorear progreso de generación"""
        print(f"⏳ Monitoreando generación {job_id}...")
        
        for attempt in range(30):  # 30 intentos máximo (30 segundos)
            try:
                response = requests.get(f"{self.api_url}/api/music/status/{job_id}", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    print(f"   Progreso: {status['progress']}% - {status['message']}")
                    
                    if status['status'] == 'completed':
                        print("✅ Generación completada exitosamente!")
                        
                        # Verificar si es generación real o simulación
                        if status.get('result', {}).get('is_simulation'):
                            print("⚠️ Se usó simulación (Suno no disponible)")
                        else:
                            print("🎉 ¡Generación real con Suno exitosa!")
                        
                        return True
                    elif status['status'] == 'failed':
                        print(f"❌ Generación falló: {status.get('error', 'Unknown error')}")
                        return False
                        
                await asyncio.sleep(1)  # Esperar 1 segundo
                
            except Exception as e:
                print(f"   Error monitoreando: {e}")
                await asyncio.sleep(1)
        
        print("⏰ Timeout en monitoreo")
        return False
    
    def show_test_summary(self):
        """Mostrar resumen de pruebas"""
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE PRUEBAS SUNO")
        print("=" * 50)
        
        print("\n🎯 Instrucciones para configurar Suno:")
        print("1. Ejecuta: python setup_suno_credentials.py")
        print("2. Ingresa tu email y password de Suno")
        print("3. Las credenciales se guardarán automáticamente")
        print("4. Reinicia el sistema: python son1k_optimized_system.py")
        
        print("\n🔧 Configuración manual:")
        print("POST /api/suno/setup")
        print('{"session_id": "tu_session_id", "cookie": "tu_cookie", "token": "tu_token"}')
        
        print("\n📋 Verificar estado:")
        print("GET /api/suno/status")

async def main():
    """Función principal"""
    tester = SunoIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
