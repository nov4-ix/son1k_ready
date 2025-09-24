#!/usr/bin/env python3
"""
🌐 EXTENSION WEBSOCKET - Comunicación en Tiempo Real con Extensión
Sistema de comunicación bidireccional entre el servidor y la extensión de Chrome
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ExtensionConnectionManager:
    """Gestor de conexiones WebSocket con extensiones"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.extension_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, connection_type: str = "extension"):
        """Conectar nueva WebSocket"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if connection_type == "extension":
            connection_id = str(uuid.uuid4())
            self.extension_connections[connection_id] = websocket
            logger.info(f"🔌 Extensión conectada: {connection_id}")
            return connection_id
        else:
            logger.info(f"🔌 Cliente conectado")
            return None
    
    def disconnect(self, websocket: WebSocket):
        """Desconectar WebSocket"""
        self.active_connections.discard(websocket)
        
        # Remover de conexiones de extensión
        for conn_id, conn in list(self.extension_connections.items()):
            if conn == websocket:
                del self.extension_connections[conn_id]
                logger.info(f"🔌 Extensión desconectada: {conn_id}")
                break
    
    async def send_to_extension(self, message: Dict[str, Any]):
        """Enviar mensaje a todas las extensiones conectadas"""
        if not self.extension_connections:
            logger.warning("⚠️ No hay extensiones conectadas")
            return False
        
        message_str = json.dumps(message)
        disconnected = []
        
        for conn_id, websocket in self.extension_connections.items():
            try:
                await websocket.send_text(message_str)
                logger.info(f"📤 Mensaje enviado a extensión {conn_id}")
            except Exception as e:
                logger.error(f"❌ Error enviando a extensión {conn_id}: {e}")
                disconnected.append(conn_id)
        
        # Limpiar conexiones desconectadas
        for conn_id in disconnected:
            del self.extension_connections[conn_id]
        
        return len(disconnected) == 0
    
    async def send_to_all(self, message: Dict[str, Any]):
        """Enviar mensaje a todas las conexiones"""
        message_str = json.dumps(message)
        disconnected = []
        
        for websocket in self.active_connections.copy():
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"❌ Error enviando mensaje: {e}")
                disconnected.append(websocket)
        
        # Limpiar conexiones desconectadas
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def handle_extension_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Manejar mensaje de extensión"""
        try:
            message_type = message.get("type")
            
            if message_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
                
            elif message_type == "suno_form_data":
                # Datos del formulario de Suno recibidos
                await self._handle_suno_form_data(message)
                
            elif message_type == "generation_request":
                # Solicitud de generación desde Suno
                await self._handle_generation_request(websocket, message)
                
            elif message_type == "generation_status":
                # Estado de generación desde Suno
                await self._handle_generation_status(message)
                
            else:
                logger.warning(f"⚠️ Tipo de mensaje desconocido: {message_type}")
                
        except Exception as e:
            logger.error(f"❌ Error manejando mensaje de extensión: {e}")
    
    async def _handle_suno_form_data(self, message: Dict[str, Any]):
        """Manejar datos del formulario de Suno"""
        try:
            form_data = message.get("data", {})
            logger.info(f"📝 Datos de formulario Suno recibidos: {form_data}")
            
            # Aquí podrías procesar los datos del formulario
            # Por ejemplo, guardarlos en una base de datos o enviarlos a Ollama
            
        except Exception as e:
            logger.error(f"❌ Error procesando datos de formulario: {e}")
    
    async def _handle_generation_request(self, websocket: WebSocket, message: Dict[str, Any]):
        """Manejar solicitud de generación desde Suno"""
        try:
            request_data = message.get("data", {})
            logger.info(f"🎵 Solicitud de generación desde Suno: {request_data}")
            
            # Procesar solicitud de generación
            # Aquí podrías integrar con el sistema de generación existente
            
            # Responder a la extensión
            await websocket.send_text(json.dumps({
                "type": "generation_response",
                "status": "received",
                "message": "Solicitud de generación recibida",
                "timestamp": datetime.now().isoformat()
            }))
            
        except Exception as e:
            logger.error(f"❌ Error manejando solicitud de generación: {e}")
    
    async def _handle_generation_status(self, message: Dict[str, Any]):
        """Manejar estado de generación desde Suno"""
        try:
            status_data = message.get("data", {})
            logger.info(f"📊 Estado de generación desde Suno: {status_data}")
            
            # Procesar estado de generación
            # Aquí podrías actualizar el estado en la base de datos
            
        except Exception as e:
            logger.error(f"❌ Error manejando estado de generación: {e}")

# Instancia global del gestor
connection_manager = ExtensionConnectionManager()

# Router para WebSocket
router = APIRouter()

@router.websocket("/ws/extension")
async def websocket_extension(websocket: WebSocket):
    """WebSocket para comunicación con extensiones"""
    connection_id = await connection_manager.connect(websocket, "extension")
    
    try:
        while True:
            # Recibir mensaje
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Manejar mensaje
            await connection_manager.handle_extension_message(websocket, message)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info(f"🔌 Extensión desconectada: {connection_id}")
    except Exception as e:
        logger.error(f"❌ Error en WebSocket de extensión: {e}")
        connection_manager.disconnect(websocket)

@router.websocket("/ws/client")
async def websocket_client(websocket: WebSocket):
    """WebSocket para comunicación con clientes web"""
    await connection_manager.connect(websocket, "client")
    
    try:
        while True:
            # Recibir mensaje
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Reenviar a extensiones si es necesario
            if message.get("target") == "extension":
                await connection_manager.send_to_extension(message)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info("🔌 Cliente desconectado")
    except Exception as e:
        logger.error(f"❌ Error en WebSocket de cliente: {e}")
        connection_manager.disconnect(websocket)

# Funciones de utilidad para enviar mensajes
async def send_to_suno_extensions(message: Dict[str, Any]):
    """Enviar mensaje a todas las extensiones de Suno"""
    return await connection_manager.send_to_extension(message)

async def send_to_all_clients(message: Dict[str, Any]):
    """Enviar mensaje a todos los clientes"""
    return await connection_manager.send_to_all(message)

# Función para solicitar generación desde Suno
async def request_suno_generation(prompt: str, lyrics: str = "", style: str = "synthwave"):
    """Solicitar generación de música desde Suno"""
    message = {
        "type": "generation_request",
        "data": {
            "prompt": prompt,
            "lyrics": lyrics,
            "style": style,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    return await send_to_suno_extensions(message)

