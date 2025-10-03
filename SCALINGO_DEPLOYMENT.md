# Deploying to Scalingo

Complete guide to deploy your MikroTik Billing System on Scalingo.

---

## 🚀 Quick Deployment

### Prerequisites
- Scalingo account: https://scalingo.com/
- Scalingo CLI: https://cli.scalingo.com/
- Git repository

### 1. Install Scalingo CLI

**Linux/macOS:**
```bash
curl -O https://cli-dl.scalingo.com/install && bash install
```

**Windows:**
Download from: https://cli.scalingo.com/

### 2. Login to Scalingo

```bash
scalingo login
```

### 3. Create Scalingo App

```bash
# Create app
scalingo create mikrotikvpn

# Add PostgreSQL
scalingo addons-add postgresql postgresql-starter-512

# Add Redis (for Celery)
scalingo addons-add redis redis-starter-256
```

### 4. Configure Environment Variables

```bash
# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set environment variables
scalingo env-set SECRET_KEY="your-generated-secret-key"
scalingo env-set DEBUG="False"
scalingo env-set ALLOWED_HOSTS=".scalingo.io,.osc-fr1.scalingo.io,yourdomain.com"
scalingo env-set DJANGO_SETTINGS_MODULE="mikrotik_billing.settings"

# If using Supabase (optional)
scalingo env-set DATABASE_URL="postgresql://postgres.xxx:password@aws-1-eu-west-2.pooler.supabase.com:5432/postgres"

# MikroTik connection settings
scalingo env-set MIKROTIK_API_PORT="8728"
scalingo env-set MIKROTIK_API_TIMEOUT="10"
```

### 5. Deploy Your App

```bash
# Add Scalingo remote
git remote add scalingo git@ssh.osc-fr1.scalingo.com:mikrotikvpn.git

# Deploy
git push scalingo master
```

### 6. Run Migrations

```bash
scalingo run python manage.py migrate
scalingo run python manage.py createsuperuser
```

### 7. Scale Your App

```bash
# Scale web process
scalingo scale web:1:S

# Scale worker process (for Celery tasks)
scalingo scale worker:1:S
```

---

## 🔐 VPN Setup Options

### Option 1: Using Tailscale (Recommended for Scalingo)

**Step 1: Get Tailscale Auth Key**
1. Sign up at https://tailscale.com/
2. Go to Settings → Keys
3. Generate an auth key (reusable, never expires)

**Step 2: Add Tailscale to Your App**

Create `.buildpacks` file:
```bash
https://github.com/mvisonneau/tailscale-buildpack
heroku/python
```

Set Tailscale auth key:
```bash
scalingo env-set TAILSCALE_AUTHKEY="tskey-auth-xxxxxxxxxxxxx"
scalingo env-set TAILSCALE_HOSTNAME="mikrotikvpn-scalingo"
```

**Step 3: Configure MikroTik Routers**

Install Tailscale on each MikroTik router:
- Follow: https://tailscale.com/kb/1019/subnets/
- Or use MikroTik container package

**Step 4: Update Django Settings**

Your app will now have a Tailscale IP (e.g., 100.64.0.1)
Routers will have IPs like 100.64.0.2, 100.64.0.3, etc.

Use these IPs in your router configuration!

---

### Option 2: Using Separate VPS for VPN

**Step 1: Setup Small VPS**

Get a cheap VPS ($3-5/month):
- Contabo: https://contabo.com/
- Vultr: https://vultr.com/
- DigitalOcean: https://digitalocean.com/

**Step 2: Install VPN Server on VPS**

```bash
# SSH to VPS
ssh root@your-vps-ip

# Install WireGuard
apt update && apt install wireguard -y

# Configure VPN (see WIREGUARD_SETUP.md)
```

**Step 3: Create API Proxy on VPS**

The VPS acts as a bridge between Scalingo and routers:

