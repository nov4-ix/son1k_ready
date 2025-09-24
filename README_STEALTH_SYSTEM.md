# 🎵 Son1k Stealth Music Generator

Sistema avanzado de generación de música con tecnología stealth y múltiples cuentas de Suno para máxima evasión.

## 🚀 Características Principales

### 🔒 Tecnología Stealth
- **Rotación de User-Agents**: Cambia automáticamente el User-Agent para evasión
- **Headers de Evasión**: Headers personalizados para parecer tráfico legítimo
- **Delays Aleatorios**: Tiempos de espera variables entre peticiones
- **Pool de Cookies**: Rotación inteligente de cookies de sesión
- **Retry Inteligente**: Reintentos con backoff exponencial

### 👥 Múltiples Cuentas
- **Balanceo de Carga**: Distribución inteligente entre cuentas
- **Rotación Automática**: Cambio automático de cuentas cada 5 minutos
- **Cooldown Inteligente**: Pausas automáticas para cuentas con fallos
- **Priorización**: Sistema de prioridades para cuentas más exitosas
- **Límites Diarios**: Control de uso diario por cuenta

### 🎯 Modos de Generación
1. **Multi Account** (Máxima evasión)
2. **Suno Stealth** (Indetectable)
3. **Suno Real** (Integración directa)
4. **Real Music Generator** (Síntesis local)
5. **Ollama Proxy** (IA local)
6. **Simulación** (Fallback)

## 📁 Estructura del Sistema

```
son1k_suno_poc_mvp_v2/
├── 🐍 Python Server (Puerto 8000)
│   ├── son1k_simple_stable.py          # Servidor principal
│   ├── multi_account_manager.py        # Gestor de múltiples cuentas
│   ├── suno_stealth_integration.py     # Integración stealth
│   └── real_music_generator.py         # Generador de música local
│
├── 🌐 Node.js Wrapper (Puerto 3001)
│   ├── suno_wrapper_server.js          # Servidor stealth
│   ├── package.json                    # Dependencias Node.js
│   └── .env                           # Variables de entorno
│
├── ⚙️ Configuración
│   ├── suno_accounts.json             # Configuración de cuentas
│   └── suno_credentials.json          # Credenciales individuales
│
├── 🧪 Scripts de Prueba
│   ├── test_complete_system.py        # Prueba completa
│   ├── test_multi_accounts.py         # Prueba múltiples cuentas
│   └── test_stealth_generation.py     # Prueba generación stealth
│
└── 🚀 Scripts de Inicio
    ├── setup_complete_system.sh       # Configuración completa
    ├── start_complete_system.sh       # Inicio del sistema
    └── setup_multi_accounts.py        # Configuración de cuentas
```

## 🛠️ Instalación y Configuración

### 1. Configuración Rápida
```bash
# Ejecutar configuración completa
./setup_complete_system.sh
```

### 2. Configuración Manual

#### Instalar Dependencias
```bash
# Python
pip3 install fastapi uvicorn aiohttp asyncio selenium numpy scipy

# Node.js
npm install
```

#### Configurar Múltiples Cuentas
```bash
# Configurar cuentas de Suno
python3 setup_multi_accounts.py
```

#### Iniciar Sistema
```bash
# Iniciar sistema completo
./start_complete_system.sh
```

## 🎵 Uso del Sistema

### Interfaz Web
- **URL**: http://localhost:3001
- **Características**: Interfaz moderna con generación en tiempo real
- **Estadísticas**: Monitoreo de cuentas y rendimiento

### API REST
```bash
# Generar música
curl -X POST http://localhost:8000/api/music/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "una canción de rock sobre la libertad", "style": "profesional"}'

# Verificar estado
curl http://localhost:8000/api/health

# Ver tracks generados
curl http://localhost:8000/api/tracks
```

### API Node.js (Stealth)
```bash
# Generar música con stealth
curl -X POST http://localhost:3001/generate-music \
  -H "Content-Type: application/json" \
  -d '{"prompt": "música electrónica futurista", "style": "profesional"}'

# Ver estadísticas
curl http://localhost:3001/stats
```

## 🔧 Configuración Avanzada

