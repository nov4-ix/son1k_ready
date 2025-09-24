#!/usr/bin/env python3
"""
🏥 HEALTH CHECKER - Verificador de Salud del Sistema
Endpoint de health check robusto para el sistema Son1k
"""

import asyncio
import logging
import time
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    uptime: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    last_generation: Optional[str] = None
    errors_count: int
    warnings_count: int

class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_generation = None
        self.errors_count = 0
        self.warnings_count = 0
        self.health_history = []
        
    def get_system_health(self) -> HealthStatus:
        """Obtener estado de salud del sistema"""
        try:
            # Información básica del sistema
            uptime = time.time() - self.start_time
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Contar conexiones activas
            active_connections = self._count_active_connections()
            
            # Determinar estado general
            status = self._determine_overall_status(cpu_usage, memory.percent, disk.percent)
            
            health_status = HealthStatus(
                status=status,
                timestamp=datetime.now().isoformat(),
                uptime=uptime,
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                active_connections=active_connections,
                last_generation=self.last_generation,
                errors_count=self.errors_count,
                warnings_count=self.warnings_count
            )
            
            # Guardar en historial
            self.health_history.append(health_status.dict())
            if len(self.health_history) > 100:  # Mantener solo últimos 100
                self.health_history.pop(0)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error obteniendo salud del sistema: {e}")
            self.errors_count += 1
            raise HTTPException(status_code=500, detail=f"Error interno: {e}")
    
    def _count_active_connections(self) -> int:
        """Contar conexiones activas del servidor"""
        try:
            connections = 0
            for conn in psutil.net_connections():
                if conn.laddr.port == 8000 and conn.status == 'LISTEN':
                    connections += 1
            return connections
        except Exception:
            return 0
    
    def _determine_overall_status(self, cpu: float, memory: float, disk: float) -> str:
        """Determinar estado general del sistema"""
        if cpu > 90 or memory > 95 or disk > 95:
            self.warnings_count += 1
            return "critical"
        elif cpu > 80 or memory > 85 or disk > 90:
            self.warnings_count += 1
            return "warning"
        elif self.errors_count > 10:
            self.warnings_count += 1
            return "degraded"
        else:
            return "healthy"
    
    def record_generation(self):
        """Registrar nueva generación de música"""
        self.last_generation = datetime.now().isoformat()
    
    def record_error(self, error: str):
        """Registrar error"""
        self.errors_count += 1
        logger.error(f"Error registrado: {error}")
    
    def record_warning(self, warning: str):
        """Registrar advertencia"""
        self.warnings_count += 1
        logger.warning(f"Advertencia registrada: {warning}")
    
    def get_health_history(self, hours: int = 1) -> list:
        """Obtener historial de salud"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            h for h in self.health_history 
            if datetime.fromisoformat(h['timestamp']) > cutoff_time
        ]
    
    def reset_counters(self):
        """Resetear contadores de errores y advertencias"""
        self.errors_count = 0
        self.warnings_count = 0

# Instancia global
health_checker = HealthChecker()

# Router para endpoints de salud
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=HealthStatus)
async def get_health():
    """Endpoint principal de health check"""
    return health_checker.get_system_health()

@router.get("/detailed")
async def get_detailed_health():
    """Health check detallado con más información"""
    try:
        health = health_checker.get_system_health()
        
        # Información adicional
        detailed_info = {
            "basic_health": health.dict(),
            "process_info": {
                "pid": os.getpid(),
                "threads": psutil.Process().num_threads(),
                "open_files": len(psutil.Process().open_files())
            },
            "system_info": {
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "recent_health": health_checker.get_health_history(hours=1)
        }
        
        return detailed_info
        
    except Exception as e:
        logger.error(f"Error en health check detallado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_health_history(hours: int = 1):
    """Obtener historial de salud"""
    try:
        return health_checker.get_health_history(hours)
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_health_counters():
    """Resetear contadores de salud"""
    try:
        health_checker.reset_counters()
        return {"message": "Contadores reseteados exitosamente"}
    except Exception as e:
        logger.error(f"Error reseteando contadores: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ready")
async def readiness_check():
    """Verificación de readiness para load balancers"""
    try:
        health = health_checker.get_system_health()
        
        if health.status in ["healthy", "warning"]:
            return {"status": "ready", "timestamp": health.timestamp}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        logger.error(f"Error en readiness check: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live")
async def liveness_check():
    """Verificación de liveness para load balancers"""
    try:
        # Verificación básica de que el proceso está vivo
        return {
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - health_checker.start_time
        }
    except Exception as e:
        logger.error(f"Error en liveness check: {e}")
        raise HTTPException(status_code=503, detail="Service not alive")



