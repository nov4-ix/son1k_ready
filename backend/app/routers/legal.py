#!/usr/bin/env python3
"""
Rutas legales para Son1k
Manejo de términos, privacidad y consentimientos
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..models import User
from ..database import get_db

router = APIRouter(prefix="/api/legal", tags=["legal"])

# Términos y condiciones actual
CURRENT_TERMS_VERSION = "1.0"
CURRENT_PRIVACY_VERSION = "1.0"

# Fecha de última actualización
TERMS_LAST_UPDATED = "2025-09-20"
PRIVACY_LAST_UPDATED = "2025-09-20"

@router.get("/terms/version")
async def get_terms_version():
    """Obtener versión actual de términos y condiciones"""
    return {
        "version": CURRENT_TERMS_VERSION,
        "last_updated": TERMS_LAST_UPDATED,
        "effective_date": TERMS_LAST_UPDATED
    }

@router.get("/privacy/version")
async def get_privacy_version():
    """Obtener versión actual de política de privacidad"""
    return {
        "version": CURRENT_PRIVACY_VERSION,
        "last_updated": PRIVACY_LAST_UPDATED,
        "effective_date": PRIVACY_LAST_UPDATED
    }

@router.post("/consent/terms")
async def accept_terms(
    user_id: str,
    version: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Registrar aceptación de términos y condiciones"""
    
    if not version:
        version = CURRENT_TERMS_VERSION
    
    try:
        # Buscar usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Registrar consentimiento
        consent_data = {
            "terms_version": version,
            "accepted_at": datetime.now().isoformat(),
            "ip_address": "0.0.0.0",  # En producción, obtener IP real
            "user_agent": "unknown"  # En producción, obtener user agent real
        }
        
        # Actualizar metadatos del usuario (simular registro de consentimiento)
        # En producción, esto se guardaría en una tabla separada de consentimientos
        logging.info(f"Usuario {user_id} aceptó términos v{version}")
        
        return {
            "success": True,
            "message": "Términos aceptados exitosamente",
            "version": version,
            "accepted_at": consent_data["accepted_at"]
        }
        
    except Exception as e:
        logging.error(f"Error recording terms consent: {e}")
        raise HTTPException(status_code=500, detail="Error al registrar aceptación")

@router.post("/consent/privacy")
async def accept_privacy(
    user_id: str,
    version: Optional[str] = None,
    marketing_consent: bool = False,
    analytics_consent: bool = True,
    db: Session = Depends(get_db)
):
    """Registrar aceptación de política de privacidad y consentimientos específicos"""
    
    if not version:
        version = CURRENT_PRIVACY_VERSION
    
    try:
        # Buscar usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Registrar consentimientos
        consent_data = {
            "privacy_version": version,
            "marketing_consent": marketing_consent,
            "analytics_consent": analytics_consent,
            "accepted_at": datetime.now().isoformat(),
            "ip_address": "0.0.0.0",  # En producción, obtener IP real
            "user_agent": "unknown"  # En producción, obtener user agent real
        }
        
        logging.info(f"Usuario {user_id} aceptó privacidad v{version} - Marketing: {marketing_consent}, Analytics: {analytics_consent}")
        
        return {
            "success": True,
            "message": "Política de privacidad aceptada exitosamente",
            "version": version,
            "consents": {
                "marketing": marketing_consent,
                "analytics": analytics_consent
            },
            "accepted_at": consent_data["accepted_at"]
        }
        
    except Exception as e:
        logging.error(f"Error recording privacy consent: {e}")
        raise HTTPException(status_code=500, detail="Error al registrar aceptación")

