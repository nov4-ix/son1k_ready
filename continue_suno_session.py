#!/usr/bin/env python3
"""
Continue Suno automation with existing session
Uses the current browser session instead of creating a new one
"""
import os
import sys
import time
import json
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from selenium_worker.browser_manager import BrowserManager
from selenium_worker.suno_automation import (
    ensure_custom_tab, get_lyrics_card_and_textarea, get_styles_card, 
    get_styles_editor, write_textarea, write_contenteditable, read_value,
    wait_captcha_if_any_with_notifications, wait_for_generation_and_fetch_audio
)
from selenium_worker.click_utils import click_create_when_enabled

def main():
    print("🎵 CONTINUANDO AUTOMATIZACIÓN DE SUNO")
    print("=" * 40)
    
    # Configuration
    lyrics = os.environ.get("SV_LYRICS", "Testing CAPTCHA system with existing session")
    prompt = os.environ.get("SV_PROMPT", "electronic test song, 120 BPM")
    novnc_url = os.environ.get("NOVNC_PUBLIC_URL", "")
    job_id = f"suno_continue_{int(time.time())}"
    
    print(f"📝 Lyrics: {len(lyrics)} characters")
    print(f"🎨 Prompt: {prompt}")
    print(f"🖥️  noVNC: {novnc_url}")
    print(f"🆔 Job ID: {job_id}")
    print()
    
    try:
        # Connect to existing browser
        print("🌐 Conectando a sesión existente...")
        bm = BrowserManager(headless=False)
        driver = bm.get_driver()
        
        print(f"📍 URL actual: {driver.current_url}")
        
        # Take initial screenshot
        driver.save_screenshot("./continue_01_start.png")
        print("📸 Screenshot inicial guardado")
        
        # Wait a moment for page to load
        time.sleep(3)
        
        # Try to activate Custom tab
        print("🎛️ Intentando activar pestaña Custom...")
        custom_success = ensure_custom_tab(driver)
        
        if custom_success:
            print("✅ Pestaña Custom activada")
        else:
            print("⚠️  No se pudo activar Custom, continuando...")
        
        driver.save_screenshot("./continue_02_custom.png")
        
        # Try to find lyrics elements
        print("🎵 Buscando elementos de lyrics...")
        lyrics_card, lyrics_textarea = get_lyrics_card_and_textarea(driver)
        
        if lyrics_textarea:
            print("✅ Campo de lyrics encontrado")
            
            # Write lyrics
            print("📝 Escribiendo lyrics...")
            if write_textarea(driver, lyrics_textarea, lyrics):
                print("✅ Lyrics escritos exitosamente")
                
                # Verify lyrics
                written_lyrics = read_value(lyrics_textarea)
                print(f"📊 Lyrics verificados: {len(written_lyrics)} caracteres")
            else:
                print("❌ Error escribiendo lyrics")
        else:
            print("❌ No se encontró campo de lyrics")
        
        driver.save_screenshot("./continue_03_lyrics.png")
        
        # Try to find styles elements
        print("🎨 Buscando elementos de styles...")
        if lyrics_card:
            styles_card = get_styles_card(driver, lyrics_card)
            if styles_card:
                styles_editor = get_styles_editor(styles_card)
                if styles_editor:
                    print("✅ Campo de styles encontrado")
                    
                    # Write styles
                    print("📝 Escribiendo prompt...")
                    is_contenteditable = styles_editor.get_attribute('contenteditable') == 'true'
                    
                    if is_contenteditable:
                        success = write_contenteditable(driver, styles_editor, prompt)
                    else:
                        success = write_textarea(driver, styles_editor, prompt)
                    
                    if success:
                        print("✅ Prompt escrito exitosamente")
                        written_prompt = read_value(styles_editor)
                        print(f"📊 Prompt verificado: {len(written_prompt)} caracteres")
                    else:
                        print("❌ Error escribiendo prompt")
                else:
                    print("❌ No se encontró editor de styles")
            else:
                print("❌ No se encontró card de styles")
        
        driver.save_screenshot("./continue_04_styles.png")
        
        # Check for CAPTCHA
        print("🛡️  Verificando CAPTCHAs...")
        captcha_ok = wait_captcha_if_any_with_notifications(
            driver, job_id, max_wait_seconds=60, 
            screenshot_callback=lambda f: driver.save_screenshot(f"./continue_captcha_{f}")
        )
        
        if captcha_ok:
            print("✅ No hay CAPTCHAs o fueron resueltos")
        else:
            print("⚠️  CAPTCHA detectado - resuélvelo en noVNC y ejecuta de nuevo")
            return
        
        # Try to click Create button
        print("🚀 Intentando hacer click en Create...")
        create_success = click_create_when_enabled(
            driver, lyrics_textarea, styles_editor, timeout=60,
            screenshot_cb=lambda f: driver.save_screenshot(f"./continue_{f}")
        )
        
        if create_success:
            print("✅ Botón Create clickeado exitosamente")
            
            # Wait for generation
            print("⏳ Esperando generación de música...")
            artifacts = wait_for_generation_and_fetch_audio(driver, timeout=300)
            
            if artifacts:
                print(f"🎉 ¡Generación exitosa! {len(artifacts)} archivos")
                for i, artifact in enumerate(artifacts):
                    print(f"   📄 {i+1}: {artifact.get('title', 'Unknown')} - {artifact.get('size', 0)} bytes")
                
                result = {
                    "success": True,
                    "message": "Music generation completed successfully",
                    "artifacts": artifacts,
                    "lyrics": lyrics,
                    "prompt": prompt,
                    "job_id": job_id,
                    "total_tracks": len(artifacts)
                }
                print(json.dumps(result, indent=2))
            else:
                print("❌ No se generaron archivos de audio")
        else:
            print("❌ No se pudo hacer click en Create")
        
        driver.save_screenshot("./continue_99_final.png")
        print("📸 Screenshot final guardado")
        
    except Exception as e:
        print(f"❌ Error en automatización: {e}")
        try:
            driver.save_screenshot("./continue_ZZ_error.png")
        except:
            pass
    
    print("🔗 Navegador sigue disponible en:", novnc_url)

if __name__ == "__main__":
    main()