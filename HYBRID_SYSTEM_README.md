# 🎵 Son1k Hybrid Stealth System

## 🚀 Sistema Híbrido: Suno Real + Ollama Proxy

### 🎯 ¿Qué es el Sistema Híbrido?

El **Son1k Hybrid Stealth System** combina lo mejor de ambos mundos:

1. **🤖 Suno Real**: Generación de música real usando Puppeteer + navegador real
2. **🧠 Ollama Proxy**: IA local como fallback inteligente cuando Suno no está disponible

### 🛡️ Características Ultra-Avanzadas

#### 🤖 Suno Real (Método Principal)
- ✅ **Navegador real** con Puppeteer
- ✅ **Cookies de autenticación** válidas
- ✅ **Interacciones humanas** simuladas
- ✅ **Descarga automática** de archivos de audio
- ✅ **Pool de navegadores** reutilizables
- ✅ **Completamente indetectable** por Suno

#### 🧠 Ollama Proxy (Fallback Inteligente)
- ✅ **IA local** con modelos Llama
- ✅ **Generación de contenido musical** detallado
- ✅ **Análisis de prompts** inteligente
- ✅ **Estructura musical** completa
- ✅ **Letras generadas** por IA
- ✅ **Funciona offline** sin dependencias externas

#### 🔄 Sistema Híbrido Inteligente
- ✅ **Fallback automático** Suno → Ollama
- ✅ **Estadísticas en tiempo real**
- ✅ **Manejo de errores robusto**
- ✅ **Múltiples métodos** de generación
- ✅ **Pool de navegadores** optimizado
- ✅ **Configuración flexible**

### 🚀 Cómo Usar

#### 1. Iniciar el Sistema
```bash
./start_hybrid_system.sh
```

#### 2. Probar el Sistema
```bash
python3 test_hybrid_system.py
```

#### 3. Usar desde el Frontend
- Accede a: http://localhost:8000
- El sistema automáticamente usará Suno real o Ollama como fallback

#### 4. Usar desde API
```bash
# Generación híbrida (automática)
curl -X POST http://localhost:3003/generate-music \
  -H "Content-Type: application/json" \
  -d '{"prompt": "una canción épica de synthwave"}'

# Solo Suno (música real)
curl -X POST http://localhost:3003/generate-music \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "forceMethod": "suno"}'

# Solo Ollama (IA local)
curl -X POST http://localhost:3003/generate-music \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "forceMethod": "ollama"}'
```

### 📊 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/generate-music` | POST | Generación híbrida automática |
| `/generate-music?forceMethod=suno` | POST | Solo Suno (música real) |
| `/generate-music?forceMethod=ollama` | POST | Solo Ollama (IA local) |
| `/health` | GET | Estado del sistema |
| `/stats` | GET | Estadísticas detalladas |

### 🔧 Configuración

#### Suno (Música Real)
- **Cuentas**: Configuradas en `SUNO_ACCOUNTS`
- **Cookies**: Actualizadas automáticamente
- **Navegadores**: Pool de 2 navegadores máximo
- **Timeout**: 30 segundos por generación

#### Ollama (IA Local)
- **URL**: http://localhost:11434
- **Modelos**: llama3.1:8b, llama3.1:70b, codellama:7b
- **Timeout**: 30 segundos por generación
- **Fallback**: Habilitado por defecto

### 📈 Estadísticas en Tiempo Real

El sistema mantiene estadísticas detalladas:

```json
{
  "suno": {
    "success": 5,
    "failures": 2,
    "successRate": "71.43%",
    "lastSuccess": "2025-09-24T16:21:24.223Z"
  },
  "ollama": {
    "success": 3,
    "failures": 1,
    "successRate": "75.00%",
    "lastSuccess": "2025-09-24T16:21:24.223Z"
  },
  "total": {
    "requests": 8,
    "attempts": 11
  }
}
```

### 🛠️ Troubleshooting

#### Suno no funciona
- **Problema**: Cookies expiradas o Suno bloquea
- **Solución**: El sistema automáticamente usa Ollama como fallback

#### Ollama no funciona
- **Problema**: Ollama no está instalado o no responde
- **Solución**: El sistema funciona solo con Suno

#### Timeout en generación
- **Problema**: Generación toma demasiado tiempo
- **Solución**: Aumentar timeout en configuración

#### Navegadores no se crean
- **Problema**: Puppeteer no puede lanzar navegadores
- **Solución**: Verificar dependencias y permisos

### 🎯 Ventajas del Sistema Híbrido

1. **🛡️ Máxima Robustez**: Si Suno falla, Ollama continúa
2. **🎵 Música Real**: Cuando Suno funciona, obtienes audio real
3. **🧠 IA Inteligente**: Ollama genera contenido musical detallado
4. **📊 Estadísticas**: Monitoreo en tiempo real del rendimiento
5. **🔄 Automático**: No necesitas intervenir manualmente
6. **⚡ Rápido**: Pool de navegadores reutilizables
7. **🔒 Indetectable**: Completamente invisible para Suno

### 🚀 Próximos Pasos

1. **Configurar Ollama** (opcional pero recomendado)
2. **Actualizar cookies** de Suno cuando sea necesario
3. **Monitorear estadísticas** para optimizar rendimiento
4. **Ajustar timeouts** según tus necesidades

---

**🎵 El Sistema Híbrido te da lo mejor de ambos mundos: música real de Suno cuando está disponible, e IA local inteligente como respaldo. ¡Nunca más te quedarás sin música!**






