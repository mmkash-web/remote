# Production Deployment Guide

This guide covers deploying the MikroTik Billing System to a production environment.

## Server Requirements

### Minimum Specifications
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS or similar

### Recommended Specifications
- **CPU**: 4 cores
- **RAM**: 4GB+
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS

## Pre-deployment Checklist

- [ ] Domain name configured with DNS
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Server firewall configured
- [ ] PostgreSQL/MySQL database set up
- [ ] Redis server installed (for Celery)
- [ ] Backup strategy planned
- [ ] Payment gateway accounts created

## Installation Steps

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies

```bash
# Python and system packages
sudo apt install python3.10 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git -y

# Install Node.js (optional, for Tailwind compilation)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

### 3. Create Application User

```bash
sudo useradd -m -s /bin/bash mikrotik
sudo su - mikrotik
```

### 4. Clone Repository

```bash
cd /home/mikrotik
git clone https://github.com/yourusername/mikrotik-billing.git
cd mikrotik-billing
```

### 5. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Database

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
psql
CREATE DATABASE mikrotik_billing;
CREATE USER mikrotik_user WITH PASSWORD 'your_secure_password';
ALTER ROLE mikrotik_user SET client_encoding TO 'utf8';
ALTER ROLE mikrotik_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE mikrotik_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE mikrotik_billing TO mikrotik_user;
\q
exit
```

### 7. Configure Environment

```bash
# Create .env file
cat > /home/mikrotik/mikrotik-billing/.env << 'EOF'
SECRET_KEY=your-very-long-and-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=mikrotik_billing
DATABASE_USER=mikrotik_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway Settings
MPESA_CONSUMER_KEY=your-mpesa-key
MPESA_CONSUMER_SECRET=your-mpesa-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey

PAYPAL_CLIENT_ID=your-paypal-id
PAYPAL_CLIENT_SECRET=your-paypal-secret
PAYPAL_MODE=live
EOF

# Secure the .env file
chmod 600 .env
```

### 8. Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 9. Set Up Gunicorn

```bash
pip install gunicorn
```

Create systemd service file:

```bash
sudo nano /etc/systemd/system/mikrotik-billing.service
```

Add:

```ini
[Unit]
Description=MikroTik Billing Gunicorn daemon
After=network.target

[Service]
User=mikrotik
Group=www-data
WorkingDirectory=/home/mikrotik/mikrotik-billing
Environment="PATH=/home/mikrotik/mikrotik-billing/venv/bin"
ExecStart=/home/mikrotik/mikrotik-billing/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/mikrotik/mikrotik-billing/mikrotik_billing.sock \
          mikrotik_billing.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 10. Set Up Celery

```bash
sudo nano /etc/systemd/system/mikrotik-celery-worker.service
```

Add:

```ini
[Unit]
Description=MikroTik Billing Celery Worker
After=network.target

[Service]
Type=forking
User=mikrotik
Group=www-data
WorkingDirectory=/home/mikrotik/mikrotik-billing
Environment="PATH=/home/mikrotik/mikrotik-billing/venv/bin"
ExecStart=/home/mikrotik/mikrotik-billing/venv/bin/celery -A mikrotik_billing worker -l info --detach

[Install]
WantedBy=multi-user.target
```

Create Celery Beat service:

```bash
sudo nano /etc/systemd/system/mikrotik-celery-beat.service
```

Add:

```ini
[Unit]
Description=MikroTik Billing Celery Beat
After=network.target

[Service]
Type=simple
User=mikrotik
Group=www-data
WorkingDirectory=/home/mikrotik/mikrotik-billing
Environment="PATH=/home/mikrotik/mikrotik-billing/venv/bin"
ExecStart=/home/mikrotik/mikrotik-billing/venv/bin/celery -A mikrotik_billing beat -l info

[Install]
WantedBy=multi-user.target
```

### 11. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/mikrotik-billing
```

Add:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/mikrotik/mikrotik-billing;
    }

    location /media/ {
        root /home/mikrotik/mikrotik-billing;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/mikrotik/mikrotik-billing/mikrotik_billing.sock;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/mikrotik-billing /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 12. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 13. Start Services

```bash
sudo systemctl start mikrotik-billing
sudo systemctl enable mikrotik-billing

sudo systemctl start mikrotik-celery-worker
sudo systemctl enable mikrotik-celery-worker

sudo systemctl start mikrotik-celery-beat
sudo systemctl enable mikrotik-celery-beat
```

### 14. Configure Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Post-Deployment

### 1. Verify Services

```bash
sudo systemctl status mikrotik-billing
sudo systemctl status mikrotik-celery-worker
sudo systemctl status mikrotik-celery-beat
sudo systemctl status nginx
```

### 2. Check Logs

```bash
# Application logs
tail -f /var/log/nginx/error.log

# Celery logs
sudo journalctl -u mikrotik-celery-worker -f
```

### 3. Set Up Monitoring

Consider using:
- **Sentry** for error tracking
- **New Relic** or **DataDog** for performance monitoring
- **UptimeRobot** for uptime monitoring

### 4. Configure Backups

```bash
# Database backup script
cat > /home/mikrotik/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/mikrotik/backups"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U mikrotik_user mikrotik_billing > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/mikrotik/mikrotik-billing/media/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /home/mikrotik/backup.sh
```

Add to crontab:

```bash
crontab -e
# Add line:
0 2 * * * /home/mikrotik/backup.sh
```

## Security Hardening

### 1. Secure PostgreSQL

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Change peer to md5 for local connections
sudo systemctl restart postgresql
```

### 2. Secure Redis

```bash
sudo nano /etc/redis/redis.conf
# Uncomment and set:
# requirepass your-redis-password
# bind 127.0.0.1
sudo systemctl restart redis
```

### 3. Fail2Ban (Optional)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### 4. Regular Updates

```bash
# Set up automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## Maintenance

### Update Application

```bash
cd /home/mikrotik/mikrotik-billing
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart mikrotik-billing
sudo systemctl restart mikrotik-celery-worker
sudo systemctl restart mikrotik-celery-beat
```

### Monitor Disk Space

```bash
df -h
du -sh /home/mikrotik/mikrotik-billing/media
```

### Clear Old Logs

```bash
# Clear logs older than 30 days
find /home/mikrotik/mikrotik-billing -name "*.log" -mtime +30 -delete
```

## Troubleshooting

### Application Won't Start

```bash
sudo journalctl -u mikrotik-billing -n 50
```

### Database Connection Issues

```bash
sudo -u postgres psql
\l  # List databases
\du # List users
```

### Nginx Issues

```bash
sudo nginx -t
sudo systemctl status nginx
tail -f /var/log/nginx/error.log
```

### Permission Issues

```bash
sudo chown -R mikrotik:www-data /home/mikrotik/mikrotik-billing
sudo chmod -R 755 /home/mikrotik/mikrotik-billing
sudo chmod -R 775 /home/mikrotik/mikrotik-billing/media
```

## Performance Optimization

### 1. Database Tuning

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_customer_username ON customers_customer(username);
CREATE INDEX idx_payment_status ON payments_payment(status);
```

### 2. Gunicorn Workers

Adjust worker count based on CPU cores:
```
workers = (2 × CPU_cores) + 1
```

### 3. Redis Optimization

```bash
sudo nano /etc/redis/redis.conf
# Set appropriate maxmemory
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## Support

For issues during deployment:
- Check logs first
- Review this guide carefully
- Consult Django deployment documentation
- Open an issue on GitHub

---

**Security Note**: Always use strong passwords, keep software updated, and regularly back up your data!

