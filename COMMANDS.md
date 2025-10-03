# MikroTik Billing - Command Reference

Quick reference for common commands and operations.

## 🚀 Setup Commands

### Initial Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create admin user and sample data
python setup_admin.py

# Check installation
python check_setup.py
```

## 🔧 Development Commands

### Running the Server
```bash
# Development server (default port 8000)
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations status
python manage.py showmigrations

# Create database backup
python manage.py dumpdata > backup.json

# Restore from backup
python manage.py loaddata backup.json

# Reset database (CAUTION: Destroys all data!)
python manage.py flush
```

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Collect without prompting
python manage.py collectstatic --noinput

# Clear static files
python manage.py collectstatic --clear --noinput
```

## 🔄 Celery Commands (Background Tasks)

### Start Celery Worker
```bash
# Development
celery -A mikrotik_billing worker -l info

# Production (with concurrency)
celery -A mikrotik_billing worker -l info --concurrency=4
```

### Start Celery Beat (Scheduler)
```bash
celery -A mikrotik_billing beat -l info
```

### Celery Flower (Monitoring)
```bash
# Install flower
pip install flower

# Start flower
celery -A mikrotik_billing flower
# Visit http://localhost:5555
```

### Run Specific Tasks
```bash
# In Django shell
python manage.py shell

# Then run:
from routers.tasks import check_all_routers_status
result = check_all_routers_status.delay()
```

## 🧪 Testing & Debugging

### Django Shell
```bash
# Interactive Python shell with Django
python manage.py shell

# Example usage:
from customers.models import Customer
customers = Customer.objects.all()
print(customers)
```

### Database Shell
```bash
# SQLite
python manage.py dbshell

# Or directly:
sqlite3 db.sqlite3
```

### Check for Issues
```bash
# Check for problems
python manage.py check

# Check deployment readiness
python manage.py check --deploy
```

### View URLs
```bash
# List all URLs
python manage.py show_urls  # Requires django-extensions
```

## 📊 Management Commands

### Custom Management Commands
```bash
# List all management commands
python manage.py help

# Get help on specific command
python manage.py help migrate
```

## 🔐 Security Commands

### Generate Secret Key
```bash
# Generate new SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Check Security
```bash
# Check security settings
python manage.py check --deploy
```

## 📦 Dependency Management

### Update Dependencies
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade Django

# Show outdated packages
pip list --outdated

# Freeze current dependencies
pip freeze > requirements.txt
```

## 🧹 Maintenance Commands

### Clear Cache
```bash
# Clear all cache
python manage.py clear_cache  # If django-extensions installed
```

### Clear Sessions
```bash
# Clear expired sessions
python manage.py clearsessions
```

### Delete Old Logs
```bash
# Linux/Mac
find . -name "*.log" -mtime +30 -delete

# Windows PowerShell
Get-ChildItem -Path . -Include *.log -Recurse | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

## 🚢 Production Commands

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Restart Services (systemd)
```bash
# Restart Gunicorn
sudo systemctl restart mikrotik-billing

# Restart Celery
sudo systemctl restart mikrotik-celery-worker
sudo systemctl restart mikrotik-celery-beat

# Restart Nginx
sudo systemctl restart nginx
```

### View Logs
```bash
# Application logs
sudo journalctl -u mikrotik-billing -f

# Celery logs
sudo journalctl -u mikrotik-celery-worker -f

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Database Backup (PostgreSQL)
```bash
# Backup
pg_dump -U mikrotik_user mikrotik_billing > backup_$(date +%Y%m%d).sql

# Restore
psql -U mikrotik_user mikrotik_billing < backup_20250101.sql
```

## 🧪 Testing API Endpoints

### Test Payment Callback
```bash
# Using curl
curl -X POST http://localhost:8000/api/payment/callback/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST001",
    "customer_username": "customer1",
    "amount": 50.00,
    "currency": "KES",
    "status": "success",
    "payment_method": "MPESA"
  }'

# Using Python requests
python -c "
import requests
import json

data = {
    'transaction_id': 'TEST001',
    'customer_username': 'customer1',
    'amount': 50.00,
    'currency': 'KES',
    'status': 'success',
    'payment_method': 'MPESA'
}

response = requests.post(
    'http://localhost:8000/api/payment/callback/',
    json=data
)
print(response.json())
"
```

## 🔍 Debugging Commands

### Show Model Schema
```bash
# Show SQL for model
python manage.py sqlmigrate customers 0001

# Show all tables
python manage.py inspectdb
```

### Django Debug Mode
```python
# In settings.py
DEBUG = True

# View SQL queries in shell
from django.db import connection
print(connection.queries)
```

## 📱 Quick Actions

### Create Sample Router
```python
python manage.py shell

from routers.models import Router
from django.contrib.auth.models import User

admin = User.objects.first()
router = Router.objects.create(
    name='TestRouter',
    vpn_ip='10.10.0.2',
    username='admin',
    password='password',
    api_port=8728,
    created_by=admin
)
print(f"Created router: {router.name}")
```

### Create Sample Customer
```python
python manage.py shell

from customers.models import Customer
from routers.models import Router
from profiles.models import Profile

router = Router.objects.first()
profile = Profile.objects.first()

customer = Customer.objects.create(
    username='testuser',
    password='password123',
    full_name='Test User',
    email='test@example.com',
    router=router,
    profile=profile
)
print(f"Created customer: {customer.username}")
```

## 🆘 Troubleshooting Commands

### Port Already in Use
```bash
# Find process using port 8000
# Linux/Mac:
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### Database Locked (SQLite)
```bash
# Close all connections and restart
python manage.py migrate
```

## 📚 Documentation Commands

### Generate Documentation
```bash
# Install Sphinx
pip install sphinx

# Generate docs
sphinx-quickstart
sphinx-build -b html docs/ docs/_build/
```

## 🎯 Quick Start Sequence

```bash
# Complete setup from scratch
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python setup_admin.py
python check_setup.py
python manage.py runserver
```

## 💡 Useful Aliases (Optional)

Add to your `.bashrc` or `.zshrc`:

```bash
# Django aliases
alias pm='python manage.py'
alias pmr='python manage.py runserver'
alias pmm='python manage.py migrate'
alias pmmm='python manage.py makemigrations'
alias pms='python manage.py shell'

# Celery aliases
alias celery-worker='celery -A mikrotik_billing worker -l info'
alias celery-beat='celery -A mikrotik_billing beat -l info'

# Quick setup
alias venv-activate='source venv/bin/activate'
```

---

**Tip**: Bookmark this file for quick reference!

For more detailed information, see:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

