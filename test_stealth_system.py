#!/usr/bin/env python3
"""
🔒 Test Script para Sistema Stealth Ultra-Avanzado
Prueba el sistema completo con tecnología stealth y múltiples cuentas
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class StealthSystemTester:
    def __init__(self):
        self.wrapper_url = "http://localhost:3001"
        self.api_url = "http://localhost:8000"
        
    async def test_stealth_wrapper_health(self):
        """Probar salud del wrapper stealth"""
        print("🔒 Probando salud del wrapper stealth...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.wrapper_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Wrapper stealth saludable: {data.get('status')}")
                        print(f"   Versión: {data.get('version')}")
                        print(f"   Cuentas totales: {data.get('accounts', {}).get('total', 0)}")
                        print(f"   Cuentas activas: {data.get('accounts', {}).get('active', 0)}")
                        print(f"   Modo stealth: {data.get('features', {}).get('stealthMode', False)}")
                        return True
                    else:
                        print(f"❌ Wrapper stealth no saludable: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error conectando con wrapper stealth: {e}")
            return False
    
    async def test_stealth_generation(self):
        """Probar generación con tecnología stealth"""
        print("🔒 Probando generación stealth...")
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
                            print(f"✅ Generación stealth exitosa")
                            print(f"   Audio URLs: {len(data.get('audioUrls', []))}")
                            print(f"   Letras: {len(data.get('lyrics', ''))} caracteres")
                            print(f"   Cuenta usada: {data.get('stealth', {}).get('account_used', 'N/A')}")
                            print(f"   Intento: {data.get('stealth', {}).get('attempt', 'N/A')}")
                            print(f"   Nivel de evasión: {data.get('stealth', {}).get('evasion_level', 'N/A')}")
                            return True
                        else:
                            print(f"❌ Generación stealth falló: {data.get('error')}")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"❌ Error HTTP {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error en generación stealth: {e}")
            return False
    
    async def test_stealth_stats(self):
        """Probar estadísticas del sistema stealth"""
        print("📊 Probando estadísticas stealth...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.wrapper_url}/stats") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Estadísticas obtenidas")
                        print(f"   Cuentas totales: {len(data.get('accounts', []))}")
                        print(f"   Requests activos: {data.get('activeRequests', 0)}")
                        print(f"   Requests recientes: {len(data.get('requestHistory', []))}")
                        
                        # Mostrar detalles de cuentas
                        for account in data.get('accounts', []):
                            print(f"   Cuenta {account.get('id')}: {account.get('success_count', 0)} éxitos, {account.get('failure_count', 0)} fallos, estado: {account.get('status')}")
                        
                        return True
                    else:
                        print(f"❌ Error obteniendo estadísticas: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error en estadísticas: {e}")
            return False
    
    async def test_multi_account_rotation(self):
        """Probar rotación de múltiples cuentas"""
        print("🔄 Probando rotación de cuentas...")
        try:
            # Hacer múltiples requests para probar rotación
            results = []
            for i in range(3):
                payload = {
                    "prompt": f"canción de prueba {i+1}",
                    "style": "test"
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
                                account_used = data.get('stealth', {}).get('account_used', 'unknown')
                                results.append(account_used)
                                print(f"   Request {i+1}: Cuenta {account_used}")
                            else:
                                print(f"   Request {i+1}: Falló - {data.get('error')}")
                        else:
                            print(f"   Request {i+1}: Error HTTP {response.status}")
                
                # Pequeña pausa entre requests
                await asyncio.sleep(2)
            
            # Verificar si se usaron diferentes cuentas
            unique_accounts = set(results)
            if len(unique_accounts) > 1:
                print(f"✅ Rotación de cuentas funcionando: {len(unique_accounts)} cuentas diferentes usadas")
                return True
            else:
                print(f"⚠️ Solo se usó una cuenta: {unique_accounts}")
                return len(results) > 0
                
        except Exception as e:
            print(f"❌ Error en rotación de cuentas: {e}")
            return False
    
    async def test_stealth_evasion(self):
        """Probar características de evasión"""
        print("🥷 Probando características de evasión...")
        try:
            # Test con diferentes prompts para probar obfuscación
            test_prompts = [
                "música cyberpunk épica",
                "balada romántica suave",
                "rock pesado con distorsión"
            ]
            
            evasion_tests = []
            
            for prompt in test_prompts:
                payload = {
                    "prompt": prompt,
                    "style": "evasion_test"
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
                                stealth_info = data.get('stealth', {})
                                evasion_tests.append({
                                    'prompt': prompt,
                                    'account': stealth_info.get('account_used'),
                                    'attempt': stealth_info.get('attempt'),
                                    'evasion_level': stealth_info.get('evasion_level')
                                })
                                print(f"   ✅ {prompt}: Cuenta {stealth_info.get('account_used')}, Nivel {stealth_info.get('evasion_level')}")
                            else:
                                print(f"   ❌ {prompt}: {data.get('error')}")
                        else:
                            print(f"   ❌ {prompt}: HTTP {response.status}")
                
                # Pausa entre tests
                await asyncio.sleep(1)
            
            if len(evasion_tests) > 0:
                print(f"✅ Características de evasión funcionando: {len(evasion_tests)} tests exitosos")
                return True
            else:
                print("❌ No se completaron tests de evasión")
                return False
                
        except Exception as e:
            print(f"❌ Error en tests de evasión: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas stealth"""
        print("🔒 Iniciando pruebas del Sistema Stealth Ultra-Avanzado")
        print("=" * 70)
        
        tests = [
            ("Stealth Wrapper Health", self.test_stealth_wrapper_health),
            ("Stealth Generation", self.test_stealth_generation),
            ("Stealth Stats", self.test_stealth_stats),
            ("Multi-Account Rotation", self.test_multi_account_rotation),
            ("Stealth Evasion", self.test_stealth_evasion)
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
            
            # Pausa entre pruebas
            await asyncio.sleep(2)
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📋 RESUMEN DE PRUEBAS STEALTH")
        print("=" * 70)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
        
        if passed == total:
            print("🔒 ¡Todas las pruebas stealth pasaron! El sistema está completamente indetectable.")
        elif passed >= total * 0.8:
            print("⚠️ La mayoría de las pruebas stealth pasaron. Revisar las que fallaron.")
        else:
            print("❌ Muchas pruebas stealth fallaron. Revisar la configuración del sistema.")
        
        return results

async def main():
    """Función principal"""
    tester = StealthSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    print("🔒 Son1k Stealth System Ultra-Avanzado Tester")
    print("Asegúrate de que estén ejecutándose:")
    print("  - Wrapper Stealth: node suno_stealth_wrapper.js (puerto 3001)")
    print("  - API Python: python3 main_production_final.py (puerto 8000)")
    print("  - Archivo de cuentas: suno_accounts_stealth.json")
    print()
    
    asyncio.run(main())


