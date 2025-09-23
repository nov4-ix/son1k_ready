# 📧 CONFIGURACIÓN CORREO IONOS CON GMAIL

Guía para configurar el correo del dominio son1kvers3.com (IONOS) con Gmail

## 📋 REQUISITOS PREVIOS

1. **Dominio activo en IONOS**: son1kvers3.com
2. **Cuenta Gmail**: La que usarás para gestionar los correos
3. **Acceso a panel IONOS**: Para configurar DNS y correo

## 🔧 PASO 1: CONFIGURACIÓN EN IONOS

### 1.1 Crear cuentas de correo
En el panel de IONOS:
```
1. Ir a "Correo electrónico" > "Configuración"
2. Crear las siguientes cuentas:
   - admin@son1kvers3.com
   - soporte@son1kvers3.com  
   - noreply@son1kvers3.com
   - info@son1kvers3.com
```

### 1.2 Configurar registros MX
```
Tipo: MX
Nombre: @
Valor: mx00.ionos.es (Prioridad: 10)
Valor: mx01.ionos.es (Prioridad: 10)
```

### 1.3 Configurar SPF (TXT)
```
Tipo: TXT
Nombre: @
Valor: v=spf1 include:_spf.ionos.es ~all
```

### 1.4 Configurar DKIM
```
Activar DKIM en panel IONOS
Copiar la clave pública generada
```

## 📱 PASO 2: CONFIGURACIÓN EN GMAIL

### 2.1 Agregar cuenta como "Enviar correo como"
```
1. Gmail > Configuración > Cuentas e importación
2. "Agregar otra dirección de correo electrónico"
3. Datos de la cuenta IONOS:
   - Nombre: Son1kVers3 Admin
   - Dirección: admin@son1kvers3.com
   - Servidor SMTP: smtp.ionos.es
   - Puerto: 587 (STARTTLS) o 465 (SSL)
   - Usuario: admin@son1kvers3.com
   - Contraseña: [contraseña de IONOS]
```

### 2.2 Configurar recepción (POP/IMAP)
```
Servidor POP: pop.ionos.es
Puerto POP: 995 (SSL)
Servidor IMAP: imap.ionos.es  
Puerto IMAP: 993 (SSL)
```

## 🔐 PASO 3: CONFIGURACIÓN DE SEGURIDAD

### 3.1 Contraseñas de aplicación
Si usas 2FA en Gmail, crear contraseña específica:
```
Google > Seguridad > Contraseñas de aplicaciones
Crear para "Correo"
```

### 3.2 DMARC (Opcional pero recomendado)
```
Tipo: TXT
Nombre: _dmarc
Valor: v=DMARC1; p=quarantine; rua=mailto:dmarc@son1kvers3.com
```

## 📧 PASO 4: CONFIGURACIÓN AUTOMÁTICA

### 4.1 Script de configuración automática
```python
# config_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def configure_ionos_email():
    config = {
        'smtp_server': 'smtp.ionos.es',
        'smtp_port': 587,
        'imap_server': 'imap.ionos.es',
        'imap_port': 993,
        'accounts': {
            'admin@son1kvers3.com': 'password_here',
            'soporte@son1kvers3.com': 'password_here',
            'noreply@son1kvers3.com': 'password_here'
        }
    }
    return config

def test_smtp_connection(email, password):
    try:
        server = smtplib.SMTP('smtp.ionos.es', 587)
        server.starttls()
        server.login(email, password)
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

## 🚀 PASO 5: INTEGRACIÓN CON SON1KVERS3

### 5.1 Variables de entorno
```bash
# .env
EMAIL_SMTP_HOST=smtp.ionos.es
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=noreply@son1kvers3.com
EMAIL_PASSWORD=your_ionos_password
EMAIL_FROM=noreply@son1kvers3.com
EMAIL_FROM_NAME=Son1kVers3
```

### 5.2 Configuración en main_production_final.py
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_CONFIG = {
    'smtp_server': 'smtp.ionos.es',
    'smtp_port': 587,
    'username': 'noreply@son1kvers3.com',
    'password': os.getenv('EMAIL_PASSWORD'),
    'from_email': 'noreply@son1kvers3.com',
    'from_name': 'Son1kVers3'
}

async def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Error enviando email: {e}")
        return False
```

## ✅ PASO 6: VERIFICACIÓN

### 6.1 Comandos de prueba
```bash
# Probar conectividad SMTP
telnet smtp.ionos.es 587

# Probar envío de correo
python3 -c "
import smtplib
from email.mime.text import MIMEText

msg = MIMEText('Test email from Son1kVers3')
msg['Subject'] = 'Test'
msg['From'] = 'admin@son1kvers3.com'
msg['To'] = 'tu-email@gmail.com'

server = smtplib.SMTP('smtp.ionos.es', 587)
server.starttls()
server.login('admin@son1kvers3.com', 'tu_password')
server.send_message(msg)
server.quit()
print('Email enviado!')
"
```

### 6.2 Endpoints de prueba
```bash
# Probar endpoint de email en Son1kVers3
curl -X POST https://son1kvers3.com/api/test-email \
  -H "Content-Type: application/json" \
  -d '{"to": "tu-email@gmail.com", "subject": "Test Son1kVers3"}'
```

## 📞 SOPORTE

### Contactos útiles:
- **IONOS Soporte**: https://www.ionos.es/ayuda/
- **Gmail Help**: https://support.google.com/mail/
- **DNS Checker**: https://dnschecker.org/

### Problemas comunes:
1. **Error 535**: Credenciales incorrectas
2. **Error 587**: Puerto bloqueado 
3. **SPF fail**: Registro SPF mal configurado
4. **DKIM fail**: DKIM no activado en IONOS

## 🎉 RESULTADO FINAL

Una vez configurado correctamente:
- ✅ Enviar correos desde Gmail usando @son1kvers3.com
- ✅ Recibir correos de son1kvers3.com en Gmail
- ✅ Correos automáticos de Son1kVers3 funcionando
- ✅ Reputación de dominio protegida con SPF/DKIM/DMARC