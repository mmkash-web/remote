#!/bin/bash
#############################################################
# MikroTik Billing System - Quick VPS Installer
# 
# One-command installation for production VPS deployment
# 
# Usage: curl -sSL https://raw.githubusercontent.com/mmkash-web/remote/main/quick-install.sh | sudo bash
#
#############################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
clear
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     MikroTik VPN Billing System - Quick Installer       ║
║                                                           ║
║     🚀 Production-Ready in 5 Minutes                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Check Ubuntu version
if ! grep -q "Ubuntu 22.04\|Ubuntu 20.04" /etc/os-release; then
    echo -e "${YELLOW}⚠️  Warning: This script is tested on Ubuntu 22.04/20.04${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}📋 Let's set up your billing system!${NC}\n"

# Get configuration from user
read -p "Enter your domain name (or VPS IP address): " DOMAIN
read -p "Enter your email (for SSL certificate): " ADMIN_EMAIL
read -p "Enter admin username for Django: " ADMIN_USERNAME
read -sp "Enter admin password: " ADMIN_PASSWORD
echo

# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
DJANGO_SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)

# Configuration
DB_NAME="mikrotik_billing"
DB_USER="billing_user"
APP_DIR="/home/deploy/mikrotikvpn"
REPO_URL="https://github.com/mmkash-web/remote.git"

echo -e "\n${GREEN}✓ Configuration ready${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Save credentials
mkdir -p /root
cat > /root/.env_backup << EOF
# MikroTik Billing System Credentials
# Generated: $(date)

DOMAIN=$DOMAIN
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD

DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
APP_DIR=$APP_DIR
EOF

echo -e "${GREEN}✓ Credentials saved to /root/.env_backup${NC}\n"

# Function to print step
print_step() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📦 $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Update system
print_step "Step 1/8: Updating System"
apt update && apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"

# Install dependencies
print_step "Step 2/8: Installing Dependencies"
apt install -y python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    git \
    ufw \
    certbot python3-certbot-nginx \
    build-essential libpq-dev
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Setup PostgreSQL
print_step "Step 3/8: Configuring Database"
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF
echo -e "${GREEN}✓ Database configured${NC}"

# Create deploy user
print_step "Step 4/8: Creating Deploy User"
if ! id -u deploy > /dev/null 2>&1; then
    useradd -m -s /bin/bash deploy
    echo -e "${GREEN}✓ Deploy user created${NC}"
else
    echo -e "${YELLOW}Deploy user already exists${NC}"
fi

# Clone repository
print_step "Step 5/8: Downloading Application"
if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Removing existing directory${NC}"
    rm -rf $APP_DIR
fi

sudo -u deploy git clone $REPO_URL $APP_DIR
cd $APP_DIR
echo -e "${GREEN}✓ Application downloaded${NC}"

# Setup Python environment
print_step "Step 6/8: Setting Up Python Environment"
sudo -u deploy python3 -m venv venv
sudo -u deploy $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u deploy $APP_DIR/venv/bin/pip install -r requirements.txt
echo -e "${GREEN}✓ Python environment ready${NC}"

# Create .env file
print_step "Step 7/8: Configuring Application"
cat > $APP_DIR/.env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=$DJANGO_SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/

# Email (optional - configure later)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Payment Gateways (configure later)
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_PASSKEY=
MPESA_SHORTCODE=

PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_MODE=sandbox
EOF

chown deploy:deploy $APP_DIR/.env
echo -e "${GREEN}✓ Application configured${NC}"

# Run migrations
sudo -u deploy $APP_DIR/venv/bin/python $APP_DIR/manage.py migrate
sudo -u deploy $APP_DIR/venv/bin/python $APP_DIR/manage.py collectstatic --noinput

# Create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD') if not User.objects.filter(username='$ADMIN_USERNAME').exists() else None" | sudo -u deploy $APP_DIR/venv/bin/python $APP_DIR/manage.py shell

# Setup Gunicorn service
cat > /etc/systemd/system/mikrotik-billing.service << EOF
[Unit]
Description=MikroTik Billing System
After=network.target postgresql.service redis.service

[Service]
User=deploy
Group=deploy
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/gunicorn.sock mikrotik_billing.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Setup Celery service
cat > /etc/systemd/system/mikrotik-celery.service << EOF
[Unit]
Description=MikroTik Billing Celery Worker
After=network.target redis.service

[Service]
User=deploy
Group=deploy
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/celery -A mikrotik_billing worker --loglevel=info

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx
cat > /etc/nginx/sites-available/mikrotik-billing << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $APP_DIR/staticfiles/;
    }

    location /media/ {
        alias $APP_DIR/media/;
    }

    location / {
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://unix:$APP_DIR/gunicorn.sock;
    }
}
EOF

ln -sf /etc/nginx/sites-available/mikrotik-billing /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t

# Setup firewall
print_step "Step 8/8: Configuring Firewall & Services"
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo -e "${GREEN}✓ Firewall configured${NC}"

# Start services
systemctl daemon-reload
systemctl enable postgresql redis-server nginx mikrotik-billing mikrotik-celery
systemctl start postgresql redis-server nginx mikrotik-billing mikrotik-celery

echo -e "\n${GREEN}✓ Services started${NC}"

# Setup SSL if domain is provided
if [[ $DOMAIN != *"."*"."* ]] && [[ $DOMAIN =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "\n${YELLOW}⚠️  Skipping SSL (IP address provided instead of domain)${NC}"
else
    echo -e "\n${BLUE}🔐 Setting up SSL certificate...${NC}"
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $ADMIN_EMAIL --redirect
    echo -e "${GREEN}✓ SSL certificate installed${NC}"
fi

# Final message
clear
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🎉 Installation Complete! 🎉                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Your MikroTik Billing System is ready!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [[ $DOMAIN =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${YELLOW}📱 Access your system:${NC}"
    echo -e "   → http://$DOMAIN"
    echo -e "   ${YELLOW}(SSL not available for IP addresses)${NC}\n"
else
    echo -e "${YELLOW}📱 Access your system:${NC}"
    echo -e "   → https://$DOMAIN\n"
fi

echo -e "${YELLOW}👤 Admin Panel:${NC}"
echo -e "   → https://$DOMAIN/admin"
echo -e "   → Username: ${GREEN}$ADMIN_USERNAME${NC}"
echo -e "   → Password: ${GREEN}$ADMIN_PASSWORD${NC}\n"

echo -e "${YELLOW}🔑 Credentials saved to:${NC}"
echo -e "   → /root/.env_backup\n"

echo -e "${YELLOW}📊 Check service status:${NC}"
echo -e "   → sudo systemctl status mikrotik-billing"
echo -e "   → sudo systemctl status mikrotik-celery"
echo -e "   → sudo systemctl status nginx\n"

echo -e "${YELLOW}📝 View logs:${NC}"
echo -e "   → sudo journalctl -u mikrotik-billing -f\n"

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Next Steps:${NC}"
echo -e "   1. Log into admin panel"
echo -e "   2. Add your MikroTik router"
echo -e "   3. Create customer profiles"
echo -e "   4. Add your first customer"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BLUE}📚 Documentation: https://github.com/mmkash-web/remote${NC}"
echo -e "${BLUE}🆘 Support: https://github.com/mmkash-web/remote/issues${NC}\n"

echo -e "${GREEN}Happy billing! 🎉${NC}\n"

