# 🚀 Automated VPS Installation

## One-Command Deployment for remote.netbill.site

---

## ⚡ Quick Start (30 minutes)

### 1. Get VPS

- Provider: DigitalOcean, Vultr, or Linode
- OS: Ubuntu 22.04 LTS
- RAM: 2GB minimum
- Cost: ~$10/month

### 2. Configure DNS

Point your domain to VPS:
```
remote.netbill.site → YOUR_VPS_IP
www.remote.netbill.site → YOUR_VPS_IP
```

### 3. Upload Code

```bash
# From your Windows PC
scp -r C:\Users\A\Desktop\mikrotikvpn root@YOUR_VPS_IP:/tmp/

# Move to correct location
ssh root@YOUR_VPS_IP
mv /tmp/mikrotikvpn /home/deploy/
```

### 4. Run Installer

```bash
# On VPS
cd ~
bash install-vps.sh
```

**That's it!** The script does everything automatically.

---

## 📦 What Gets Installed

✅ **System Security**
- Firewall (UFW)
- Fail2ban
- User accounts

✅ **VPN Server**
- WireGuard VPN
- Network: 10.10.0.0/24
- Port: 51820 (UDP)

✅ **Databases**
- PostgreSQL
- Redis

✅ **Django Application**
- Python 3.11
- Virtual environment
- All dependencies
- Database migrations
- Admin user

