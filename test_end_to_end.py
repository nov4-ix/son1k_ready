#!/usr/bin/env python3
"""
Test End-to-End completo del sistema Son1k-Suno
Simula todo el flujo desde frontend hasta descarga
"""
import os
import sys
import time
import json
import requests
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_api_health():
    """Verificar que la API esté funcionando"""
    try:
        response = requests.get("http://localhost:8000/api/captcha/health", timeout=5)
        if response.status_code == 200:
            print("✅ API CAPTCHA funcionando")
            return True
        else:
            print(f"❌ API responde con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando a API: {e}")
        return False

def simulate_frontend_request():
    """Simular petición desde frontend Son1k"""
    print("🎵 SIMULANDO PETICIÓN DESDE FRONTEND SON1K")
    print("=" * 50)
    
    # Datos de prueba que enviaría el frontend
    test_request = {
        "lyrics": "Testing end-to-end workflow\nFrom Son1k frontend to Suno\nComplete automation test\nWith CAPTCHA resolution",
        "prompt": "upbeat electronic test song, 120 BPM, energetic synthesizers and drums",
        "style": "electronic",
        "user_id": "test_user_001",
        "session_id": f"test_{int(time.time())}"
    }
    
    print(f"📝 Lyrics: {len(test_request['lyrics'])} caracteres")
    print(f"🎨 Prompt: {test_request['prompt']}")
    print(f"👤 User ID: {test_request['user_id']}")
    print(f"🆔 Session: {test_request['session_id']}")
    
    return test_request

def test_suno_automation(test_request):
    """Ejecutar automatización de Suno"""
    print("\n🤖 EJECUTANDO AUTOMATIZACIÓN DE SUNO")
    print("=" * 40)
    
    try:
        from selenium_worker.browser_manager import BrowserManager
        from selenium_worker.suno_automation import (
            ensure_custom_tab, get_lyrics_card_and_textarea, 
            get_styles_card, get_styles_editor, write_textarea, 
            write_contenteditable, read_value,
            wait_captcha_if_any_with_notifications, 
            wait_for_generation_and_fetch_audio
        )
        from selenium_worker.click_utils import click_create_when_enabled
        
        print("🌐 Conectando a navegador remoto...")
        bm = BrowserManager(headless=False)
        driver = bm.get_driver()
        
        print(f"📍 URL actual: {driver.current_url}")
        
        # Si no estamos en Suno, navegar
        if "suno.com" not in driver.current_url:
            print("🎯 Navegando a Suno...")
            driver.get("https://suno.com")
            time.sleep(5)
        
        # Activar pestaña Custom
        print("🎛️ Activando pestaña Custom...")
        custom_success = ensure_custom_tab(driver)
        
        if custom_success:
            print("✅ Pestaña Custom activada")
            
            # Completar campos
            print("📝 Completando campos...")
            lyrics_card, lyrics_textarea = get_lyrics_card_and_textarea(driver)
            
            if lyrics_textarea:
                if write_textarea(driver, lyrics_textarea, test_request["lyrics"]):
                    print("✅ Lyrics escritos")
                
                # Completar prompt
                styles_card = get_styles_card(driver, lyrics_card)
                if styles_card:
                    styles_editor = get_styles_editor(styles_card)
                    if styles_editor:
                        is_contenteditable = styles_editor.get_attribute('contenteditable') == 'true'
                        
                        if is_contenteditable:
                            success = write_contenteditable(driver, styles_editor, test_request["prompt"])
                        else:
                            success = write_textarea(driver, styles_editor, test_request["prompt"])
                        
                        if success:
                            print("✅ Prompt escrito")
                
                # Verificar CAPTCHAs
                print("🛡️ Verificando CAPTCHAs...")
                job_id = test_request["session_id"]
                captcha_ok = wait_captcha_if_any_with_notifications(
                    driver, job_id, max_wait_seconds=60
                )
                
                if captcha_ok:
                    print("✅ CAPTCHAs verificados")
                    
                    # Hacer clic en Create
                    print("🚀 Haciendo clic en Create...")
                    create_success = click_create_when_enabled(
                        driver, lyrics_textarea, styles_editor, timeout=60
                    )
                    
                    if create_success:
                        print("✅ Generación iniciada")
                        
                        # Esperar generación
                        print("⏳ Esperando generación completa...")
                        artifacts = wait_for_generation_and_fetch_audio(driver, timeout=300)
                        
                        if artifacts:
                            print(f"🎉 ¡Generación exitosa! {len(artifacts)} archivos")
                            return artifacts
                        else:
                            print("❌ No se generaron archivos")
                            return None
                    else:
                        print("❌ No se pudo hacer clic en Create")
                        return None
                else:
                    print("⚠️ CAPTCHA pendiente - resuélvelo manualmente")
                    return None
            else:
                print("❌ No se encontró campo de lyrics")
                return None
        else:
            print("❌ No se pudo activar pestaña Custom")
            return None
    
    except Exception as e:
        print(f"❌ Error en automatización: {e}")
        return None

def simulate_frontend_response(artifacts):
    """Simular respuesta al frontend"""
    if artifacts:
        print("\n📤 ENVIANDO RESPUESTA AL FRONTEND")
        print("=" * 35)
        
        response = {
            "status": "success",
            "message": "Música generada exitosamente",
            "tracks": [],
            "download_urls": [],
            "metadata": {
                "generation_time": int(time.time()),
                "provider": "suno",
                "total_tracks": len(artifacts)
            }
        }
        
        for i, artifact in enumerate(artifacts):
            track_info = {
                "id": f"track_{i+1}",
                "title": artifact.get("title", f"Track {i+1}"),
                "duration": artifact.get("duration", "Unknown"),
                "url": artifact.get("url", ""),
                "download_url": artifact.get("download_url", ""),
                "size": artifact.get("size", 0)
            }
            response["tracks"].append(track_info)
            response["download_urls"].append(track_info["download_url"])
        
        print(f"🎵 Tracks generados: {len(response['tracks'])}")
        for track in response["tracks"]:
            print(f"   📄 {track['title']} - {track['duration']}")
        
        print("\n🎉 ¡TEST END-TO-END COMPLETADO EXITOSAMENTE!")
        return response
    else:
        print("\n❌ TEST END-TO-END FALLIDO")
        return {"status": "error", "message": "No se generaron archivos"}

def main():
    print("🧪 INICIANDO TEST END-TO-END COMPLETO")
    print("=" * 60)
    
    # 1. Verificar API
    if not test_api_health():
        print("❌ Sistema no está listo")
        return
    
    # 2. Simular petición frontend
    test_request = simulate_frontend_request()
    
    # 3. Ejecutar automatización
    artifacts = test_suno_automation(test_request)
    
    # 4. Simular respuesta
    result = simulate_frontend_response(artifacts)
    
    # 5. Mostrar resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    print(json.dumps(result, indent=2))
    
    if result.get("status") == "success":
        print("\n✅ SISTEMA END-TO-END FUNCIONANDO CORRECTAMENTE")
        print("🔗 Navegador remoto disponible en: https://3f7a528a8973.ngrok-free.app")
    else:
        print("\n❌ SISTEMA REQUIERE ATENCIÓN")

if __name__ == "__main__":
    main()