# VPS Deployment Quick Summary

**One-page overview of complete VPS deployment**

---

## 🎯 What You Need

1. **VPS** - Any Ubuntu 22.04 server ($5-10/month)
2. **Domain** (optional) - For SSL and easy access
3. **2-3 hours** - Total setup time

---

## 📋 Complete Setup Steps

### 1️⃣ VPS Initial Setup (15 min)
```bash
ssh root@YOUR_VPS_IP
apt update && apt upgrade -y
adduser deploy
usermod -aG sudo deploy
ufw allow 22,80,443,51820/tcp
ufw allow 51820/udp
ufw enable
```

### 2️⃣ Install WireGuard VPN (20 min)
```bash
apt install wireguard -y
cd /etc/wireguard
wg genkey | tee server_private.key | wg pubkey > server_public.key
nano wg0.conf  # Configure VPN
wg-quick up wg0
systemctl enable wg-quick@wg0
```

### 3️⃣ Install Databases (15 min)
```bash
# PostgreSQL
apt install postgresql postgresql-contrib -y
sudo -u postgres createdb mikrotik_billing
sudo -u postgres createuser billing_user

# Redis
apt install redis-server -y
systemctl enable redis-server
```

### 4️⃣ Deploy Django (30 min)
```bash
git clone your-repo mikrotikvpn
cd mikrotikvpn
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 5️⃣ Setup Nginx (20 min)
```bash
apt install nginx -y
nano /etc/nginx/sites-available/mikrotik_billing
ln -s /etc/nginx/sites-available/mikrotik_billing /etc/nginx/sites-enabled/
systemctl restart nginx
```

### 6️⃣ Configure Services (15 min)
```bash
# Create systemd services for:
# - Gunicorn (Django)
# - Celery Worker
# - Celery Beat

systemctl enable mikrotik-billing celery-worker celery-beat
systemctl start mikrotik-billing celery-worker celery-beat
```

### 7️⃣ Setup SSL (10 min)
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com
```

### 8️⃣ Configure MikroTik Routers (10 min each)
```bash
# On MikroTik:
/interface/wireguard/add name=wg-vpn
/interface/wireguard/peers/add interface=wg-vpn \
    public-key="VPS_PUBLIC_KEY" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    persistent-keepalive=25s
/ip/address/add address=10.10.0.2/24 interface=wg-vpn
/ip/service/set api disabled=no port=8728
```

---

## 🔍 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  INTERNET                           │
└────────────────────┬────────────────────────────────┘
                     │
            ┌────────▼──────────┐
            │   Your VPS        │
            │  (Ubuntu 22.04)   │
            │                   │
            │  Public IP:       │
            │  XX.XX.XX.XX      │
            └─────────┬─────────┘
                      │
        ┌─────────────┼──────────────┐
        │             │              │
   ┌────▼────┐  ┌────▼─────┐  ┌────▼─────┐
   │ Nginx   │  │ Django   │  │WireGuard │
   │  :80    │  │  :8000   │  │  :51820  │
   │  :443   │  │          │  │  VPN     │
   └─────────┘  └────┬─────┘  └────┬─────┘
                     │             │
          ┌──────────┼─────────────┘
          │          │
     ┌────▼───┐ ┌───▼────┐
     │Postgres│ │ Redis  │
     │  :5432 │ │  :6379 │
     └────────┘ └────────┘

                VPN Network: 10.10.0.0/24
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼──────┐┌───▼──────┐┌───▼──────┐
    │ Router 1  ││ Router 2 ││ Router 3 │
    │10.10.0.2  ││10.10.0.3 ││10.10.0.4 │
    │ Nairobi   ││ Mombasa  ││ Kisumu   │
    └───────────┘└──────────┘└──────────┘
