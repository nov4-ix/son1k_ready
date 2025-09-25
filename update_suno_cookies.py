#!/usr/bin/env python3
"""
🍪 Script para actualizar cookies de Suno
Obtiene cookies frescas y válidas de Suno.com
"""

import json
import time
import requests
from datetime import datetime

def update_suno_cookies():
    """Actualizar cookies de Suno en el archivo de configuración"""
    
    print("🍪 Actualizando cookies de Suno...")
    print("=" * 50)
    
    # Leer configuración actual
    try:
        with open('suno_accounts_stealth.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Archivo suno_accounts_stealth.json no encontrado")
        return False
    
    print("📋 Instrucciones para obtener cookies frescas:")
    print("1. Abre tu navegador y ve a https://suno.com")
    print("2. Inicia sesión con tu cuenta")
    print("3. Abre las herramientas de desarrollador (F12)")
    print("4. Ve a la pestaña 'Application' o 'Aplicación'")
    print("5. En el panel izquierdo, busca 'Cookies' > 'https://suno.com'")
    print("6. Copia TODAS las cookies (especialmente __session)")
    print("7. Pégalas aquí cuando estés listo")
    print()
    
    # Solicitar cookies frescas
    print("🔑 Pega las cookies frescas aquí (presiona Enter cuando termines):")
    print("(Formato: cookie1=valor1; cookie2=valor2; ...)")
    print()
    
    new_cookies = input("🍪 Cookies: ").strip()
    
    if not new_cookies:
        print("❌ No se proporcionaron cookies")
        return False
    
    # Validar que las cookies contengan elementos importantes
    required_cookies = ['__session', 'clerk_active_context']
    missing_cookies = []
    
    for required in required_cookies:
        if required not in new_cookies:
            missing_cookies.append(required)
    
    if missing_cookies:
        print(f"⚠️ Advertencia: Faltan cookies importantes: {', '.join(missing_cookies)}")
        print("Esto puede causar problemas de autenticación")
        
        continue_anyway = input("¿Continuar de todos modos? (y/N): ").lower()
        if continue_anyway != 'y':
            return False
    
    # Actualizar la configuración
    if config['accounts']:
        # Actualizar la primera cuenta
        config['accounts'][0]['cookie'] = new_cookies
        config['accounts'][0]['last_used'] = 0
        config['accounts'][0]['success_count'] = 0
        config['accounts'][0]['failure_count'] = 0
        config['accounts'][0]['status'] = 'active'
        
        print(f"✅ Cookies actualizadas para cuenta: {config['accounts'][0]['email']}")
    else:
        print("❌ No hay cuentas configuradas")
        return False
    
    # Guardar configuración actualizada
    try:
        with open('suno_accounts_stealth.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Configuración guardada exitosamente")
        
        # Mostrar resumen
        print("\n📊 Resumen de la actualización:")
        print(f"   Cuenta: {config['accounts'][0]['email']}")
        print(f"   Cookies: {len(new_cookies)} caracteres")
        print(f"   Estado: {config['accounts'][0]['status']}")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False

def test_cookies():
    """Probar las cookies actualizadas"""
    print("\n🧪 Probando cookies actualizadas...")
    
    try:
        with open('suno_accounts_stealth.json', 'r') as f:
            config = json.load(f)
        
        if not config['accounts']:
            print("❌ No hay cuentas configuradas")
            return False
        
        cookie = config['accounts'][0]['cookie']
        
        # Hacer una petición de prueba a Suno
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Cookie': cookie,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://suno.com/',
            'Origin': 'https://suno.com'
        }
        
        print("🔍 Probando conexión con Suno...")
        response = requests.get('https://suno.com/api/v1/songs', headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Cookies válidas - Conexión exitosa con Suno")
            return True
        elif response.status_code == 401:
            print("❌ Cookies inválidas - Error de autenticación")
            return False
        elif response.status_code == 403:
            print("❌ Cookies bloqueadas - Acceso denegado")
            return False
        else:
            print(f"⚠️ Respuesta inesperada: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Verificar conexión a internet")
        return False
    except Exception as e:
        print(f"❌ Error probando cookies: {e}")
        return False

def main():
    """Función principal"""
    print("🍪 Actualizador de Cookies Suno")
    print("=" * 40)
    
    # Actualizar cookies
    if update_suno_cookies():
        print("\n🔄 Reiniciando wrapper stealth...")
        print("Ejecuta: pkill -f suno_stealth_wrapper.js && node suno_stealth_wrapper.js &")
        
        # Probar cookies
        if test_cookies():
            print("\n🎉 ¡Cookies actualizadas y funcionando!")
            print("El sistema debería funcionar correctamente ahora")
        else:
            print("\n⚠️ Las cookies pueden no ser válidas")
            print("Verifica que hayas copiado todas las cookies correctamente")
    else:
        print("\n❌ No se pudieron actualizar las cookies")

if __name__ == "__main__":
    main()



