# 🚀 Quick VPS Installation (5 Minutes)

Deploy the complete MikroTik VPN Billing System on your VPS with a single command!

## ⚡ One-Command Installation

```bash
curl -sSL https://raw.githubusercontent.com/mmkash-web/remote/main/quick-install.sh | sudo bash
```

**That's it!** The script will:
- ✅ Install all dependencies (PostgreSQL, Redis, Nginx)
- ✅ Set up Django application
- ✅ Configure database automatically
- ✅ Set up SSL certificate (Let's Encrypt)
- ✅ Create systemd services
- ✅ Start everything automatically

---

## 📋 Prerequisites

### 1. **Get a VPS** (Recommended Providers)

| Provider | Price/Month | Link |
|----------|-------------|------|
| **DigitalOcean** | $6 | https://www.digitalocean.com |
| **Vultr** | $6 | https://www.vultr.com |
| **Linode** | $5 | https://www.linode.com |
| **Contabo** | $4 | https://contabo.com |
| **Hetzner** | €4 | https://www.hetzner.com |

**Requirements:**
- Ubuntu 22.04 LTS (recommended)
- 1GB RAM minimum (2GB recommended)
- 1 CPU core
- 20GB storage

### 2. **Domain Name** (Optional but Recommended)

Point your domain's A record to your VPS IP address.

Example: `billing.yourdomain.com → 203.0.113.45`

---

## 🎯 Installation Steps

### Step 1: Connect to Your VPS

```bash
ssh root@YOUR_VPS_IP
```

### Step 2: Run the Installer

```bash
curl -sSL https://raw.githubusercontent.com/mmkash-web/remote/main/quick-install.sh | sudo bash
```

### Step 3: Follow the Prompts

The installer will ask you:

1. **Domain name** (or use IP address)
2. **Admin email** (for SSL certificate)
3. **Admin username** (for Django admin)
4. **Admin password**

### Step 4: Access Your System

After installation completes (5-10 minutes):

```
🎉 Installation Complete!

Access your billing system:
→ https://yourdomain.com

Admin Panel:
→ https://yourdomain.com/admin
→ Username: your_admin_username
→ Password: your_admin_password

API Endpoint:
→ https://yourdomain.com/api/

Database:
→ Name: mikrotik_billing
→ User: billing_user
→ Password: [saved in /root/.env_backup]
```

---

## 🔧 Post-Installation

### Connect Your MikroTik Router

1. **Log into your billing system**
   ```
   https://yourdomain.com/admin
   ```

2. **Add a Router**
   - Go to "Routers" → "Add Router"
   - Enter: Name, IP, Username, Password

3. **Add a Profile**
   - Go to "Profiles" → "Add Profile"
   - Set bandwidth limits and duration

4. **Add Customers**
   - Go to "Customers" → "Add Customer"
   - Assign router and profile

### Configure MikroTik

SSH into your MikroTik router and run:

```bash
/ppp profile add name="1Mbps-30Days" local-address=10.10.10.1 remote-address=dhcp-pool
/ip pool add name=dhcp-pool ranges=10.10.10.2-10.10.10.254

# Enable API
/ip service set api address=YOUR_VPS_IP port=8728
```

---

## 📱 Features You Get

### 1. **Customer Management**
- Add/edit/delete customers
- Automatic expiry tracking
- Bulk operations
- Import/export

### 2. **Payment Processing**
- M-Pesa integration
- PayPal integration
- Manual payments
- Payment history

### 3. **Voucher System**
- Generate voucher batches
- Print vouchers
- Redeem codes
- Track usage

### 4. **Reports & Analytics**
- Revenue reports
- Customer statistics
- Router performance
- Export to CSV

### 5. **API Access**
- RESTful API
- Token authentication
- Webhooks for M-Pesa
- Complete documentation

---

## 🛠️ Management Commands

### Check System Status
```bash
sudo systemctl status mikrotik-billing
sudo systemctl status mikrotik-celery
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

### View Logs
```bash
# Application logs
sudo journalctl -u mikrotik-billing -f

# Celery logs
sudo journalctl -u mikrotik-celery -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart mikrotik-billing
sudo systemctl restart mikrotik-celery
sudo systemctl restart nginx
```

### Update Application
```bash
cd /home/deploy/mikrotikvpn
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart mikrotik-billing
sudo systemctl restart mikrotik-celery
```

---

## 🔐 Security

The installer automatically:
- ✅ Enables UFW firewall
- ✅ Configures SSH key authentication
- ✅ Installs Fail2Ban
- ✅ Sets up SSL certificate
- ✅ Secures PostgreSQL
- ✅ Creates secure passwords

**Open Ports:**
- 22 (SSH)
- 80 (HTTP - redirects to HTTPS)
- 443 (HTTPS)

---

## 🆘 Troubleshooting

### Can't Access Website

```bash
# Check if Nginx is running
sudo systemctl status nginx

# Check if app is running
sudo systemctl status mikrotik-billing

# Check firewall
sudo ufw status
```

### Database Connection Error

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
sudo -u postgres psql -d mikrotik_billing -c "SELECT 1;"
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## 📞 Support

- **Documentation:** https://github.com/mmkash-web/remote
- **Issues:** https://github.com/mmkash-web/remote/issues
- **Email:** admin@netbill.site

---

## 🎓 Video Tutorial

Coming soon! Subscribe to our channel for step-by-step video guides.

---

## ⚠️ Important Notes

1. **Backup your data regularly**
   ```bash
   # Database backup
   sudo -u postgres pg_dump mikrotik_billing > backup_$(date +%Y%m%d).sql
   ```

2. **Keep your system updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Monitor your resources**
   ```bash
   htop
   df -h
   free -h
   ```

4. **SSL certificates renew automatically**
   - Certbot creates a cron job
   - Check: `sudo certbot certificates`

---

## 🚀 Next Steps

After installation:

1. ✅ Log into admin panel
2. ✅ Add your first router
3. ✅ Create customer profiles
4. ✅ Configure payment methods (M-Pesa/PayPal)
5. ✅ Add your first customer
6. ✅ Generate vouchers (optional)
7. ✅ Test VPN connection

---

**Enjoy your automated MikroTik billing system! 🎉**

