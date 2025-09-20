# 💳 Guía de Configuración de Stripe para Son1k

## 📋 Resumen

Esta guía te ayudará a configurar completamente Stripe para recibir pagos en Son1k, incluyendo la creación de productos, precios y webhooks.

## 🚀 Paso 1: Crear Cuenta de Stripe

1. **Registrarse en Stripe:**
   - Ir a https://stripe.com
   - Crear cuenta con tu email
   - Completar verificación de identidad
   - Activar cuenta para pagos en vivo

2. **Configurar información de la empresa:**
   - Nombre: "Son1k Music Generation"
   - Sitio web: https://son1kvers3.com
   - Descripción: "Generación de música con inteligencia artificial"

## 🔑 Paso 2: Obtener Claves API

### Claves de Prueba (para desarrollo):
```bash
# Dashboard > Developers > API keys
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Claves de Producción (para son1kvers3.com):
```bash
# Activar modo en vivo en Dashboard
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

## 📦 Paso 3: Crear Productos y Precios

### En Stripe Dashboard > Products:

#### 1. Plan Básico
```
Nombre: Plan Básico Son1k
Descripción: 50 canciones por mes, duración hasta 3 minutos
Precio: $9.99 USD
Tipo: Suscripción mensual
ID del precio: price_basic_monthly
```

#### 2. Plan Pro  
```
Nombre: Plan Pro Son1k
Descripción: 200 canciones por mes, duración hasta 5 minutos, uso comercial
Precio: $19.99 USD
Tipo: Suscripción mensual
ID del precio: price_pro_monthly
```

#### 3. Plan Ilimitado
```
Nombre: Plan Ilimitado Son1k
Descripción: Canciones ilimitadas, duración hasta 10 minutos, uso comercial, API access
Precio: $49.99 USD
Tipo: Suscripción mensual  
ID del precio: price_unlimited_monthly
```

### Script para crear productos automáticamente:

```bash
# Ejecutar en tu terminal con Stripe CLI
stripe products create \
  --name="Plan Básico Son1k" \
  --description="50 canciones por mes, duración hasta 3 minutos"

stripe prices create \
  --product=prod_XXXXXXXXXX \
  --unit-amount=999 \
  --currency=usd \
  --recurring="interval=month" \
  --lookup-key="basic_monthly"
```

## 🔄 Paso 4: Configurar Webhooks

### 1. Crear Webhook en Dashboard:
- Ir a: Dashboard > Developers > Webhooks
- Añadir endpoint: `https://api.son1kvers3.com/api/subscription/webhook`

### 2. Eventos a escuchar:
```
✅ checkout.session.completed
✅ customer.subscription.created  
✅ customer.subscription.updated
✅ customer.subscription.deleted
✅ invoice.payment_succeeded
✅ invoice.payment_failed
```

### 3. Obtener Webhook Secret:
```bash
# Copiar el signing secret del webhook
STRIPE_WEBHOOK_SECRET=whsec_...
```

## ⚙️ Paso 5: Configurar Variables de Entorno

### Actualizar .env.production:
```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_YOUR_ACTUAL_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_ACTUAL_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_ACTUAL_WEBHOOK_SECRET

# Price IDs from Stripe Dashboard
STRIPE_PRICE_BASIC=price_1234567890_basic
STRIPE_PRICE_PRO=price_1234567890_pro  
STRIPE_PRICE_UNLIMITED=price_1234567890_unlimited
```

## 🧪 Paso 6: Probar la Integración

### 1. Tarjetas de prueba de Stripe:
```
✅ Éxito: 4242 4242 4242 4242
❌ Fallo:  4000 0000 0000 0002
📱 3D Secure: 4000 0025 0000 3155
```

### 2. Flujo de prueba:
1. Ir a https://son1kvers3.com/pricing
2. Seleccionar plan
3. Completar checkout con tarjeta de prueba
4. Verificar webhook en Dashboard
5. Confirmar activación de suscripción

## 🏦 Paso 7: Configurar Pagos

### 1. Información bancaria:
- Añadir cuenta bancaria en Dashboard > Settings > Payouts
- Verificar cuenta con micro-depósitos
- Configurar calendario de pagos (diario/semanal)

### 2. Facturación:
- Configurar información fiscal
- Establecer statement descriptor: "SON1K MUSIC"
- Configurar emails de recibos

## 📊 Paso 8: Dashboard y Reportes

### Métricas importantes a monitorear:
- **MRR (Monthly Recurring Revenue)**
- **Churn Rate** (cancelaciones)
- **Conversion Rate** (visitas → suscripciones)
- **Customer Lifetime Value**

### Configurar alertas:
- Pagos fallidos
- Cancelaciones
- Disputas/chargebacks

## 🔒 Paso 9: Seguridad y Cumplimiento

### 1. PCI Compliance:
- Stripe maneja automáticamente
- Nunca almacenar datos de tarjetas
- Usar Stripe Elements en frontend

### 2. GDPR/Privacidad:
- Configurar retención de datos
- Permitir eliminación de customers
- Política de privacidad actualizada

## 🚨 Paso 10: Ir a Producción

### Lista de verificación final:
- [ ] Cuenta Stripe activada y verificada
- [ ] Productos y precios creados
- [ ] Webhooks configurados y funcionando
- [ ] Variables de entorno de producción
- [ ] Tarjetas de prueba funcionando
- [ ] Información bancaria verificada
- [ ] Statement descriptor configurado
- [ ] Políticas legales actualizadas

### Activar modo en vivo:
1. En Dashboard, activar "View live data"
2. Actualizar claves API en producción
3. Probar con tarjeta real (mínimo $0.50)
4. Verificar webhook en producción

## 💰 Comisiones de Stripe

### Precios estándar:
- **Tarjetas:** 2.9% + $0.30 por transacción exitosa
- **Suscripciones:** Misma tarifa
- **Disputas:** $15 por disputa
- **Internacionales:** +1.5%

### Optimizaciones:
- Facturación anual (descuentos)
- Pagos en lote
- Optimización de retry logic

## 🛠️ Testing en Desarrollo

### Variables de entorno de desarrollo:
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...
```

### Comando para probar webhooks localmente:
```bash
stripe listen --forward-to localhost:8000/api/subscription/webhook
```

## 📞 Soporte

### Recursos útiles:
- **Documentación:** https://stripe.com/docs
- **Dashboard:** https://dashboard.stripe.com
- **Soporte:** https://support.stripe.com
- **Status:** https://status.stripe.com

### Para problemas:
1. Revisar logs en Dashboard > Developers > Logs
2. Verificar webhooks en Dashboard > Developers > Webhooks
3. Contactar soporte de Stripe si es necesario

---

## ✅ Una vez completado:

Tu integración de Stripe estará lista para recibir pagos reales en son1kvers3.com, con todas las funcionalidades de suscripción, facturación automática y manejo de cancelaciones.