```

---

## 🌐 Service Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| SSH | 22 | TCP | Server access |
| HTTP | 80 | TCP | Web (redirects to HTTPS) |
| HTTPS | 443 | TCP | Secure web access |
| WireGuard | 51820 | UDP | VPN for routers |
| PostgreSQL | 5432 | TCP | Database (local only) |
| Redis | 6379 | TCP | Cache (local only) |
| Django | 8000 | TCP | App (local only) |
| MikroTik API | 8728 | TCP | Router management (VPN only) |

---

## 📂 Directory Structure

```
/home/deploy/
└── mikrotikvpn/
    ├── venv/                    # Virtual environment
    ├── mikrotik_billing/        # Django project
    ├── routers/                 # Routers app
    ├── customers/               # Customers app
    ├── profiles/                # Profiles app
    ├── payments/                # Payments app
    ├── static/                  # Static files (dev)
    ├── staticfiles/             # Collected static (prod)
    ├── media/                   # Uploaded files
    ├── logs/                    # Application logs
    ├── manage.py                # Django management
    ├── requirements.txt         # Python packages
    └── .env                     # Environment config

/etc/
├── nginx/
│   └── sites-available/
│       └── mikrotik_billing     # Nginx config
├── systemd/system/
│   ├── mikrotik-billing.service # Gunicorn service
│   ├── celery-worker.service    # Celery worker
│   └── celery-beat.service      # Celery scheduler
└── wireguard/
    └── wg0.conf                 # VPN config
```

---

## 🔧 Essential Commands

### Service Management
```bash
# Start all services
sudo systemctl start mikrotik-billing celery-worker celery-beat

# Check status
sudo systemctl status mikrotik-billing

# View logs
tail -f ~/mikrotikvpn/logs/error.log

# Restart after code changes
sudo systemctl restart mikrotik-billing celery-worker celery-beat
```

### VPN Management
```bash
# Check VPN status
sudo wg show

# Restart VPN
sudo wg-quick down wg0
sudo wg-quick up wg0

# Test router connection
ping 10.10.0.2
```

### Database Management
```bash
# Backup database
sudo -u postgres pg_dump mikrotik_billing > backup.sql

# Restore database
sudo -u postgres psql mikrotik_billing < backup.sql

# Access database
sudo -u postgres psql mikrotik_billing
```

---

## ✅ Testing Checklist

### After Deployment, Test:

1. **Website Access**
   ```
   Visit: https://yourdomain.com
   Expected: Login page appears
   ```

2. **Admin Login**
   ```
   Login with superuser credentials
   Expected: Dashboard loads
   ```

3. **VPN Connection**
   ```bash
   sudo wg show
   ping 10.10.0.2
   Expected: Router responds
   ```

4. **API Connection**
   ```bash
   telnet 10.10.0.2 8728
   Expected: Connected
   ```

5. **Add Router in Django**
   ```
   Go to: Routers → Add Router
   VPN IP: 10.10.0.2
   Test Connection
   Expected: ✅ Success
   ```

6. **Create Customer**
   ```
   Create profile first
   Then create customer
   Check on MikroTik: /ppp/secret/print
   Expected: Customer appears
   ```

---

## 🚨 Common Issues & Fixes

### Issue 1: Can't access website
```bash
# Check Nginx
sudo systemctl status nginx
sudo nginx -t

# Check Gunicorn
sudo systemctl status mikrotik-billing
sudo journalctl -u mikrotik-billing -n 50
```

### Issue 2: VPN not connecting
```bash
# Check WireGuard
sudo wg show
sudo systemctl status wg-quick@wg0

# Check firewall
sudo ufw status

# Verify router config
# On MikroTik: /interface wireguard print
```

### Issue 3: Database errors
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check connection
psql -U billing_user -d mikrotik_billing -h localhost

# Run migrations
cd ~/mikrotikvpn
source venv/bin/activate
python manage.py migrate
```

### Issue 4: Can't create users on MikroTik
```bash
# Test API from VPS
telnet 10.10.0.2 8728

# Check MikroTik API service
# On MikroTik: /ip service print

# Verify VPN IP in Django matches router's VPN IP
```

---

## 💾 Backup Script

