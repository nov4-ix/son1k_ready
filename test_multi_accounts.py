#!/usr/bin/env python3
"""
Script de prueba para múltiples cuentas de Suno
"""
import asyncio
import aiohttp
import json
import time
from multi_account_manager import MultiAccountManager

async def test_multi_accounts():
    """Probar el sistema de múltiples cuentas"""
    
    print("🚀 Probando Sistema de Múltiples Cuentas de Suno")
    print("=" * 50)
    
    # Inicializar gestor de cuentas
    manager = MultiAccountManager()
    await manager.initialize()
    
    # Mostrar estadísticas de cuentas
    stats = await manager.get_account_stats()
    print(f"\n📊 Estadísticas de cuentas:")
    print(f"   Total: {stats['total_accounts']}")
    print(f"   Activas: {stats['active_accounts']}")
    print(f"   Disponibles: {stats['available_accounts']}")
    
    if stats['available_accounts'] == 0:
        print("❌ No hay cuentas disponibles para probar")
        return
    
    print(f"\n📋 Detalles de cuentas:")
    for account in stats['accounts']:
        status = "✅" if account['is_available'] else "❌"
        print(f"   {status} {account['email']} - Score: {account['score']} - Uso: {account['daily_usage']}")
    
    # Probar generación de música
    test_prompts = [
        "una canción de rock clásico sobre la libertad",
        "música electrónica ambient para estudiar",
        "jazz suave con piano y saxofón"
    ]
    
    print(f"\n🎵 Probando generación con {len(test_prompts)} prompts...")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Prueba {i}: {prompt} ---")
        
        start_time = time.time()
        
        try:
            result = await manager.generate_music(prompt, "", "profesional")
            
            duration = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ ¡Éxito! ({duration:.1f}s)")
                print(f"   Cuenta usada: {result.get('account_used', 'N/A')}")
                print(f"   Audios generados: {len(result.get('audio_urls', []))}")
                
                if result.get('lyrics'):
                    print(f"   Letras: {result['lyrics'][:100]}...")
            else:
                print(f"❌ Fallo: {result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Pausa entre pruebas
        if i < len(test_prompts):
            print("⏳ Esperando 10 segundos...")
            await asyncio.sleep(10)
    
    # Mostrar estadísticas finales
    print(f"\n📊 Estadísticas finales:")
    final_stats = await manager.get_account_stats()
    
    for account in final_stats['accounts']:
        print(f"   {account['email']}: {account['success_rate']} éxito, {account['daily_usage']} usos")
    
    await manager.cleanup()
    print("\n✅ Pruebas completadas")

async def test_load_balancing():
    """Probar el balanceo de carga"""
    
    print("\n🔄 Probando Balanceo de Carga")
    print("=" * 30)
    
    manager = MultiAccountManager()
    await manager.initialize()
    
    # Cambiar a modo round_robin
    manager.load_balancer = "round_robin"
    
    print("🎯 Modo: Round Robin")
    
    # Generar 10 peticiones rápidas
    for i in range(10):
        try:
            result = await manager.generate_music(f"test song {i}", "", "test")
            account_used = result.get('account_used', 'N/A')
            print(f"   Petición {i+1}: {account_used}")
        except Exception as e:
            print(f"   Petición {i+1}: Error - {e}")
        
        await asyncio.sleep(1)  # Pausa corta
    
    await manager.cleanup()

async def test_account_rotation():
    """Probar la rotación de cuentas"""
    
    print("\n🔄 Probando Rotación de Cuentas")
    print("=" * 30)
    
    manager = MultiAccountManager()
    await manager.initialize()
    
    # Forzar rotación
    await manager.rotate_accounts()
    
    print("✅ Rotación completada")
    
    # Mostrar estado después de rotación
    stats = await manager.get_account_stats()
    print(f"📊 Cuentas disponibles después de rotación: {stats['available_accounts']}")
    
    await manager.cleanup()

async def main():
    """Función principal"""
    print("🎵 Son1k Multi-Account Test Suite")
    print("=" * 40)
    
    try:
        await test_multi_accounts()
        await test_load_balancing()
        await test_account_rotation()
        
        print("\n" + "=" * 40)
        print("🏁 Todas las pruebas completadas")
        
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")

if __name__ == "__main__":
    asyncio.run(main())




