"""
Gestor de múltiples cuentas de Suno para máxima evasión
"""
import asyncio
import aiohttp
import json
import logging
import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class SunoAccount:
    """Representa una cuenta de Suno"""
    id: str
    cookie: str
    email: str
    last_used: float = 0
    success_count: int = 0
    failure_count: int = 0
    daily_usage: int = 0
    max_daily_usage: int = 50
    is_active: bool = True
    cooldown_until: float = 0
    priority: int = 1  # 1 = alta, 2 = media, 3 = baja
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def is_available(self) -> bool:
        return (self.is_active and 
                self.daily_usage < self.max_daily_usage and 
                time.time() > self.cooldown_until)
    
    @property
    def score(self) -> float:
        """Calcula el score de la cuenta para selección"""
        base_score = self.success_rate * 100
        time_penalty = (time.time() - self.last_used) / 3600  # Penalty por tiempo sin usar
        usage_penalty = self.daily_usage / self.max_daily_usage * 50  # Penalty por uso diario
        priority_bonus = (4 - self.priority) * 10  # Bonus por prioridad
        
        return base_score - time_penalty - usage_penalty + priority_bonus

class MultiAccountManager:
    """Gestor de múltiples cuentas de Suno"""
    
    def __init__(self, wrapper_url: str = "http://localhost:3001"):
        self.wrapper_url = wrapper_url
        self.accounts: Dict[str, SunoAccount] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.rotation_interval = 300  # 5 minutos
        self.last_rotation = 0
        self.current_account_id: Optional[str] = None
        self.load_balancer = "round_robin"  # round_robin, weighted, random
        
    async def initialize(self):
        """Inicializar el gestor"""
        self.session = aiohttp.ClientSession()
        await self.load_accounts_from_config()
        await self.verify_accounts()
        logger.info(f"✅ MultiAccountManager inicializado con {len(self.accounts)} cuentas")
    
    async def load_accounts_from_config(self):
        """Cargar cuentas desde archivo de configuración"""
        config_file = "suno_accounts.json"
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            for account_data in config.get('accounts', []):
                account = SunoAccount(
                    id=account_data['id'],
                    cookie=account_data['cookie'],
                    email=account_data['email'],
                    priority=account_data.get('priority', 1),
                    max_daily_usage=account_data.get('max_daily_usage', 50)
                )
                self.accounts[account.id] = account
                logger.info(f"📝 Cuenta cargada: {account.email} (Prioridad: {account.priority})")
                
        except FileNotFoundError:
            logger.warning(f"⚠️ Archivo {config_file} no encontrado, creando plantilla")
            await self.create_account_template()
        except Exception as e:
            logger.error(f"❌ Error cargando cuentas: {e}")
    
    async def create_account_template(self):
        """Crear plantilla de configuración de cuentas"""
        template = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "tu_email_1@gmail.com",
                    "cookie": "tu_cookie_de_suno_1_aqui",
                    "priority": 1,
                    "max_daily_usage": 50
                },
                {
                    "id": "account_2", 
                    "email": "tu_email_2@gmail.com",
                    "cookie": "tu_cookie_de_suno_2_aqui",
                    "priority": 1,
                    "max_daily_usage": 50
                },
                {
                    "id": "account_3",
                    "email": "tu_email_3@gmail.com", 
                    "cookie": "tu_cookie_de_suno_3_aqui",
                    "priority": 2,
                    "max_daily_usage": 30
                }
            ],
            "settings": {
                "rotation_interval": 300,
                "load_balancer": "weighted",
                "cooldown_time": 60,
                "max_concurrent": 3
            }
        }
        
        with open("suno_accounts.json", 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info("📝 Plantilla de cuentas creada en suno_accounts.json")
    
    async def verify_accounts(self):
        """Verificar que las cuentas estén funcionando"""
        logger.info("🔍 Verificando cuentas de Suno...")
        
        for account_id, account in self.accounts.items():
            try:
                # Agregar cookie al wrapper
                async with self.session.post(
                    f"{self.wrapper_url}/add-cookie",
                    json={"cookie": account.cookie}
                ) as response:
                    if response.status == 200:
                        account.is_active = True
                        logger.info(f"✅ Cuenta {account.email} verificada")
                    else:
                        account.is_active = False
                        logger.warning(f"⚠️ Cuenta {account.email} no verificada")
            except Exception as e:
                account.is_active = False
                logger.error(f"❌ Error verificando cuenta {account.email}: {e}")
    
    def get_best_account(self) -> Optional[SunoAccount]:
        """Obtener la mejor cuenta disponible"""
        available_accounts = [acc for acc in self.accounts.values() if acc.is_available]
        
        if not available_accounts:
            logger.warning("⚠️ No hay cuentas disponibles")
            return None
        
        if self.load_balancer == "random":
            return random.choice(available_accounts)
        elif self.load_balancer == "round_robin":
            # Rotación simple
            sorted_accounts = sorted(available_accounts, key=lambda x: x.last_used)
            return sorted_accounts[0]
        else:  # weighted
            # Selección por score
            sorted_accounts = sorted(available_accounts, key=lambda x: x.score, reverse=True)
            return sorted_accounts[0]
    
    async def generate_music(self, prompt: str, lyrics: str = "", style: str = "profesional") -> Dict[str, Any]:
        """Generar música usando la mejor cuenta disponible"""
        account = self.get_best_account()
        
        if not account:
            return {
                "success": False,
                "error": "No hay cuentas de Suno disponibles",
                "mode": "multi_account"
            }
        
        logger.info(f"🎵 [MULTI] Usando cuenta: {account.email} (Score: {account.score:.1f})")
        
        try:
            # Actualizar uso de la cuenta
            account.last_used = time.time()
            account.daily_usage += 1
            
            # Generar música
            payload = {
                "prompt": prompt,
                "lyrics": lyrics,
                "style": style
            }
            
            async with self.session.post(
                f"{self.wrapper_url}/generate-music",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        account.success_count += 1
                        logger.info(f"✅ [MULTI] Música generada con {account.email}")
                        
                        return {
                            "success": True,
                            "audio_urls": data.get('audioUrls', []),
                            "lyrics": data.get('lyrics', lyrics),
                            "metadata": data.get('metadata', {}),
                            "account_used": account.email,
                            "mode": "multi_account"
                        }
                    else:
                        account.failure_count += 1
                        account.cooldown_until = time.time() + 300  # 5 minutos de cooldown
                        logger.warning(f"⚠️ [MULTI] Fallo con {account.email}: {data.get('error')}")
                        
                        # Intentar con otra cuenta
                        return await self.generate_music_fallback(prompt, lyrics, style, account.id)
                else:
                    account.failure_count += 1
                    error_text = await response.text()
                    logger.error(f"❌ [MULTI] Error HTTP {response.status} con {account.email}: {error_text}")
                    return await self.generate_music_fallback(prompt, lyrics, style, account.id)
                    
        except Exception as e:
            account.failure_count += 1
            account.cooldown_until = time.time() + 300
            logger.error(f"❌ [MULTI] Error con {account.email}: {e}")
            return await self.generate_music_fallback(prompt, lyrics, style, account.id)
    
    async def generate_music_fallback(self, prompt: str, lyrics: str, style: str, failed_account_id: str) -> Dict[str, Any]:
        """Intentar generación con otra cuenta si la primera falla"""
        logger.info(f"🔄 [MULTI] Intentando con cuenta alternativa...")
        
        available_accounts = [
            acc for acc in self.accounts.values() 
            if acc.is_available and acc.id != failed_account_id
        ]
        
        if not available_accounts:
            return {
                "success": False,
                "error": "Todas las cuentas están en cooldown o no disponibles",
                "mode": "multi_account"
            }
        
        # Usar la siguiente mejor cuenta
        account = available_accounts[0]
        logger.info(f"🔄 [MULTI] Usando cuenta alternativa: {account.email}")
        
        # Recursión con la cuenta alternativa
        return await self.generate_music(prompt, lyrics, style)
    
    async def rotate_accounts(self):
        """Rotar cuentas para evitar detección"""
        if time.time() - self.last_rotation < self.rotation_interval:
            return
        
        logger.info("🔄 [MULTI] Rotando cuentas...")
        
        # Resetear contadores diarios si es un nuevo día
        current_day = datetime.now().date()
        for account in self.accounts.values():
            if hasattr(account, 'last_reset_day'):
                if account.last_reset_day != current_day:
                    account.daily_usage = 0
                    account.last_reset_day = current_day
            else:
                account.last_reset_day = current_day
        
        # Reducir cooldowns
        for account in self.accounts.values():
            if account.cooldown_until > 0 and time.time() > account.cooldown_until:
                account.cooldown_until = 0
                logger.info(f"✅ [MULTI] Cuenta {account.email} salió de cooldown")
        
        self.last_rotation = time.time()
    
    async def get_account_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de todas las cuentas"""
        stats = {
            "total_accounts": len(self.accounts),
            "active_accounts": len([acc for acc in self.accounts.values() if acc.is_active]),
            "available_accounts": len([acc for acc in self.accounts.values() if acc.is_available]),
            "accounts": []
        }
        
        for account in self.accounts.values():
            stats["accounts"].append({
                "id": account.id,
                "email": account.email,
                "is_active": account.is_active,
                "is_available": account.is_available,
                "success_rate": f"{account.success_rate:.1%}",
                "daily_usage": f"{account.daily_usage}/{account.max_daily_usage}",
                "score": f"{account.score:.1f}",
                "priority": account.priority
            })
        
        return stats
    
    async def cleanup(self):
        """Limpiar recursos"""
        if self.session:
            await self.session.close()
            self.session = None

# Instancia global
multi_account_manager = MultiAccountManager()

async def generate_music_with_multi_account(prompt: str, lyrics: str = "", style: str = "profesional") -> Dict[str, Any]:
    """Función de conveniencia para generar música con múltiples cuentas"""
    if not multi_account_manager.session:
        await multi_account_manager.initialize()
    
    # Rotar cuentas si es necesario
    await multi_account_manager.rotate_accounts()
    
    return await multi_account_manager.generate_music(prompt, lyrics, style)




