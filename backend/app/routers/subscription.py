#!/usr/bin/env python3
"""
Sistema de Suscripciones y Pagos para Son1k
Integración completa con Stripe y manejo de usuarios
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import stripe
import os
import logging
from datetime import datetime, timedelta
import uuid

from ..models import User, SUBSCRIPTION_PLANS
from ..database import get_db

# Configuración de Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

@router.get("/plans")
async def get_subscription_plans():
    """Obtener todos los planes de suscripción disponibles"""
    return {
        "success": True,
        "plans": SUBSCRIPTION_PLANS,
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY
    }

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan_id: str,
    user_email: str,
    db: Session = Depends(get_db)
):
    """Crear sesión de checkout de Stripe para una suscripción"""
    
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Plan no válido")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    if plan_id == "free":
        raise HTTPException(status_code=400, detail="Plan gratuito no requiere pago")
    
    try:
        # Buscar o crear usuario
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user_id = str(uuid.uuid4())
            user = User(
                id=user_id,
                email=user_email,
                plan="free",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Crear o obtener customer de Stripe
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user_email,
                metadata={'user_id': user.id}
            )
            user.stripe_customer_id = customer.id
            db.commit()
        
        # Crear sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"https://son1kvers3.com/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="https://son1kvers3.com/pricing?cancelled=true",
            client_reference_id=user.id,
            metadata={
                'user_id': user.id,
                'plan_id': plan_id,
                'user_email': user_email
            },
            subscription_data={
                'metadata': {
                    'user_id': user.id,
                    'plan_id': plan_id
                }
            }
        )
        
        return {
            "success": True,
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail=f"Error de Stripe: {str(e)}")
    except Exception as e:
        logging.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Error al crear sesión de pago")

@router.get("/status/{user_id}")
async def get_subscription_status(user_id: str, db: Session = Depends(get_db)):
    """Obtener estado de suscripción del usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    current_plan = SUBSCRIPTION_PLANS.get(user.plan, SUBSCRIPTION_PLANS["free"])
    
    return {
        "success": True,
        "user_id": user.id,
        "email": user.email,
        "current_plan": {
            "id": user.plan,
            "name": current_plan["name"],
            "price": current_plan["price"],
            "features": current_plan["features"]
        },
        "subscription_status": user.subscription_status,
        "credits_remaining": user.credits_remaining,
        "credits_used_this_month": user.credits_used_this_month,
        "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
        "stripe_customer_id": user.stripe_customer_id
    }

