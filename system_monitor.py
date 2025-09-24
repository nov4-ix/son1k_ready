#!/usr/bin/env python3
"""
🛡️ SON1K SYSTEM MONITOR - Sistema de Monitoreo y Recuperación Automática
Monitorea el sistema, detecta problemas y ejecuta recuperación automática
"""

import asyncio
import logging
import psutil
import requests
import time
import subprocess
import signal
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor del sistema con recuperación automática"""
    
    def __init__(self):
        self.app_port = 8000
        self.health_check_interval = 30  # segundos
        self.max_cpu_usage = 80.0  # %
        self.max_memory_usage = 85.0  # %
        self.max_response_time = 10.0  # segundos
        self.max_uptime_hours = 2  # reiniciar cada 2 horas
        self.restart_threshold = 3  # reiniciar después de 3 fallos consecutivos
        self.failure_count = 0
        self.last_restart = None
        self.process_pid = None
        self.is_running = False
        
    async def start_monitoring(self):
        """Iniciar monitoreo continuo"""
        logger.info("🛡️ Iniciando Sistema de Monitoreo Son1k")
        self.is_running = True
        
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Error en monitoreo: {e}")
                await asyncio.sleep(10)
    
    async def _perform_health_check(self):
        """Realizar verificación de salud del sistema"""
        try:
            # 1. Verificar si el proceso está ejecutándose
            if not self._is_process_running():
                logger.warning("⚠️ Proceso principal no encontrado, reiniciando...")
                await self._restart_application()
                return
            
            # 2. Verificar respuesta HTTP
            if not await self._check_http_health():
                logger.warning("⚠️ Servidor no responde, reiniciando...")
                await self._restart_application()
                return
            
            # 3. Verificar uso de recursos
            if not self._check_resource_usage():
                logger.warning("⚠️ Uso excesivo de recursos, reiniciando...")
                await self._restart_application()
                return
            
            # 4. Verificar tiempo de ejecución
            if self._should_restart_by_uptime():
                logger.info("🔄 Reinicio programado por tiempo de ejecución")
                await self._restart_application()
                return
            
            # 5. Verificar archivos de log por errores críticos
            if self._check_critical_errors():
                logger.warning("⚠️ Errores críticos detectados, reiniciando...")
                await self._restart_application()
                return
            
            # Si llegamos aquí, todo está bien
            self.failure_count = 0
            logger.info("✅ Sistema saludable")
            
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
            self.failure_count += 1
    
    def _is_process_running(self) -> bool:
        """Verificar si el proceso principal está ejecutándose"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'son1k_optimized_system.py' in cmdline:
                        self.process_pid = proc.info['pid']
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            logger.error(f"Error verificando proceso: {e}")
            return False
    
    async def _check_http_health(self) -> bool:
        """Verificar salud del servidor HTTP"""
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:{self.app_port}/", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < self.max_response_time:
                return True
            else:
                logger.warning(f"⚠️ Respuesta HTTP lenta: {response_time:.2f}s")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Error HTTP: {e}")
            return False
    
    def _check_resource_usage(self) -> bool:
        """Verificar uso de recursos del sistema"""
        try:
            if not self.process_pid:
                return False
                
            process = psutil.Process(self.process_pid)
            cpu_percent = process.cpu_percent()
            memory_percent = process.memory_percent()
            
            if cpu_percent > self.max_cpu_usage:
                logger.warning(f"⚠️ CPU alto: {cpu_percent:.1f}%")
                return False
            
            if memory_percent > self.max_memory_usage:
                logger.warning(f"⚠️ Memoria alta: {memory_percent:.1f}%")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error verificando recursos: {e}")
            return False
    
    def _should_restart_by_uptime(self) -> bool:
        """Verificar si debe reiniciar por tiempo de ejecución"""
        if not self.process_pid:
            return True
            
        try:
            process = psutil.Process(self.process_pid)
            uptime = time.time() - process.create_time()
            uptime_hours = uptime / 3600
            
            if uptime_hours > self.max_uptime_hours:
                logger.info(f"⏰ Tiempo de ejecución: {uptime_hours:.1f}h")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error verificando uptime: {e}")
            return True
    
    def _check_critical_errors(self) -> bool:
        """Verificar errores críticos en logs"""
        try:
            log_files = [
                'system_monitor.log',
                'son1k_optimized_system.log',
                'error.log'
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    # Verificar errores de las últimas 5 minutos
                    cutoff_time = time.time() - 300
                    with open(log_file, 'r') as f:
                        for line in f:
                            if 'CRITICAL' in line or 'FATAL' in line:
                                return True
            return False
        except Exception as e:
            logger.error(f"Error verificando logs: {e}")
            return False
    
    async def _restart_application(self):
        """Reiniciar la aplicación"""
        try:
            logger.info("🔄 Iniciando reinicio de aplicación...")
            
            # 1. Detener proceso actual
            if self.process_pid:
                await self._kill_process(self.process_pid)
                await asyncio.sleep(2)
            
            # 2. Limpiar recursos
            await self._cleanup_resources()
            
            # 3. Reiniciar aplicación
            await self._start_application()
            
            # 4. Verificar que inició correctamente
            await asyncio.sleep(5)
            if await self._check_http_health():
                logger.info("✅ Aplicación reiniciada exitosamente")
                self.failure_count = 0
                self.last_restart = datetime.now()
            else:
                logger.error("❌ Fallo al reiniciar aplicación")
                self.failure_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error reiniciando aplicación: {e}")
            self.failure_count += 1
    
    async def _kill_process(self, pid: int):
        """Terminar proceso de forma segura"""
        try:
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                process.terminate()
                
                # Esperar terminación graceful
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    # Forzar terminación
                    process.kill()
                    process.wait(timeout=5)
                
                logger.info(f"✅ Proceso {pid} terminado")
        except Exception as e:
            logger.error(f"Error terminando proceso {pid}: {e}")
    
    async def _cleanup_resources(self):
        """Limpiar recursos del sistema"""
        try:
            # Limpiar archivos temporales
            temp_dir = Path("generated_audio")
            if temp_dir.exists():
                for file in temp_dir.glob("*.tmp"):
                    file.unlink()
            
            # Limpiar logs antiguos
            log_files = ['system_monitor.log', 'error.log']
            for log_file in log_files:
                if os.path.exists(log_file):
                    # Mantener solo las últimas 1000 líneas
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    if len(lines) > 1000:
                        with open(log_file, 'w') as f:
                            f.writelines(lines[-1000:])
            
            logger.info("🧹 Recursos limpiados")
        except Exception as e:
            logger.error(f"Error limpiando recursos: {e}")
    
    async def _start_application(self):
        """Iniciar la aplicación"""
        try:
            # Cambiar al directorio del proyecto
            os.chdir("/Users/nov4-ix/Downloads/son1k_suno_poc_mvp_v2 2")
            
            # Activar entorno virtual y ejecutar
            cmd = "source .venv/bin/activate && python son1k_optimized_system.py"
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            logger.info("🚀 Aplicación iniciada")
        except Exception as e:
            logger.error(f"Error iniciando aplicación: {e}")
            raise
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        logger.info("🛑 Deteniendo monitoreo del sistema")
        self.is_running = False

async def main():
    """Función principal"""
    monitor = SystemMonitor()
    
    # Manejar señales de terminación
    def signal_handler(signum, frame):
        logger.info("🛑 Señal de terminación recibida")
        monitor.stop_monitoring()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("🛑 Monitoreo detenido por usuario")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())