```bash
# Create ~/backup.sh
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump mikrotik_billing > $BACKUP_DIR/db_$DATE.sql

# Backup code
tar -czf $BACKUP_DIR/code_$DATE.tar.gz ~/mikrotikvpn

# Backup VPN config
sudo tar -czf $BACKUP_DIR/wireguard_$DATE.tar.gz /etc/wireguard

# Keep last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

# Run daily at 2 AM
# crontab -e
# Add: 0 2 * * * /home/deploy/backup.sh
```

---

## 📊 Monitoring

### Check System Health

```bash
# CPU/Memory usage
htop

# Disk space
df -h

# Active connections
sudo netstat -tlnp

# View all logs
tail -f ~/mikrotikvpn/logs/*.log

# Database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

---

## 🔐 Security Hardening

```bash
# 1. Change SSH port (optional)
sudo nano /etc/ssh/sshd_config
# Change: Port 22 → Port 2222

# 2. Disable root login
# In /etc/ssh/sshd_config:
# PermitRootLogin no

# 3. Install fail2ban
sudo apt install fail2ban -y

# 4. Enable automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades

# 5. Strong passwords for database
# 6. Keep SECRET_KEY secret
# 7. Regular backups
```

---

## 💰 Cost Breakdown

### Monthly Costs:

| Item | Cost |
|------|------|
| VPS (2GB RAM, 2 CPU) | $10/month |
| Domain (.com) | ~$1/month ($12/year) |
| SSL Certificate | FREE (Let's Encrypt) |
| Bandwidth (1TB) | Included |
| **Total** | **~$11/month** |

### One-Time Costs:
- Domain registration: $10-15/year
- Initial setup time: 2-3 hours

---

## 🚀 Scaling Options

### For Growing Business:

**10-50 routers:**
- 2GB RAM VPS: $10-20/month
- Current setup is sufficient

**50-100 routers:**
- 4GB RAM VPS: $20-30/month
- Add load balancer

**100+ routers:**
- Multiple VPS servers
- Separate database server
- CDN for static files
- ~$100-200/month

---

## 📞 Support Resources

### Documentation Files:
- `VPS_COMPLETE_DEPLOYMENT.md` - Full deployment guide
- `TESTING_VPN_CONNECTION.md` - Testing & verification
- `MIKROTIK_WIREGUARD_SETUP.md` - MikroTik VPN setup
- `SCALINGO_DEPLOYMENT.md` - Alternative (PaaS)

### Quick Commands:
```bash
# Update code
cd ~/mikrotikvpn && git pull && sudo systemctl restart mikrotik-billing

# View errors
tail -f ~/mikrotikvpn/logs/error.log

# Restart everything
sudo systemctl restart mikrotik-billing celery-worker celery-beat nginx

# Check all services
sudo systemctl status mikrotik-billing celery-worker celery-beat nginx postgresql redis-server

# Full system reboot
sudo reboot
```

---

## ✅ Success Indicators

**You know it's working when:**

1. ✅ Website loads at https://yourdomain.com
2. ✅ Can login to admin panel
3. ✅ `sudo wg show` displays connected routers
4. ✅ Can ping routers: `ping 10.10.0.2`
5. ✅ Adding router shows "Connection successful"
6. ✅ Creating customer adds user to MikroTik
7. ✅ Customer can connect to hotspot
8. ✅ All systemd services show "active (running)"

---

## 🎓 Next Actions

1. ✅ Complete VPS deployment (follow `VPS_COMPLETE_DEPLOYMENT.md`)
2. ✅ Configure first router with WireGuard
3. ✅ Test connection thoroughly
4. ✅ Create profiles for your packages
5. ✅ Add first customer
6. ✅ Configure payment gateway (M-Pesa/PayPal)
7. ✅ Setup monitoring and backups
8. ✅ Scale as business grows!

---

**🎉 Your complete production system is ready!**

**Access:** https://yourdomain.com  
**Manage routers:** 10.10.0.2, 10.10.0.3, etc.  
**Start billing!** 💰

---

**Need help?** Refer to the detailed guide: `VPS_COMPLETE_DEPLOYMENT.md`

