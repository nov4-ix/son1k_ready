#!/usr/bin/env python3
"""
📊 SON1KVERS3 - Analytics System
Sistema de analytics para tracking de uso y métricas
"""

import json
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import uuid
import hashlib

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MusicGenerationEvent:
    """Evento de generación musical"""
    id: str
    user_id: str
    prompt: str
    style: str
    duration: float
    tempo: int
    scale: str
    instruments: List[str]
    mood: str
    ai_enhanced: bool
    generation_time: float
    success: bool
    error_message: Optional[str]
    timestamp: datetime
    ip_address: str
    user_agent: str

@dataclass
class UserSession:
    """Sesión de usuario"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    page_views: int
    music_generations: int
    ai_usage: int
    total_time: float
    ip_address: str
    user_agent: str

@dataclass
class UserInteraction:
    """Interacción del usuario"""
    id: str
    session_id: str
    user_id: str
    action: str
    element: str
    value: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class AnalyticsDatabase:
    """Base de datos para analytics"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de eventos de generación musical
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS music_generations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                style TEXT NOT NULL,
                duration REAL NOT NULL,
                tempo INTEGER NOT NULL,
                scale TEXT NOT NULL,
                instruments TEXT NOT NULL,
                mood TEXT NOT NULL,
                ai_enhanced BOOLEAN NOT NULL,
                generation_time REAL NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                timestamp DATETIME NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL
            )
        ''')
        
        # Tabla de sesiones de usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                page_views INTEGER DEFAULT 0,
                music_generations INTEGER DEFAULT 0,
                ai_usage INTEGER DEFAULT 0,
                total_time REAL DEFAULT 0,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL
            )
        ''')
        
        # Tabla de interacciones de usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                element TEXT NOT NULL,
                value TEXT,
                timestamp DATETIME NOT NULL,
                metadata TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
            )
        ''')
        
        # Tabla de métricas agregadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aggregated_metrics (
                date TEXT PRIMARY KEY,
                total_generations INTEGER DEFAULT 0,
                successful_generations INTEGER DEFAULT 0,
                failed_generations INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0,
                avg_generation_time REAL DEFAULT 0,
                ai_usage_count INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                avg_session_duration REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Base de datos de analytics inicializada")
    
    def save_music_generation(self, event: MusicGenerationEvent):
        """Guardar evento de generación musical"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO music_generations 
            (id, user_id, prompt, style, duration, tempo, scale, instruments, 
             mood, ai_enhanced, generation_time, success, error_message, 
             timestamp, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.id, event.user_id, event.prompt, event.style, event.duration,
            event.tempo, event.scale, json.dumps(event.instruments), event.mood,
            event.ai_enhanced, event.generation_time, event.success, event.error_message,
            event.timestamp.isoformat(), event.ip_address, event.user_agent
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"📊 Evento de generación guardado: {event.id}")
    
    def save_user_session(self, session: UserSession):
        """Guardar sesión de usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions
            (session_id, user_id, start_time, end_time, page_views, 
             music_generations, ai_usage, total_time, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id, session.user_id, session.start_time.isoformat(),
            session.end_time.isoformat() if session.end_time else None,
            session.page_views, session.music_generations, session.ai_usage,
            session.total_time, session.ip_address, session.user_agent
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"📊 Sesión guardada: {session.session_id}")
    
    def save_user_interaction(self, interaction: UserInteraction):
        """Guardar interacción de usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_interactions
            (id, session_id, user_id, action, element, value, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction.id, interaction.session_id, interaction.user_id,
            interaction.action, interaction.element, interaction.value,
            interaction.timestamp.isoformat(), json.dumps(interaction.metadata)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"📊 Interacción guardada: {interaction.id}")
    
    def get_analytics_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Obtener datos de analytics para un rango de fechas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Métricas de generación musical
        cursor.execute('''
            SELECT 
                COUNT(*) as total_generations,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_generations,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_generations,
                AVG(duration) as avg_duration,
                AVG(generation_time) as avg_generation_time,
                SUM(CASE WHEN ai_enhanced = 1 THEN 1 ELSE 0 END) as ai_usage_count
            FROM music_generations
            WHERE timestamp BETWEEN ? AND ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        music_metrics = cursor.fetchone()
        
        # Métricas de sesiones
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(total_time) as avg_session_duration
            FROM user_sessions
            WHERE start_time BETWEEN ? AND ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        session_metrics = cursor.fetchone()
        
        # Estilos más populares
        cursor.execute('''
            SELECT style, COUNT(*) as count
            FROM music_generations
            WHERE timestamp BETWEEN ? AND ? AND success = 1
            GROUP BY style
            ORDER BY count DESC
            LIMIT 10
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        popular_styles = cursor.fetchall()
        
        # Prompts más populares
        cursor.execute('''
            SELECT prompt, COUNT(*) as count
            FROM music_generations
            WHERE timestamp BETWEEN ? AND ? AND success = 1
            GROUP BY prompt
            ORDER BY count DESC
            LIMIT 10
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        popular_prompts = cursor.fetchall()
        
        # Uso de IA por día
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM music_generations
            WHERE timestamp BETWEEN ? AND ? AND ai_enhanced = 1
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        ai_usage_by_day = cursor.fetchall()
        
        conn.close()
        
        return {
            'music_metrics': {
                'total_generations': music_metrics[0] or 0,
                'successful_generations': music_metrics[1] or 0,
                'failed_generations': music_metrics[2] or 0,
                'avg_duration': music_metrics[3] or 0,
                'avg_generation_time': music_metrics[4] or 0,
                'ai_usage_count': music_metrics[5] or 0
            },
            'session_metrics': {
                'total_sessions': session_metrics[0] or 0,
                'unique_users': session_metrics[1] or 0,
                'avg_session_duration': session_metrics[2] or 0
            },
            'popular_styles': [{'style': style, 'count': count} for style, count in popular_styles],
            'popular_prompts': [{'prompt': prompt, 'count': count} for prompt, count in popular_prompts],
            'ai_usage_by_day': [{'date': date, 'count': count} for date, count in ai_usage_by_day]
        }

class AnalyticsCollector:
    """Recolector de analytics"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db = AnalyticsDatabase(db_path)
        self.active_sessions = {}
        self.session_timeouts = {}
    
    def start_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Iniciar nueva sesión"""
        session_id = str(uuid.uuid4())
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
            end_time=None,
            page_views=0,
            music_generations=0,
            ai_usage=0,
            total_time=0,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.active_sessions[session_id] = session
        self.db.save_user_session(session)
        
        # Configurar timeout de sesión (30 minutos)
        self.session_timeouts[session_id] = asyncio.create_task(
            self._session_timeout(session_id)
        )
        
        logger.info(f"📊 Nueva sesión iniciada: {session_id}")
        return session_id
    
    def end_session(self, session_id: str):
        """Finalizar sesión"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.end_time = datetime.now()
            session.total_time = (session.end_time - session.start_time).total_seconds()
            
            self.db.save_user_session(session)
            del self.active_sessions[session_id]
            
            if session_id in self.session_timeouts:
                self.session_timeouts[session_id].cancel()
                del self.session_timeouts[session_id]
            
            logger.info(f"📊 Sesión finalizada: {session_id}")
    
    def track_music_generation(self, session_id: str, user_id: str, prompt: str, 
                             style: str, duration: float, tempo: int, scale: str,
                             instruments: List[str], mood: str, ai_enhanced: bool,
                             generation_time: float, success: bool, 
                             error_message: Optional[str], ip_address: str, 
                             user_agent: str) -> str:
        """Rastrear generación musical"""
        event_id = str(uuid.uuid4())
        event = MusicGenerationEvent(
            id=event_id,
            user_id=user_id,
            prompt=prompt,
            style=style,
            duration=duration,
            tempo=tempo,
            scale=scale,
            instruments=instruments,
            mood=mood,
            ai_enhanced=ai_enhanced,
            generation_time=generation_time,
            success=success,
            error_message=error_message,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.save_music_generation(event)
        
        # Actualizar sesión
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.music_generations += 1
            if ai_enhanced:
                session.ai_usage += 1
            self.db.save_user_session(session)
        
        logger.info(f"📊 Generación musical rastreada: {event_id}")
        return event_id
    
    def track_interaction(self, session_id: str, user_id: str, action: str, 
                         element: str, value: Optional[str] = None, 
                         metadata: Dict[str, Any] = None) -> str:
        """Rastrear interacción de usuario"""
        interaction_id = str(uuid.uuid4())
        interaction = UserInteraction(
            id=interaction_id,
            session_id=session_id,
            user_id=user_id,
            action=action,
            element=element,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.db.save_user_interaction(interaction)
        
        # Actualizar sesión
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if action == 'page_view':
                session.page_views += 1
            self.db.save_user_session(session)
        
        logger.info(f"📊 Interacción rastreada: {interaction_id}")
        return interaction_id
    
    async def _session_timeout(self, session_id: str):
        """Timeout de sesión"""
        await asyncio.sleep(1800)  # 30 minutos
        if session_id in self.active_sessions:
            self.end_session(session_id)
    
    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Obtener analytics de los últimos N días"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return self.db.get_analytics_data(start_date, end_date)

class AnalyticsServer:
    """Servidor HTTP para analytics"""
    
    def __init__(self, host: str = "localhost", port: int = 8002):
        self.host = host
        self.port = port
        self.collector = AnalyticsCollector()
        self.app = None
        
    def init(self):
        """Inicializar servidor"""
        from aiohttp import web
        
        self.app = web.Application()
        self.app.router.add_post('/api/track/generation', self.track_generation_endpoint)
        self.app.router.add_post('/api/track/interaction', self.track_interaction_endpoint)
        self.app.router.add_post('/api/session/start', self.start_session_endpoint)
        self.app.router.add_post('/api/session/end', self.end_session_endpoint)
        self.app.router.add_get('/api/analytics', self.analytics_endpoint)
        self.app.router.add_get('/api/health', self.health_endpoint)
        
        return self.app
    
    async def track_generation_endpoint(self, request):
        """Endpoint para rastrear generación musical"""
        try:
            data = await request.json()
            
            event_id = self.collector.track_music_generation(
                session_id=data.get('session_id'),
                user_id=data.get('user_id'),
                prompt=data.get('prompt'),
                style=data.get('style'),
                duration=data.get('duration'),
                tempo=data.get('tempo'),
                scale=data.get('scale'),
                instruments=data.get('instruments', []),
                mood=data.get('mood'),
                ai_enhanced=data.get('ai_enhanced', False),
                generation_time=data.get('generation_time'),
                success=data.get('success', True),
                error_message=data.get('error_message'),
                ip_address=request.remote,
                user_agent=request.headers.get('User-Agent', '')
            )
            
            return web.json_response({
                'success': True,
                'event_id': event_id,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def track_interaction_endpoint(self, request):
        """Endpoint para rastrear interacciones"""
        try:
            data = await request.json()
            
            interaction_id = self.collector.track_interaction(
                session_id=data.get('session_id'),
                user_id=data.get('user_id'),
                action=data.get('action'),
                element=data.get('element'),
                value=data.get('value'),
                metadata=data.get('metadata', {})
            )
            
            return web.json_response({
                'success': True,
                'interaction_id': interaction_id,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def start_session_endpoint(self, request):
        """Endpoint para iniciar sesión"""
        try:
            data = await request.json()
            
            session_id = self.collector.start_session(
                user_id=data.get('user_id'),
                ip_address=request.remote,
                user_agent=request.headers.get('User-Agent', '')
            )
            
            return web.json_response({
                'success': True,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def end_session_endpoint(self, request):
        """Endpoint para finalizar sesión"""
        try:
            data = await request.json()
            session_id = data.get('session_id')
            
            self.collector.end_session(session_id)
            
            return web.json_response({
                'success': True,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def analytics_endpoint(self, request):
        """Endpoint para obtener analytics"""
        try:
            days = int(request.query.get('days', 7))
            analytics_data = self.collector.get_analytics(days)
            
            return web.json_response({
                'success': True,
                'data': analytics_data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def health_endpoint(self, request):
        """Endpoint de salud"""
        return web.json_response({
            'status': 'healthy',
            'active_sessions': len(self.collector.active_sessions),
            'timestamp': datetime.now().isoformat()
        })

def main():
    """Función principal para ejecutar el servidor"""
    from aiohttp import web
    
    server = AnalyticsServer()
    app = server.init()
    
    print(f"📊 Iniciando servidor de analytics en http://{server.host}:{server.port}")
    web.run_app(app, host=server.host, port=server.port)

if __name__ == "__main__":
    main()
