# 🎵 Son1kVers3 - Sistema Completo de Generación Musical con IA

**www.son1kvers3.com**

## 🚀 Estado del Proyecto

✅ **COMPLETADO** - El sistema está ahora completamente funcional con:
- Backend FastAPI completo con todos los endpoints
- Servidor Node.js con integración Suno AI
- Frontend inmersivo cyberpunk
- Sistema de autenticación y usuarios
- Base de datos SQLite
- Scripts de inicio automatizados

## 🛠️ Instalación y Configuración

### 1. Clonar y Preparar

```bash
git clone <tu-repositorio>
cd son1k_suno_poc_mvp_v2
chmod +x start_son1k.sh
```

### 2. Instalar Dependencias

```bash
# Dependencias Python
pip3 install fastapi uvicorn sqlalchemy pydantic email-validator PyJWT requests

# Dependencias Node.js
npm install express cors suno-api
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar con tus valores
nano .env
```

**Variables importantes:**
```env
# Cookies de Suno AI (OBLIGATORIO)
SUNO_COOKIE=tu_cookie_suno_aqui
SUNO_COOKIE_2=cookie_adicional_suno
SUNO_COOKIE_3=tercera_cookie_suno

# Configuración de la API
SECRET_KEY=son1k_ultra_secret_key_2024
NODE_SERVER_URL=http://localhost:3001
PYTHON_SERVER_URL=http://localhost:8000
```

### 4. Obtener Cookies de Suno AI

1. Ve a [suno.com](https://suno.com)
2. Inicia sesión en tu cuenta
3. Abre las herramientas de desarrollador (F12)
4. Ve a la pestaña "Application" > "Cookies"
5. Copia el valor de la cookie de sesión
6. Pégala en tu archivo `.env`

## 🚀 Iniciar el Sistema

### Opción 1: Script Automatizado (Recomendado)

```bash
./start_son1k.sh
```

### Opción 2: Manual

```bash
# Terminal 1 - Servidor Node.js
node suno_wrapper_server.js

# Terminal 2 - Servidor Python
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3 - Servidor de archivos estáticos (opcional)
python3 -m http.server 3000
```

## 🌐 Acceso al Sistema

- **Frontend Principal**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Node.js**: http://localhost:3001
- **Health Check**: http://localhost:8000/health

## 🎯 Funcionalidades Principales

### 🎼 Generación Musical
- **Conversión Texto → Música**: Transforma cualquier idea en música
- **IA Avanzada**: Integración con Suno AI y Ollama
- **Múltiples Estilos**: Rock, pop, synthwave, clásica, etc.
- **Letras Inteligentes**: Generación automática de letras

### 👻 Ghost Studio
- **Estudio Virtual**: Herramientas profesionales de edición
- **Efectos Especiales**: Biblioteca completa de efectos
- **Masterización Automática**: Optimización de calidad
- **Postprocesamiento**: Efectos Rupert Neve

### 📚 Archivo de la Resistencia
- **Biblioteca Musical**: Colección de creaciones
- **Categorización Inteligente**: Por género, mood y estilo
- **Descarga Gratuita**: Acceso a todas las creaciones
- **Historial Personal**: Tus creaciones organizadas

### 🎮 Interfaz NEXUS (Inmersiva)
- **Modo Inmersivo**: Experiencia cyberpunk única
- **Easter Eggs**: Funcionalidades ocultas
- **Activación Múltiple**:
  - `Ctrl+Alt+H` (escritorio)
  - 3 clicks rápidos en el logo S3
  - Botón flotante (móviles)
- **Tema Matrix**: Efectos de lluvia de código

## 🔧 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión

### Generación Musical
- `POST /api/generate-music` - Generar música
- `POST /api/generate-with-credits` - Generar con créditos
- `POST /api/generate-prompt` - Mejorar prompt
- `POST /api/generate-lyrics` - Generar letras

### Sistema NEXUS
- `POST /api/nexus/chat` - Chat con PIXEL AI
- `POST /api/nexus/analyze-threats` - Análisis de amenazas
- `POST /api/nexus/optimize-systems` - Optimización
- `POST /api/nexus/generate-strategy` - Generar estrategia
- `POST /api/nexus/scan-network` - Escanear red
- `POST /api/nexus/deploy-countermeasures` - Contramedidas
- `POST /api/nexus/apply-enhancement` - Aplicar mejoras
- `POST /api/nexus/quantum-analysis` - Análisis cuántico
- `POST /api/nexus/activate-protocols` - Activar protocolos
- `GET /api/nexus/status` - Estado del sistema

### Sistema de Resistencia
- `POST /api/resistance/chat` - Chat de Resistencia
- `POST /api/resistance/create-collaboration` - Crear colaboración
- `GET /api/resistance/status` - Estado de Resistencia

### Easter Eggs
- `POST /api/easter-eggs/portal` - Portal de Resistencia
- `POST /api/easter-eggs/konami` - Código Konami
- `POST /api/easter-eggs/glitch` - Modo Glitch

### Otros
- `GET /api/tracks` - Obtener tracks
- `GET /api/user/usage` - Uso del usuario
- `POST /api/chat` - Chat con IA
- `POST /api/postprocess/rupert-neve` - Postprocesamiento
- `POST /api/transform-audio` - Transformar audio

## 🗄️ Base de Datos

El sistema usa SQLite con las siguientes tablas:

- **users**: Información de usuarios y créditos
- **generations**: Historial de generaciones musicales
- **tracks**: Biblioteca de tracks disponibles

## 🔒 Seguridad

- **Autenticación JWT**: Tokens seguros
- **HTTPS**: Comunicación encriptada
- **CORS**: Configuración de seguridad
- **Validación**: Validación de entrada con Pydantic
- **Rate Limiting**: Límites de uso por usuario

## 📊 Monitoreo

- **Health Checks**: Verificación de estado
- **Logging**: Sistema de logs completo
- **Métricas**: Estadísticas de uso
- **Alertas**: Notificaciones de errores

## 🚀 Despliegue en Producción

### Railway (Recomendado)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Desplegar
railway up
```

### Docker

```bash
# Construir imagen
docker build -t son1kvers3 .

# Ejecutar contenedor
docker run -p 8000:8000 -p 3001:3001 son1kvers3
```

## 🐛 Solución de Problemas

### Error: "No hay cookies disponibles"
- Verifica que las cookies de Suno estén configuradas en `.env`
- Asegúrate de que las cookies sean válidas y no hayan expirado

### Error: "Puerto ya en uso"
- Cambia los puertos en la configuración
- Mata los procesos que usan los puertos: `lsof -ti:8000 | xargs kill`

### Error: "Módulo no encontrado"
- Instala las dependencias: `pip3 install -r requirements.txt`
- Verifica que estés en el directorio correcto

### Error: "Base de datos no encontrada"
- El sistema creará automáticamente la base de datos
- Verifica permisos de escritura en el directorio

## 📈 Próximas Mejoras

- [ ] Integración con Ollama para IA local
- [ ] Sistema de cola con Celery
- [ ] Cache con Redis
- [ ] Notificaciones por email
- [ ] API pública para desarrolladores
- [ ] Integración con DAWs
- [ ] Marketplace de samples
- [ ] Realidad virtual

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Email**: contact@son1kvers3.com
- **GitHub**: [github.com/nov4-ix/son1k_ready](https://github.com/nov4-ix/son1k_ready)
- **Desarrollado por**: NOV4-IX

---

**"Lo imperfecto también es sagrado"** — Son1kVers3

*Únete a La Resistencia Musical Digital*



