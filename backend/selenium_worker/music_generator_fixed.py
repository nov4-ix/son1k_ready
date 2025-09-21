#!/usr/bin/env python3
"""
🎵 Son1k Music Generator (Fixed)
Motor de generación musical mejorado con nombres dinámicos
"""
import os
import time
import json
import logging
import re
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SongNameGenerator:
    """Generador de nombres dinámicos para canciones"""
    
    @staticmethod
    def generate_name_from_lyrics(lyrics: str) -> str:
        """Generar nombre desde la primera frase de las lyrics"""
        if not lyrics or not lyrics.strip():
            return f"Instrumental_{int(time.time())}"
        
        # Limpiar y procesar lyrics
        clean_lyrics = lyrics.strip()
        
        # Tomar primera línea/frase significativa
        lines = clean_lyrics.split('\n')
        first_line = ""
        
        for line in lines:
            line = line.strip()
            # Buscar primera línea con contenido real (no vacía, no solo signos)
            if line and len(line) > 3 and not line.isspace():
                first_line = line
                break
        
        if not first_line:
            # Si no hay primera línea, usar las primeras palabras
            words = clean_lyrics.split()[:4]
            first_line = " ".join(words) if words else "Sin Título"
        
        # Limpiar el nombre
        song_name = SongNameGenerator.clean_filename(first_line)
        
        # Limitar longitud
        if len(song_name) > 50:
            song_name = song_name[:47] + "..."
        
        return song_name or f"Canción_{int(time.time())}"
    
    @staticmethod
    def clean_filename(text: str) -> str:
        """Limpiar texto para usar como nombre de archivo"""
        # Remover caracteres especiales problemáticos
        cleaned = re.sub(r'[<>:"/\\|?*]', '', text)
        
        # Reemplazar múltiples espacios con uno solo
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remover espacios al inicio y final
        cleaned = cleaned.strip()
        
        # Capitalizar primera letra de cada palabra
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        return cleaned

