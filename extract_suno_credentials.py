#!/usr/bin/env python3
"""
Script para extraer credenciales válidas de Suno desde navegador
Ejecutar: python3 extract_suno_credentials.py
"""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

def get_chrome_cookies():
    """Extraer cookies de Chrome en macOS"""
    try:
        # Ruta de cookies de Chrome en macOS
        chrome_cookie_path = Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
        
        if not chrome_cookie_path.exists():
            print("❌ Chrome cookies no encontradas")
            return None
        
        # Crear copia temporal (Chrome puede bloquear acceso directo)
        temp_cookie_path = "/tmp/chrome_cookies_temp.db"
        subprocess.run(["cp", str(chrome_cookie_path), temp_cookie_path], check=True)
        
        # Conectar a SQLite
        conn = sqlite3.connect(temp_cookie_path)
        cursor = conn.cursor()
        
        # Buscar cookies de suno.com
        cursor.execute("""
            SELECT name, value, host_key 
            FROM cookies 
            WHERE host_key LIKE '%suno%' OR host_key LIKE '%.suno.%'
            ORDER BY creation_utc DESC
        """)
        
        cookies = cursor.fetchall()
        conn.close()
        
        # Limpiar archivo temporal
        os.remove(temp_cookie_path)
        
        return cookies
        
    except Exception as e:
        print(f"❌ Error extrayendo cookies de Chrome: {e}")
        return None

def get_safari_cookies():
    """Extraer cookies de Safari en macOS"""
    try:
        safari_cookie_path = Path.home() / "Library/Cookies/Cookies.binarycookies"
        
        if not safari_cookie_path.exists():
            print("❌ Safari cookies no encontradas")
            return None
        
        print("⚠️  Safari usa formato binario complejo, usa Chrome para extraer cookies")
        return None
        
    except Exception as e:
        print(f"❌ Error con Safari: {e}")
        return None

def extract_session_from_cookies(cookies):
    """Extraer session_id y otros datos importantes"""
    session_data = {}
    cookie_string = ""
    
    for name, value, host in cookies:
        cookie_string += f"{name}={value}; "
        
        # Buscar session_id específico
        if name.startswith("__session") or "sess_" in value:
            session_data["session_id"] = value
        
        # Clerk session (común en Suno)
        if "sess_" in name and name.startswith("__client"):
            session_data["clerk_session"] = value
    
    session_data["full_cookie"] = cookie_string.rstrip("; ")
    return session_data

def manual_input():
    """Input manual si no se pueden extraer automáticamente"""
    print("\n🔧 EXTRACCIÓN MANUAL DE CREDENCIALES")
    print("=" * 50)
    print("1. Ve a https://suno.com y loguéate")
    print("2. Abre DevTools (F12) → Network tab")
    print("3. Busca cualquier request a studio-api.suno.ai")
    print("4. En Request Headers, copia el valor de 'Cookie:'")
    print("5. Busca también cualquier session que empiece con 'sess_'")
    print("")
    
    cookie = input("📋 Pega aquí la cookie completa: ").strip()
    session = input("🔑 Pega aquí el session_id (sess_xxxx): ").strip()
    
    if not session.startswith("sess_"):
        # Intentar extraer session de la cookie
        if "sess_" in cookie:
            import re
            session_match = re.search(r'sess_[A-Za-z0-9]+', cookie)
            if session_match:
                session = session_match.group()
                print(f"✅ Session extraído automáticamente: {session}")
    
    return {
        "session_id": session,
        "full_cookie": cookie
    }

def validate_credentials(session_id, cookie):
    """Validar credenciales haciendo request a Suno API"""
    try:
        import requests
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Cookie": cookie,
            "Referer": "https://suno.com/",
        }
        
        # Test endpoint simple
        response = requests.get("https://studio-api.suno.ai/api/billing/info/", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Credenciales VÁLIDAS")
            return True
        elif response.status_code == 401:
            print("❌ Credenciales INVÁLIDAS (no autenticado)")
            return False
        elif response.status_code == 403:
            print("⚠️  Credenciales posiblemente SUSPENDIDAS")
            return False
        else:
            print(f"⚠️  Status incierto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error validando: {e}")
        return False

def save_credentials(session_id, cookie):
    """Guardar credenciales en archivos"""
    try:
        # Guardar en .env local
        env_content = f"""
# Suno Credentials - Extracted {__import__('datetime').datetime.now()}
export SUNO_SESSION_ID="{session_id}"
export SUNO_COOKIE="{cookie}"
"""
        
        with open("suno_credentials.env", "w") as f:
            f.write(env_content)
        
        # Guardar en formato Python
        py_content = f'''
# Suno Credentials - Para main_production.py
SUNO_SESSION_ID = "{session_id}"
SUNO_COOKIE = """{cookie}"""
'''
        
        with open("suno_credentials.py", "w") as f:
            f.write(py_content)
        
        print("✅ Credenciales guardadas en:")
        print("  - suno_credentials.env")
        print("  - suno_credentials.py")
        
    except Exception as e:
        print(f"❌ Error guardando: {e}")

def main():
    print("🎵 EXTRACTOR DE CREDENCIALES SUNO")
    print("=" * 40)
    
    # Intentar extraer automáticamente
    print("🔍 Buscando cookies en navegadores...")
    
    cookies = get_chrome_cookies()
    if not cookies:
        cookies = get_safari_cookies()
    
    if cookies:
        print(f"✅ Encontradas {len(cookies)} cookies de Suno")
        session_data = extract_session_from_cookies(cookies)
        
        if session_data.get("session_id"):
            print(f"🔑 Session ID: {session_data['session_id'][:20]}...")
            
            # Validar
            is_valid = validate_credentials(session_data["session_id"], 
                                          session_data["full_cookie"])
            
            if is_valid:
                save_credentials(session_data["session_id"], 
                               session_data["full_cookie"])
                print("\n✅ CREDENCIALES EXTRAÍDAS Y VALIDADAS")
                return
    
    # Si no funciona automático, input manual
    print("\n⚠️  Extracción automática falló, procediendo manualmente...")
    manual_data = manual_input()
    
    if manual_data["session_id"] and manual_data["full_cookie"]:
        is_valid = validate_credentials(manual_data["session_id"], 
                                      manual_data["full_cookie"])
        
        if is_valid:
            save_credentials(manual_data["session_id"], 
                           manual_data["full_cookie"])
            print("\n✅ CREDENCIALES MANUALES VALIDADAS")
        else:
            print("\n❌ Las credenciales manuales no son válidas")
    else:
        print("\n❌ No se proporcionaron credenciales válidas")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")