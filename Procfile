web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && python -m celery worker -A app.queue.celery_app --loglevel=info
beat: cd backend && python -m celery beat -A app.queue.celery_app --loglevel=info