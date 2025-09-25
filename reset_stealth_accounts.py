#!/usr/bin/env python3
"""
🔄 Reset Stealth Accounts
Resetea el estado de las cuentas para eliminar cooldowns
"""

import json
import time
from datetime import datetime

def reset_accounts():
    """Resetear estado de cuentas"""
    try:
        # Leer configuración actual
        with open('suno_accounts_stealth.json', 'r') as f:
            config = json.load(f)
        
        print("🔄 Reseteando cuentas stealth...")
        
        # Resetear estado de todas las cuentas
        for account in config['accounts']:
            account['last_used'] = 0
            account['success_count'] = 0
            account['failure_count'] = 0
            account['status'] = 'active'
            account['cooldown_until'] = 0
            
            print(f"✅ Cuenta reseteada: {account['email']}")
        
        # Guardar configuración actualizada
        with open('suno_accounts_stealth.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Configuración guardada")
        print("🔄 Reiniciando wrapper ultra-stealth...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reseteando cuentas: {e}")
        return False

def main():
    """Función principal"""
    print("🔄 Reset Stealth Accounts")
    print("=" * 30)
    
    if reset_accounts():
        print("\n🎉 ¡Cuentas reseteadas exitosamente!")
        print("🔒 Las cuentas están ahora activas y listas para usar")
        print("💡 Reinicia el wrapper para aplicar los cambios")
    else:
        print("\n❌ Error reseteando cuentas")

if __name__ == "__main__":
    main()



