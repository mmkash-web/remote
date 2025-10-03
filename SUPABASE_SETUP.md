# Supabase PostgreSQL Setup Guide

This guide shows you how to configure the MikroTik Billing System with Supabase PostgreSQL database.

## 📋 Your Supabase Database Details

- **Host**: `db.seuzxvthbxowmofxalmm.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: `Emmkash20`

## 🚀 Quick Setup

### Step 1: Create Environment File

Create a `.env` file in your project root:

```bash
# Windows PowerShell
Copy-Item .env.production .env

# Linux/Mac
cp .env.production .env
```

Or create manually with this content:

```env
# Django Settings
SECRET_KEY=django-insecure-change-this-to-random-string-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase PostgreSQL Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=postgres
DATABASE_USER=postgres
DATABASE_PASSWORD=Emmkash20
DATABASE_HOST=db.seuzxvthbxowmofxalmm.supabase.co
DATABASE_PORT=5432

# Email (optional for now)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery (optional - for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 2: Install PostgreSQL Driver

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install psycopg2 (PostgreSQL driver)
pip install psycopg2-binary
```

### Step 3: Test Database Connection

```bash
# Test connection
python manage.py check
```

**Expected output**: No errors about database connection

### Step 4: Run Migrations

```bash
# Create database tables
python manage.py migrate
```

**Expected output**: 
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  ...
  (Many more migrations)
```

### Step 5: Create Admin User

```bash
# Run setup script
python setup_admin.py
```

**Or manually:**
```bash
python manage.py createsuperuser
# Follow prompts to create username/password
```

### Step 6: Start Server

```bash
python manage.py runserver
```

**Visit**: http://127.0.0.1:8000

## ✅ Verify Database Connection

Run this Python script to test the connection:

```bash
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrotik_billing.settings')
import django
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print('✓ Connected to PostgreSQL!')
        print(f'Database version: {version[0]}')
except Exception as e:
    print(f'✗ Connection failed: {e}')
"
```

## 🔧 Connection Options

Your Supabase database provides three connection types:

### 1. Direct Connection (Recommended for Development)
```
postgresql://postgres:Emmkash20@db.seuzxvthbxowmofxalmm.supabase.co:5432/postgres
```
- Best for long-lived connections
- IPv6 only
- Your current configuration uses this

### 2. Transaction Pooler (For Production/Serverless)
```
postgresql://postgres.seuzxvthbxowmofxalmm:Emmkash20@aws-1-eu-west-2.pooler.supabase.com:6543/postgres
```
- Best for serverless/short-lived connections
- IPv4 compatible
- Use this if deploying to platforms like Vercel, Netlify

### 3. Session Pooler (Alternative)
```
postgresql://postgres.seuzxvthbxowmofxalmm:Emmkash20@aws-1-eu-west-2.pooler.supabase.com:5432/postgres
```
- IPv4 compatible
- Use if on IPv4-only network

## 🔄 Switching Connection Types

To use **Transaction Pooler** (for production):

Update your `.env` file:
```env
DATABASE_HOST=aws-1-eu-west-2.pooler.supabase.com
DATABASE_PORT=6543
DATABASE_USER=postgres.seuzxvthbxowmofxalmm
```

To use **Session Pooler**:
```env
DATABASE_HOST=aws-1-eu-west-2.pooler.supabase.com
DATABASE_PORT=5432
DATABASE_USER=postgres.seuzxvthbxowmofxalmm
```

## 🔐 Security Best Practices

### 1. Never Commit .env File

The `.env` file is already in `.gitignore`. Never commit database credentials to Git!

### 2. Generate Strong SECRET_KEY

For production:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy the output to your `.env` file as `SECRET_KEY`.

### 3. Enable SSL (Production)

For production, update `.env`:
```env
DATABASE_OPTIONS={"sslmode": "require"}
```

And update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': config('DATABASE_USER', default=''),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default=''),
        'PORT': config('DATABASE_PORT', default=''),
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

## 📊 View Database in Supabase Dashboard

1. Go to: https://supabase.com/dashboard
2. Login to your account
3. Select your project
4. Click **Table Editor** to view tables
5. After running migrations, you'll see all Django tables

## 🧪 Testing with Supabase

### Check Connected Tables

```bash
python manage.py dbshell
```

Then in PostgreSQL shell:
```sql
-- List all tables
\dt

-- View customers table structure
\d customers_customer

-- Count records
SELECT COUNT(*) FROM customers_customer;

-- Exit
\q
```

## 🚀 Deployment Checklist

When deploying to production:

- [ ] Update `SECRET_KEY` to random string
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Consider using Transaction Pooler for better scalability
- [ ] Enable SSL with `sslmode=require`
- [ ] Set up database backups in Supabase dashboard
- [ ] Configure environment variables on hosting platform
- [ ] Test connection from production server

## 🔄 Database Backup

Supabase provides automatic backups, but you can also backup manually:

```bash
# Export database to file
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Restore from file
python manage.py loaddata backup_20250103.json
```

## 📈 Monitoring

### Check Database Size
```sql
SELECT 
    pg_size_pretty(pg_database_size('postgres')) as db_size;
```

### Check Table Sizes
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🆘 Troubleshooting

### Error: "could not connect to server"

**Check:**
1. Internet connection working
2. Supabase project is active (not paused)
3. Credentials are correct in `.env`
4. Firewall not blocking connection

**Test connection:**
```bash
# Windows (PowerShell)
Test-NetConnection -ComputerName db.seuzxvthbxowmofxalmm.supabase.co -Port 5432

# Linux/Mac
nc -zv db.seuzxvthbxowmofxalmm.supabase.co 5432
```

### Error: "FATAL: password authentication failed"

**Solution**: 
1. Go to Supabase Dashboard
2. Settings → Database
3. Reset database password
4. Update `.env` file with new password

### Error: "psycopg2 not installed"

**Solution**:
```bash
pip install psycopg2-binary
```

### Error: "SSL connection required"

**Solution**: Add to `.env`:
```env
DATABASE_OPTIONS={"sslmode": "require"}
```

### Database Connection Slow

**Solution**: Use Transaction Pooler instead of Direct Connection

Update `.env`:
```env
DATABASE_HOST=aws-1-eu-west-2.pooler.supabase.com
DATABASE_PORT=6543
DATABASE_USER=postgres.seuzxvthbxowmofxalmm
```

## 📚 Additional Resources

- **Supabase Documentation**: https://supabase.com/docs
- **Django PostgreSQL Guide**: https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes
- **Connection Pooling**: https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler

## 🎉 Next Steps

After successful setup:

1. ✅ Run: `python run_tests.py` to verify everything works
2. ✅ Follow [TESTING_GUIDE.md](TESTING_GUIDE.md) for complete testing
3. ✅ Create test data: profiles, routers, customers
4. ✅ Deploy to production with [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Your database is configured and ready!** 🚀

All your data (routers, customers, payments, vouchers) will now be stored in Supabase PostgreSQL instead of local SQLite.

