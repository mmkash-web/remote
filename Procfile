# Procfile for Scalingo deployment

# Web process (Gunicorn)
web: gunicorn mikrotik_billing.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120

# Worker process (Celery)
worker: celery -A mikrotik_billing worker --loglevel=info --concurrency=2

# Celery Beat scheduler (for periodic tasks)
beat: celery -A mikrotik_billing beat --loglevel=info

