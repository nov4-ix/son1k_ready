#!/usr/bin/env python3
"""
📊 SON1KVERS3 - Test Analytics System
Script de prueba para el sistema de analytics
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta

class AnalyticsTester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session = None
        
    async def init(self):
        """Inicializar cliente HTTP"""
        self.session = aiohttp.ClientSession()
        print("📊 Cliente de analytics inicializado")
    
    async def close(self):
        """Cerrar cliente HTTP"""
        if self.session:
            await self.session.close()
    
    async def test_health(self):
        """Probar endpoint de salud"""
        print("\n🔍 Probando endpoint de salud...")
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check exitoso: {data}")
                    return True
                else:
                    print(f"❌ Health check falló: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return False
    
    async def test_session_management(self):
        """Probar gestión de sesiones"""
        print("\n🔍 Probando gestión de sesiones...")
        try:
            # Iniciar sesión
            async with self.session.post(f"{self.base_url}/api/session/start", 
                                       json={"user_id": "test_user_123"}) as response:
                if response.status == 200:
                    data = await response.json()
                    session_id = data['session_id']
                    print(f"✅ Sesión iniciada: {session_id}")
                    
                    # Finalizar sesión
                    async with self.session.post(f"{self.base_url}/api/session/end", 
                                               json={"session_id": session_id}) as response:
                        if response.status == 200:
                            print("✅ Sesión finalizada correctamente")
                            return True
                        else:
                            print(f"❌ Error finalizando sesión: {response.status}")
                            return False
                else:
                    print(f"❌ Error iniciando sesión: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error en gestión de sesiones: {e}")
            return False
    
    async def test_music_generation_tracking(self):
        """Probar tracking de generación musical"""
        print("\n🔍 Probando tracking de generación musical...")
        try:
            # Iniciar sesión
            async with self.session.post(f"{self.base_url}/api/session/start", 
                                       json={"user_id": "test_user_456"}) as response:
                data = await response.json()
                session_id = data['session_id']
            
            # Simular eventos de generación musical
            test_events = [
                {
                    "session_id": session_id,
                    "user_id": "test_user_456",
                    "prompt": "una canción épica de synthwave",
                    "style": "synthwave",
                    "duration": 120.5,
                    "tempo": 140,
                    "scale": "C major",
                    "instruments": ["synth", "drums", "bass"],
                    "mood": "epic",
                    "ai_enhanced": True,
                    "generation_time": 15.2,
                    "success": True,
                    "error_message": None
                },
                {
                    "session_id": session_id,
                    "user_id": "test_user_456",
                    "prompt": "música lenta y misteriosa",
                    "style": "ambient",
                    "duration": 95.3,
                    "tempo": 80,
                    "scale": "A minor",
                    "instruments": ["piano", "strings"],
                    "mood": "mysterious",
                    "ai_enhanced": False,
                    "generation_time": 8.7,
                    "success": True,
                    "error_message": None
                },
                {
                    "session_id": session_id,
                    "user_id": "test_user_456",
                    "prompt": "beat rápido de electrónica",
                    "style": "electronic",
                    "duration": 0,
                    "tempo": 160,
                    "scale": "C major",
                    "instruments": ["drums", "synth"],
                    "mood": "energetic",
                    "ai_enhanced": True,
                    "generation_time": 12.1,
                    "success": False,
                    "error_message": "Error de generación"
                }
            ]
            
            success_count = 0
            for i, event in enumerate(test_events):
                async with self.session.post(f"{self.base_url}/api/track/generation", 
                                           json=event) as response:
                    if response.status == 200:
                        print(f"✅ Evento {i+1} enviado correctamente")
                        success_count += 1
                    else:
                        print(f"❌ Error enviando evento {i+1}: {response.status}")
            
            # Finalizar sesión
            await self.session.post(f"{self.base_url}/api/session/end", 
                                  json={"session_id": session_id})
            
            print(f"✅ {success_count}/{len(test_events)} eventos enviados correctamente")
            return success_count == len(test_events)
            
        except Exception as e:
            print(f"❌ Error en tracking de generación musical: {e}")
            return False
    
    async def test_interaction_tracking(self):
        """Probar tracking de interacciones"""
        print("\n🔍 Probando tracking de interacciones...")
        try:
            # Iniciar sesión
            async with self.session.post(f"{self.base_url}/api/session/start", 
                                       json={"user_id": "test_user_789"}) as response:
                data = await response.json()
                session_id = data['session_id']
            
            # Simular interacciones
            test_interactions = [
                {
                    "session_id": session_id,
                    "user_id": "test_user_789",
                    "action": "click",
                    "element": "button#generarMusica",
                    "value": None,
                    "metadata": {"timestamp": datetime.now().isoformat()}
                },
                {
                    "session_id": session_id,
                    "user_id": "test_user_789",
                    "action": "keydown",
                    "element": "input#promptMusical",
                    "value": "Enter",
                    "metadata": {"timestamp": datetime.now().isoformat()}
                },
                {
                    "session_id": session_id,
                    "user_id": "test_user_789",
                    "action": "page_view",
                    "element": "body",
                    "value": None,
                    "metadata": {"timestamp": datetime.now().isoformat(), "url": "http://localhost:8080"}
                }
            ]
            
            success_count = 0
            for i, interaction in enumerate(test_interactions):
                async with self.session.post(f"{self.base_url}/api/track/interaction", 
                                           json=interaction) as response:
                    if response.status == 200:
                        print(f"✅ Interacción {i+1} enviada correctamente")
                        success_count += 1
                    else:
                        print(f"❌ Error enviando interacción {i+1}: {response.status}")
            
            # Finalizar sesión
            await self.session.post(f"{self.base_url}/api/session/end", 
                                  json={"session_id": session_id})
            
            print(f"✅ {success_count}/{len(test_interactions)} interacciones enviadas correctamente")
            return success_count == len(test_interactions)
            
        except Exception as e:
            print(f"❌ Error en tracking de interacciones: {e}")
            return False
    
    async def test_analytics_retrieval(self):
        """Probar obtención de analytics"""
        print("\n🔍 Probando obtención de analytics...")
        try:
            # Probar diferentes rangos de días
            for days in [1, 7, 30]:
                async with self.session.get(f"{self.base_url}/api/analytics?days={days}") as response:
                    if response.status == 200:
                        data = await response.json()
                        analytics = data['data']
                        
                        print(f"✅ Analytics de {days} días obtenidos:")
                        print(f"   - Generaciones totales: {analytics['music_metrics']['total_generations']}")
                        print(f"   - Generaciones exitosas: {analytics['music_metrics']['successful_generations']}")
                        print(f"   - Sesiones totales: {analytics['session_metrics']['total_sessions']}")
                        print(f"   - Usuarios únicos: {analytics['session_metrics']['unique_users']}")
                        print(f"   - Estilos populares: {len(analytics['popular_styles'])}")
                        print(f"   - Prompts populares: {len(analytics['popular_prompts'])}")
                    else:
                        print(f"❌ Error obteniendo analytics de {days} días: {response.status}")
                        return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error obteniendo analytics: {e}")
            return False
    
    async def test_stress(self):
        """Probar carga del sistema"""
        print("\n🔍 Probando carga del sistema...")
        try:
            # Crear múltiples sesiones simultáneamente
            tasks = []
            for i in range(10):
                task = self.create_test_session(f"stress_user_{i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for result in results if result is True)
            print(f"✅ {success_count}/10 sesiones de prueba completadas")
            
            return success_count >= 8  # 80% de éxito
            
        except Exception as e:
            print(f"❌ Error en prueba de carga: {e}")
            return False
    
    async def create_test_session(self, user_id):
        """Crear una sesión de prueba"""
        try:
            # Iniciar sesión
            async with self.session.post(f"{self.base_url}/api/session/start", 
                                       json={"user_id": user_id}) as response:
                if response.status != 200:
                    return False
                data = await response.json()
                session_id = data['session_id']
            
            # Simular algunas interacciones
            for i in range(5):
                interaction = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "action": "click",
                    "element": f"button#test_{i}",
                    "value": None,
                    "metadata": {"timestamp": datetime.now().isoformat()}
                }
                
                async with self.session.post(f"{self.base_url}/api/track/interaction", 
                                           json=interaction) as response:
                    if response.status != 200:
                        return False
            
            # Finalizar sesión
            async with self.session.post(f"{self.base_url}/api/session/end", 
                                       json={"session_id": session_id}) as response:
                return response.status == 200
                
        except Exception as e:
            print(f"❌ Error en sesión de prueba {user_id}: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE ANALYTICS")
        print("=" * 50)
        
        await self.init()
        
        tests = [
            ("Health Check", self.test_health),
            ("Gestión de Sesiones", self.test_session_management),
            ("Tracking de Generación Musical", self.test_music_generation_tracking),
            ("Tracking de Interacciones", self.test_interaction_tracking),
            ("Obtención de Analytics", self.test_analytics_retrieval),
            ("Prueba de Carga", self.test_stress)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = await test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: EXITOSO")
                else:
                    print(f"❌ {test_name}: FALLÓ")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        await self.close()
        
        # Resumen de resultados
        print("\n" + "="*50)
        print("📊 RESUMEN DE PRUEBAS")
        print("="*50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ EXITOSO" if result else "❌ FALLÓ"
            print(f"{test_name}: {status}")
        
        print(f"\nTotal: {passed}/{total} pruebas exitosas ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        elif passed >= total * 0.8:
            print("⚠️ La mayoría de pruebas exitosas, revisar las fallidas")
        else:
            print("❌ Muchas pruebas fallaron, revisar el sistema")
        
        return passed == total

async def main():
    """Función principal"""
    tester = AnalyticsTester()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