@router.get("/consent/{user_id}")
async def get_user_consents(user_id: str, db: Session = Depends(get_db)):
    """Obtener estado de consentimientos del usuario"""
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # En producción, esto vendría de una tabla de consentimientos
        # Por ahora, simulamos datos
        return {
            "user_id": user_id,
            "terms": {
                "accepted": True,
                "version": CURRENT_TERMS_VERSION,
                "accepted_at": user.created_at.isoformat(),
                "current_version": CURRENT_TERMS_VERSION,
                "needs_update": False
            },
            "privacy": {
                "accepted": True,
                "version": CURRENT_PRIVACY_VERSION,
                "accepted_at": user.created_at.isoformat(),
                "current_version": CURRENT_PRIVACY_VERSION,
                "needs_update": False,
                "marketing_consent": False,
                "analytics_consent": True
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting user consents: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener consentimientos")

@router.post("/consent/revoke")
async def revoke_consent(
    user_id: str,
    consent_type: str,  # 'marketing', 'analytics', 'all'
    db: Session = Depends(get_db)
):
    """Revocar consentimientos específicos"""
    
    valid_types = ['marketing', 'analytics', 'all']
    if consent_type not in valid_types:
        raise HTTPException(status_code=400, detail="Tipo de consentimiento inválido")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        revoked_consents = []
        
        if consent_type == 'marketing' or consent_type == 'all':
            revoked_consents.append('marketing')
            
        if consent_type == 'analytics' or consent_type == 'all':
            revoked_consents.append('analytics')
        
        logging.info(f"Usuario {user_id} revocó consentimientos: {revoked_consents}")
        
        return {
            "success": True,
            "message": f"Consentimientos revocados: {', '.join(revoked_consents)}",
            "revoked": revoked_consents,
            "revoked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error revoking consent: {e}")
        raise HTTPException(status_code=500, detail="Error al revocar consentimiento")

@router.get("/data-retention")
async def get_data_retention_policy():
    """Obtener política de retención de datos"""
    
    return {
        "retention_periods": {
            "account_data": "Mientras la cuenta esté activa + 30 días",
            "billing_data": "7 años (requisitos fiscales)",
            "generated_music": "90 días después de la generación",
            "usage_logs": "12 meses",
            "marketing_data": "Hasta revocación del consentimiento"
        },
        "deletion_process": {
            "automatic": "Sistemas automatizados eliminan datos cuando expiran",
            "manual": "Solicitar eliminación manual en privacy@son1kvers3.com",
            "verification": "Verificamos identidad antes de eliminar datos",
            "timeframe": "Eliminación completada dentro de 30 días"
        },
        "exceptions": {
            "legal_requirements": "Algunos datos pueden retenerse por obligaciones legales",
            "security": "Logs de seguridad pueden retenerse hasta 2 años",
            "fraud_prevention": "Datos de prevención de fraude según regulaciones"
        }
    }

@router.post("/data-request")
async def request_data_export(
    user_id: str,
    request_type: str,  # 'export', 'delete', 'correct'
    details: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Solicitar exportación, eliminación o corrección de datos"""
    
    valid_types = ['export', 'delete', 'correct']
    if request_type not in valid_types:
        raise HTTPException(status_code=400, detail="Tipo de solicitud inválido")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Generar ID de solicitud
        request_id = f"DR_{request_type.upper()}_{int(datetime.now().timestamp())}"
        
        # En producción, esto se guardaría en una tabla de solicitudes
        request_data = {
            "request_id": request_id,
            "user_id": user_id,
            "type": request_type,
            "details": details,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "estimated_completion": "5 días hábiles"
        }
        
        logging.info(f"Solicitud de datos creada: {request_id} para usuario {user_id}")
        
        # Enviar email de confirmación (simular)
        email_sent = True
        
        return {
            "success": True,
            "request_id": request_id,
            "status": "pending",
            "message": f"Solicitud de {request_type} de datos creada exitosamente",
            "estimated_completion": "5 días hábiles",
            "next_steps": [
                "Recibirás un email de confirmación",
                "Verificaremos tu identidad",
                "Procesaremos la solicitud",
                "Te notificaremos cuando esté completada"
            ],
            "contact": "privacy@son1kvers3.com para consultas"
        }
        
    except Exception as e:
        logging.error(f"Error creating data request: {e}")
        raise HTTPException(status_code=500, detail="Error al crear solicitud")

@router.get("/compliance")
async def get_compliance_info():
    """Información sobre cumplimiento de regulaciones"""
    
    return {
        "regulations": {
            "GDPR": {
                "applicable": True,
                "scope": "Usuarios en la Unión Europea",
                "rights": ["acceso", "rectificación", "borrado", "restricción", "portabilidad", "oposición"],
                "dpo_contact": "dpo@son1kvers3.com"
            },
            "CCPA": {
                "applicable": True,
                "scope": "Residentes de California",
                "rights": ["conocer", "eliminar", "optar por no vender", "no discriminación"],
                "contact": "privacy@son1kvers3.com"
            },
            "PIPEDA": {
                "applicable": True,
                "scope": "Usuarios canadienses",
                "contact": "privacy@son1kvers3.com"
            }
        },
        "certifications": {
            "SOC2": "En proceso",
            "ISO27001": "Planificado para 2026",
            "Privacy_Shield": "No aplicable (programa terminado)"
        },
        "security": {
            "encryption_in_transit": "TLS 1.3",
            "encryption_at_rest": "AES-256",
            "access_controls": "Basado en roles",
            "monitoring": "24/7",
            "incident_response": "Plan documentado"
        },
        "audits": {
            "frequency": "Anual",
            "last_audit": "2025-01-15",
            "next_audit": "2026-01-15",
            "external_auditor": "Firma certificada"
        }
    }

@router.get("/contact")
async def get_legal_contacts():
    """Información de contacto legal"""
    
    return {
        "privacy_officer": {
            "email": "privacy@son1kvers3.com",
            "response_time": "5 días hábiles",
            "languages": ["español", "inglés"]
        },
        "data_protection_officer": {
            "email": "dpo@son1kvers3.com",
            "response_time": "5 días hábiles",
            "scope": "Usuarios de la UE"
        },
        "legal_department": {
            "email": "legal@son1kvers3.com",
            "response_time": "7 días hábiles",
            "matters": ["términos", "licencias", "disputas"]
        },
        "compliance": {
            "email": "compliance@son1kvers3.com",
            "response_time": "3 días hábiles",
            "matters": ["auditorías", "regulaciones", "reportes"]
        },
        "postal_address": {
            "company": "Son1k Inc.",
            "address": "Delaware, Estados Unidos",
            "attention": "Departamento Legal"
        }
    }

@router.get("/changelog")
async def get_legal_changelog():
    """Historial de cambios en documentos legales"""
    
    return {
        "terms_and_conditions": [
            {
                "version": "1.0",
                "date": "2025-09-20",
                "changes": ["Versión inicial"],
                "effective_date": "2025-09-20"
            }
        ],
        "privacy_policy": [
            {
                "version": "1.0", 
                "date": "2025-09-20",
                "changes": ["Versión inicial"],
                "effective_date": "2025-09-20"
            }
        ],
        "notification_policy": {
            "minor_changes": "Notificación en el sitio web",
            "major_changes": "Email con 30 días de anticipación",
            "substantial_changes": "Consentimiento explícito requerido"
        }
    }