✅ **Web Server**
- Nginx
- SSL Certificate (Let's Encrypt)
- HTTPS enabled

✅ **Background Services**
- Gunicorn (Django server)
- Celery Worker (tasks)
- Celery Beat (scheduler)

✅ **Automation**
- Auto-start on boot
- Automatic backups (daily)
- Log rotation

---

## 🎯 After Installation

### Access Your Site

Visit: **https://remote.netbill.site**

Login:
- Username: `admin`
- Password: `admin123`

**⚠️ Change password immediately!**

### Configure Routers

1. Get VPN server public key:
   ```bash
   sudo cat /etc/wireguard/server_public.key
   ```

2. Edit router config:
   ```
   mikrotik-configs/router1-netbill.rsc
   - Replace YOUR_VPS_IP
   - Replace VPS_PUBLIC_KEY
   ```

3. Upload to MikroTik and import:
   ```
   /import file=router1-netbill.rsc
   ```

4. Add router's key to VPS:
   ```bash
   sudo nano /etc/wireguard/wg0.conf
   # Add peer section
   sudo wg-quick down wg0 && sudo wg-quick up wg0
   ```

5. Test:
   ```bash
   ping 10.10.0.2
   ```

### Add Router in Django

1. Go to: Routers → Add Router
2. Enter:
   - Name: Router1-NetBill
   - VPN IP: 10.10.0.2
   - Username: admin
   - Password: (your router password)
   - Port: 8728
3. Click "Test Connection"
4. Should show: ✅ Success!

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **`QUICKSTART_NETBILL.md`** | **START HERE** - 30-min quick start |
| `AUTOMATED_VPS_INSTALL.md` | Full installation guide |
| `install-vps.sh` | Automated installer script |
| `mikrotik-configs/router1-netbill.rsc` | Router 1 config (pre-configured) |
| `mikrotik-configs/router2-netbill.rsc` | Router 2 config |
| `mikrotik-configs/router3-netbill.rsc` | Router 3 config |
| `TESTING_VPN_CONNECTION.md` | How to test everything works |
| `VPS_COMPLETE_DEPLOYMENT.md` | Manual installation (if needed) |

---

## ✅ Verification

Check everything works:

```bash
# 1. Website accessible
curl -I https://remote.netbill.site
# Should return: 200 OK

# 2. Services running
sudo systemctl status mikrotik-billing celery-worker celery-beat
# All should show: active (running)

# 3. VPN active
sudo wg show
# Should show: interface wg0

# 4. Router connected
ping 10.10.0.2
# Should work

# 5. Database accessible
sudo -u postgres psql -c "SELECT version();"
# Should show PostgreSQL version
```

---

## 🔧 Common Commands

### Service Management

```bash
# Check all services
sudo systemctl status mikrotik-billing celery-worker celery-beat nginx

# Restart all services
sudo systemctl restart mikrotik-billing celery-worker celery-beat

# View logs
tail -f /home/deploy/mikrotikvpn/logs/error.log
```

### VPN Management

```bash
# Check VPN status
sudo wg show

# Add router (after getting its public key)
sudo nano /etc/wireguard/wg0.conf
# Add [Peer] section
sudo wg-quick down wg0 && sudo wg-quick up wg0

# Test router connection
ping 10.10.0.2
```

### Update Application

```bash
cd /home/deploy/mikrotikvpn
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart mikrotik-billing celery-worker celery-beat
```

---

## 🆘 Troubleshooting

### Website not loading?

```bash
sudo systemctl status nginx mikrotik-billing
sudo nginx -t
tail -f /home/deploy/mikrotikvpn/logs/error.log
```

### SSL certificate failed?

```bash
# Check DNS first
ping remote.netbill.site

# Try again
sudo certbot --nginx -d remote.netbill.site -d www.remote.netbill.site
```

### VPN not working?

```bash
sudo wg show
sudo systemctl status wg-quick@wg0
sudo ufw status
```

### Service won't start?

```bash
sudo journalctl -u mikrotik-billing -n 50
sudo systemctl restart mikrotik-billing
```

---

## 💾 Backups

### Automatic Backups

Location: `/home/deploy/backups/`

Schedule: Daily at 2 AM

Contents:
- Database dump
- Application code
- VPN configuration

### Manual Backup

```bash
/home/deploy/backup.sh
```

### Restore

```bash
# Database
sudo -u postgres psql mikrotik_billing < /home/deploy/backups/db_YYYYMMDD_HHMMSS.sql

# Code
tar -xzf /home/deploy/backups/code_YYYYMMDD_HHMMSS.tar.gz -C /

# VPN config
sudo tar -xzf /home/deploy/backups/wireguard_YYYYMMDD_HHMMSS.tar.gz -C /
```

---

## 📊 File Structure

```
/home/deploy/mikrotikvpn/
├── mikrotik_billing/     # Django project
├── routers/              # Routers app
├── customers/            # Customers app
├── profiles/             # Profiles app
├── payments/             # Payments app
├── venv/                 # Virtual environment
├── logs/                 # Application logs
├── static/               # Static files (dev)
├── staticfiles/          # Static files (prod)
├── media/                # Uploaded files
├── .env                  # Environment config
├── manage.py             # Django management
└── requirements.txt      # Python packages

/etc/
├── nginx/
│   └── sites-available/mikrotik-billing
├── systemd/system/
│   ├── mikrotik-billing.service
│   ├── celery-worker.service
│   └── celery-beat.service
└── wireguard/
    └── wg0.conf

/home/deploy/
├── mikrotikvpn/          # Application
├── backups/              # Automatic backups
└── backup.sh             # Backup script
```

---

## 🔐 Important Credentials

**Location:** `/root/installation-details.txt`

Contains:
- Website URL
- Admin username/password
- Database credentials
- Django secret key
- VPN server public key
- Service information

**Keep this file secure!**

---

## 🎓 Training Workflow

### For New Routers:

1. Download router config: `router1-netbill.rsc`
2. Edit VPS IP and public key
3. Upload to MikroTik
4. Import: `/import file=router1-netbill.rsc`
5. Get router's public key
6. Add to VPS config
7. Test connection
8. Add in Django admin

### For New Customers:

1. Create profile (if not exists)
2. Go to Customers → Add Customer
3. Enter details
4. Select router and profile
5. Save
6. Customer created on MikroTik automatically
7. Enable customer
8. Customer can now connect

---

## 📈 Scaling

### Current Setup (1-20 routers)

- VPS: 2GB RAM ($10/month)
- Handles: Up to 500 customers
- Performance: Excellent

### Medium Scale (20-50 routers)

- VPS: 4GB RAM ($20/month)
- Add: Redis caching
- Optimize: Database queries

### Large Scale (50+ routers)

- Multiple VPS servers
- Load balancer
- Separate database server
- CDN for static files
- Cost: ~$100-200/month

---

## 💰 Cost Summary

| Item | Cost |
|------|------|
| VPS (2GB) | $10/month |
| Domain | $12/year (~$1/month) |
| SSL Certificate | FREE |
| **Total** | **~$11/month** |

---

## ✅ Success Checklist

- [ ] VPS created
- [ ] DNS configured
- [ ] Code uploaded
- [ ] Installer run successfully
- [ ] Website accessible via HTTPS
- [ ] Admin login works
- [ ] Admin password changed
- [ ] VPN server running
- [ ] Router 1 configured
- [ ] Router 1 connected to VPN
- [ ] Router 1 added in Django
- [ ] Test connection successful
- [ ] Profile created
- [ ] Test customer created
- [ ] Customer appears on MikroTik
- [ ] Backups working
- [ ] All services running

---

## 🎉 You're Done!

Your complete MikroTik Billing System is now live at:

### **https://remote.netbill.site** 🚀

---

## 📞 Quick Links

- **Website:** https://remote.netbill.site
- **Admin:** https://remote.netbill.site/admin/
- **Reports:** https://remote.netbill.site/reports/
- **API Docs:** https://remote.netbill.site/api/

---

## 🆘 Support

**Guides:**
- Quick Start: `QUICKSTART_NETBILL.md`
- Full Install: `AUTOMATED_VPS_INSTALL.md`
- Testing: `TESTING_VPN_CONNECTION.md`
- Manual Install: `VPS_COMPLETE_DEPLOYMENT.md`

**Logs:**
```bash
tail -f /home/deploy/mikrotikvpn/logs/error.log
```

**Service Status:**
```bash
sudo systemctl status mikrotik-billing
```

---

**Happy Billing!** 💰🎊

