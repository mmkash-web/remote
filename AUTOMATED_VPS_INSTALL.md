# Automated VPS Installation Guide

**Complete automated deployment for remote.netbill.site**

---

## 🎯 What This Does

The automated installer will setup **everything** in one go:

✅ System security & firewall  
✅ WireGuard VPN server  
✅ PostgreSQL database  
✅ Redis cache  
✅ Django application  
✅ Nginx web server  
✅ SSL certificate (Let's Encrypt)  
✅ All systemd services  
✅ Automatic backups  

**Total Time:** 15-20 minutes (mostly automated!)

---

## 📋 Prerequisites

### 1. Get a VPS

**Recommended:**
- **Provider:** DigitalOcean, Vultr, or Linode
- **OS:** Ubuntu 22.04 LTS (x64)
- **RAM:** 2GB minimum
- **Storage:** 25GB minimum
- **Cost:** ~$10/month

### 2. Configure Domain DNS

**Point your domain to VPS:**

Go to your DNS provider and add these records:

```
Type: A
Name: remote.netbill.site
Value: YOUR_VPS_IP_ADDRESS
TTL: 3600

Type: A
Name: www.remote.netbill.site
Value: YOUR_VPS_IP_ADDRESS
TTL: 3600
```

**Wait 5-10 minutes** for DNS to propagate.

Test with: `ping remote.netbill.site`

---

## 🚀 Installation Steps

### Step 1: Connect to Your VPS

```bash
ssh root@YOUR_VPS_IP
# Enter password
```

### Step 2: Upload Your Code (Choose One Method)

#### Method A: Upload via SCP (from your PC)

On your Windows PC (PowerShell):

```powershell
# Compress your project first
cd C:\Users\A\Desktop
Compress-Archive -Path mikrotikvpn -DestinationPath mikrotikvpn.zip

# Upload to VPS
scp mikrotikvpn.zip root@YOUR_VPS_IP:/tmp/

# On VPS, unzip
ssh root@YOUR_VPS_IP
cd /tmp
apt install unzip -y
unzip mikrotikvpn.zip
mkdir -p /home/deploy/mikrotikvpn
mv mikrotikvpn/* /home/deploy/mikrotikvpn/
```

#### Method B: Upload via Git (Recommended)

```bash
# On VPS
cd /home/deploy
git clone https://github.com/yourusername/mikrotikvpn.git

# Or initialize git and push
# On your PC:
cd C:\Users\A\Desktop\mikrotikvpn
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/mikrotikvpn.git
git push -u origin main
```

#### Method C: Use WinSCP

1. Download WinSCP: https://winscp.net/
2. Connect to your VPS
3. Upload `mikrotikvpn` folder to `/home/deploy/`

### Step 3: Download and Run Installer

```bash
# Download installer script
cd ~
wget https://raw.githubusercontent.com/yourusername/mikrotikvpn/main/install-vps.sh

# Or if not on GitHub yet, create it manually:
nano install-vps.sh
# Paste the content of install-vps.sh
# Press Ctrl+X, Y, Enter to save

# Make executable
chmod +x install-vps.sh

# Run installer
./install-vps.sh
```

### Step 4: Follow On-Screen Prompts

The installer will:

1. ✅ Show installation plan
2. ✅ Ask for confirmation
3. ✅ Install all components (15-20 min)
4. ✅ Configure SSL certificate
5. ✅ Display all credentials

**Just press Enter when prompted!**

---

## ✅ What Happens During Installation

### Phase 1: System Setup (3 min)
- Updates system packages
- Installs essential tools
- Creates deployment user
- Configures firewall

### Phase 2: VPN Server (3 min)
- Installs WireGuard
- Generates encryption keys
- Configures VPN network
- Opens firewall ports

### Phase 3: Databases (2 min)
- Installs PostgreSQL
- Creates database & user
- Installs Redis
- Tests connections

### Phase 4: Django App (5 min)
- Creates virtual environment
- Installs Python packages
- Runs database migrations
- Collects static files
- Creates admin user

### Phase 5: Web Server (3 min)
- Installs Nginx
- Configures reverse proxy
- Gets SSL certificate
- Enables HTTPS

### Phase 6: Services (2 min)
- Creates systemd services
- Enables auto-start
- Starts all services
- Verifies status

---

## 📊 After Installation

You'll see this summary:

```
╔════════════════════════════════════════════════════════════╗
║          Installation Completed Successfully! 🎉          ║
╚════════════════════════════════════════════════════════════╝

Access Information:
═══════════════════════════════════════════════════════════
  Website:        https://remote.netbill.site
  Admin Panel:    https://remote.netbill.site/admin/
  
  Username:       admin
  Password:       admin123
  ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!

VPN Server Information:
═══════════════════════════════════════════════════════════
  VPN IP:         10.10.0.1
  VPN Port:       51820 (UDP)
  Public Key:     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  
  Configure your MikroTik routers with this public key

Database Credentials:
═══════════════════════════════════════════════════════════
  Database:       mikrotik_billing
  User:           billing_user
  Password:       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  (Saved in /home/deploy/mikrotikvpn/.env)

Service Status:
═══════════════════════════════════════════════════════════
  ✓ Django (Gunicorn)  - Running
  ✓ Celery Worker      - Running
  ✓ Celery Beat        - Running
  ✓ Nginx Web Server   - Running
  ✓ PostgreSQL         - Running
  ✓ Redis              - Running
  ✓ WireGuard VPN      - Running
```

**Save this information!** It's also saved in `/root/installation-details.txt`

---

## 🔧 Post-Installation Steps

### 1. Access Your Website

Visit: **https://remote.netbill.site**

You should see the login page!

### 2. Change Admin Password

```
1. Login with admin/admin123
2. Click your username (top right)
3. Click "Change Password"
4. Set a strong password
5. Save
```

### 3. Configure MikroTik Routers

Copy the **VPN Server Public Key** from installation output.

Then use the pre-configured router scripts (see below).

---

## 🔐 Configure MikroTik Routers

### Get VPN Server Public Key

```bash
# On VPS
sudo cat /etc/wireguard/server_public.key
```

### Configure Router 1

Download: `mikrotik-configs/router1-netbill.rsc`

Edit the file:
```
Replace: YOUR_VPS_IP → Your actual VPS IP
Replace: VPS_PUBLIC_KEY → The key from above
```

Upload to MikroTik and import:
```
/import file=router1-netbill.rsc
```

### Add Router's Key to VPS

After router connects, get its public key:
```
# On MikroTik
/interface/wireguard/print
# Copy the public key
```

Add to VPS:
```bash
# On VPS
sudo nano /etc/wireguard/wg0.conf

# Add at the end:
[Peer]
PublicKey = ROUTER_PUBLIC_KEY_HERE
AllowedIPs = 10.10.0.2/32

# Save and restart
sudo wg-quick down wg0
sudo wg-quick up wg0

# Verify
sudo wg show
ping 10.10.0.2
```

---

## ✅ Verify Everything Works

### Test 1: Website Accessible
```
Visit: https://remote.netbill.site
Expected: Login page loads
```

### Test 2: SSL Certificate
```
Look for 🔒 (padlock) in browser
Click it → Certificate should be valid
```

### Test 3: Admin Panel
```
Login to: https://remote.netbill.site/admin/
Expected: Django admin loads
```

### Test 4: VPN Server
```bash
# On VPS
sudo wg show

# Should show interface wg0 listening
```

### Test 5: Services Running
```bash
# On VPS
sudo systemctl status mikrotik-billing celery-worker celery-beat

# All should show "active (running)"
```

### Test 6: Add Router in Django
```
1. Go to Routers → Add Router
2. Name: Router1
3. VPN IP: 10.10.0.2
4. Username: admin
5. Password: your-router-password
6. Port: 8728
7. Click "Test Connection"
8. Expected: ✅ Success!
```

---

## 🛠️ Useful Commands

### Check Services

```bash
# All services status
sudo systemctl status mikrotik-billing celery-worker celery-beat nginx

# Individual service
sudo systemctl status mikrotik-billing
```

### View Logs

```bash
# Django logs
tail -f /home/deploy/mikrotikvpn/logs/error.log

# Nginx logs
tail -f /var/log/nginx/error.log

# System logs
journalctl -u mikrotik-billing -f
```

### Restart Services

```bash
# Restart Django
sudo systemctl restart mikrotik-billing

# Restart all
sudo systemctl restart mikrotik-billing celery-worker celery-beat nginx
```

### VPN Management

```bash
# Check VPN status
sudo wg show

# Restart VPN
sudo wg-quick down wg0
sudo wg-quick up wg0

# View VPN config
sudo cat /etc/wireguard/wg0.conf
```

### Database Access

```bash
# Access database
sudo -u postgres psql mikrotik_billing

# Backup database
sudo -u postgres pg_dump mikrotik_billing > backup.sql

# Restore database
sudo -u postgres psql mikrotik_billing < backup.sql
```

---

## 🔄 Update Application

When you make changes to code:

```bash
# On VPS
cd /home/deploy/mikrotikvpn

# Pull latest code (if using Git)
git pull origin main

# Or upload new files via SCP/WinSCP

# Activate virtual environment
source venv/bin/activate

# Install new packages (if any)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart mikrotik-billing celery-worker celery-beat

# Check status
sudo systemctl status mikrotik-billing
```

---

## 🆘 Troubleshooting

### Website not loading?

```bash
# Check Nginx
sudo systemctl status nginx
sudo nginx -t

# Check Django
sudo systemctl status mikrotik-billing
tail -f /home/deploy/mikrotikvpn/logs/error.log
```

### SSL certificate failed?

```bash
# Check DNS
ping remote.netbill.site

# Try again manually
sudo certbot --nginx -d remote.netbill.site -d www.remote.netbill.site
```

### VPN not connecting?

```bash
# Check WireGuard
sudo wg show
sudo systemctl status wg-quick@wg0

# Check firewall
sudo ufw status

# Restart VPN
sudo wg-quick down wg0
sudo wg-quick up wg0
```

### Database errors?

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
sudo -u postgres psql -c "SELECT version();"

# Check database exists
sudo -u postgres psql -l | grep mikrotik
```

### Services won't start?

```bash
# Check logs
sudo journalctl -u mikrotik-billing -n 50
sudo journalctl -u celery-worker -n 50

# Check file permissions
ls -la /home/deploy/mikrotikvpn

# Verify .env file
cat /home/deploy/mikrotikvpn/.env
```

---

## 💾 Backups

### Automatic Backups

Backups run automatically every day at 2 AM.

Location: `/home/deploy/backups/`

Contents:
- Database dump
- Application code
- WireGuard configuration

### Manual Backup

```bash
# Run backup script
/home/deploy/backup.sh

# List backups
ls -lh /home/deploy/backups/

# Restore database
sudo -u postgres psql mikrotik_billing < /home/deploy/backups/db_20250103_020000.sql
```

---

## 🔐 Security Checklist

After installation:

- [ ] Changed admin password
- [ ] Updated email in `.env` file
- [ ] Configured payment gateways
- [ ] Setup backup monitoring
- [ ] Added SSH keys (disable password auth)
- [ ] Reviewed firewall rules
- [ ] Changed database password (if needed)
- [ ] Setup monitoring/alerts
- [ ] Documented VPN keys securely
- [ ] Tested disaster recovery

---

## 📊 Performance Monitoring

### Check System Resources

```bash
# CPU and memory
htop

# Disk space
df -h

# Network connections
sudo netstat -tlnp

# Service resource usage
systemctl status mikrotik-billing
```

### Monitor Logs

```bash
# Watch error logs
watch -n 1 "tail -20 /home/deploy/mikrotikvpn/logs/error.log"

# Count errors
grep -i error /home/deploy/mikrotikvpn/logs/error.log | wc -l
```

---

## 🚀 Scaling

### When you need more resources:

**50+ routers:**
- Upgrade to 4GB RAM VPS ($20/month)
- Add database connection pooling
- Enable Redis caching

**100+ routers:**
- Separate database server
- Load balancer
- Multiple app servers
- CDN for static files

---

## 📞 Quick Reference

| What | Command/URL |
|------|-------------|
| **Website** | https://remote.netbill.site |
| **Admin** | https://remote.netbill.site/admin/ |
| **SSH** | `ssh deploy@remote.netbill.site` |
| **Logs** | `tail -f ~/mikrotikvpn/logs/error.log` |
| **Restart** | `sudo systemctl restart mikrotik-billing` |
| **VPN Status** | `sudo wg show` |
| **Backup** | `/home/deploy/backup.sh` |
| **Update Code** | `cd ~/mikrotikvpn && git pull` |

---

## ✅ Success Indicators

**Everything is working when:**

1. ✅ https://remote.netbill.site loads
2. ✅ Can login to admin panel
3. ✅ SSL certificate shows valid (🔒)
4. ✅ `sudo wg show` displays VPN interface
5. ✅ Can ping routers from VPS
6. ✅ All services show "active (running)"
7. ✅ Can add routers in Django
8. ✅ Can create customers
9. ✅ Customers appear on MikroTik
10. ✅ Payment callbacks work

---

**🎉 Your production system is now live at https://remote.netbill.site! 🚀**

---

## 📚 Additional Resources

- **Full Manual Guide:** `VPS_COMPLETE_DEPLOYMENT.md`
- **Testing Guide:** `TESTING_VPN_CONNECTION.md`
- **Router Setup:** `MIKROTIK_WIREGUARD_SETUP.md`
- **Troubleshooting:** `VPN_COMPARISON_GUIDE.md`

---

**Need help? All credentials are saved in `/root/installation-details.txt`**

