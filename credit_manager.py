"""
Sistema de Gestión de Créditos para Son1kvers3
Implementa la arquitectura de créditos por tiers según la guía
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CreditManager:
    def __init__(self):
        self.total_credits = 7500  # Plan Pro contratado
        self.used_credits = 0
        self.user_usage = {}
        self.credit_allocation = {
            "free_pool": 1500,      # 20%
            "pro_pool": 4500,       # 60% 
            "premium_pool": 1500    # 20%
        }
        self.user_limits = {
            "free": {
                "max_generations_per_month": 3,
                "credits_per_generation": 10,
                "models_allowed": ["nuro"],
                "premium_features": False,
                "ollama_model": "llama3.1:8b"  # Usar el modelo disponible
            },
            "pro": {
                "max_generations_per_month": 45,
                "credits_per_generation": 10,
                "models_allowed": ["suno", "riffusion", "nuro"],
                "premium_features": True,
                "ollama_model": "llama3.1:8b"
            },
            "premium": {
                "max_generations_per_month": "unlimited",
                "credits_per_generation": 10,
                "models_allowed": ["suno", "riffusion", "nuro"],
                "premium_features": True,
                "ollama_model": "llama3.1:8b"
            }
        }
        self.load_usage_data()
    
    def load_usage_data(self):
        """Cargar datos de uso desde archivo"""
        try:
            if os.path.exists("usage_data.json"):
                with open("usage_data.json", "r") as f:
                    data = json.load(f)
                    self.used_credits = data.get("used_credits", 0)
                    self.user_usage = data.get("user_usage", {})
                    logger.info("✅ Datos de uso cargados correctamente")
        except Exception as e:
            logger.warning(f"⚠️ Error cargando datos de uso: {e}")
    
    def save_usage_data(self):
        """Guardar datos de uso en archivo"""
        try:
            data = {
                "used_credits": self.used_credits,
                "user_usage": self.user_usage,
                "last_updated": datetime.now().isoformat()
            }
            with open("usage_data.json", "w") as f:
                json.dump(data, f, indent=2)
            logger.info("✅ Datos de uso guardados")
        except Exception as e:
            logger.error(f"❌ Error guardando datos de uso: {e}")
    
    def check_user_limits(self, user_id: str, user_tier: str) -> Tuple[bool, str]:
        """Verificar límites del usuario"""
        current_month = datetime.now().strftime("%Y-%m")
        user_key = f"{user_id}_{current_month}"
        
        if user_key not in self.user_usage:
            self.user_usage[user_key] = {
                "generations": 0,
                "credits_used": 0,
                "tier": user_tier,
                "last_activity": datetime.now().isoformat()
            }
        
        limits = self.user_limits[user_tier]
        current_usage = self.user_usage[user_key]
        
        # Verificar límite mensual de generaciones
        if limits["max_generations_per_month"] != "unlimited":
            if current_usage["generations"] >= limits["max_generations_per_month"]:
                return False, f"Límite mensual alcanzado ({limits['max_generations_per_month']} generaciones)"
        
        # Verificar créditos globales disponibles
        if self.used_credits >= self.total_credits:
            return False, "Sin créditos suficientes en el pool global"
        
        return True, "OK"
    
    def consume_credits(self, user_id: str, user_tier: str, credits: int) -> Tuple[bool, str]:
        """Consumir créditos del usuario"""
        can_use, message = self.check_user_limits(user_id, user_tier)
        if not can_use:
            return False, message
        
        current_month = datetime.now().strftime("%Y-%m")
        user_key = f"{user_id}_{current_month}"
        
        # Actualizar uso global
        self.used_credits += credits
        
        # Actualizar uso del usuario
        if user_key not in self.user_usage:
            self.user_usage[user_key] = {
                "generations": 0,
                "credits_used": 0,
                "tier": user_tier,
                "last_activity": datetime.now().isoformat()
            }
        
        self.user_usage[user_key]["generations"] += 1
        self.user_usage[user_key]["credits_used"] += credits
        self.user_usage[user_key]["last_activity"] = datetime.now().isoformat()
        
        # Guardar datos
        self.save_usage_data()
        
        logger.info(f"✅ Créditos consumidos: {credits} para usuario {user_id} (tier: {user_tier})")
        return True, "Créditos consumidos exitosamente"
    
    def refund_credits(self, user_id: str, credits: int):
        """Reembolsar créditos en caso de error"""
        current_month = datetime.now().strftime("%Y-%m")
        user_key = f"{user_id}_{current_month}"
        
        if user_key in self.user_usage:
            self.used_credits = max(0, self.used_credits - credits)
            self.user_usage[user_key]["generations"] = max(0, self.user_usage[user_key]["generations"] - 1)
            self.user_usage[user_key]["credits_used"] = max(0, self.user_usage[user_key]["credits_used"] - credits)
            self.save_usage_data()
            logger.info(f"🔄 Créditos reembolsados: {credits} para usuario {user_id}")
    
    def get_user_usage(self, user_id: str, user_tier: str) -> Dict[str, Any]:
        """Obtener información de uso del usuario"""
        current_month = datetime.now().strftime("%Y-%m")
        user_key = f"{user_id}_{current_month}"
        
        usage = self.user_usage.get(user_key, {
            "generations": 0,
            "credits_used": 0,
            "tier": user_tier,
            "last_activity": None
        })
        
        limits = self.user_limits[user_tier]
        remaining = limits["max_generations_per_month"]
        if remaining != "unlimited":
            remaining = max(0, remaining - usage["generations"])
        
        return {
            "user_id": user_id,
            "tier": user_tier,
            "current_month": current_month,
            "generations_used": usage["generations"],
            "credits_used": usage["credits_used"],
            "remaining_generations": remaining,
            "models_allowed": limits["models_allowed"],
            "ollama_model": limits["ollama_model"],
            "premium_features": limits["premium_features"]
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        # Calcular distribución de usuarios por tier
        free_users = len([u for u in self.user_usage.keys() if self.user_usage[u].get("tier") == "free"])
        pro_users = len([u for u in self.user_usage.keys() if self.user_usage[u].get("tier") == "pro"])
        premium_users = len([u for u in self.user_usage.keys() if self.user_usage[u].get("tier") == "premium"])
        
        return {
            "total_credits": self.total_credits,
            "used_credits": self.used_credits,
            "remaining_credits": self.total_credits - self.used_credits,
            "credit_allocation": self.credit_allocation,
            "user_distribution": {
                "free_users": free_users,
                "pro_users": pro_users,
                "premium_users": premium_users,
                "total_active_users": free_users + pro_users + premium_users
            },
            "credit_utilization_percentage": (self.used_credits / self.total_credits) * 100
        }
    
    def get_available_models(self, user_tier: str) -> list:
        """Obtener modelos disponibles para el tier del usuario"""
        return self.user_limits[user_tier]["models_allowed"]
    
    def is_model_allowed(self, user_tier: str, model: str) -> bool:
        """Verificar si un modelo está permitido para el tier"""
        return model in self.user_limits[user_tier]["models_allowed"]
    
    def get_ollama_config(self, user_tier: str) -> Dict[str, Any]:
        """Obtener configuración de Ollama para el tier"""
        model = self.user_limits[user_tier]["ollama_model"]
        
        configs = {
            "free": {
                "model": model,
                "max_tokens": 500,
                "temperature": 0.7,
                "quality": "básica",
                "languages": ["es", "en"]
            },
            "pro": {
                "model": model,
                "max_tokens": 1000,
                "temperature": 0.8,
                "quality": "profesional",
                "languages": ["es", "en", "fr", "pt"],
                "custom_styles": True
            },
            "premium": {
                "model": model,
                "max_tokens": 2000,
                "temperature": 0.9,
                "quality": "premium",
                "languages": ["es", "en", "fr", "pt", "de", "it"],
                "custom_styles": True,
                "fine_tuned_genres": True
            }
        }
        
        return configs[user_tier]

# Instancia global del gestor de créditos
credit_manager = CreditManager()
