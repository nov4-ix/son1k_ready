#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Configurador de Credenciales Suno
Script para obtener y configurar credenciales de Suno automáticamente
"""

import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SunoCredentialsExtractor:
    """Extractor de credenciales de Suno usando Selenium"""
    
    def __init__(self):
        self.driver = None
        self.credentials = {}
        
    def setup_driver(self):
        """Configurar driver de Chrome"""
        options = Options()
        
        # Configuración para evitar detección
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent realista
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Configuración de ventana
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Scripts anti-detección
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                delete navigator.__proto__.webdriver;
                window.chrome = {runtime: {}};
            """)
            
            logger.info("✅ Driver de Chrome configurado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando driver: {e}")
            return False
    
    def login_to_suno(self, email: str, password: str):
        """Iniciar sesión en Suno"""
        try:
            logger.info("🌐 Navegando a Suno.com...")
            self.driver.get("https://suno.com")
            
            # Esperar a que cargue la página
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Buscar botón de login
            login_selectors = [
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Login')]",
                "//a[contains(text(), 'Sign In')]",
                "//a[contains(text(), 'Login')]",
                "[data-testid='login-button']",
                ".login-button"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                logger.error("❌ No se encontró botón de login")
                return False
            
            logger.info("🔑 Haciendo clic en botón de login...")
            login_button.click()
            
            # Esperar formulario de login
            time.sleep(3)
            
            # Buscar campos de email y password
            email_selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email' i]"
            ]
            
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password' i]"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not email_field:
                logger.error("❌ No se encontró campo de email")
                return False
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.error("❌ No se encontró campo de password")
                return False
            
            # Ingresar credenciales
            logger.info("📝 Ingresando credenciales...")
            email_field.clear()
            email_field.send_keys(email)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Buscar botón de submit
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), 'Submit')]"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        submit_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not submit_button:
                logger.error("❌ No se encontró botón de submit")
                return False
            
            logger.info("🚀 Enviando formulario de login...")
            submit_button.click()
            
            # Esperar a que se complete el login
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            success_indicators = [
                "//button[contains(text(), 'Create')]",
                "[data-testid='user-menu']",
                ".user-avatar",
                "a[href*='/create']"
            ]
            
            for selector in success_indicators:
                try:
                    if selector.startswith("//"):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element:
                        logger.info("✅ Login exitoso")
                        return True
                except NoSuchElementException:
                    continue
            
            logger.warning("⚠️ No se pudo verificar el login, continuando...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return False
    
    def extract_credentials(self):
        """Extraer credenciales de la sesión actual"""
        try:
            logger.info("🔍 Extrayendo credenciales de la sesión...")
            
            # Obtener cookies
            cookies = self.driver.get_cookies()
            cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            
            # Obtener session ID de las cookies
            session_id = None
            for cookie in cookies:
                if 'session' in cookie['name'].lower() or 'sid' in cookie['name'].lower():
                    session_id = cookie['value']
                    break
            
            if not session_id:
                # Generar un session ID basado en la URL actual
                session_id = self.driver.current_url.split('/')[-1] or "default_session"
            
            # Obtener token si está disponible
            token = None
            try:
                # Buscar token en localStorage
                token = self.driver.execute_script("return localStorage.getItem('token') || localStorage.getItem('auth_token') || localStorage.getItem('access_token');")
            except:
                pass
            
            self.credentials = {
                "session_id": session_id,
                "cookie": cookie_string,
                "token": token,
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info("✅ Credenciales extraídas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo credenciales: {e}")
            return False
    
    def save_credentials(self, filename: str = "suno_credentials.json"):
        """Guardar credenciales en archivo"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.credentials, f, indent=2)
            
            logger.info(f"✅ Credenciales guardadas en {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando credenciales: {e}")
            return False
    
    def close(self):
        """Cerrar driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Función principal"""
    print("🎵 SON1KVERS3 - Configurador de Credenciales Suno")
    print("=" * 50)
    
    # Solicitar credenciales
    email = input("📧 Email de Suno: ").strip()
    password = input("🔑 Password de Suno: ").strip()
    
    if not email or not password:
        print("❌ Email y password son requeridos")
        return
    
    extractor = SunoCredentialsExtractor()
    
    try:
        # Configurar driver
        if not extractor.setup_driver():
            print("❌ Error configurando driver de Chrome")
            return
        
        # Login
        if not extractor.login_to_suno(email, password):
            print("❌ Error en login")
            return
        
        # Extraer credenciales
        if not extractor.extract_credentials():
            print("❌ Error extrayendo credenciales")
            return
        
        # Guardar credenciales
        if not extractor.save_credentials():
            print("❌ Error guardando credenciales")
            return
        
        print("\n✅ ¡Credenciales configuradas exitosamente!")
        print(f"📁 Archivo: suno_credentials.json")
        print(f"🔑 Session ID: {extractor.credentials['session_id'][:20]}...")
        print(f"🍪 Cookie: {extractor.credentials['cookie'][:50]}...")
        
        print("\n🚀 Próximos pasos:")
        print("1. Ejecuta: python son1k_optimized_system.py")
        print("2. El sistema cargará automáticamente las credenciales")
        print("3. ¡Disfruta de la generación musical real con Suno!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
