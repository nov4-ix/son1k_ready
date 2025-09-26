#!/usr/bin/env python3
"""
Resistance Social Network Backend
Santuario - Red Social de la Resistencia para Son1kVers3
Solo para miembros Pro y Premium
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import sqlite3
import asyncio
import random
from datetime import datetime, timedelta
import uuid

app = FastAPI(title="Resistance Social Network API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_database():
    conn = sqlite3.connect('resistance_social.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resistance_members (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            plan TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            rank TEXT DEFAULT 'Recruit',
            online_status TEXT DEFAULT 'offline',
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resistance_messages (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_type TEXT DEFAULT 'chat',
            FOREIGN KEY (user_id) REFERENCES resistance_members (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collaborations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            creator_id TEXT NOT NULL,
            members_required INTEGER NOT NULL,
            current_members INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES resistance_members (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            reward_xp INTEGER NOT NULL,
            status TEXT DEFAULT 'planned',
            scheduled_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resistance_stats (
            id INTEGER PRIMARY KEY,
            pro_members INTEGER DEFAULT 0,
            premium_members INTEGER DEFAULT 0,
            online_members INTEGER DEFAULT 0,
            active_operations INTEGER DEFAULT 0,
            completed_operations INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            active_collaborations INTEGER DEFAULT 0,
            completed_collaborations INTEGER DEFAULT 0,
            threat_level TEXT DEFAULT 'MODERATE',
            detections INTEGER DEFAULT 0,
            protection_level INTEGER DEFAULT 85,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default stats if not exists
    cursor.execute('SELECT COUNT(*) FROM resistance_stats')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO resistance_stats (
                pro_members, premium_members, online_members,
                active_operations, completed_operations, success_rate,
                active_collaborations, completed_collaborations,
                threat_level, detections, protection_level
            ) VALUES (247, 89, 23, 12, 156, 94.2, 8, 43, 'ALTO', 3, 87)
        ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Pydantic models
class ResistanceMessage(BaseModel):
    message: str
    user_id: str
    user_plan: str
    context: str = "resistance_social"

class CollaborationCreate(BaseModel):
    name: str
    description: str
    type: str
    members_required: int
    creator_id: str
    creator_plan: str

class ResistanceMember(BaseModel):
    username: str
    display_name: str
    plan: str
    level: int = 1
    xp: int = 0
    rank: str = "Recruit"

# Resistance AI responses
RESISTANCE_RESPONSES = [
    "Operación recibida. Coordinando con otros miembros de la resistencia.",
    "XentriX detecta actividad sospechosa. Implementando contramedidas.",
    "Nuevo algoritmo de evasión desplegado exitosamente.",
    "Colaboración disponible. Revisando compatibilidad de miembros.",
    "Análisis de amenaza completado. Vulnerabilidades identificadas.",
    "Protocolo de resistencia activado. Manteniendo comunicación segura.",
    "Sistema de encriptación actualizado. Comunicaciones protegidas.",
    "Inteligencia recopilada. Preparando siguiente fase de operación.",
    "Red de resistencia fortalecida. Nuevos miembros integrados.",
    "Contramedidas desplegadas. XentriX neutralizado temporalmente."
]

# Resistance ranks
RESISTANCE_RANKS = [
    "Recruit", "Private", "Corporal", "Sergeant", "Lieutenant",
    "Captain", "Major", "Colonel", "Resistance Commander", "General"
]

@app.get("/api/resistance/status")
async def get_resistance_status():
    """Get current resistance network status"""
    try:
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resistance_stats ORDER BY last_updated DESC LIMIT 1')
        stats = cursor.fetchone()
        
        if stats:
            return {
                "status": "success",
                "pro_members": stats[1],
                "premium_members": stats[2],
                "online_members": stats[3],
                "total_members": stats[1] + stats[2],
                "active_operations": stats[4],
                "completed_operations": stats[5],
                "success_rate": f"{stats[6]:.1f}%",
                "next_operation": "En 2h",
                "active_collaborations": stats[7],
                "completed_collaborations": stats[8],
                "collaboration_rate": "+23%",
                "pending_collaborations": 5,
                "threat_level": stats[9],
                "detections": stats[10],
                "countermeasures": "ACTIVAS",
                "protection_level": f"{stats[11]}%"
            }
        else:
            return {
                "status": "success",
                "pro_members": 247,
                "premium_members": 89,
                "online_members": 23,
                "total_members": 336,
                "active_operations": 12,
                "completed_operations": 156,
                "success_rate": "94.2%",
                "next_operation": "En 2h",
                "active_collaborations": 8,
                "completed_collaborations": 43,
                "collaboration_rate": "+23%",
                "pending_collaborations": 5,
                "threat_level": "ALTO",
                "detections": 3,
                "countermeasures": "ACTIVAS",
                "protection_level": "87%"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        if 'conn' in locals():
            conn.close()

@app.post("/api/resistance/chat")
async def resistance_chat(message_data: ResistanceMessage):
    """Handle resistance chat messages"""
    try:
        # Check if user has Pro or Premium access
        if message_data.user_plan not in ['Pro', 'Premium']:
            return {
                "status": "error",
                "error": "Solo miembros Pro y Premium pueden acceder al Santuario"
            }
        
        # Generate AI response
        ai_response = random.choice(RESISTANCE_RESPONSES)
        
        # Store message in database
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        message_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO resistance_messages (id, user_id, message, message_type)
            VALUES (?, ?, ?, ?)
        ''', (message_id, message_data.user_id, message_data.message, 'chat'))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "response": ai_response,
            "message_id": message_id
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/resistance/create-collaboration")
async def create_collaboration(collab_data: CollaborationCreate):
    """Create a new collaboration"""
    try:
        # Check if user has Pro or Premium access
        if collab_data.creator_plan not in ['Pro', 'Premium']:
            return {
                "status": "error",
                "error": "Solo miembros Pro y Premium pueden crear colaboraciones"
            }
        
        # Create collaboration
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        collab_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO collaborations (
                id, name, description, type, creator_id, members_required, current_members
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (
            collab_id, collab_data.name, collab_data.description,
            collab_data.type, collab_data.creator_id, collab_data.members_required
        ))
        
        # Update stats
        cursor.execute('''
            UPDATE resistance_stats 
            SET active_collaborations = active_collaborations + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
        ''')
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "collaboration_id": collab_id,
            "message": "Colaboración creada exitosamente"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/resistance/collaborations")
async def get_collaborations():
    """Get active collaborations"""
    try:
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, m.display_name as creator_name
            FROM collaborations c
            JOIN resistance_members m ON c.creator_id = m.id
            WHERE c.status = 'active'
            ORDER BY c.created_at DESC
        ''')
        
        collaborations = []
        for row in cursor.fetchall():
            collaborations.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "type": row[3],
                "creator_name": row[8],
                "members_required": row[5],
                "current_members": row[6],
                "created_at": row[7]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "collaborations": collaborations
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/resistance/operations")
async def get_operations():
    """Get resistance operations"""
    try:
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM operations 
            WHERE status IN ('planned', 'active')
            ORDER BY scheduled_time ASC
        ''')
        
        operations = []
        for row in cursor.fetchall():
            operations.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "difficulty": row[3],
                "reward_xp": row[4],
                "status": row[5],
                "scheduled_time": row[6]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "operations": operations
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/resistance/members/online")
async def get_online_members():
    """Get online resistance members"""
    try:
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT display_name, online_status, last_seen
            FROM resistance_members
            WHERE online_status = 'online'
            ORDER BY last_seen DESC
            LIMIT 10
        ''')
        
        members = []
        for row in cursor.fetchall():
            members.append({
                "name": row[0],
                "status": row[1],
                "last_seen": row[2]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "members": members
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/resistance/join-collaboration/{collab_id}")
async def join_collaboration(collab_id: str, user_id: str):
    """Join a collaboration"""
    try:
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        # Check if collaboration exists and has space
        cursor.execute('''
            SELECT members_required, current_members FROM collaborations
            WHERE id = ? AND status = 'active'
        ''', (collab_id,))
        
        result = cursor.fetchone()
        if not result:
            return {
                "status": "error",
                "error": "Colaboración no encontrada o inactiva"
            }
        
        members_required, current_members = result
        if current_members >= members_required:
            return {
                "status": "error",
                "error": "Colaboración llena"
            }
        
        # Add member to collaboration
        cursor.execute('''
            UPDATE collaborations 
            SET current_members = current_members + 1
            WHERE id = ?
        ''', (collab_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Te has unido a la colaboración exitosamente"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/resistance/leaderboard")
async def get_leaderboard():
    """Get resistance leaderboard"""
    try:
        conn = sqlite3.connect('resistance_social.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT display_name, xp, level, rank
            FROM resistance_members
            ORDER BY xp DESC
            LIMIT 10
        ''')
        
        leaderboard = []
        for i, row in enumerate(cursor.fetchall(), 1):
            leaderboard.append({
                "rank": i,
                "name": row[0],
                "xp": row[1],
                "level": row[2],
                "rank_title": row[3]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "leaderboard": leaderboard
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