@router.post("/webhook")
async def stripe_webhook(
    request: Request, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Webhook de Stripe para manejar eventos de suscripción"""
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logging.error("Invalid payload in webhook")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logging.error("Invalid signature in webhook")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Procesar evento en background
    background_tasks.add_task(process_stripe_event, event, db)
    
    return {"status": "success"}

async def process_stripe_event(event: Dict[str, Any], db: Session):
    """Procesar eventos de Stripe"""
    
    event_type = event['type']
    data_object = event['data']['object']
    
    logging.info(f"Processing Stripe event: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            await handle_checkout_completed(data_object, db)
        
        elif event_type == 'customer.subscription.created':
            await handle_subscription_created(data_object, db)
        
        elif event_type == 'customer.subscription.updated':
            await handle_subscription_updated(data_object, db)
        
        elif event_type == 'customer.subscription.deleted':
            await handle_subscription_cancelled(data_object, db)
        
        elif event_type == 'invoice.payment_succeeded':
            await handle_payment_succeeded(data_object, db)
        
        elif event_type == 'invoice.payment_failed':
            await handle_payment_failed(data_object, db)
        
        else:
            logging.info(f"Unhandled event type: {event_type}")
    
    except Exception as e:
        logging.error(f"Error processing Stripe event {event_type}: {e}")

async def handle_checkout_completed(session: Dict[str, Any], db: Session):
    """Manejar checkout completado"""
    user_id = session['metadata'].get('user_id')
    plan_id = session['metadata'].get('plan_id')
    
    if not user_id or not plan_id:
        logging.error("Missing user_id or plan_id in checkout session")
        return
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.error(f"User {user_id} not found for checkout session")
        return
    
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    if not plan:
        logging.error(f"Plan {plan_id} not found")
        return
    
    # Actualizar usuario con nueva suscripción
    user.plan = plan_id
    user.subscription_status = "active"
    user.subscription_end_date = datetime.now() + timedelta(days=30)
    user.credits_remaining = plan['credits_per_month']
    user.credits_used_this_month = 0
    
    db.commit()
    
    logging.info(f"User {user_id} successfully subscribed to {plan_id}")

async def handle_subscription_created(subscription: Dict[str, Any], db: Session):
    """Manejar suscripción creada"""
    user_id = subscription['metadata'].get('user_id')
    
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.subscription_status = "active"
            db.commit()

async def handle_subscription_updated(subscription: Dict[str, Any], db: Session):
    """Manejar actualización de suscripción"""
    user_id = subscription['metadata'].get('user_id')
    
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Actualizar estado basado en el status de Stripe
            status_mapping = {
                'active': 'active',
                'past_due': 'past_due',
                'canceled': 'cancelled',
                'unpaid': 'past_due'
            }
            user.subscription_status = status_mapping.get(subscription['status'], 'inactive')
            db.commit()

async def handle_subscription_cancelled(subscription: Dict[str, Any], db: Session):
    """Manejar cancelación de suscripción"""
    user_id = subscription['metadata'].get('user_id')
    
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.plan = "free"
            user.subscription_status = "cancelled"
            user.credits_remaining = 3  # Resetear a plan gratuito
            user.credits_used_this_month = 0
            db.commit()
            
            logging.info(f"User {user_id} subscription cancelled, reverted to free plan")

async def handle_payment_succeeded(invoice: Dict[str, Any], db: Session):
    """Manejar pago exitoso (renovaciones)"""
    subscription_id = invoice.get('subscription')
    
    if subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            user_id = subscription['metadata'].get('user_id')
            plan_id = subscription['metadata'].get('plan_id')
            
            if user_id and plan_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    plan = SUBSCRIPTION_PLANS.get(plan_id)
                    if plan:
                        # Renovar créditos
                        user.credits_remaining = plan['credits_per_month']
                        user.credits_used_this_month = 0
                        user.subscription_end_date = datetime.now() + timedelta(days=30)
                        user.subscription_status = "active"
                        db.commit()
                        
                        logging.info(f"Credits renewed for user {user_id}, plan {plan_id}")
        
        except Exception as e:
            logging.error(f"Error processing payment succeeded: {e}")

async def handle_payment_failed(invoice: Dict[str, Any], db: Session):
    """Manejar fallo en el pago"""
    subscription_id = invoice.get('subscription')
    
    if subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            user_id = subscription['metadata'].get('user_id')
            
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.subscription_status = "past_due"
                    db.commit()
                    
                    logging.warning(f"Payment failed for user {user_id}")
        
        except Exception as e:
            logging.error(f"Error processing payment failed: {e}")

@router.post("/cancel/{user_id}")
async def cancel_subscription(user_id: str, db: Session = Depends(get_db)):
    """Cancelar suscripción del usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Usuario no tiene suscripción activa")
    
    try:
        # Obtener suscripciones activas del customer
        subscriptions = stripe.Subscription.list(
            customer=user.stripe_customer_id,
            status='active'
        )
        
        if not subscriptions.data:
            raise HTTPException(status_code=400, detail="No hay suscripciones activas")
        
        # Cancelar la primera suscripción activa
        stripe.Subscription.delete(subscriptions.data[0].id)
        
        return {"success": True, "message": "Suscripción cancelada exitosamente"}
        
    except stripe.error.StripeError as e:
        logging.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Error de Stripe: {str(e)}")
    except Exception as e:
        logging.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail="Error al cancelar suscripción")

@router.get("/customer-portal/{user_id}")
async def create_customer_portal_session(user_id: str, db: Session = Depends(get_db)):
    """Crear sesión del portal del cliente de Stripe"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.stripe_customer_id:
        raise HTTPException(status_code=404, detail="Usuario o customer no encontrado")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url="https://son1kvers3.com/account"
        )
        
        return {"success": True, "portal_url": session.url}
        
    except stripe.error.StripeError as e:
        logging.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail=f"Error de Stripe: {str(e)}")

@router.post("/use-credit/{user_id}")
async def use_credit(user_id: str, db: Session = Depends(get_db)):
    """Consumir un crédito para generar música"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    plan = SUBSCRIPTION_PLANS.get(user.plan, SUBSCRIPTION_PLANS["free"])
    
    # Verificar si el usuario tiene créditos
    if plan['credits_per_month'] != -1 and user.credits_remaining <= 0:
        raise HTTPException(
            status_code=402, 
            detail={
                "error": "Sin créditos disponibles",
                "message": "Has agotado tus créditos mensuales. Actualiza tu plan para continuar.",
                "current_plan": user.plan,
                "upgrade_url": "https://son1kvers3.com/pricing"
            }
        )
    
    # Consumir crédito si no es plan ilimitado
    if plan['credits_per_month'] != -1:
        user.credits_remaining -= 1
        user.credits_used_this_month += 1
    
    db.commit()
    
    return {
        "success": True,
        "credits_remaining": user.credits_remaining if plan['credits_per_month'] != -1 else -1,
        "plan": user.plan,
        "message": "Crédito consumido exitosamente"
    }