#!/usr/bin/env python3
"""
🌐 OLLAMA BROWSER CONTROLLER - Control Directo del Navegador
Ollama controla directamente el navegador para usar Suno como usuario normal
"""

import asyncio
import logging
import time
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

logger = logging.getLogger(__name__)

class OllamaBrowserController:
    """Controlador de navegador controlado por Ollama"""
    
    def __init__(self):
        self.driver = None
        self.ollama_url = "http://localhost:11434"
        self.suno_url = "https://suno.com"
        self.audio_dir = Path("generated_audio")
        self.audio_dir.mkdir(exist_ok=True)
        self.session_active = False
        
    async def initialize_browser(self) -> bool:
        """Inicializar navegador con configuración anti-detección"""
        try:
            options = Options()
            
            # Configuración anti-detección
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent realista
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Configuración de ventana
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            
            # Configurar descarga de archivos
            prefs = {
                "download.default_directory": str(self.audio_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=options)
            
            # Scripts anti-detección
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                delete navigator.__proto__.webdriver;
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)
            
            logger.info("✅ Navegador inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando navegador: {e}")
            return False
    
    async def login_to_suno(self) -> bool:
        """Iniciar sesión en Suno usando credenciales guardadas"""
        try:
            logger.info("🔐 Iniciando sesión en Suno...")
            
            # Verificar si existe el archivo de credenciales
            if not os.path.exists('suno_credentials.json'):
                logger.warning("⚠️ No se encontró suno_credentials.json, usando modo manual")
                return await self.manual_login()
            
            # Cargar credenciales
            with open('suno_credentials.json', 'r') as f:
                creds = json.load(f)
            
            # Ir a Suno
            self.driver.get(self.suno_url)
            await asyncio.sleep(3)
            
            # Intentar cargar cookies guardadas si existen
            cookies_data = creds.get('cookie', '[]')
            if cookies_data and cookies_data != '[]':
                try:
                    cookies = json.loads(cookies_data)
                    for cookie in cookies:
                        try:
                            self.driver.add_cookie(cookie)
                        except Exception as cookie_error:
                            logger.debug(f"Cookie no válida: {cookie_error}")
                    
                    # Recargar página para aplicar cookies
                    self.driver.refresh()
                    await asyncio.sleep(3)
                except json.JSONDecodeError:
                    logger.warning("⚠️ Cookies mal formateadas, continuando sin ellas")
            
            # Verificar si ya estamos logueados
            try:
                # Buscar indicadores de que estamos logueados
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='create-button']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Create']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/create']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button:contains('Create')"))
                    )
                )
                self.session_active = True
                logger.info("✅ Sesión activa en Suno")
                return True
            except TimeoutException:
                logger.warning("⚠️ No se pudo verificar sesión automáticamente")
                return await self.manual_login()
                
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return await self.manual_login()
    
    async def manual_login(self) -> bool:
        """Modo manual de login - el usuario debe hacer login manualmente"""
        try:
            logger.info("👤 Modo manual: Por favor inicia sesión en Suno manualmente")
            logger.info("🔗 El navegador está abierto en: https://suno.com")
            logger.info("⏳ Esperando 30 segundos para que completes el login...")
            
            # Esperar a que el usuario haga login manualmente
            await asyncio.sleep(30)
            
            # Verificar si ahora estamos logueados
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='create-button']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Create']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/create']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button:contains('Create')"))
                    )
                )
                self.session_active = True
                logger.info("✅ Login manual exitoso")
                return True
            except TimeoutException:
                logger.warning("⚠️ No se detectó login manual, continuando sin autenticación")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en login manual: {e}")
            return False
    
    async def generate_music_with_ollama(self, prompt: str, lyrics: str = "", style: str = "synthwave") -> Dict[str, Any]:
        """Generar música usando Ollama para controlar el navegador"""
        try:
            logger.info(f"🎵 Generando música: {prompt}")
            
            # 1. Usar Ollama para optimizar el prompt
            optimized_prompt = await self._optimize_prompt_with_ollama(prompt, lyrics, style)
            logger.info(f"📝 Prompt optimizado: {optimized_prompt}")
            
            # 2. Navegar a la página de creación
            await self._navigate_to_create_page()
            
            # 3. Usar Ollama para llenar el formulario
            await self._fill_form_with_ollama(optimized_prompt, lyrics, style)
            
            # 4. Iniciar generación
            await self._start_generation()
            
            # 5. Monitorear progreso
            result = await self._monitor_generation()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en generación: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error en generación con navegador"
            }
    
    async def _optimize_prompt_with_ollama(self, prompt: str, lyrics: str, style: str) -> str:
        """Usar Ollama para optimizar el prompt"""
        try:
            # Verificar si Ollama está disponible
            if not await self._check_ollama_availability():
                logger.warning("⚠️ Ollama no disponible, usando prompt original")
                return prompt
            
            system_prompt = f"""Eres un experto en generación musical para Suno AI. 
Crea un prompt natural, descriptivo y efectivo en INGLÉS para generar música:

Prompt original: {prompt}
Letras: {lyrics}
Estilo: {style}

Reglas:
- Usa máximo 200 caracteres
- Incluye género musical específico
- Menciona instrumentos si es relevante
- Usa lenguaje natural y descriptivo
- NO incluyas letras en el prompt (solo descripción musical)

Responde SOLO con el prompt optimizado, sin explicaciones adicionales."""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.1:latest",
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 100
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized = result.get("response", prompt).strip()
                # Limpiar respuesta de Ollama
                optimized = optimized.replace('"', '').replace("'", "").strip()
                if len(optimized) > 200:
                    optimized = optimized[:200]
                logger.info(f"🤖 Ollama optimizó: '{prompt}' -> '{optimized}'")
                return optimized
            else:
                logger.warning(f"⚠️ Ollama error {response.status_code}: {response.text}")
                return prompt
                
        except Exception as e:
            logger.warning(f"⚠️ Error optimizando prompt: {e}")
            return prompt
    
    async def _check_ollama_availability(self) -> bool:
        """Verificar si Ollama está disponible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def _navigate_to_create_page(self):
        """Navegar a la página de creación de Suno"""
        try:
            logger.info("🎯 Navegando a página de creación...")
            
            # Ir a la página de creación
            self.driver.get(f"{self.suno_url}/create")
            await asyncio.sleep(3)
            
            # Esperar a que cargue la página
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("✅ Página de creación cargada")
            
        except Exception as e:
            logger.error(f"❌ Error navegando a creación: {e}")
            raise
    
    async def _fill_form_with_ollama(self, prompt: str, lyrics: str, style: str):
        """Usar Ollama para llenar el formulario de Suno"""
        try:
            logger.info("📝 Llenando formulario con Ollama...")
            
            # Usar Ollama para analizar la página y encontrar campos
            page_analysis = await self._analyze_page_with_ollama()
            
            # Buscar campo de prompt/descripción
            prompt_selectors = [
                "textarea[placeholder*='description']",
                "textarea[placeholder*='prompt']",
                "input[placeholder*='description']",
                "textarea[placeholder*='song']",
                "textarea[placeholder*='music']",
                "textarea",
                "input[type='text']"
            ]
            
            prompt_field = None
            for selector in prompt_selectors:
                try:
                    prompt_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if prompt_field:
                # Limpiar y escribir prompt
                prompt_field.clear()
                await self._type_like_human(prompt_field, prompt)
                logger.info("✅ Prompt ingresado")
                
                # Usar Ollama para verificar que el prompt se ingresó correctamente
                await self._verify_input_with_ollama(prompt_field, prompt)
            else:
                logger.warning("⚠️ No se encontró campo de prompt")
            
            # Buscar campo de letras si existe
            if lyrics:
                lyrics_selectors = [
                    "textarea[placeholder*='lyrics']",
                    "textarea[placeholder*='lyric']",
                    "textarea[placeholder*='song']",
                    "textarea[placeholder*='text']"
                ]
                
                for selector in lyrics_selectors:
                    try:
                        lyrics_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        lyrics_field.clear()
                        await self._type_like_human(lyrics_field, lyrics)
                        logger.info("✅ Letras ingresadas")
                        break
                    except NoSuchElementException:
                        continue
            
            # Usar Ollama para seleccionar estilo si hay opciones
            await self._select_style_with_ollama(style)
            
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Error llenando formulario: {e}")
            raise
    
    async def _analyze_page_with_ollama(self) -> Dict[str, Any]:
        """Usar Ollama para analizar la página y encontrar elementos"""
        try:
            if not await self._check_ollama_availability():
                return {}
            
            # Obtener HTML de la página
            page_source = self.driver.page_source[:2000]  # Primeros 2000 caracteres
            
            system_prompt = f"""Analiza este HTML de Suno y encuentra los campos de formulario:

