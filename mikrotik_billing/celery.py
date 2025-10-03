"""
Celery configuration for MikroTik Billing System.
This allows running background tasks like router health checks and payment processing.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrotik_billing.settings')

app = Celery('mikrotik_billing')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'check-router-status-every-5-minutes': {
        'task': 'routers.tasks.check_all_routers_status',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-expired-users-daily': {
        'task': 'customers.tasks.check_expired_users',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'generate-daily-reports': {
        'task': 'reports.tasks.generate_daily_report',
        'schedule': crontab(hour=23, minute=55),  # Daily at 11:55 PM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

