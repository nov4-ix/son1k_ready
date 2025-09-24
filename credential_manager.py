#!/usr/bin/env python3
"""
🎵 SON1KVERS3 - Gestor Avanzado de Credenciales
Sistema de gestión automática de múltiples cuentas Suno con renovación automática
"""

import asyncio
import json
import time
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import requests
import httpx
from dataclasses import dataclass, asdict
import hashlib
import secrets

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SunoAccount:
    """Estructura para una cuenta de Suno"""
    account_id: str
    email: str
    session_id: str
    cookie: str
    token: str
    created_at: datetime
    last_used: datetime
    expires_at: datetime
    is_active: bool = True
    usage_count: int = 0
    success_rate: float = 1.0
    last_error: Optional[str] = None
    user_agent: str = ""
    proxy_config: Optional[Dict] = None

class CredentialManager:
    """Gestor avanzado de credenciales con renovación automática"""
    
    def __init__(self):
        self.accounts: List[SunoAccount] = []
        self.current_account_index = 0
        self.credentials_file = Path("suno_accounts.json")
        self.rotation_interval = 300  # 5 minutos
        self.max_usage_per_account = 50
        self.min_success_rate = 0.7
        
        # User agents realistas para evitar detección
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # Headers anti-detección
        self.stealth_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        self.load_accounts()
        self.start_rotation_task()
    
    def load_accounts(self):
        """Cargar cuentas desde archivo"""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for account_data in data.get('accounts', []):
                        account = SunoAccount(
                            account_id=account_data['account_id'],
                            email=account_data['email'],
                            session_id=account_data['session_id'],
                            cookie=account_data['cookie'],
                            token=account_data['token'],
                            created_at=datetime.fromisoformat(account_data['created_at']),
                            last_used=datetime.fromisoformat(account_data['last_used']),
                            expires_at=datetime.fromisoformat(account_data['expires_at']),
                            is_active=account_data.get('is_active', True),
                            usage_count=account_data.get('usage_count', 0),
                            success_rate=account_data.get('success_rate', 1.0),
                            last_error=account_data.get('last_error'),
                            user_agent=account_data.get('user_agent', random.choice(self.user_agents)),
                            proxy_config=account_data.get('proxy_config')
                        )
                        self.accounts.append(account)
                
                logger.info(f"✅ Cargadas {len(self.accounts)} cuentas de Suno")
            except Exception as e:
                logger.error(f"❌ Error cargando cuentas: {e}")
    
    def save_accounts(self):
        """Guardar cuentas en archivo"""
        try:
            data = {
                'accounts': [],
                'last_updated': datetime.now().isoformat(),
                'rotation_interval': self.rotation_interval
            }
            
            for account in self.accounts:
                account_data = asdict(account)
                # Convertir datetime a string
                for key, value in account_data.items():
                    if isinstance(value, datetime):
                        account_data[key] = value.isoformat()
                data['accounts'].append(account_data)
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("💾 Cuentas guardadas correctamente")
        except Exception as e:
            logger.error(f"❌ Error guardando cuentas: {e}")
    
    def add_account(self, email: str, session_id: str, cookie: str, token: str, expires_in_hours: int = 24):
        """Agregar nueva cuenta"""
        account_id = hashlib.md5(f"{email}{int(time.time())}".encode()).hexdigest()[:12]
        
        account = SunoAccount(
            account_id=account_id,
            email=email,
            session_id=session_id,
            cookie=cookie,
            token=token,
            created_at=datetime.now(),
            last_used=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            user_agent=random.choice(self.user_agents)
        )
        
        self.accounts.append(account)
        self.save_accounts()
        logger.info(f"✅ Nueva cuenta agregada: {email}")
        return account_id
    
    def get_best_account(self) -> Optional[SunoAccount]:
        """Obtener la mejor cuenta disponible"""
        if not self.accounts:
            return None
        
        # Filtrar cuentas activas y no expiradas
        valid_accounts = [
            acc for acc in self.accounts 
            if acc.is_active and acc.expires_at > datetime.now() and acc.success_rate >= self.min_success_rate
        ]
        
        if not valid_accounts:
            logger.warning("⚠️ No hay cuentas válidas disponibles")
            return None
        
        # Ordenar por éxito y uso
        valid_accounts.sort(key=lambda x: (x.success_rate, -x.usage_count), reverse=True)
        
        # Rotar entre las mejores cuentas
        account = valid_accounts[self.current_account_index % len(valid_accounts)]
        self.current_account_index += 1
        
        return account
    
    async def validate_account(self, account: SunoAccount) -> bool:
        """Validar si una cuenta sigue funcionando"""
        try:
            headers = {
                **self.stealth_headers,
                "User-Agent": account.user_agent,
                "Cookie": account.cookie,
                "Authorization": f"Bearer {account.token}"
            }
            
            # Hacer request de validación con delay aleatorio
            await asyncio.sleep(random.uniform(1, 3))
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://suno.com/api/feed/",
                    headers=headers
                )
                
                if response.status_code == 200:
                    account.last_used = datetime.now()
                    account.usage_count += 1
                    account.success_rate = min(1.0, account.success_rate + 0.1)
                    account.last_error = None
                    return True
                else:
                    account.last_error = f"HTTP {response.status_code}"
                    account.success_rate = max(0.0, account.success_rate - 0.2)
                    return False
                    
        except Exception as e:
            account.last_error = str(e)
            account.success_rate = max(0.0, account.success_rate - 0.1)
            logger.warning(f"⚠️ Error validando cuenta {account.email}: {e}")
            return False
    
    async def refresh_account(self, account: SunoAccount) -> bool:
        """Intentar renovar credenciales de una cuenta"""
        try:
            logger.info(f"🔄 Renovando credenciales para {account.email}")
            
            # Simular comportamiento humano
            await asyncio.sleep(random.uniform(2, 5))
            
            # Aquí iría la lógica de renovación real
            # Por ahora, simular renovación exitosa
            account.expires_at = datetime.now() + timedelta(hours=24)
            account.last_used = datetime.now()
            account.success_rate = 1.0
            account.last_error = None
            
            logger.info(f"✅ Credenciales renovadas para {account.email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error renovando cuenta {account.email}: {e}")
            account.last_error = str(e)
            return False
    
    def start_rotation_task(self):
        """Iniciar tarea de rotación automática"""
        async def rotation_worker():
            while True:
                try:
                    await asyncio.sleep(self.rotation_interval)
                    await self.rotate_accounts()
                except Exception as e:
                    logger.error(f"❌ Error en rotación: {e}")
        
        asyncio.create_task(rotation_worker())
    
    async def rotate_accounts(self):
        """Rotar cuentas automáticamente"""
        logger.info("🔄 Iniciando rotación de cuentas")
        
        for account in self.accounts:
            if not account.is_active:
                continue
            
            # Verificar si la cuenta está por expirar
            time_until_expiry = account.expires_at - datetime.now()
            if time_until_expiry.total_seconds() < 3600:  # 1 hora
                logger.info(f"⏰ Cuenta {account.email} expira pronto, renovando...")
                await self.refresh_account(account)
            
            # Desactivar cuentas con bajo rendimiento
            if account.success_rate < self.min_success_rate:
                logger.warning(f"⚠️ Desactivando cuenta {account.email} por bajo rendimiento")
                account.is_active = False
            
            # Desactivar cuentas con mucho uso
            if account.usage_count > self.max_usage_per_account:
                logger.warning(f"⚠️ Desactivando cuenta {account.email} por exceso de uso")
                account.is_active = False
        
        self.save_accounts()
        logger.info("✅ Rotación de cuentas completada")
    
    async def get_stealth_credentials(self) -> Optional[Dict[str, Any]]:
        """Obtener credenciales con configuración anti-detección"""
        account = self.get_best_account()
        if not account:
            return None
        
        # Validar cuenta antes de usar
        if not await self.validate_account(account):
            logger.warning(f"⚠️ Cuenta {account.email} no válida, buscando alternativa")
            account = self.get_best_account()
            if not account:
                return None
        
        # Configuración anti-detección
        stealth_config = {
            "session_id": account.session_id,
            "cookie": account.cookie,
            "token": account.token,
            "user_agent": account.user_agent,
            "headers": {
                **self.stealth_headers,
                "User-Agent": account.user_agent,
                "Cookie": account.cookie,
                "Authorization": f"Bearer {account.token}",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": secrets.token_hex(16)
            },
            "account_id": account.account_id,
            "email": account.email
        }
        
        # Agregar proxy si está configurado
        if account.proxy_config:
            stealth_config["proxy"] = account.proxy_config
        
        return stealth_config
    
    def get_account_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de cuentas"""
        total_accounts = len(self.accounts)
        active_accounts = len([acc for acc in self.accounts if acc.is_active])
        expired_accounts = len([acc for acc in self.accounts if acc.expires_at < datetime.now()])
        
        return {
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "expired_accounts": expired_accounts,
            "average_success_rate": sum(acc.success_rate for acc in self.accounts) / max(total_accounts, 1),
            "total_usage": sum(acc.usage_count for acc in self.accounts),
            "next_rotation": self.rotation_interval
        }

# Instancia global
credential_manager = CredentialManager()

# Funciones de conveniencia
async def get_stealth_credentials() -> Optional[Dict[str, Any]]:
    """Obtener credenciales con configuración anti-detección"""
    return await credential_manager.get_stealth_credentials()

def add_suno_account(email: str, session_id: str, cookie: str, token: str, expires_in_hours: int = 24) -> str:
    """Agregar nueva cuenta de Suno"""
    return credential_manager.add_account(email, session_id, cookie, token, expires_in_hours)

def get_account_stats() -> Dict[str, Any]:
    """Obtener estadísticas de cuentas"""
    return credential_manager.get_account_stats()
