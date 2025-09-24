#!/usr/bin/env python3
"""
Middleware de Autenticación para Son1kVers3
- Manejo de sesiones y tokens
- Verificación de límites de generación
- Roles y permisos
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt
import secrets
from datetime import datetime, timedelta
from user_manager import UserManager, UserRole

# Configuración JWT
SECRET_KEY = "son1kvers3_secret_key_2024_music_generation"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 horas

security = HTTPBearer()
user_manager = UserManager()

class AuthManager:
    def __init__(self):
        self.user_manager = UserManager()
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Crear token de acceso JWT"""
        to_encode = user_data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Token inválido")
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuario con email y contraseña"""
        user = self.user_manager.authenticate_user(email, password)
        if not user:
            return None
        
        # Crear token
        token_data = {
            "user_id": user["user_id"],
            "email": user["email"],
            "role": user["role"],
            "api_key": user["api_key"]
        }
        access_token = self.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Obtener usuario actual desde token"""
        token = credentials.credentials
        payload = self.verify_token(token)
        
        # Obtener datos actualizados del usuario
        user = self.user_manager.get_user_by_api_key(payload.get("api_key"))
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return user
    
    def check_generation_permission(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Verificar permisos de generación"""
        return self.user_manager.check_generation_limit(user["user_id"])
    
    def is_admin(self, user: Dict[str, Any]) -> bool:
        """Verificar si el usuario es administrador"""
        return user.get("role") == UserRole.ADMIN.value
    
    def is_pro_or_enterprise(self, user: Dict[str, Any]) -> bool:
        """Verificar si el usuario es pro o enterprise"""
        role = user.get("role")
        return role in [UserRole.PRO_TESTER.value, UserRole.ENTERPRISE_TESTER.value]

# Instancia global
auth_manager = AuthManager()

# Dependencias de FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependencia para obtener usuario actual"""
    return auth_manager.get_current_user(credentials)

async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Dependencia para obtener usuario administrador"""
    if not auth_manager.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
    return current_user

async def get_pro_or_enterprise_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Dependencia para obtener usuario pro o enterprise"""
    if not auth_manager.is_pro_or_enterprise(current_user):
        raise HTTPException(status_code=403, detail="Se requiere cuenta Pro o Enterprise")
    return current_user

# Funciones de utilidad
def check_generation_limits(user: Dict[str, Any]) -> Dict[str, Any]:
    """Verificar límites de generación del usuario"""
    return auth_manager.check_generation_permission(user)

def increment_generation_count(user: Dict[str, Any]) -> bool:
    """Incrementar contador de generaciones del usuario"""
    return auth_manager.user_manager.increment_generation_count(user["user_id"])

# Modelos Pydantic para autenticación
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class UserStatsResponse(BaseModel):
    email: str
    role: str
    generation_limit: int
    generations_used: int
    remaining: str
    is_active: bool
