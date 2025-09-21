#!/usr/bin/env python3
"""
🎵 Suno Commercial Integration
Conexión comercial transparente entre Son1kVers3 y Suno
"""
import os
import time
import json
import asyncio
import logging
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SunoCommercialEngine:
    """Motor comercial de Suno para Son1kVers3"""
    
    def __init__(self):
        self.driver = None
        self.session_active = False
        self.base_url = "https://suno.com"
        self.api_url = "http://localhost:8000"
        
    def initialize_driver(self):
        """Inicializar driver con configuración comercial"""
        options = Options()
        
        # Configuración anti-detección comercial
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent comercial
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        
        # Configuración de ventana
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        
        # Usar Selenium remoto
        remote_url = os.environ.get("SV_SELENIUM_URL", "http://localhost:4444/wd/hub")
        
        try:
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
            """)
            
            logger.info("Driver comercial inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando driver: {e}")
            return False
    
    def check_session(self):
        """Verificar si hay sesión activa en Suno"""
        try:
            if not self.driver:
                return False
                
            self.driver.get(f"{self.base_url}/create")
            time.sleep(3)
            
            # Verificar si estamos logueados
            current_url = self.driver.current_url
            if "/create" in current_url or "/home" in current_url:
                logger.info("Sesión activa detectada")
                self.session_active = True
                return True
            else:
                logger.info("No hay sesión activa")
                self.session_active = False
                return False
                
        except Exception as e:
            logger.error(f"Error verificando sesión: {e}")
            return False
    
    def ensure_login(self):
        """Asegurar que hay login activo"""
        if self.check_session():
            return True
            
        try:
            # Ir a página principal
            self.driver.get(self.base_url)
            time.sleep(5)
            
            # Si no está logueado, mandar a login
            if "sign" in self.driver.current_url.lower():
                logger.info("Redirigiendo a login manual")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False
    
    def fill_generation_form(self, lyrics: str, prompt: str, instrumental: bool = False):
        """Llenar formulario de generación en Suno"""
        try:
            # Ir a página de creación
            self.driver.get(f"{self.base_url}/create")
            time.sleep(5)
            
            # Activar modo Custom si no está activo
            try:
                custom_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Custom')]")
                if custom_tab:
                    custom_tab.click()
                    time.sleep(2)
            except:
                pass
            
            # Llenar lyrics
            if not instrumental and lyrics:
                lyrics_selectors = [
                    "textarea[placeholder*='lyrics' i]",
                    "textarea[data-testid*='lyrics']",
                    "div[contenteditable='true'][aria-label*='lyrics' i]"
                ]
                
                for selector in lyrics_selectors:
                    try:
                        lyrics_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        lyrics_field.clear()
                        lyrics_field.send_keys(lyrics)
                        logger.info("Lyrics completados")
                        break
                    except:
                        continue
            
            # Llenar prompt de estilo
            if prompt:
                prompt_selectors = [
                    "input[placeholder*='style' i]",
                    "input[placeholder*='prompt' i]",
                    "div[contenteditable='true'][aria-label*='style' i]"
                ]
                
                for selector in prompt_selectors:
                    try:
                        prompt_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        prompt_field.clear()
                        prompt_field.send_keys(prompt)
                        logger.info("Prompt completado")
                        break
                    except:
                        continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error llenando formulario: {e}")
            return False
    
    def handle_captcha(self, job_id: str):
        """Manejar CAPTCHAs automáticamente"""
        try:
            # Detectar CAPTCHAs
            captcha_selectors = [
                "iframe[src*='hcaptcha']",
                "iframe[src*='recaptcha']",
                "iframe[src*='turnstile']",
                ".h-captcha",
                ".g-recaptcha"
            ]
            
            captcha_found = False
            for selector in captcha_selectors:
                try:
                    captcha = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if captcha.is_displayed():
                        logger.info(f"CAPTCHA detectado: {selector}")
                        captcha_found = True
                        
                        # Notificar al backend
                        self.notify_captcha_event(job_id, "NEEDED")
                        break
                except:
                    continue
            
            if not captcha_found:
                return True
            
            # Esperar resolución manual
            max_wait = 300  # 5 minutos
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # Verificar si CAPTCHA sigue presente
                captcha_still_present = False
                for selector in captcha_selectors:
                    try:
                        captcha = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if captcha.is_displayed():
                            captcha_still_present = True
                            break
                    except:
                        continue
                
                if not captcha_still_present:
                    logger.info("CAPTCHA resuelto")
                    self.notify_captcha_event(job_id, "RESOLVED")
                    return True
                
                time.sleep(2)
            
            logger.error("Timeout esperando resolución de CAPTCHA")
            return False
            
        except Exception as e:
            logger.error(f"Error manejando CAPTCHA: {e}")
            return False
    
    def start_generation(self):
        """Iniciar generación de música"""
        try:
            # Buscar botón Create
            create_selectors = [
                "button[aria-label*='Create' i]",
                "button:has-text('Create')",
                "button[data-testid*='create']",
                "button[type='submit']"
            ]
            
            for selector in create_selectors:
                try:
                    create_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if create_btn.is_enabled():
                        create_btn.click()
                        logger.info("Generación iniciada")
                        return True
                except:
                    continue
            
            # Fallback: buscar por texto
            try:
                create_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
                create_btn.click()
                logger.info("Generación iniciada (fallback)")
                return True
            except:
                pass
            
            logger.error("No se pudo encontrar botón Create")
            return False
            
        except Exception as e:
            logger.error(f"Error iniciando generación: {e}")
            return False
    
    def wait_for_completion(self, timeout: int = 300):
        """Esperar completación de generación"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Verificar si hay resultados
                try:
                    # Buscar elementos de tracks generados
                    tracks = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='track'], .track, audio")
                    if tracks and len(tracks) > 0:
                        logger.info(f"Generación completada: {len(tracks)} tracks")
                        return self.extract_results()
                    
                    # Verificar si hay errores
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, [data-testid*='error']")
                    if error_elements:
                        logger.error("Error en generación detectado")
                        return None
                    
                except:
                    pass
                
                time.sleep(5)
            
            logger.error("Timeout esperando completación")
            return None
            
        except Exception as e:
            logger.error(f"Error esperando completación: {e}")
            return None
    
    def extract_results(self):
        """Extraer resultados de la generación"""
        try:
            results = []
            
            # Buscar tracks generados
            track_containers = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='track'], .track-container, .song-item")
            
            for i, container in enumerate(track_containers):
                try:
                    # Extraer título
                    title_elem = container.find_element(By.CSS_SELECTOR, "h1, h2, h3, .title, [data-testid*='title']")
                    title = title_elem.text if title_elem else f"Track {i+1}"
                    
                    # Extraer duración
                    duration_elem = container.find_element(By.CSS_SELECTOR, ".duration, [data-testid*='duration']")
                    duration = duration_elem.text if duration_elem else "Unknown"
                    
                    # Extraer URL de audio
                    audio_elem = container.find_element(By.CSS_SELECTOR, "audio, [src*='.mp3'], [src*='.wav']")
                    audio_url = audio_elem.get_attribute("src") if audio_elem else None
                    
                    # Extraer URL de descarga
                    download_elem = container.find_element(By.CSS_SELECTOR, "a[download], [data-testid*='download']")
                    download_url = download_elem.get_attribute("href") if download_elem else audio_url
                    
                    result = {
                        "id": f"track_{i+1}",
                        "title": title,
                        "duration": duration,
                        "url": audio_url,
                        "download_url": download_url,
                        "generated_at": int(time.time())
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Error extrayendo track {i+1}: {e}")
                    continue
            
            logger.info(f"Extraídos {len(results)} tracks")
            return results
            
        except Exception as e:
            logger.error(f"Error extrayendo resultados: {e}")
            return []
    
    def notify_captcha_event(self, job_id: str, status: str):
        """Notificar evento al backend"""
        try:
            event_data = {
                "job_id": job_id,
                "provider": "suno",
                "status": status,
                "timestamp": int(time.time())
            }
            
            response = requests.post(
                f"{self.api_url}/api/captcha/event",
                json=event_data,
                timeout=5
            )
            
            logger.info(f"Evento {status} notificado para job {job_id}")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error notificando evento: {e}")
            return False
    
    def generate_music(self, lyrics: str, prompt: str, job_id: str, instrumental: bool = False):
        """Proceso completo de generación de música"""
        try:
            logger.info(f"Iniciando generación para job {job_id}")
            
            # 1. Inicializar driver si no existe
            if not self.driver:
                if not self.initialize_driver():
                    return None
            
            # 2. Verificar/establecer sesión
            if not self.ensure_login():
                logger.error("No se pudo establecer sesión")
                return None
            
            # 3. Llenar formulario
            self.notify_captcha_event(job_id, "STARTED")
            
            if not self.fill_generation_form(lyrics, prompt, instrumental):
                logger.error("Error llenando formulario")
                return None
            
            # 4. Manejar CAPTCHAs
            if not self.handle_captcha(job_id):
                logger.error("Error con CAPTCHA")
                return None
            
            # 5. Iniciar generación
            if not self.start_generation():
                logger.error("Error iniciando generación")
                return None
            
            # 6. Esperar completación
            results = self.wait_for_completion()
            
            if results:
                self.notify_captcha_event(job_id, "COMPLETED")
                logger.info("Generación completada exitosamente")
            else:
                self.notify_captcha_event(job_id, "ERROR")
                logger.error("Generación falló")
            
            return results
            
        except Exception as e:
            logger.error(f"Error en generación completa: {e}")
            self.notify_captcha_event(job_id, "ERROR")
            return None
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None