HTML: {page_source}

Responde en JSON con:
- prompt_field: selector CSS del campo de descripción
- lyrics_field: selector CSS del campo de letras (si existe)
- style_options: array de opciones de estilo disponibles
- create_button: selector CSS del botón de crear

Responde SOLO con el JSON, sin explicaciones."""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.1:latest",
                    "prompt": system_prompt,
                    "stream": False
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                try:
                    return json.loads(result.get("response", "{}"))
                except:
                    return {}
            return {}
            
        except Exception as e:
            logger.warning(f"⚠️ Error analizando página: {e}")
            return {}
    
    async def _verify_input_with_ollama(self, field, expected_text: str):
        """Usar Ollama para verificar que el input se ingresó correctamente"""
        try:
            if not await self._check_ollama_availability():
                return
            
            current_value = field.get_attribute("value")
            if current_value != expected_text:
                logger.warning(f"⚠️ Input no coincide: '{current_value}' vs '{expected_text}'")
                # Reintentar
                field.clear()
                await self._type_like_human(field, expected_text)
            
        except Exception as e:
            logger.warning(f"⚠️ Error verificando input: {e}")
    
    async def _select_style_with_ollama(self, style: str):
        """Usar Ollama para seleccionar estilo musical"""
        try:
            if not await self._check_ollama_availability():
                return
            
            # Buscar opciones de estilo
            style_selectors = [
                "select[name*='style']",
                "select[name*='genre']",
                "div[class*='style']",
                "button[class*='style']"
            ]
            
            for selector in style_selectors:
                try:
                    style_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if style_element.tag_name == "select":
                        # Es un dropdown
                        from selenium.webdriver.support.ui import Select
                        select = Select(style_element)
                        options = [opt.text for opt in select.options]
                        
                        # Usar Ollama para encontrar la mejor opción
                        best_option = await self._find_best_style_option_with_ollama(style, options)
                        if best_option:
                            select.select_by_visible_text(best_option)
                            logger.info(f"✅ Estilo seleccionado: {best_option}")
                    break
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Error seleccionando estilo: {e}")
    
    async def _find_best_style_option_with_ollama(self, requested_style: str, available_options: List[str]) -> str:
        """Usar Ollama para encontrar la mejor opción de estilo"""
        try:
            system_prompt = f"""Encuentra la mejor opción de estilo musical:

