#!/usr/bin/env python3
"""
🛠️ ERROR HANDLER - Manejador de Errores Robusto
Sistema avanzado de manejo de errores y recuperación automática
"""

import asyncio
import logging
import traceback
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, Union
from enum import Enum
import functools
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Niveles de severidad de errores"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categorías de errores"""
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    AUTHENTICATION = "authentication"
    GENERATION = "generation"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class ErrorRecoveryStrategy(Enum):
    """Estrategias de recuperación"""
    RETRY = "retry"
    FALLBACK = "fallback"
    RESTART = "restart"
    IGNORE = "ignore"
    ESCALATE = "escalate"

class ErrorHandler:
    """Manejador centralizado de errores"""
    
    def __init__(self):
        self.error_history = []
        self.retry_counts = {}
        self.circuit_breakers = {}
        self.max_retries = 3
        self.retry_delay = 1.0  # segundos
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutos
        
    def handle_error(
        self,
        error: Exception,
        context: str = "",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        recovery_strategy: ErrorRecoveryStrategy = ErrorRecoveryStrategy.RETRY,
        max_retries: Optional[int] = None,
        custom_handler: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Manejar error con estrategia de recuperación"""
        
        error_id = f"ERR_{int(time.time())}_{id(error)}"
        error_info = {
            "id": error_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "severity": severity.value,
            "category": category.value,
            "recovery_strategy": recovery_strategy.value,
            "traceback": traceback.format_exc()
        }
        
        # Registrar error
        self._log_error(error_info)
        self.error_history.append(error_info)
        
        # Limpiar historial antiguo
        self._cleanup_old_errors()
        
        # Aplicar estrategia de recuperación
        recovery_result = self._apply_recovery_strategy(
            error, error_info, recovery_strategy, max_retries, custom_handler
        )
        
        error_info["recovery_result"] = recovery_result
        return error_info
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Registrar error en logs"""
        severity = error_info["severity"]
        message = f"[{error_info['id']}] {error_info['error_type']}: {error_info['error_message']}"
        
        if severity == "critical":
            logger.critical(message)
        elif severity == "high":
            logger.error(message)
        elif severity == "medium":
            logger.warning(message)
        else:
            logger.info(message)
    
    def _cleanup_old_errors(self):
        """Limpiar errores antiguos del historial"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.error_history = [
            error for error in self.error_history
            if datetime.fromisoformat(error["timestamp"]) > cutoff_time
        ]
    
    def _apply_recovery_strategy(
        self,
        error: Exception,
        error_info: Dict[str, Any],
        strategy: ErrorRecoveryStrategy,
        max_retries: Optional[int],
        custom_handler: Optional[Callable]
    ) -> Dict[str, Any]:
        """Aplicar estrategia de recuperación"""
        
        if custom_handler:
            try:
                return custom_handler(error, error_info)
            except Exception as e:
                logger.error(f"Error en custom handler: {e}")
        
        if strategy == ErrorRecoveryStrategy.RETRY:
            return self._retry_strategy(error, error_info, max_retries)
        elif strategy == ErrorRecoveryStrategy.FALLBACK:
            return self._fallback_strategy(error, error_info)
        elif strategy == ErrorRecoveryStrategy.RESTART:
            return self._restart_strategy(error, error_info)
        elif strategy == ErrorRecoveryStrategy.IGNORE:
            return {"status": "ignored", "message": "Error ignorado"}
        elif strategy == ErrorRecoveryStrategy.ESCALATE:
            return self._escalate_strategy(error, error_info)
        else:
            return {"status": "unknown_strategy", "message": "Estrategia desconocida"}
    
    def _retry_strategy(self, error: Exception, error_info: Dict[str, Any], max_retries: Optional[int]) -> Dict[str, Any]:
        """Estrategia de reintento"""
        error_key = f"{error_info['context']}_{type(error).__name__}"
        current_retries = self.retry_counts.get(error_key, 0)
        max_attempts = max_retries or self.max_retries
        
        if current_retries >= max_attempts:
            self.retry_counts[error_key] = 0  # Reset counter
            return {
                "status": "max_retries_exceeded",
                "message": f"Máximo de reintentos ({max_attempts}) excedido",
                "retries": current_retries
            }
        
        self.retry_counts[error_key] = current_retries + 1
        delay = self.retry_delay * (2 ** current_retries)  # Exponential backoff
        
        return {
            "status": "retrying",
            "message": f"Reintentando en {delay} segundos",
            "retries": current_retries + 1,
            "delay": delay
        }
    
    def _fallback_strategy(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Estrategia de fallback"""
        # Implementar lógica de fallback específica según la categoría
        category = error_info["category"]
        
        if category == "api":
            return {
                "status": "fallback",
                "message": "Usando API de respaldo",
                "action": "switch_to_backup_api"
            }
        elif category == "generation":
            return {
                "status": "fallback",
                "message": "Usando generador de respaldo",
                "action": "switch_to_backup_generator"
            }
        else:
            return {
                "status": "fallback",
                "message": "Activando modo de respaldo",
                "action": "enable_fallback_mode"
            }
    
    def _restart_strategy(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Estrategia de reinicio"""
        return {
            "status": "restart_required",
            "message": "Reinicio del servicio requerido",
            "action": "restart_service"
        }
    
    def _escalate_strategy(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Estrategia de escalación"""
        # Enviar notificación a administradores
        self._notify_administrators(error_info)
        
        return {
            "status": "escalated",
            "message": "Error escalado a administradores",
            "action": "notify_administrators"
        }
    
    def _notify_administrators(self, error_info: Dict[str, Any]):
        """Notificar a administradores sobre errores críticos"""
        try:
            # Aquí se implementaría la lógica de notificación
            # Por ejemplo, enviar email, Slack, etc.
            logger.critical(f"NOTIFICACIÓN ADMIN: {error_info['id']} - {error_info['error_message']}")
        except Exception as e:
            logger.error(f"Error notificando administradores: {e}")
    
    def get_error_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener estadísticas de errores"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            error for error in self.error_history
            if datetime.fromisoformat(error["timestamp"]) > cutoff_time
        ]
        
        stats = {
            "total_errors": len(recent_errors),
            "by_severity": {},
            "by_category": {},
            "by_strategy": {},
            "recent_errors": recent_errors[-10:]  # Últimos 10 errores
        }
        
        for error in recent_errors:
            severity = error["severity"]
            category = error["category"]
            strategy = error["recovery_strategy"]
            
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1
        
        return stats

# Instancia global
error_handler = ErrorHandler()

def handle_errors(
    context: str = "",
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    recovery_strategy: ErrorRecoveryStrategy = ErrorRecoveryStrategy.RETRY,
    max_retries: Optional[int] = None,
    custom_handler: Optional[Callable] = None
):
    """Decorator para manejo automático de errores"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_error(
                    e, context, severity, category, recovery_strategy, max_retries, custom_handler
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_error(
                    e, context, severity, category, recovery_strategy, max_retries, custom_handler
                )
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def safe_execute(
    func: Callable,
    *args,
    context: str = "",
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    recovery_strategy: ErrorRecoveryStrategy = ErrorRecoveryStrategy.RETRY,
    **kwargs
) -> Any:
    """Ejecutar función de forma segura con manejo de errores"""
    try:
        if asyncio.iscoroutinefunction(func):
            return asyncio.run(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    except Exception as e:
        return error_handler.handle_error(
            e, context, severity, category, recovery_strategy
        )

