#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema Ollama y créditos
"""

import requests
import json
import time
from credit_manager import credit_manager
from lyrics_generator import LyricsGenerator

def test_ollama_connection():
    """Probar conexión con Ollama"""
    print("🔍 Probando conexión con Ollama...")
    
    try:
        # Verificar que Ollama esté corriendo
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama está corriendo. Modelos disponibles: {len(models)}")
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Error en Ollama: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con Ollama: {e}")
        return False

def test_ollama_generation():
    """Probar generación con Ollama"""
    print("\n🎵 Probando generación de letras con Ollama...")
    
    try:
        lyrics_gen = LyricsGenerator("free")
        result = lyrics_gen.generate_lyrics(
            theme="resistencia digital",
            genre="synthwave",
            language="es"
        )
        
        if result.get("success"):
            print("✅ Generación de letras exitosa")
            print(f"Modelo usado: {result.get('model_used')}")
            print(f"Calidad: {result.get('quality')}")
            print(f"Fuente: {result.get('source')}")
            print(f"Letras generadas:\n{result.get('lyrics', '')[:200]}...")
            return True
        else:
            print("❌ Error en generación de letras")
            return False
            
    except Exception as e:
        print(f"❌ Error en generación: {e}")
        return False

def test_credit_system():
    """Probar sistema de créditos"""
    print("\n💰 Probando sistema de créditos...")
    
    try:
        # Probar estado del sistema
        status = credit_manager.get_system_status()
        print(f"✅ Sistema de créditos funcionando")
        print(f"Total créditos: {status['total_credits']}")
        print(f"Créditos usados: {status['used_credits']}")
        print(f"Créditos restantes: {status['remaining_credits']}")
        
        # Probar uso de usuario
        user_usage = credit_manager.get_user_usage("test_user", "free")
        print(f"Uso del usuario test_user: {user_usage['generations_used']} generaciones")
        
        # Probar consumo de créditos
        can_consume, message = credit_manager.consume_credits("test_user", "free", 10)
        if can_consume:
            print("✅ Consumo de créditos exitoso")
        else:
            print(f"❌ Error consumiendo créditos: {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema de créditos: {e}")
        return False

def test_prompt_generation():
    """Probar generación de prompts"""
    print("\n🎛️ Probando generación de prompts...")
    
    try:
        lyrics_gen = LyricsGenerator("pro")
        result = lyrics_gen.generate_prompt(
            user_input="música cyberpunk épica",
            genre="synthwave",
            mood="energético"
        )
        
        if result.get("success"):
            print("✅ Generación de prompt exitosa")
            print(f"Prompt generado: {result.get('generated_prompt', '')[:150]}...")
            return True
        else:
            print("❌ Error en generación de prompt")
            return False
            
    except Exception as e:
        print(f"❌ Error en generación de prompt: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del sistema Son1kvers3")
    print("=" * 50)
    
    tests = [
        ("Conexión Ollama", test_ollama_connection),
        ("Sistema de Créditos", test_credit_system),
        ("Generación de Letras", test_ollama_generation),
        ("Generación de Prompts", test_prompt_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
