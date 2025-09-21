web: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
worker: python -m celery worker -A backend.app.queue.celery_app --loglevel=info
beat: python -m celery beat -A backend.app.queue.celery_app --loglevel=info