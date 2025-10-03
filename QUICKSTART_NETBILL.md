# Quick Start Guide for remote.netbill.site

**Get your MikroTik Billing System online in 30 minutes!**

---

## 🎯 Overview

This guide will help you deploy your complete billing system with domain: **remote.netbill.site**

---

## 📋 What You Need

1. ✅ **VPS** - Ubuntu 22.04, 2GB RAM ($10/month)
2. ✅ **Domain DNS** - Point remote.netbill.site to your VPS IP
3. ✅ **Your code** - The mikrotikvpn project
4. ✅ **30 minutes** - For complete setup

---

## 🚀 Part 1: Deploy to VPS (20 minutes)

### Step 1: Get VPS & Configure DNS (5 min)

1. Sign up at DigitalOcean/Vultr
2. Create Ubuntu 22.04 droplet (2GB RAM)
3. Note your VPS IP: `203.45.67.89` (example)
4. Add DNS records:
   ```
   remote.netbill.site → 203.45.67.89
   www.remote.netbill.site → 203.45.67.89
   ```
5. Wait 5 minutes for DNS propagation

### Step 2: Connect to VPS (1 min)

```bash
ssh root@YOUR_VPS_IP
```

### Step 3: Upload Your Code (3 min)

Choose one:

**Option A: Via SCP (from Windows)**
```powershell
scp -r C:\Users\A\Desktop\mikrotikvpn root@YOUR_VPS_IP:/tmp/
```

**Option B: Via Git**
```bash
# On VPS
cd /home/deploy
git clone https://github.com/yourusername/mikrotikvpn.git
```

**Option C: Via WinSCP** (drag & drop)

### Step 4: Run Automated Installer (15 min)

```bash
# On VPS
cd ~
wget https://raw.githubusercontent.com/yourusername/mikrotikvpn/main/install-vps.sh
chmod +x install-vps.sh
./install-vps.sh
```

**Just press Enter when prompted!**

The script will:
- ✅ Setup system security
- ✅ Install WireGuard VPN
- ✅ Install PostgreSQL & Redis
- ✅ Deploy Django app
- ✅ Configure Nginx
- ✅ Get SSL certificate
- ✅ Start all services

### Step 5: Save Credentials

After installation, you'll see:

```
Website: https://remote.netbill.site
Username: admin
Password: admin123

VPN Server Public Key: xxxxxxxxxxxxxx
```

**Save these!** Also saved in `/root/installation-details.txt`

---

## 🔧 Part 2: Connect Routers (10 minutes per router)

### Step 1: Get VPN Server Key

```bash
# On VPS
sudo cat /etc/wireguard/server_public.key
# Copy this key
```

### Step 2: Configure Router 1

1. Download: `mikrotik-configs/router1-netbill.rsc`
2. Edit the file:
   - Replace `YOUR_VPS_IP` with your actual VPS IP
   - Replace `VPS_PUBLIC_KEY` with the key from Step 1
3. Upload to MikroTik via Winbox (Files section)
4. In MikroTik terminal:
   ```
   /import file=router1-netbill.rsc
   ```
5. Copy the router's public key that appears
6. Add to VPS:
   ```bash
   sudo nano /etc/wireguard/wg0.conf
   # Add at end:
   [Peer]
   PublicKey = ROUTER_PUBLIC_KEY
   AllowedIPs = 10.10.0.2/32
   
   # Save and restart
   sudo wg-quick down wg0 && sudo wg-quick up wg0
   ```

### Step 3: Test Connection

```bash
# On VPS
ping 10.10.0.2
# Should work!
```

### Step 4: Add Router in Django

1. Visit: https://remote.netbill.site/admin/
2. Login: admin / admin123
3. **Change password immediately!**
4. Go to: Routers → Add Router
5. Fill in:
   - Name: Router1-NetBill
   - VPN IP: `10.10.0.2`
   - Username: `admin`
   - Password: (your router password)
   - Port: `8728`
6. Click "Test Connection"
7. Should show: ✅ Success!

---

## ✅ Verification Checklist

- [ ] Website loads: https://remote.netbill.site
- [ ] SSL certificate valid (🔒 icon in browser)
- [ ] Can login to admin panel
- [ ] Changed admin password
- [ ] Router VPN connected (sudo wg show)
- [ ] Can ping router from VPS (ping 10.10.0.2)
- [ ] Router added in Django
- [ ] "Test Connection" shows success

---

## 🎯 Quick Start Workflow

### 1. Create a Profile

