# Complete VPS Deployment Guide

Deploy your entire MikroTik Billing System on a VPS with VPN, Django, and all services.

---

## 🎯 What You'll Get

After following this guide:
- ✅ Django billing system running on VPS
- ✅ WireGuard VPN server for routers
- ✅ PostgreSQL database
- ✅ Nginx web server with SSL
- ✅ Celery for background tasks
- ✅ Redis for caching
- ✅ Automatic startup on boot
- ✅ Professional production setup

**Total Time:** 2-3 hours

---

## 📋 Prerequisites

### 1. Get a VPS

**Recommended Providers:**
- **DigitalOcean** - $6/month (1GB RAM, 25GB SSD)
- **Vultr** - $6/month
- **Linode** - $5/month
- **Contabo** - $4/month (best value)
- **Hetzner** - €4.15/month

**Minimum Requirements:**
- 1GB RAM (2GB recommended)
- 1 CPU core
- 25GB storage
- Ubuntu 22.04 LTS

### 2. Domain Name (Optional but Recommended)

- Register at Namecheap, GoDaddy, or Cloudflare
- Point A record to your VPS IP
- Example: `billing.yourdomain.com`

---

## 🚀 Part 1: Initial VPS Setup (15 minutes)

### Step 1: Connect to VPS

```bash
# SSH to your VPS (replace with your IP)
ssh root@YOUR_VPS_IP

# Enter password when prompted
```

### Step 2: Create Non-Root User

```bash
# Create user
adduser deploy
# Set a strong password

# Add to sudo group
usermod -aG sudo deploy

# Switch to new user
su - deploy
```

### Step 3: Update System

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y build-essential git curl wget \
    software-properties-common ufw fail2ban
```

### Step 4: Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS, and VPN
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 51820/udp   # WireGuard VPN

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 🔐 Part 2: Install WireGuard VPN Server (20 minutes)

### Step 1: Install WireGuard

```bash
# Install WireGuard
sudo apt install -y wireguard

# Enable IP forwarding
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Step 2: Generate Server Keys

```bash
# Create directory
sudo mkdir -p /etc/wireguard
cd /etc/wireguard

# Generate keys
wg genkey | sudo tee server_private.key | wg pubkey | sudo tee server_public.key

# Set permissions
sudo chmod 600 server_private.key
```

### Step 3: Create WireGuard Configuration

```bash
# Get your server's network interface name
ip route list default
# Note the interface name (usually eth0, ens3, etc.)

# Create config file
sudo nano /etc/wireguard/wg0.conf
```

Paste this configuration (replace `SERVER_PRIVATE_KEY` and `eth0` with your values):

```ini
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = SERVER_PRIVATE_KEY_HERE

# NAT rules (replace eth0 with your interface)
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Router 1 (add more as needed)
[Peer]
# PublicKey will be added after router configuration
# AllowedIPs = 10.10.0.2/32

# Router 2
[Peer]
# PublicKey = 
# AllowedIPs = 10.10.0.3/32

# Router 3
[Peer]
# PublicKey = 
# AllowedIPs = 10.10.0.4/32
```

Save and exit (Ctrl+X, Y, Enter)

### Step 4: Start WireGuard

```bash
# Start WireGuard
sudo wg-quick up wg0

# Enable on boot
sudo systemctl enable wg-quick@wg0

# Check status
sudo wg show

# You should see your interface listening
```

### Step 5: Save Server Public Key

```bash
# Display server public key (save this - you'll need it for MikroTik config)
sudo cat /etc/wireguard/server_public.key
```

✅ **VPN Server is now ready!**

---

## 🐍 Part 3: Install Python & Dependencies (15 minutes)

### Step 1: Install Python 3.11

```bash
# Add Python PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Verify installation
python3.11 --version
```