```python
# Simple Flask proxy on VPS
from flask import Flask, request, jsonify
import librouteros

app = Flask(__name__)

@app.route('/api/mikrotik/<router_ip>', methods=['POST'])
def proxy_to_router(router_ip):
    # Forward API calls from Scalingo to local VPN routers
    data = request.json
    # Connect to router via VPN IP
    # Execute command
    # Return result
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
```

**Step 4: Configure Scalingo to Use Proxy**

```bash
scalingo env-set MIKROTIK_PROXY_URL="https://your-vps-ip:5000"
scalingo env-set MIKROTIK_USE_PROXY="True"
```

---

### Option 3: Direct Connection (Not Recommended)

If your routers have public IPs:

```bash
scalingo env-set MIKROTIK_VPN_TYPE="direct"
```

Use public IPs in router configuration.

**⚠️ Security Warning:**
- Enable MikroTik firewall
- Use API-SSL (port 8729)
- Whitelist only Scalingo IPs
- Use strong passwords

---

## 🗄️ Database Options

### Option 1: Scalingo PostgreSQL (Included)

Automatically configured via `DATABASE_URL` environment variable.

```bash
# View database credentials
scalingo env | grep DATABASE_URL
```

### Option 2: Supabase (Your Current Setup)

```bash
scalingo env-set DATABASE_URL="postgresql://postgres.seuzxvthbxowmofxalmm:Emmkash20@aws-1-eu-west-2.pooler.supabase.com:5432/postgres"
```

Your Django app will automatically use this!

---

## 📊 Monitoring & Logs

### View Logs
```bash
scalingo logs --tail
```

### Access Django Shell
```bash
scalingo run python manage.py shell
```

### Check App Status
```bash
scalingo ps
```

---

## 🔧 Custom Domain

### Add Your Domain

```bash
scalingo domains-add yourdomain.com
scalingo domains-add www.yourdomain.com
```

### Configure DNS

Add CNAME record:
```
yourdomain.com → your-app.osc-fr1.scalingo.io
```

### Enable SSL (Free)

```bash
scalingo domains-ssl yourdomain.com
```

---

## 💰 Cost Estimation

### Minimal Setup (Tailscale)
- Scalingo S plan: $7/month
- PostgreSQL starter: Included
- Redis starter: $5/month
- Tailscale: Free (up to 20 devices)
- **Total: ~$12/month**

### Standard Setup (VPS for VPN)
- Scalingo S plan: $7/month
- PostgreSQL starter: Included
- Redis starter: $5/month
- Small VPS: $4/month (Contabo)
- **Total: ~$16/month**

### Production Setup
- Scalingo M plan: $20/month
- PostgreSQL: $15/month
- Redis: $10/month
- VPS: $5/month
- **Total: ~$50/month**

---

## 🚨 Troubleshooting

### App won't start
```bash
# Check logs
scalingo logs --tail

# Verify environment variables
scalingo env

# Run migrations manually
scalingo run python manage.py migrate
```

### Database connection issues
```bash
# Check DATABASE_URL
scalingo env | grep DATABASE

# Test connection
scalingo run python manage.py dbshell
```

### Celery not working
```bash
# Check Redis connection
scalingo env | grep REDIS

# Check worker logs
scalingo logs --filter worker
```

---

## 📚 Additional Resources

- Scalingo Documentation: https://doc.scalingo.com/
- Django on Scalingo: https://doc.scalingo.com/languages/python/django/start
- Tailscale Setup: https://tailscale.com/kb/
- MikroTik API: https://wiki.mikrotik.com/wiki/Manual:API

---

## ✅ Deployment Checklist

- [ ] Scalingo account created
- [ ] App created on Scalingo
- [ ] PostgreSQL addon added
- [ ] Redis addon added
- [ ] Environment variables configured
- [ ] VPN solution chosen and configured
- [ ] Code deployed via Git
- [ ] Migrations run
- [ ] Superuser created
- [ ] Static files collected
- [ ] Worker process scaled
- [ ] Custom domain configured (optional)
- [ ] SSL enabled
- [ ] First router tested
- [ ] Payment callback tested

---

**Your app will be live at:** `https://mikrotikvpn.osc-fr1.scalingo.io` 🚀

