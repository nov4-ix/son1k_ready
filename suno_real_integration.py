#!/usr/bin/env python3
"""
🎵 SUNO REAL INTEGRATION - Integración Directa con Suno.com
Genera música real que aparece en tu biblioteca de Suno
"""

import asyncio
import logging
import time
import json
import os
import requests
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import uuid

logger = logging.getLogger(__name__)

class SunoRealIntegration:
    """Integración real con Suno.com para generar música que aparezca en tu biblioteca"""
    
    def __init__(self):
        self.driver = None
        self.suno_url = "https://suno.com"
        self.session_active = False
        self.credentials = self.load_credentials()
        
    def load_credentials(self) -> Dict[str, Any]:
        """Cargar credenciales de Suno"""
        try:
            if os.path.exists('suno_credentials.json'):
                with open('suno_credentials.json', 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error cargando credenciales: {e}")
            return {}
    
    async def initialize_browser(self) -> bool:
        """Inicializar navegador para Suno"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Navegador inicializado para Suno")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando navegador: {e}")
            return False
    
    async def login_to_suno(self) -> bool:
        """Iniciar sesión en Suno.com"""
        try:
            logger.info("🔐 Iniciando sesión en Suno...")
            
            if not self.credentials.get('email') or not self.credentials.get('password'):
                logger.warning("⚠️ Credenciales no configuradas")
                return await self.manual_login()
            
            # Ir a Suno
            self.driver.get(self.suno_url)
            await asyncio.sleep(3)
            
            # Buscar botón de login
            try:
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in') or contains(text(), 'Sign in')]"))
                )
                login_button.click()
                await asyncio.sleep(2)
            except TimeoutException:
                logger.warning("⚠️ No se encontró botón de login, continuando...")
            
            # Llenar email
            try:
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                email_field.clear()
                email_field.send_keys(self.credentials['email'])
                await asyncio.sleep(1)
            except TimeoutException:
                logger.warning("⚠️ No se encontró campo de email")
            
            # Llenar password
            try:
                password_field = self.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(self.credentials['password'])
                await asyncio.sleep(1)
            except NoSuchElementException:
                logger.warning("⚠️ No se encontró campo de password")
            
            # Hacer clic en submit
            try:
                submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
                await asyncio.sleep(5)
            except NoSuchElementException:
                logger.warning("⚠️ No se encontró botón de submit")
            
            # Verificar si el login fue exitoso
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Create')]")),
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/create')]")),
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Create')]"))
                    )
                )
                self.session_active = True
                logger.info("✅ Login exitoso en Suno")
                return True
            except TimeoutException:
                logger.warning("⚠️ No se pudo verificar login automático")
                return await self.manual_login()
                
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return await self.manual_login()
    
    async def manual_login(self) -> bool:
        """Login manual - el usuario debe hacer login manualmente"""
        try:
            logger.info("👤 Modo manual: Por favor inicia sesión en Suno manualmente")
            logger.info("🔗 El navegador está abierto en: https://suno.com")
            logger.info("⏳ Esperando 60 segundos para que completes el login...")
            
            # Esperar a que el usuario haga login
            await asyncio.sleep(60)
            
            # Verificar si ahora estamos logueados
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Create')]")),
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/create')]")),
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Create')]"))
                    )
                )
                self.session_active = True
                logger.info("✅ Login manual exitoso")
                return True
            except TimeoutException:
                logger.warning("⚠️ No se detectó login manual")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error en login manual: {e}")
            return False
    
    async def generate_music_in_suno(self, prompt: str, lyrics: str = "", style: str = "pop") -> Dict[str, Any]:
        """Generar música real en Suno.com"""
        try:
            logger.info(f"🎵 Generando música en Suno: {prompt}")
            
            # Ir a la página de creación
            self.driver.get(f"{self.suno_url}/create")
            await asyncio.sleep(3)
            
            # Buscar campo de descripción
            try:
                description_field = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//textarea[contains(@placeholder, 'description') or contains(@placeholder, 'prompt')]"))
                )
                description_field.clear()
                description_field.send_keys(prompt)
                logger.info("✅ Descripción ingresada")
            except TimeoutException:
                logger.warning("⚠️ No se encontró campo de descripción")
            
            # Buscar campo de letras si existe
            if lyrics:
                try:
                    lyrics_field = self.driver.find_element(By.XPATH, "//textarea[contains(@placeholder, 'lyrics') or contains(@placeholder, 'lyric')]")
                    lyrics_field.clear()
                    lyrics_field.send_keys(lyrics)
                    logger.info("✅ Letras ingresadas")
                except NoSuchElementException:
                    logger.warning("⚠️ No se encontró campo de letras")
            
            # Hacer clic en crear
            try:
                create_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Generate')]"))
                )
                create_button.click()
                logger.info("✅ Generación iniciada en Suno")
            except TimeoutException:
                logger.warning("⚠️ No se encontró botón de crear")
            
            # Monitorear progreso
            await asyncio.sleep(10)  # Esperar a que inicie
            
            # Buscar el resultado
            try:
                # Buscar enlaces de audio o elementos de resultado
                audio_elements = WebDriverWait(self.driver, 300).until(  # 5 minutos máximo
                    EC.any_of(
                        EC.presence_of_element_located((By.TAG_NAME, "audio")),
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.mp3') or contains(@href, '.wav')]")),
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'audio') or contains(@class, 'player')]"))
                    )
                )
                
                # Obtener URL del audio
                audio_url = None
                if audio_elements.tag_name == "audio":
                    audio_url = audio_elements.get_attribute("src")
                elif audio_elements.tag_name == "a":
                    audio_url = audio_elements.get_attribute("href")
                
                if audio_url:
                    logger.info(f"✅ Música generada en Suno: {audio_url}")
                    return {
                        "success": True,
                        "audio_url": audio_url,
                        "suno_url": self.driver.current_url,
                        "message": "Música generada exitosamente en Suno.com"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Música generada pero no se pudo obtener URL del audio"
                    }
                    
            except TimeoutException:
                logger.warning("⚠️ Timeout esperando resultado de Suno")
                return {
                    "success": False,
                    "message": "Timeout esperando resultado de Suno"
                }
                
        except Exception as e:
            logger.error(f"❌ Error generando música en Suno: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error generando música en Suno"
            }
    
    def cleanup(self):
        """Limpiar recursos"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Navegador cerrado")
        except Exception as e:
            logger.error(f"❌ Error cerrando navegador: {e}")

# Instancia global
suno_real = SunoRealIntegration()

async def generate_music_in_suno_real(prompt: str, lyrics: str = "", style: str = "pop") -> Dict[str, Any]:
    """Función de conveniencia para generar música real en Suno"""
    try:
        # Inicializar navegador si no está activo
        if not suno_real.driver:
            if not await suno_real.initialize_browser():
                return {"success": False, "error": "No se pudo inicializar navegador"}
        
        # Iniciar sesión si no está activa
        if not suno_real.session_active:
            if not await suno_real.login_to_suno():
                return {"success": False, "error": "No se pudo iniciar sesión en Suno"}
        
        # Generar música
        return await suno_real.generate_music_in_suno(prompt, lyrics, style)
        
    except Exception as e:
        logger.error(f"❌ Error en generación real: {e}")
        return {"success": False, "error": str(e)}