### Archivo de Cuentas (`suno_accounts.json`)
```json
{
  "accounts": [
    {
      "id": "account_1",
      "email": "cuenta1@gmail.com",
      "cookie": "cookie_de_suno_1",
      "priority": 1,
      "max_daily_usage": 50
    },
    {
      "id": "account_2",
      "email": "cuenta2@gmail.com", 
      "cookie": "cookie_de_suno_2",
      "priority": 1,
      "max_daily_usage": 50
    }
  ],
  "settings": {
    "rotation_interval": 300,
    "load_balancer": "weighted",
    "cooldown_time": 60,
    "max_concurrent": 3
  }
}
```

### Variables de Entorno (`.env`)
```bash
PORT=3001
MAX_CONCURRENT_REQUESTS=3
RETRY_ATTEMPTS=3
DELAY_BETWEEN_ATTEMPTS=2000
ROTATION_INTERVAL=300
```

## 📊 Monitoreo y Estadísticas

### Endpoints de Monitoreo
- `GET /health` - Estado del sistema
- `GET /stats` - Estadísticas detalladas
- `GET /api/tracks` - Tracks generados

### Métricas Disponibles
- **Cuentas**: Total, activas, disponibles
- **Rendimiento**: Tasa de éxito, tiempo de respuesta
- **Uso**: Generaciones por cuenta, límites diarios
- **Sistema**: Memoria, CPU, uptime

## 🧪 Pruebas

### Prueba Completa
```bash
python3 test_complete_system.py
```

### Prueba Múltiples Cuentas
```bash
python3 test_multi_accounts.py
```

### Prueba Generación Stealth
```bash
python3 test_stealth_generation.py
```

## 🔒 Características de Evasión

### Headers de Evasión
- User-Agent rotativo
- Headers de servidor falsos
- Headers de seguridad estándar

### Patrones de Tráfico
- Delays aleatorios entre peticiones
- Rotación de cuentas cada 5 minutos
- Límites de uso diario por cuenta
- Cooldown automático en fallos

### Pool de Cookies
- Múltiples cookies de sesión
- Rotación inteligente
- Validación automática
- Fallback entre cuentas

## 🚨 Solución de Problemas

### Problemas Comunes

#### Servidor Node.js no inicia
```bash
# Verificar puerto
lsof -i :3001

# Reiniciar
pkill -f "node suno_wrapper_server.js"
node suno_wrapper_server.js
```

#### Servidor Python no inicia
```bash
# Verificar puerto
lsof -i :8000

# Reiniciar
pkill -f "python3 son1k_simple_stable.py"
python3 son1k_simple_stable.py
```

#### Cuentas no funcionan
```bash
# Verificar configuración
python3 setup_multi_accounts.py

# Verificar cookies
curl http://localhost:3001/stats
```

### Logs del Sistema
- **Python**: Logs en consola y archivos
- **Node.js**: Logs en consola
- **Debug**: Usar `test_complete_system.py`

## 📈 Optimización

### Para Máximo Rendimiento
1. **Más Cuentas**: 5-10 cuentas para mejor distribución
2. **Prioridades**: Cuentas premium con prioridad alta
3. **Límites**: Ajustar límites diarios según plan de Suno
4. **Rotación**: Reducir intervalo de rotación si es necesario

### Para Máxima Evasión
1. **Delays**: Aumentar delays entre peticiones
2. **Headers**: Personalizar headers por cuenta
3. **Patrones**: Variar patrones de uso
4. **Cooldown**: Aumentar tiempo de cooldown

## 🎯 Casos de Uso

### Generación Masiva
- Múltiples cuentas para alto volumen
- Balanceo de carga automático
- Monitoreo de límites

### Generación Stealth
- Evasión de detección
- Patrones de tráfico naturales
- Rotación de identidades

### Desarrollo y Pruebas
- Múltiples entornos
- Pruebas A/B
- Monitoreo de rendimiento

## 📞 Soporte

### Archivos de Log
- Revisar logs de consola
- Usar scripts de prueba
- Verificar configuración

### Debugging
```bash
# Estado del sistema
curl http://localhost:8000/api/health
curl http://localhost:3001/health

# Estadísticas detalladas
curl http://localhost:3001/stats

# Probar generación
python3 test_complete_system.py
```

---

## 🎉 ¡Sistema Listo!

El sistema Son1k Stealth está configurado con:
- ✅ Múltiples cuentas de Suno
- ✅ Tecnología stealth avanzada
- ✅ Balanceo de carga inteligente
- ✅ Monitoreo completo
- ✅ Interfaz web moderna
- ✅ API REST completa

**¡Disfruta generando música con máxima evasión!** 🎵🚀



