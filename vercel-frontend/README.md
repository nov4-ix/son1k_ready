# Son1k Frontend - Vercel Deployment

Este es el frontend de Son1k optimizado para deployment en Vercel.

## 🚀 Deploy en Vercel

### Opción 1: GitHub Integration (Recomendado)
1. Hacer push de este código a GitHub
2. Conectar Vercel con GitHub
3. Importar este repositorio
4. Configurar variables de entorno
5. Deploy automático

### Opción 2: Vercel CLI
```bash
npm i -g vercel
vercel --prod
```

## ⚙️ Configuración

### Variables de Entorno en Vercel:
```
API_BASE_URL=https://api.son1kvers3.com
ENVIRONMENT=production
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### Dominios:
- Primario: `son1kvers3.com`
- Alias: `www.son1kvers3.com`

## 📁 Estructura
```
vercel-frontend/
├── index.html          # Página principal
├── pricing.html        # Planes de suscripción
├── terms.html          # Términos y condiciones
├── privacy.html        # Política de privacidad
├── account.html        # Gestión de cuenta
├── success.html        # Confirmación de pago
├── consent-banner.js   # Sistema de cookies GDPR
├── vercel.json         # Configuración Vercel
├── package.json        # Metadatos del proyecto
└── README.md           # Esta documentación
```

## 🔧 Características

### ✅ Optimizaciones incluidas:
- Routing para SPA
- Proxy para API calls
- Security headers
- CORS configurado
- Compresión automática
- CDN global

### ✅ Páginas funcionales:
- `/` - Generador de música
- `/pricing` - Planes de suscripción
- `/terms` - Términos legales
- `/privacy` - Política de privacidad
- `/account` - Panel de usuario
- `/success` - Confirmación de pago

## 📡 API Integration

El frontend está configurado para conectar con:
- **Backend API**: `https://api.son1kvers3.com`
- **Stripe Checkout**: Integración directa
- **Legal endpoints**: Compliance GDPR/CCPA

## 🛡️ Seguridad

- Headers de seguridad configurados
- HTTPS obligatorio
- Validación CORS
- XSS protection
- Content Security Policy

## 📊 Analytics

Ready para integrar:
- Google Analytics 4
- Vercel Analytics
- Plausible (privacy-focused)

## 🎯 Next Steps

1. Deploy en Vercel
2. Configurar dominio personalizado
3. Conectar con backend en Hetzner
4. Activar Stripe en modo producción
5. Configurar analytics

## 💡 Tips

- Vercel redeploy automático en git push
- Preview deployments para testing
- Edge functions para lógica avanzada
- Image optimization automática