### Step 2: Install PostgreSQL

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE mikrotik_billing;
CREATE USER billing_user WITH PASSWORD 'YourStrongPassword123';
ALTER ROLE billing_user SET client_encoding TO 'utf8';
ALTER ROLE billing_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE billing_user SET timezone TO 'Africa/Nairobi';
GRANT ALL PRIVILEGES ON DATABASE mikrotik_billing TO billing_user;
\q
EOF

echo "✅ PostgreSQL database created!"
```

### Step 3: Install Redis

```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Change: supervised no → supervised systemd
# Save and exit

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

---

## 📦 Part 4: Deploy Django Application (30 minutes)

### Step 1: Clone Your Project

```bash
# Go to home directory
cd ~

# Clone from GitHub (or upload your code)
git clone https://github.com/yourusername/mikrotikvpn.git
# OR upload via SCP/SFTP

# If uploading manually:
# On your PC: scp -r C:\Users\A\Desktop\mikrotikvpn deploy@YOUR_VPS_IP:~/

cd mikrotikvpn
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Packages

```bash
# Install requirements
pip install -r requirements.txt

# Install production server
pip install gunicorn

# Install PostgreSQL driver
pip install psycopg2-binary
```

### Step 4: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Paste this configuration:

```bash
# Django Settings
SECRET_KEY=your-very-long-random-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=YOUR_VPS_IP,yourdomain.com,www.yourdomain.com

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=mikrotik_billing
DATABASE_USER=billing_user
DATABASE_PASSWORD=YourStrongPassword123
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# MikroTik API
MIKROTIK_API_PORT=8728
MIKROTIK_API_TIMEOUT=10

# Email (optional - configure later)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Timezone
TIME_ZONE=Africa/Nairobi

# Security (in production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

Save and exit (Ctrl+X, Y, Enter)

### Step 5: Run Migrations

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Enter username: admin
# Enter email (optional)
# Enter password: (choose a strong password)

# Collect static files
python manage.py collectstatic --noinput
```

### Step 6: Test Django

```bash
# Test run (should work on port 8000)
python manage.py runserver 0.0.0.0:8000

# Visit: http://YOUR_VPS_IP:8000
# If it works, press Ctrl+C to stop
```

✅ **Django is installed and running!**

---

## 🌐 Part 5: Configure Nginx Web Server (20 minutes)

### Step 1: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 2: Create Nginx Configuration

```bash
# Create config file
sudo nano /etc/nginx/sites-available/mikrotik_billing
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name YOUR_VPS_IP yourdomain.com www.yourdomain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /home/deploy/mikrotikvpn/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/deploy/mikrotikvpn/media/;
        expires 7d;
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny access to sensitive files
    location ~ /\.(?!well-known) {
        deny all;
    }
}
```

Save and exit

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/mikrotik_billing /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## ⚙️ Part 6: Configure Systemd Services (15 minutes)

### Service 1: Gunicorn (Django)

```bash
# Create Gunicorn service
sudo nano /etc/systemd/system/mikrotik-billing.service
```

Paste:

```ini
[Unit]
Description=MikroTik Billing System
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/mikrotikvpn
Environment="PATH=/home/deploy/mikrotikvpn/venv/bin"
ExecStart=/home/deploy/mikrotikvpn/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --access-logfile /home/deploy/mikrotikvpn/logs/access.log \
    --error-logfile /home/deploy/mikrotikvpn/logs/error.log \
    mikrotik_billing.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Service 2: Celery Worker

```bash
# Create Celery worker service
sudo nano /etc/systemd/system/celery-worker.service
```

Paste:

```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/mikrotikvpn
Environment="PATH=/home/deploy/mikrotikvpn/venv/bin"
ExecStart=/home/deploy/mikrotikvpn/venv/bin/celery -A mikrotik_billing worker \
    --loglevel=info \
    --logfile=/home/deploy/mikrotikvpn/logs/celery-worker.log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Service 3: Celery Beat (Scheduler)

```bash
# Create Celery beat service
sudo nano /etc/systemd/system/celery-beat.service
```

Paste:

```ini
[Unit]
Description=Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/mikrotikvpn
Environment="PATH=/home/deploy/mikrotikvpn/venv/bin"
ExecStart=/home/deploy/mikrotikvpn/venv/bin/celery -A mikrotik_billing beat \
    --loglevel=info \
    --logfile=/home/deploy/mikrotikvpn/logs/celery-beat.log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Create Log Directory

