web: gunicorn app:app
worker: celery worker -A app.celery --loglevel=info
