# Son1kVers3 × Suno — MVP v2 (escala real)
Incluye:
- FastAPI + Celery/Redis
- Postgres (modelos: users, jobs, songs, assets)
- Rate limiting básico (Redis, por header `X-User-Id`)
- WebSocket `/ws/{user_id}` para actualizaciones
- Extensión Chrome MV3 (puente PoC)
- Docker Compose listo

> Solo para pruebas personales con tu cuenta Suno. Respeta ToS.

## 1) Levantar servicios
```bash
docker compose up --build
# API: http://localhost:8000/api/health
```
Postgres y Redis levantan con Compose. Las tablas se crean al iniciar.

## 2) Probar una creación
```bash
curl -X POST http://localhost:8000/api/songs/create   -H "Content-Type: application/json"   -H "X-User-Id: nov4ix"   -d '{"prompt":"Cyberpunk ballad, minor key, 90 BPM", "length_sec":60, "mode":"original"}'
```
Responde `{ ok: true, job_id }`. Estado simulado en `/api/songs/status/{job_id}`.

## 3) WebSocket de estado
Conecta a: `ws://localhost:8000/ws/nov4ix`  
Recibirás `queued → running → done` (demo). Cambia la lógica cuando integres workers reales.

## 4) Extensión Chrome (MV3)
1. `chrome://extensions` → Developer Mode → Load unpacked → `extension/`
2. En el popup pon `http://localhost:8000` y pulsa **Vincular/Probar**
3. Con sesión Suno abierta, la extensión intenta inyectar y postear a `/api/suno/results`
> Ajusta selectores en `extension/content.js` al DOM real de Suno.

## 5) Migración a API oficial Suno
Sustituye la tarea `generate_with_suno` por el cliente API real manteniendo `enqueue_generation(payload)`.

## 6) Producción (VPS)
- NGINX reverse proxy → API
- Certbot TLS
- Postgres gestionado (Supabase/Neon)
- S3/R2 + CDN para assets
- Logs/metrics (OTel/Prometheus)

## Estructura
```
backend/
  app/
    main.py, queue.py, settings.py, db.py, models.py, deps.py, ws.py
  Dockerfile
  requirements.txt
docker-compose.yml
extension/
  manifest.json, background.js, content.js, popup.html
.env.example
```
Hecho por la Resistencia Sonora ⚡
