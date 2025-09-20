#!/usr/bin/env python3
"""
Sistema de Pagos para Son1k
Integración con Stripe para planes de suscripción
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import stripe
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from ..models import User, Subscription, Payment
from ..database import get_db
import json

# Configuración de Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Planes de suscripción
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Plan Gratuito",
        "price": 0,
        "credits_per_month": 3,
        "max_duration": 60,  # segundos
        "features": ["3 canciones por mes", "Duración máxima 60s", "Calidad estándar"]
    },
    "basic": {
        "name": "Plan Básico", 
        "price": 9.99,
        "stripe_price_id": "price_basic_monthly",  # Se configura en Stripe
        "credits_per_month": 50,
        "max_duration": 180,
        "features": ["50 canciones por mes", "Duración máxima 3min", "Calidad alta", "Sin marca de agua"]
    },
    "pro": {
        "name": "Plan Pro",
        "price": 19.99, 
        "stripe_price_id": "price_pro_monthly",
        "credits_per_month": 200,
        "max_duration": 300,
        "features": ["200 canciones por mes", "Duración máxima 5min", "Calidad premium", "Descarga en múltiples formatos", "Uso comercial"]
    },
    "unlimited": {
        "name": "Plan Ilimitado",
        "price": 49.99,
        "stripe_price_id": "price_unlimited_monthly", 
        "credits_per_month": -1,  # Ilimitado
        "max_duration": 600,
        "features": ["Canciones ilimitadas", "Duración máxima 10min", "Calidad premium", "Uso comercial", "API access", "Soporte prioritario"]
    }
}

@router.get("/plans")
async def get_subscription_plans():
    """Obtener todos los planes disponibles"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY
    }

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    plan_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Crear sesión de checkout de Stripe"""
    
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Plan no válido")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    if plan_id == "free":
        raise HTTPException(status_code=400, detail="Plan gratuito no requiere pago")
    
    try:
        # Crear sesión de checkout en Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"https://son1kvers3.com/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="https://son1kvers3.com/cancel",
            client_reference_id=user_id,
            metadata={
                'user_id': user_id,
                'plan_id': plan_id
            }
        )
        
        return {"checkout_url": checkout_session.url}
        
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Error al crear sesión de pago")

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook de Stripe para manejar eventos de pago"""
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Manejar diferentes tipos de eventos
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_successful_payment(session, db)
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        await handle_subscription_update(subscription, db)
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancellation(subscription, db)
        
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        await handle_recurring_payment(invoice, db)
        
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        await handle_payment_failure(invoice, db)
    
    return {"status": "success"}

async def handle_successful_payment(session: Dict[str, Any], db: Session):
    """Manejar pago exitoso"""
    user_id = session['client_reference_id']
    plan_id = session['metadata']['plan_id']
    
    # Actualizar suscripción del usuario
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Crear o actualizar suscripción
        subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        
        if not subscription:
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                stripe_subscription_id=session['subscription'],
                status='active',
                current_period_start=datetime.now(),
                current_period_end=datetime.now() + timedelta(days=30),
                credits_remaining=SUBSCRIPTION_PLANS[plan_id]['credits_per_month']
            )
            db.add(subscription)
        else:
            subscription.plan_id = plan_id
            subscription.stripe_subscription_id = session['subscription']
            subscription.status = 'active'
            subscription.current_period_start = datetime.now()
            subscription.current_period_end = datetime.now() + timedelta(days=30)
            subscription.credits_remaining = SUBSCRIPTION_PLANS[plan_id]['credits_per_month']
        
        # Registrar pago
        payment = Payment(
            user_id=user_id,
            stripe_payment_id=session['payment_intent'],
            amount=session['amount_total'] / 100,  # Stripe usa centavos
            currency=session['currency'],
            status='succeeded',
            plan_id=plan_id
        )
        db.add(payment)
        
        db.commit()
        
        logging.info(f"Usuario {user_id} suscrito exitosamente al plan {plan_id}")

async def handle_subscription_update(subscription: Dict[str, Any], db: Session):
    """Manejar actualización de suscripción"""
    # Actualizar datos de suscripción en la base de datos
    pass

async def handle_subscription_cancellation(subscription: Dict[str, Any], db: Session):
    """Manejar cancelación de suscripción"""
    # Marcar suscripción como cancelada
    pass

async def handle_recurring_payment(invoice: Dict[str, Any], db: Session):
    """Manejar pago recurrente exitoso"""
    # Renovar créditos y periodo de suscripción
    pass

async def handle_payment_failure(invoice: Dict[str, Any], db: Session):
    """Manejar fallo en el pago"""
    # Notificar al usuario y manejar la suspensión del servicio
    pass

@router.get("/subscription/{user_id}")
async def get_user_subscription(user_id: str, db: Session = Depends(get_db)):
    """Obtener suscripción actual del usuario"""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    if not subscription:
        return {
            "plan": "free",
            "status": "active",
            "credits_remaining": 3,
            "credits_per_month": 3,
            "current_period_end": None
        }
    
    plan = SUBSCRIPTION_PLANS.get(subscription.plan_id, SUBSCRIPTION_PLANS["free"])
    
    return {
        "plan": subscription.plan_id,
        "status": subscription.status,
        "credits_remaining": subscription.credits_remaining,
        "credits_per_month": plan['credits_per_month'],
        "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "plan_details": plan
    }

@router.post("/use-credit/{user_id}")
async def use_credit(user_id: str, db: Session = Depends(get_db)):
    """Consumir un crédito de generación"""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    if not subscription:
        # Usuario en plan gratuito
        # Verificar si ya usó sus 3 créditos del mes
        # (implementar lógica de tracking)
        return {"credits_remaining": 2}  # Ejemplo
    
    if subscription.credits_remaining == 0:
        raise HTTPException(status_code=402, detail="Sin créditos disponibles. Actualiza tu plan.")
    
    if subscription.credits_remaining > 0:
        subscription.credits_remaining -= 1
        db.commit()
    
    return {
        "credits_remaining": subscription.credits_remaining,
        "plan": subscription.plan_id
    }

@router.get("/payment-history/{user_id}")
async def get_payment_history(user_id: str, db: Session = Depends(get_db)):
    """Obtener historial de pagos del usuario"""
    payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).all()
    
    return {
        "payments": [
            {
                "id": payment.id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "plan_id": payment.plan_id,
                "created_at": payment.created_at.isoformat()
            }
            for payment in payments
        ]
    }

@router.post("/cancel-subscription/{user_id}")
async def cancel_subscription(user_id: str, db: Session = Depends(get_db)):
    """Cancelar suscripción del usuario"""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    
    try:
        # Cancelar en Stripe
        stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        # Actualizar en base de datos
        subscription.status = 'cancelled'
        db.commit()
        
        return {"message": "Suscripción cancelada exitosamente"}
        
    except Exception as e:
        logging.error(f"Error cancelando suscripción: {e}")
        raise HTTPException(status_code=500, detail="Error al cancelar suscripción")

@router.get("/analytics")
async def get_payment_analytics(db: Session = Depends(get_db)):
    """Analytics de pagos para el administrador"""
    # Solo para administradores - agregar autenticación
    
    total_subscribers = db.query(Subscription).filter(Subscription.status == 'active').count()
    total_revenue = db.query(Payment).filter(Payment.status == 'succeeded').with_entities(
        db.func.sum(Payment.amount)
    ).scalar() or 0
    
    return {
        "total_subscribers": total_subscribers,
        "total_revenue": total_revenue,
        "revenue_this_month": 0,  # Implementar cálculo
        "new_subscribers_today": 0  # Implementar cálculo
    }