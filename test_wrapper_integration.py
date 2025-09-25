#!/usr/bin/env python3
"""
🎵 Test Script para Integración Suno Wrapper
Prueba la integración completa entre frontend, wrapper y API
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class WrapperIntegrationTester:
    def __init__(self):
        self.wrapper_url = "http://localhost:3001"
        self.api_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8000"  # Frontend servido por FastAPI
        
    async def test_wrapper_health(self):
        """Probar salud del wrapper"""
        print("🔍 Probando salud del wrapper...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.wrapper_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Wrapper saludable: {data.get('status')}")
                        print(f"   Versión: {data.get('version')}")
                        print(f"   Cookies activas: {data.get('cookies', {}).get('active', 0)}")
                        return True
                    else:
                        print(f"❌ Wrapper no saludable: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error conectando con wrapper: {e}")
            return False
    
    async def test_api_health(self):
        """Probar salud de la API principal"""
        print("🔍 Probando salud de la API principal...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/api/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ API saludable: {data.get('api')}")
                        return True
                    else:
                        print(f"❌ API no saludable: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error conectando con API: {e}")
            return False
    
    async def test_wrapper_generation(self):
        """Probar generación con wrapper"""
        print("🎵 Probando generación con wrapper...")
        try:
            test_prompt = "una canción épica de synthwave sobre la resistencia digital"
            test_lyrics = "En las redes del tiempo, donde los datos susurran,\nNOV4-IX despierta con ritmos que perduran."
            
            payload = {
                "prompt": test_prompt,
                "lyrics": test_lyrics,
                "style": "profesional"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.wrapper_url}/generate-music",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            print(f"✅ Generación exitosa con wrapper")
                            print(f"   Audio URLs: {len(data.get('audioUrls', []))}")
                            print(f"   Letras: {len(data.get('lyrics', ''))} caracteres")
                            return True
                        else:
                            print(f"❌ Generación falló: {data.get('error')}")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"❌ Error HTTP {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error en generación con wrapper: {e}")
            return False
    
    async def test_api_generation(self):
        """Probar generación con API principal"""
        print("🎵 Probando generación con API principal...")
        try:
            test_prompt = "música cyberpunk épica"
            
            payload = {
                "prompt": test_prompt,
                "lyrics": "",
                "style": "synthwave"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Generación exitosa con API principal")
                        print(f"   Job ID: {data.get('job_id', 'N/A')}")
                        print(f"   Status: {data.get('status', 'N/A')}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Error HTTP {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error en generación con API: {e}")
            return False
    
    async def test_frontend_integration(self):
        """Probar integración del frontend"""
        print("🌐 Probando integración del frontend...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.frontend_url}/") as response:
                    if response.status == 200:
                        content = await response.text()
                        if "suno_wrapper_integration.js" in content:
                            print("✅ Script de integración Suno encontrado en frontend")
                            return True
                        else:
                            print("⚠️ Script de integración Suno no encontrado en frontend")
                            return False
                    else:
                        print(f"❌ Frontend no accesible: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error accediendo al frontend: {e}")
            return False
    
    async def test_wrapper_stats(self):
        """Probar estadísticas del wrapper"""
        print("📊 Probando estadísticas del wrapper...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.wrapper_url}/stats") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Estadísticas obtenidas")
                        print(f"   Cookies totales: {len(data.get('cookies', []))}")
                        print(f"   Uptime: {data.get('uptime', 0):.2f} segundos")
                        return True
                    else:
                        print(f"❌ Error obteniendo estadísticas: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error en estadísticas: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas de integración Suno Wrapper")
        print("=" * 60)
        
        tests = [
            ("Wrapper Health", self.test_wrapper_health),
            ("API Health", self.test_api_health),
            ("Frontend Integration", self.test_frontend_integration),
            ("Wrapper Stats", self.test_wrapper_stats),
            ("Wrapper Generation", self.test_wrapper_generation),
            ("API Generation", self.test_api_generation)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🧪 Ejecutando: {test_name}")
            try:
                result = await test_func()
                results[test_name] = result
                print(f"{'✅' if result else '❌'} {test_name}: {'PASÓ' if result else 'FALLÓ'}")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results[test_name] = False
            
            # Pequeña pausa entre pruebas
            await asyncio.sleep(1)
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
        
        if passed == total:
            print("🎉 ¡Todas las pruebas pasaron! La integración está funcionando correctamente.")
        elif passed >= total * 0.8:
            print("⚠️ La mayoría de las pruebas pasaron. Revisar las que fallaron.")
        else:
            print("❌ Muchas pruebas fallaron. Revisar la configuración del sistema.")
        
        return results

async def main():
    """Función principal"""
    tester = WrapperIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    print("🎵 Son1k Suno Wrapper Integration Tester")
    print("Asegúrate de que estén ejecutándose:")
    print("  - Wrapper Node.js: npm start (puerto 3001)")
    print("  - API Python: python3 main_production_final.py (puerto 8000)")
    print()
    
    asyncio.run(main())