class MusicGeneratorFixed:
    """Motor de generación musical corregido"""
    
    def __init__(self):
        self.driver = None
        self.session_active = False
        self.base_url = "https://suno.com"
        
    def initialize_driver(self):
        """Inicializar driver con configuración optimizada"""
        try:
            options = Options()
            
            # Configuración anti-detección
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent real
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            
            # Configuración de ventana
            options.add_argument('--window-size=1920,1080')
            
            # Usar Selenium remoto
            remote_url = os.environ.get("SV_SELENIUM_URL", "http://localhost:4444/wd/hub")
            
            self.driver = webdriver.Remote(
                command_executor=remote_url,
                options=options
            )
            
            # Scripts anti-detección
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                delete navigator.__proto__.webdriver;
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)
            
            logger.info("Driver inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando driver: {e}")
            return False
    
    def check_session(self):
        """Verificar sesión activa"""
        try:
            if not self.driver:
                return False
                
            self.driver.get(f"{self.base_url}/create")
            time.sleep(3)
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Verificar si estamos en la página correcta y logueados
            if "/create" in current_url and "sign" not in page_source:
                logger.info("Sesión activa confirmada")
                self.session_active = True
                return True
            else:
                logger.warning("Sesión no activa o redirigido a login")
                self.session_active = False
                return False
                
        except Exception as e:
            logger.error(f"Error verificando sesión: {e}")
            return False
    
    def wait_for_element_with_retry(self, selector: str, timeout: int = 10, max_retries: int = 3):
        """Esperar elemento con reintentos"""
        for attempt in range(max_retries):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed():
                    return element
                    
            except TimeoutException:
                logger.warning(f"Intento {attempt + 1} fallido para selector: {selector}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                    
        return None
    
    def activate_custom_mode(self):
        """Activar modo Custom con detección mejorada"""
        try:
            # Esperar a que la página cargue completamente
            time.sleep(3)
            
            # Buscar y hacer clic en pestaña Custom con múltiples estrategias
            custom_selectors = [
                "button[data-testid*='custom']",
                "//button[contains(text(), 'Custom')]", 
                "//button[contains(@aria-label, 'Custom')]",
                "[role='tab'][aria-label*='Custom']",
                "button:contains('Custom')",
                ".tab[data-value='custom']",
                "button[value='custom']"
            ]
            
            for selector in custom_selectors:
                try:
                    if "//" in selector:  # XPath
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:  # CSS
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element and element.is_displayed() and element.is_enabled():
                            # Scroll al elemento si es necesario
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            
                            # Intentar hacer clic
                            element.click()
                            logger.info("✅ Modo Custom activado")
                            time.sleep(2)
                            return True
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} falló: {e}")
                    continue
            
            # Fallback: buscar por texto visible
            try:
                custom_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in custom_buttons:
                    if button.text and "custom" in button.text.lower():
                        button.click()
                        logger.info("✅ Modo Custom activado (fallback)")
                        time.sleep(2)
                        return True
            except:
                pass
            
            logger.warning("⚠️ No se pudo activar modo Custom, continuando...")
            return False
            
        except Exception as e:
            logger.error(f"Error activando Custom: {e}")
            return False
    
    def fill_lyrics_field(self, lyrics: str):
        """Llenar campo de lyrics"""
        try:
            lyrics_selectors = [
                "textarea[placeholder*='lyrics' i]",
                "textarea[data-testid*='lyrics']",
                "div[contenteditable='true'][aria-label*='lyrics' i]",
                "textarea:first-of-type"
            ]
            
            for selector in lyrics_selectors:
                try:
                    element = self.wait_for_element_with_retry(selector, 5)
                    if element:
                        # Limpiar campo
                        element.clear()
                        
                        # Escribir lyrics
                        element.send_keys(lyrics)
                        
                        # Verificar que se escribió
                        if element.get_attribute('value') or element.text:
                            logger.info("Lyrics completados exitosamente")
                            return True
                            
                except Exception as e:
                    logger.warning(f"Error con selector {selector}: {e}")
                    continue
            
            logger.error("No se pudo llenar campo de lyrics")
            return False
            
        except Exception as e:
            logger.error(f"Error llenando lyrics: {e}")
            return False
    
    def fill_prompt_field(self, prompt: str):
        """Llenar campo de prompt/style"""
        try:
            prompt_selectors = [
                "input[placeholder*='style' i]",
                "input[placeholder*='prompt' i]",
                "div[contenteditable='true'][aria-label*='style' i]",
                "input[type='text']:not([placeholder*='lyrics'])"
            ]
            
            for selector in prompt_selectors:
                try:
                    element = self.wait_for_element_with_retry(selector, 5)
                    if element:
                        element.clear()
                        element.send_keys(prompt)
                        
                        if element.get_attribute('value'):
                            logger.info("Prompt completado exitosamente")
                            return True
                            
                except Exception as e:
                    logger.warning(f"Error con selector {selector}: {e}")
                    continue
            
            logger.error("No se pudo llenar campo de prompt")
            return False
            
        except Exception as e:
            logger.error(f"Error llenando prompt: {e}")
            return False
    
    def click_create_button(self):
        """Hacer clic en botón Create"""
        try:
            create_selectors = [
                "button[aria-label*='Create' i]",
                "button:has-text('Create')",
                "//button[contains(text(), 'Create')]",
                "button[data-testid*='create']",
                "button[type='submit']"
            ]
            
            for selector in create_selectors:
                try:
                    if "//" in selector:  # XPath
                        element = self.driver.find_element(By.XPATH, selector)
                    else:  # CSS
                        element = self.wait_for_element_with_retry(selector, 5)
                    
                    if element and element.is_enabled() and element.is_displayed():
                        element.click()
                        logger.info("Botón Create clickeado")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Error con selector {selector}: {e}")
                    continue
            
            logger.error("No se pudo hacer clic en Create")
            return False
            
        except Exception as e:
            logger.error(f"Error haciendo clic en Create: {e}")
            return False
    
    def wait_for_generation(self, timeout: int = 300):
        """Esperar completación de generación"""
        try:
            start_time = time.time()
            logger.info("Esperando generación de música...")
            
            while time.time() - start_time < timeout:
                try:
                    # Buscar elementos de tracks generados
                    track_selectors = [
                        "[data-testid*='track']",
                        ".track-container",
                        ".song-item",
                        "audio",
                        "[src*='.mp3']"
                    ]
                    
                    tracks_found = []
                    for selector in track_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                tracks_found.extend(elements)
                        except:
                            continue
                    
                    # Si encontramos tracks, extraer información
                    if tracks_found:
                        logger.info(f"Generación completada: {len(tracks_found)} elementos encontrados")
                        return self.extract_tracks_info(tracks_found, getattr(self, '_current_lyrics', ''))
                    
                    # Verificar errores
                    error_selectors = [".error", "[data-testid*='error']", ".alert-error"]
                    for selector in error_selectors:
                        try:
                            error_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if error_elem and error_elem.is_displayed():
                                logger.error("Error en generación detectado")
                                return None
                        except:
                            continue
                    
                    # Esperar y continuar
                    time.sleep(5)
                    
                except Exception as e:
                    logger.warning(f"Error en loop de espera: {e}")
                    time.sleep(5)
                    continue
            
            logger.error("Timeout esperando generación")
            return None
            
        except Exception as e:
            logger.error(f"Error esperando generación: {e}")
            return None
    
    def extract_tracks_info(self, track_elements, lyrics: str = ""):
        """Extraer información de tracks con nombres dinámicos"""
        try:
            results = []
            
            # Generar nombre base desde lyrics
            base_name = SongNameGenerator.generate_name_from_lyrics(lyrics)
            
            for i, element in enumerate(track_elements):
                try:
                    # Extraer título dinámico
                    title = f"{base_name}"
                    if len(track_elements) > 1:
                        title += f" - Parte {i+1}"
                    
                    # Extraer duración
                    duration = "Unknown"
                    duration_selectors = [".duration", "[data-testid*='duration']", ".time", ".length"]
                    for selector in duration_selectors:
                        try:
                            duration_elem = element.find_element(By.CSS_SELECTOR, selector)
                            if duration_elem and duration_elem.text:
                                duration = duration_elem.text
                                break
                        except:
                            continue
                    
                    # Extraer URL de audio con múltiples intentos
                    audio_url = None
                    audio_selectors = [
                        "audio source[src]",
                        "audio[src]", 
                        "[src*='.mp3']",
                        "[src*='.wav']",
                        "[href*='.mp3']",
                        "[href*='.wav']"
                    ]
                    
                    for selector in audio_selectors:
                        try:
                            audio_elem = element.find_element(By.CSS_SELECTOR, selector)
                            if audio_elem:
                                url = audio_elem.get_attribute("src") or audio_elem.get_attribute("href")
                                if url and ("mp3" in url or "wav" in url):
                                    audio_url = url
                                    break
                        except:
                            continue
                    
                    # Si no encontramos URL, buscar en elemento padre
                    if not audio_url:
                        try:
                            parent_audio = self.driver.find_elements(By.CSS_SELECTOR, "audio[src], [src*='.mp3']")
                            if parent_audio:
                                audio_url = parent_audio[0].get_attribute("src")
                        except:
                            pass
                    
                    # Crear resultado con nombre dinámico
                    result = {
                        "id": f"track_{int(time.time())}_{i+1}",
                        "title": title,  # Nombre dinámico basado en lyrics
                        "duration": duration,
                        "url": audio_url,
                        "download_url": audio_url,
                        "generated_at": int(time.time()),
                        "provider": "Son1k",
                        "lyrics_preview": lyrics[:100] + "..." if len(lyrics) > 100 else lyrics,
                        "filename": f"{base_name.replace(' ', '_')}.mp3"  # Nombre de archivo limpio
                    }
                    
                    results.append(result)
                    logger.info(f"✅ Track extraído: {title}")
                    
                except Exception as e:
                    logger.warning(f"Error extrayendo track {i+1}: {e}")
                    continue
            
            return results if results else None
            
        except Exception as e:
            logger.error(f"Error extrayendo tracks: {e}")
            return None
    
    def generate_music(self, lyrics: str, prompt: str, job_id: str, instrumental: bool = False):
        """Proceso completo de generación"""
        try:
            logger.info(f"Iniciando generación: {job_id}")
            
            # 1. Inicializar driver
            if not self.driver:
                if not self.initialize_driver():
                    logger.error("No se pudo inicializar driver")
                    return None
            
            # 2. Verificar sesión
            if not self.check_session():
                logger.error("Sesión no válida en Suno")
                return None
            
            # 3. Activar modo Custom
            if not self.activate_custom_mode():
                logger.warning("No se pudo activar modo Custom, continuando...")
            
            # 4. Llenar campos
            if not instrumental and lyrics:
                if not self.fill_lyrics_field(lyrics):
                    logger.error("Error llenando lyrics")
                    return None
            
            if prompt:
                if not self.fill_prompt_field(prompt):
                    logger.error("Error llenando prompt")
                    return None
            
            # 5. Iniciar generación
            if not self.click_create_button():
                logger.error("Error haciendo clic en Create")
                return None
            
            # 6. Guardar lyrics para extracción dinámica de nombres
            self._current_lyrics = lyrics
            
            # 7. Esperar resultados
            results = self.wait_for_generation()
            
            if results:
                logger.info(f"Generación exitosa: {len(results)} tracks")
                return results
            else:
                logger.error("No se generaron resultados")
                return None
            
        except Exception as e:
            logger.error(f"Error en generación completa: {e}")
            return None
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

# Función de conveniencia
def generate_music_fixed(lyrics: str, prompt: str, job_id: str, instrumental: bool = False):
    """Función principal para generación musical"""
    generator = MusicGeneratorFixed()
    try:
        return generator.generate_music(lyrics, prompt, job_id, instrumental)
    finally:
        generator.cleanup()