```
Go to: Profiles → Add Profile
Name: 1GB Daily
Speed: 5M/5M (download/upload)
Duration: 1 day
Price: 50
Save
```

### 2. Create a Customer

```
Go to: Customers → Add Customer
Username: testuser1
Password: test123
Full Name: Test User
Router: Router1-NetBill
Profile: 1GB Daily
Save
```

Customer is automatically created on MikroTik! ✅

### 3. Verify on MikroTik

```
# On MikroTik terminal
/ppp/secret/print
# Should show: testuser1
```

### 4. Enable Customer

```
In Django: Customers → testuser1 → Enable
Customer can now connect to hotspot!
```

---

## 🔐 Change Default Password

**IMPORTANT:** Change immediately after first login!

```
1. Login: https://remote.netbill.site/admin/
2. Click "admin" (top right)
3. Click "Change password"
4. Enter:
   - Old password: admin123
   - New password: (strong password)
   - Confirm
5. Save
```

---

## 🛠️ Common Commands

### On VPS:

```bash
# Check all services
sudo systemctl status mikrotik-billing celery-worker celery-beat

# View logs
tail -f /home/deploy/mikrotikvpn/logs/error.log

# Check VPN
sudo wg show

# Restart services
sudo systemctl restart mikrotik-billing celery-worker celery-beat

# Check if router is reachable
ping 10.10.0.2
```

### On MikroTik:

```bash
# Check VPN status
/interface wireguard print

# Test VPS connection
/ping 10.10.0.1

# Check API
/ip service print

# List customers
/ppp/secret/print
```

---

## 💰 Add More Routers

For Router 2, Router 3, etc.:

1. Use: `router2-netbill.rsc`, `router3-netbill.rsc`
2. VPN IPs: `10.10.0.3`, `10.10.0.4`, etc.
3. Same process as Router 1
4. Add each router's key to VPS config

---

## 🔄 Update Application

When you make code changes:

```bash
# On VPS
cd /home/deploy/mikrotikvpn
git pull origin main  # Or upload new files
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart mikrotik-billing celery-worker celery-beat
```

---

## 📊 Monitor System

### Dashboard

Visit: https://remote.netbill.site/reports/

View:
- Revenue reports
- Customer statistics
- Router status
- Payment history

### System Health

```bash
# On VPS
htop  # CPU/Memory
df -h  # Disk space
sudo systemctl status --all  # All services
```

---

## 🆘 Quick Troubleshooting

### Website not loading?
```bash
sudo systemctl status nginx mikrotik-billing
sudo nginx -t
```

### Can't connect to router?
```bash
ping 10.10.0.2
sudo wg show
# On MikroTik: /ping 10.10.0.1
```

### Database errors?
```bash
sudo systemctl status postgresql
cd /home/deploy/mikrotikvpn
source venv/bin/activate
python manage.py migrate
```

---

## 📞 Quick Reference

| Item | Value |
|------|-------|
| **Website** | https://remote.netbill.site |
| **Admin** | https://remote.netbill.site/admin/ |
| **Default User** | admin |
| **Default Pass** | admin123 (CHANGE THIS!) |
| **VPS SSH** | `ssh deploy@remote.netbill.site` |
| **VPN Network** | 10.10.0.0/24 |
| **VPS VPN IP** | 10.10.0.1 |
| **Router 1 IP** | 10.10.0.2 |
| **Router 2 IP** | 10.10.0.3 |
| **API Port** | 8728 |
| **Logs** | `/home/deploy/mikrotikvpn/logs/` |

---

## ✅ Success!

**You now have:**

- ✅ Professional billing system
- ✅ Secure VPN network
- ✅ SSL-encrypted website
- ✅ Automatic router management
- ✅ Payment processing ready
- ✅ Customer self-service portal
- ✅ Comprehensive reporting

**Start selling internet packages!** 💰🚀

---

## 🎓 Next Steps

1. ✅ Add all your routers
2. ✅ Create your packages (profiles)
3. ✅ Add customers
4. ✅ Configure payment gateway (M-Pesa/PayPal)
5. ✅ Customize branding
6. ✅ Setup email notifications
7. ✅ Train your staff
8. ✅ Go live!

---

**Need detailed help?**
- Full guide: `AUTOMATED_VPS_INSTALL.md`
- Testing: `TESTING_VPN_CONNECTION.md`
- Router setup: `MIKROTIK_WIREGUARD_SETUP.md`

**Your billing system is ready!** 🎉