```bash
# Create logs directory
mkdir -p ~/mikrotikvpn/logs

# Set permissions
chmod 755 ~/mikrotikvpn/logs
```

### Start All Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable mikrotik-billing celery-worker celery-beat

# Start services
sudo systemctl start mikrotik-billing
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Check status
sudo systemctl status mikrotik-billing
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

✅ **All services running!**

---

## 🔒 Part 7: Setup SSL Certificate (10 minutes)

### Install Certbot (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: Yes)

# Test auto-renewal
sudo certbot renew --dry-run
```

✅ **SSL Certificate installed!**

Your site is now accessible via: `https://yourdomain.com`

---

## 🔧 Part 8: Configure MikroTik Routers (10 minutes per router)

### On Each MikroTik Router:

#### Step 1: Create WireGuard Interface

```bash
# SSH to MikroTik
ssh admin@192.168.88.1

# Create WireGuard interface
/interface/wireguard/add name=wg-vpn listen-port=51820

# Get router's public key (SAVE THIS!)
/interface/wireguard/print
```

#### Step 2: Add VPS as Peer

```bash
# Add VPS server as peer
/interface/wireguard/peers/add \
    interface=wg-vpn \
    public-key="YOUR_VPS_SERVER_PUBLIC_KEY" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s

# Assign IP address (10.10.0.2 for router 1, 10.10.0.3 for router 2, etc.)
/ip/address/add address=10.10.0.2/24 interface=wg-vpn

# Enable API
/ip/service/set api disabled=no port=8728

# Test connection
/ping 10.10.0.1 count=5
```

#### Step 3: Add Router's Key to VPS

Back on VPS:

```bash
# Edit WireGuard config
sudo nano /etc/wireguard/wg0.conf

# Add peer section (uncomment and add public key):
[Peer]
PublicKey = ROUTER_PUBLIC_KEY_HERE
AllowedIPs = 10.10.0.2/32

# Save and restart WireGuard
sudo wg-quick down wg0
sudo wg-quick up wg0

# Verify connection
sudo wg show
ping 10.10.0.2
```

✅ **Router connected via VPN!**

---

## ✅ Part 9: Final Testing

### Test 1: Access Website

```bash
# Visit your site
https://yourdomain.com
# or
http://YOUR_VPS_IP

# Login with superuser credentials
```

### Test 2: Add Router in Django

```
1. Go to: https://yourdomain.com/routers/create/
2. Add router:
   - Name: Router1
   - VPN IP: 10.10.0.2
   - Username: admin
   - Password: (router password)
   - Port: 8728
3. Click "Test Connection"
4. Should show: ✅ Success!
```

### Test 3: Create Customer

```
1. Create a profile first
2. Then create a customer
3. Check on MikroTik: /ppp/secret/print
4. Customer should appear!
```

✅ **System is fully operational!**

---

## 📊 Part 10: Monitoring & Maintenance

### Check Service Status

```bash
# Check all services
sudo systemctl status mikrotik-billing
sudo systemctl status celery-worker
sudo systemctl status celery-beat
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# Check WireGuard
sudo wg show

# View logs
tail -f ~/mikrotikvpn/logs/access.log
tail -f ~/mikrotikvpn/logs/error.log
tail -f ~/mikrotikvpn/logs/celery-worker.log
```

### Restart Services

```bash
# Restart Django
sudo systemctl restart mikrotik-billing

# Restart Celery
sudo systemctl restart celery-worker celery-beat

# Restart Nginx
sudo systemctl restart nginx

# Restart everything
sudo systemctl restart mikrotik-billing celery-worker celery-beat nginx
```