Estilo solicitado: {requested_style}
Opciones disponibles: {', '.join(available_options)}

Responde SOLO con la opción más cercana, sin explicaciones."""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.1:latest",
                    "prompt": system_prompt,
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                best_option = result.get("response", "").strip()
                if best_option in available_options:
                    return best_option
                else:
                    # Buscar coincidencia parcial
                    for option in available_options:
                        if best_option.lower() in option.lower() or option.lower() in best_option.lower():
                            return option
                    return available_options[0] if available_options else ""
            return ""
            
        except Exception as e:
            logger.warning(f"⚠️ Error encontrando estilo: {e}")
            return available_options[0] if available_options else ""
    
    async def _type_like_human(self, element, text: str):
        """Escribir texto de forma humana"""
        for char in text:
            element.send_keys(char)
            await asyncio.sleep(0.05)  # Pausa entre caracteres
    
    async def _start_generation(self):
        """Iniciar la generación de música"""
        try:
            logger.info("🚀 Iniciando generación...")
            
            # Buscar botón de crear/generar
            create_selectors = [
                "button[data-testid='create-button']",
                "button[aria-label='Create']",
                "button:contains('Create')",
                "button:contains('Generate')",
                "button[type='submit']",
                "button.btn-primary",
                "button[class*='create']"
            ]
            
            create_button = None
            for selector in create_selectors:
                try:
                    create_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if create_button:
                create_button.click()
                logger.info("✅ Generación iniciada")
            else:
                raise Exception("No se encontró botón de crear")
                
        except Exception as e:
            logger.error(f"❌ Error iniciando generación: {e}")
            raise
    
    async def _monitor_generation(self) -> Dict[str, Any]:
        """Monitorear el progreso de generación"""
        try:
            logger.info("⏳ Monitoreando generación...")
            
            # Esperar a que aparezca el progreso
            await asyncio.sleep(5)
            
            # Monitorear por hasta 5 minutos
            for i in range(60):  # 60 * 5 segundos = 5 minutos
                try:
                    # Buscar indicadores de progreso
                    progress_indicators = [
                        "div[class*='progress']",
                        "div[class*='loading']",
                        "div[class*='generating']",
                        "span:contains('Generating')",
                        "div:contains('Creating')"
                    ]
                    
                    progress_found = False
                    for selector in progress_indicators:
                        try:
                            self.driver.find_element(By.CSS_SELECTOR, selector)
                            progress_found = True
                            break
                        except NoSuchElementException:
                            continue
                    
                    if not progress_found:
                        # Buscar audio generado
                        audio_elements = self.driver.find_elements(By.CSS_SELECTOR, "audio, [class*='audio'], [class*='player']")
                        if audio_elements:
                            logger.info("✅ Audio generado encontrado")
                            break
                    
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error monitoreando: {e}")
                    await asyncio.sleep(5)
            
            # Buscar archivo de audio descargado
            audio_file = await self._find_downloaded_audio()
            
            if audio_file:
                return {
                    "success": True,
                    "filename": audio_file.name,
                    "file_path": str(audio_file),
                    "audio_url": f"/api/tracks/{audio_file.stem}/audio",
                    "message": "Música generada exitosamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo encontrar el archivo de audio generado"
                }
                
        except Exception as e:
            logger.error(f"❌ Error monitoreando generación: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error monitoreando generación"
            }
    
    async def _find_downloaded_audio(self) -> Optional[Path]:
        """Buscar archivo de audio descargado"""
        try:
            # Buscar archivos de audio recientes
            audio_files = list(self.audio_dir.glob("*.mp3")) + list(self.audio_dir.glob("*.wav"))
            
            if audio_files:
                # Devolver el más reciente
                latest_file = max(audio_files, key=lambda x: x.stat().st_mtime)
                
                # Verificar que sea reciente (últimos 10 minutos)
                if time.time() - latest_file.stat().st_mtime < 600:
                    return latest_file
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error buscando audio: {e}")
            return None
    
    def cleanup(self):
        """Limpiar recursos"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Navegador cerrado")
        except Exception as e:
            logger.error(f"❌ Error cerrando navegador: {e}")

# Instancia global
browser_controller = OllamaBrowserController()

async def generate_music_with_browser(prompt: str, lyrics: str = "", style: str = "synthwave") -> Dict[str, Any]:
    """Función de conveniencia para generar música con navegador"""
    try:
        # Inicializar navegador si no está activo
        if not browser_controller.driver:
            if not await browser_controller.initialize_browser():
                return {"success": False, "error": "No se pudo inicializar navegador"}
        
        # Iniciar sesión si no está activa
        if not browser_controller.session_active:
            if not await browser_controller.login_to_suno():
                return {"success": False, "error": "No se pudo iniciar sesión en Suno"}
        
        # Generar música
        return await browser_controller.generate_music_with_ollama(prompt, lyrics, style)
        
    except Exception as e:
        logger.error(f"❌ Error en generación con navegador: {e}")
        return {"success": False, "error": str(e)}
