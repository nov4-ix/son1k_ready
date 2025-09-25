#!/usr/bin/env python3
"""
Script simple para configurar la cookie de Suno
"""
import json
import time
import requests

def setup_suno_cookie():
    """Configurar cookie de Suno"""
    
    print("🍪 Configurando Cookie de Suno")
    print("=" * 30)
    print()
    print("Para que la música aparezca en tu biblioteca de Suno,")
    print("necesitamos configurar tu cookie de sesión.")
    print()
    print("📋 Pasos para obtener la cookie:")
    print("1. Ve a https://suno.com en tu navegador")
    print("2. Inicia sesión con tu cuenta")
    print("3. Abre las herramientas de desarrollador (F12)")
    print("4. Ve a Application > Storage > Cookies > https://suno.com")
    print("5. Busca 'session_token' o 'auth_token'")
    print("6. Copia el valor completo")
    print()
    
    # Solicitar cookie
    cookie = input("Pega aquí la cookie de Suno: ").strip()
    
    if not cookie:
        print("❌ No se proporcionó cookie")
        return False
    
    # Crear configuración
    config = {
        "accounts": [
            {
                "id": "account_1",
                "email": "nov4-ix@gmail.com",
                "cookie": cookie,
                "priority": 1,
                "max_daily_usage": 50,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            }
        ],
        "settings": {
            "rotation_interval": 300,
            "load_balancer": "weighted",
            "cooldown_time": 60,
            "max_concurrent": 3
        }
    }
    
    # Guardar configuración
    with open("suno_accounts.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Cookie guardada en suno_accounts.json")
    
    # Agregar cookie al wrapper
    print("🔄 Agregando cookie al wrapper...")
    
    try:
        response = requests.post(
            "http://localhost:3001/add-cookie",
            json={"cookie": cookie},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Cookie agregada al wrapper exitosamente")
            print()
            print("🎵 ¡Listo! Ahora la música aparecerá en tu biblioteca de Suno")
            print("   Prueba generando una canción desde:")
            print("   - http://localhost:3001 (interfaz stealth)")
            print("   - http://localhost:8000 (interfaz principal)")
            return True
        else:
            print(f"⚠️ Error agregando cookie al wrapper: {response.status_code}")
            print("   Asegúrate de que el wrapper esté ejecutándose")
            return False
            
    except Exception as e:
        print(f"⚠️ Error conectando con el wrapper: {e}")
        print("   Asegúrate de que el wrapper esté ejecutándose")
        return False

if __name__ == "__main__":
    setup_suno_cookie()