### Update Code

```bash
# When you make changes
cd ~/mikrotikvpn

# Pull latest code
git pull origin main

# Activate venv
source venv/bin/activate

# Install any new requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart mikrotik-billing celery-worker celery-beat
```

---

## 🔐 Security Checklist

```
□ Changed default SSH port
□ Disabled root SSH login
□ Configured fail2ban
□ Firewall (UFW) enabled
□ SSL certificate installed
□ Strong database password
□ Django SECRET_KEY is random and secure
□ DEBUG=False in production
□ Regular backups configured
□ WireGuard VPN secured
□ MikroTik API password strong
```

---

## 📦 Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
# Backup script

BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump mikrotik_billing > $BACKUP_DIR/db_$DATE.sql

# Backup code
tar -czf $BACKUP_DIR/code_$DATE.tar.gz ~/mikrotikvpn

# Backup WireGuard config
sudo tar -czf $BACKUP_DIR/wireguard_$DATE.tar.gz /etc/wireguard

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and add to crontab:

```bash
chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/deploy/backup.sh
```

---

## 🚀 Quick Command Reference

```bash
# Start services
sudo systemctl start mikrotik-billing celery-worker celery-beat

# Stop services
sudo systemctl stop mikrotik-billing celery-worker celery-beat

# Restart services
sudo systemctl restart mikrotik-billing celery-worker celery-beat

# View logs
tail -f ~/mikrotikvpn/logs/error.log

# Check VPN status
sudo wg show

# Test API from VPS
python3 << EOF
from librouteros import connect
api = connect(username='admin', password='password', host='10.10.0.2')
print(list(api('/system/identity/print')))
EOF
```

---

## 💰 Cost Summary

| Service | Cost |
|---------|------|
| VPS (2GB RAM) | $10/month |
| Domain Name | $10-15/year |
| SSL Certificate | FREE (Let's Encrypt) |
| **Total** | **~$10-11/month** |

---

## ✅ Success Checklist

```
INFRASTRUCTURE:
□ VPS running Ubuntu 22.04
□ Firewall configured
□ Non-root user created
□ SSH secured

VPN:
□ WireGuard installed
□ Server running (sudo wg show)
□ Routers connected
□ Can ping routers from VPS

DJANGO:
□ Python 3.11 installed
□ PostgreSQL database created
□ Redis running
□ Django app deployed
□ Migrations applied
□ Superuser created
□ Static files collected

WEB SERVER:
□ Nginx installed and running
□ SSL certificate installed
□ Site accessible via HTTPS

SERVICES:
□ Gunicorn running
□ Celery worker running
□ Celery beat running
□ All services auto-start on boot

TESTING:
□ Can access website
□ Can login to admin
□ Can add routers
□ Can create customers
□ Customers sync to MikroTik
□ Payment callbacks work
```

---

## 🆘 Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u mikrotik-billing -n 50
sudo journalctl -u celery-worker -n 50

# Check file permissions
ls -la ~/mikrotikvpn

# Verify paths in service files
cat /etc/systemd/system/mikrotik-billing.service
```

### Can't connect to router

```bash
# Test VPN
ping 10.10.0.2

# Check WireGuard
sudo wg show

# Check router firewall
# On MikroTik: /ip firewall filter print
```

### Database errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U billing_user -d mikrotik_billing -h localhost

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

---

## 🎓 Next Steps

1. ✅ Add your routers
2. ✅ Create profiles
3. ✅ Add customers
4. ✅ Test payment flow
5. ✅ Configure M-Pesa/PayPal
6. ✅ Setup monitoring
7. ✅ Configure backups
8. ✅ Add more routers as you scale

---

**🎉 Congratulations! Your production MikroTik Billing System is live!**

Visit: `https://yourdomain.com`

Login and start managing your hotspot business! 💰🚀

