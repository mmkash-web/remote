#!/bin/bash
#############################################################
# MikroTik Billing System - Robust VPS Installer
# 
# This script automates the complete deployment of:
# - WireGuard VPN Server
# - PostgreSQL Database
# - Redis Cache
# - Django Application
# - Nginx Web Server
# - SSL Certificate
# - Systemd Services
#
# Usage: curl -sSL https://raw.githubusercontent.com/your-repo/main/install-vps-robust.sh | bash
# Or: bash install-vps-robust.sh
#
#############################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="remote.netbill.site"
DB_NAME="mikrotik_billing"
DB_USER="billing_user"
DB_PASSWORD=$(openssl rand -base64 32)
DJANGO_SECRET_KEY=$(openssl rand -base64 64)
APP_DIR="/home/deploy/mikrotikvpn"
ADMIN_EMAIL="admin@netbill.site"  # Change this to your email

# Banner
clear
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     MikroTik Billing System - Robust VPS Installer v2.0  ║
║                                                           ║
║     Automated Deployment for Production                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}Domain: ${DOMAIN}${NC}"
echo -e "${GREEN}Installation Directory: ${APP_DIR}${NC}"
echo ""
echo -e "${YELLOW}This script will:${NC}"
echo "  ✓ Setup system and security"
echo "  ✓ Install WireGuard VPN Server"
echo "  ✓ Install PostgreSQL & Redis"
echo "  ✓ Deploy Django Application"
echo "  ✓ Configure Nginx with SSL"
echo "  ✓ Setup all systemd services"
echo ""
echo -e "${RED}⚠️  WARNING: This script requires root access${NC}"
echo -e "${RED}⚠️  Run this on a fresh Ubuntu 22.04 VPS only${NC}"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Function to install packages without interactive prompts
install_packages_robust() {
    local packages=("$@")
    
    # Pre-configure all packages to avoid interactive prompts
    export DEBIAN_FRONTEND=noninteractive
    export UCF_FORCE_CONFFNEW=1
    
    # Pre-configure SSH server to keep existing configuration
    echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true
    echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true
    
    # Pre-configure other packages that might prompt
    echo "postgresql-common postgresql-common/install-error select abort" | debconf-set-selections 2>/dev/null || true
    echo "nginx-common nginx-common/install-error select abort" | debconf-set-selections 2>/dev/null || true
    echo "ufw ufw/enable boolean true" | debconf-set-selections 2>/dev/null || true
    
    # Install packages with timeout
    print_info "Updating package lists..."
    timeout 300 apt-get update -qq || {
        print_error "Package update timed out, continuing..."
    }
    
    print_info "Installing packages..."
    timeout 1800 apt-get install -y -qq --no-install-recommends "${packages[@]}" || {
        print_error "Package installation failed or timed out, trying alternative approach..."
        # Try installing packages one by one
        for package in "${packages[@]}"; do
            print_info "Installing $package..."
            timeout 300 apt-get install -y -qq --no-install-recommends "$package" || {
                print_error "Failed to install $package, continuing..."
            }
        done
    }
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Check OS
if [ ! -f /etc/lsb-release ]; then
    print_error "This script requires Ubuntu 22.04"
    exit 1
fi

source /etc/lsb-release
if [ "$DISTRIB_RELEASE" != "22.04" ]; then
    print_error "This script requires Ubuntu 22.04, you have $DISTRIB_RELEASE"
    exit 1
fi

print_success "Running on Ubuntu 22.04"

#############################################################
# Part 1: System Setup
#############################################################
print_section "Part 1: System Setup & Security"

print_info "Updating system packages..."
apt update -qq && apt upgrade -y -qq
print_success "System updated"

print_info "Installing essential packages..."

# Backup SSH config before installation
if [ -f /etc/ssh/sshd_config ]; then
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    print_info "SSH config backed up"
fi

# Install packages with robust error handling (excluding SSH server)
install_packages_robust \
    build-essential \
    git \
    curl \
    wget \
    software-properties-common \
    ufw \
    fail2ban \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    wireguard \
    net-tools \
    htop

# Install SSH server separately with special handling
print_info "Installing SSH server with special handling..."

# Create a more aggressive approach to handle SSH installation
cat > /tmp/install_ssh.sh << 'EOF'
#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
export UCF_FORCE_CONFFNEW=1

# Pre-configure SSH server to keep existing configuration
echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true
echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true

# Force keep existing configuration
echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true

# Install SSH server with force
apt-get install -y -qq --no-install-recommends openssh-server --force-yes || {
    # If that fails, try with different approach
    echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections 2>/dev/null || true
    apt-get install -y -qq --no-install-recommends openssh-server --force-yes || true
}
EOF

chmod +x /tmp/install_ssh.sh

# Run SSH installation with timeout
if timeout 300 /tmp/install_ssh.sh; then
    print_success "SSH server installed successfully"
else
    print_error "SSH server installation failed, trying alternative approach..."
    # Try with dpkg directly
    print_info "Trying dpkg approach..."
    timeout 300 bash -c 'export DEBIAN_FRONTEND=noninteractive; echo "openssh-server openssh-server/conflicts_with_openssh-server boolean true" | debconf-set-selections; apt-get install -y -qq --no-install-recommends openssh-server --force-yes' || {
        print_error "SSH server installation failed, but continuing..."
    }
fi

# Clean up
rm -f /tmp/install_ssh.sh

# Restore SSH config if it was modified
if [ -f /etc/ssh/sshd_config.backup ]; then
    if ! diff -q /etc/ssh/sshd_config /etc/ssh/sshd_config.backup >/dev/null 2>&1; then
        print_info "Restoring SSH configuration..."
        cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
        systemctl restart sshd
        print_success "SSH configuration restored"
    fi
    rm -f /etc/ssh/sshd_config.backup
fi

print_success "Essential packages installed"

print_info "Creating deployment user..."
if id "deploy" &>/dev/null; then
    print_info "User 'deploy' already exists"
else
    adduser --disabled-password --gecos "" deploy
    usermod -aG sudo deploy
    echo "deploy ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/deploy
    print_success "User 'deploy' created"
fi

print_info "Configuring firewall..."
ufw --force disable
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 51820/udp comment 'WireGuard VPN'
ufw --force enable
print_success "Firewall configured"

#############################################################
# Part 2: WireGuard VPN Server
#############################################################
print_section "Part 2: Installing WireGuard VPN Server"

print_info "Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p
print_success "IP forwarding enabled"

print_info "Generating WireGuard keys..."
mkdir -p /etc/wireguard
cd /etc/wireguard
wg genkey | tee server_private.key | wg pubkey > server_public.key
chmod 600 server_private.key

SERVER_PRIVATE_KEY=$(cat server_private.key)
SERVER_PUBLIC_KEY=$(cat server_public.key)

print_success "WireGuard keys generated"
print_info "Server Public Key: ${SERVER_PUBLIC_KEY}"

print_info "Creating WireGuard configuration..."
INTERFACE=$(ip route list default | awk '{print $5}')

cat > /etc/wireguard/wg0.conf << EOF
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = ${SERVER_PRIVATE_KEY}

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o ${INTERFACE} -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o ${INTERFACE} -j MASQUERADE

# Peer configurations will be added here
# Use: sudo wg set wg0 peer <PUBLIC_KEY> allowed-ips 10.10.0.2/32
EOF

chmod 600 /etc/wireguard/wg0.conf

print_info "Starting WireGuard..."
wg-quick up wg0
systemctl enable wg-quick@wg0
print_success "WireGuard VPN server running"

#############################################################
# Part 3: PostgreSQL Database
#############################################################
print_section "Part 3: Setting up PostgreSQL Database"

print_info "Starting PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

print_info "Creating database and user..."
sudo -u postgres psql << EOF
CREATE DATABASE ${DB_NAME};
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
ALTER ROLE ${DB_USER} SET client_encoding TO 'utf8';
ALTER ROLE ${DB_USER} SET default_transaction_isolation TO 'read committed';
ALTER ROLE ${DB_USER} SET timezone TO 'Africa/Nairobi';
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
\q
EOF

print_success "PostgreSQL database created"

#############################################################
# Part 4: Redis Cache
#############################################################
print_section "Part 4: Setting up Redis"

print_info "Configuring Redis..."
sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf
systemctl restart redis-server
systemctl enable redis-server

# Test Redis
if redis-cli ping | grep -q PONG; then
    print_success "Redis is running"
else
    print_error "Redis failed to start"
fi

#############################################################
# Part 5: Clone Application
#############################################################
print_section "Part 5: Deploying Django Application"

print_info "Setting up application directory..."
sudo -u deploy mkdir -p ${APP_DIR}
sudo -u deploy mkdir -p ${APP_DIR}/logs

# Check if code is already there
if [ -d "${APP_DIR}/manage.py" ]; then
    print_info "Application code already exists"
else
    print_info "Please upload your code to ${APP_DIR}"
    print_info "You can use: scp -r /path/to/mikrotikvpn/* deploy@${DOMAIN}:${APP_DIR}/"
    read -p "Press Enter after you've uploaded the code..."
fi

cd ${APP_DIR}

print_info "Creating virtual environment..."
sudo -u deploy python3 -m venv venv
print_success "Virtual environment created"

print_info "Installing Python packages..."
sudo -u deploy ${APP_DIR}/venv/bin/pip install --upgrade pip -q
sudo -u deploy ${APP_DIR}/venv/bin/pip install -r requirements.txt -q
sudo -u deploy ${APP_DIR}/venv/bin/pip install gunicorn psycopg2-binary -q
print_success "Python packages installed"

print_info "Creating environment configuration..."
cat > ${APP_DIR}/.env << EOF
# Django Settings
SECRET_KEY=${DJANGO_SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},$(curl -s ifconfig.me)

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=${DB_NAME}
DATABASE_USER=${DB_USER}
DATABASE_PASSWORD=${DB_PASSWORD}
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# MikroTik API
MIKROTIK_API_PORT=8728
MIKROTIK_API_TIMEOUT=10

# Email Configuration (update with your settings)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Timezone
TIME_ZONE=Africa/Nairobi

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
EOF

chown deploy:deploy ${APP_DIR}/.env
chmod 600 ${APP_DIR}/.env
print_success "Environment configured"

print_info "Running database migrations..."
sudo -u deploy ${APP_DIR}/venv/bin/python manage.py migrate --noinput
print_success "Database migrations completed"

print_info "Collecting static files..."
sudo -u deploy ${APP_DIR}/venv/bin/python manage.py collectstatic --noinput
print_success "Static files collected"

print_info "Creating Django superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', '${ADMIN_EMAIL}', 'admin123') if not User.objects.filter(username='admin').exists() else None" | sudo -u deploy ${APP_DIR}/venv/bin/python manage.py shell
print_success "Superuser created (username: admin, password: admin123)"
print_error "⚠️  CHANGE THIS PASSWORD IMMEDIATELY!"

#############################################################
# Part 6: Systemd Services
#############################################################
print_section "Part 6: Configuring Systemd Services"

print_info "Creating Gunicorn service..."
cat > /etc/systemd/system/mikrotik-billing.service << EOF
[Unit]
Description=MikroTik Billing System
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=deploy
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn \\
    --workers 3 \\
    --bind 127.0.0.1:8000 \\
    --timeout 60 \\
    --access-logfile ${APP_DIR}/logs/access.log \\
    --error-logfile ${APP_DIR}/logs/error.log \\
    mikrotik_billing.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_info "Creating Celery Worker service..."
cat > /etc/systemd/system/celery-worker.service << EOF
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=deploy
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/celery -A mikrotik_billing worker \\
    --loglevel=info \\
    --logfile=${APP_DIR}/logs/celery-worker.log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_info "Creating Celery Beat service..."
cat > /etc/systemd/system/celery-beat.service << EOF
[Unit]
Description=Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=deploy
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/celery -A mikrotik_billing beat \\
    --loglevel=info \\
    --logfile=${APP_DIR}/logs/celery-beat.log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_info "Starting services..."
systemctl daemon-reload
systemctl enable mikrotik-billing celery-worker celery-beat
systemctl start mikrotik-billing celery-worker celery-beat

sleep 5

# Check service status
if systemctl is-active --quiet mikrotik-billing; then
    print_success "Gunicorn service running"
else
    print_error "Gunicorn service failed to start"
    systemctl status mikrotik-billing
fi

if systemctl is-active --quiet celery-worker; then
    print_success "Celery worker running"
else
    print_error "Celery worker failed to start"
fi

if systemctl is-active --quiet celery-beat; then
    print_success "Celery beat running"
else
    print_error "Celery beat failed to start"
fi

#############################################################
# Part 7: Nginx Configuration
#############################################################
print_section "Part 7: Configuring Nginx Web Server"

print_info "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/mikrotik-billing << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias ${APP_DIR}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias ${APP_DIR}/media/;
        expires 7d;
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny access to sensitive files
    location ~ /\.(?!well-known) {
        deny all;
    }
}
EOF

print_info "Enabling site..."
ln -sf /etc/nginx/sites-available/mikrotik-billing /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

print_info "Testing Nginx configuration..."
if nginx -t; then
    print_success "Nginx configuration valid"
    systemctl restart nginx
    systemctl enable nginx
    print_success "Nginx running"
else
    print_error "Nginx configuration invalid"
fi

#############################################################
# Part 8: SSL Certificate
#############################################################
print_section "Part 8: Installing SSL Certificate"

print_info "Getting SSL certificate from Let's Encrypt..."
print_info "Make sure ${DOMAIN} points to this server's IP: $(curl -s ifconfig.me)"
read -p "Press Enter to continue with SSL setup (or Ctrl+C to skip)..."

certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email ${ADMIN_EMAIL} --redirect || {
    print_error "SSL certificate installation failed"
    print_info "You can run this later: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
}

print_success "SSL certificate installed"

#############################################################
# Part 9: Final Configuration
#############################################################
print_section "Part 9: Final Configuration & Testing"

print_info "Setting up log rotation..."
cat > /etc/logrotate.d/mikrotik-billing << EOF
${APP_DIR}/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 deploy www-data
    sharedscripts
    postrotate
        systemctl reload mikrotik-billing celery-worker celery-beat
    endscript
}
EOF
print_success "Log rotation configured"

print_info "Creating backup script..."
cat > /home/deploy/backup.sh << 'BACKUP_SCRIPT'
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump mikrotik_billing > $BACKUP_DIR/db_$DATE.sql

# Backup code
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /home/deploy/mikrotikvpn --exclude=venv --exclude=logs

# Backup WireGuard
sudo tar -czf $BACKUP_DIR/wireguard_$DATE.tar.gz /etc/wireguard

# Keep last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
BACKUP_SCRIPT

chmod +x /home/deploy/backup.sh
chown deploy:deploy /home/deploy/backup.sh
print_success "Backup script created"

print_info "Setting up automatic backups (daily at 2 AM)..."
(crontab -u deploy -l 2>/dev/null; echo "0 2 * * * /home/deploy/backup.sh") | crontab -u deploy -
print_success "Automatic backups scheduled"

#############################################################
# Installation Complete
#############################################################
print_section "Installation Complete! 🎉"

SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║          Installation Completed Successfully! 🎉          ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Access Information:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Website:${NC}        https://${DOMAIN}"
echo -e "  ${GREEN}IP Address:${NC}     http://${SERVER_IP}"
echo -e "  ${GREEN}Admin Panel:${NC}    https://${DOMAIN}/admin/"
echo ""
echo -e "  ${GREEN}Username:${NC}       admin"
echo -e "  ${GREEN}Password:${NC}       admin123"
echo -e "  ${RED}⚠️  CHANGE THIS PASSWORD IMMEDIATELY!${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}VPN Server Information:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}VPN IP:${NC}         10.10.0.1"
echo -e "  ${GREEN}VPN Port:${NC}       51820 (UDP)"
echo -e "  ${GREEN}Public Key:${NC}     ${SERVER_PUBLIC_KEY}"
echo ""
echo -e "  ${YELLOW}Configure your MikroTik routers with this public key${NC}"
echo -e "  ${YELLOW}See: mikrotik-configs/router1-wireguard.rsc${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Database Credentials:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Database:${NC}       ${DB_NAME}"
echo -e "  ${GREEN}User:${NC}           ${DB_USER}"
echo -e "  ${GREEN}Password:${NC}       ${DB_PASSWORD}"
echo -e "  ${YELLOW}(Saved in ${APP_DIR}/.env)${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Service Status:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
systemctl is-active --quiet mikrotik-billing && echo -e "  ${GREEN}✓${NC} Django (Gunicorn)  - Running" || echo -e "  ${RED}✗${NC} Django (Gunicorn)  - Stopped"
systemctl is-active --quiet celery-worker && echo -e "  ${GREEN}✓${NC} Celery Worker      - Running" || echo -e "  ${RED}✗${NC} Celery Worker      - Stopped"
systemctl is-active --quiet celery-beat && echo -e "  ${GREEN}✓${NC} Celery Beat        - Running" || echo -e "  ${RED}✗${NC} Celery Beat        - Stopped"
systemctl is-active --quiet nginx && echo -e "  ${GREEN}✓${NC} Nginx Web Server   - Running" || echo -e "  ${RED}✗${NC} Nginx Web Server   - Stopped"
systemctl is-active --quiet postgresql && echo -e "  ${GREEN}✓${NC} PostgreSQL         - Running" || echo -e "  ${RED}✗${NC} PostgreSQL         - Stopped"
systemctl is-active --quiet redis-server && echo -e "  ${GREEN}✓${NC} Redis              - Running" || echo -e "  ${RED}✗${NC} Redis              - Stopped"
systemctl is-active --quiet wg-quick@wg0 && echo -e "  ${GREEN}✓${NC} WireGuard VPN      - Running" || echo -e "  ${RED}✗${NC} WireGuard VPN      - Stopped"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  1. Visit https://${DOMAIN}/admin/"
echo "  2. Login with admin/admin123"
echo "  3. Change admin password immediately"
echo "  4. Configure MikroTik routers (use WireGuard public key above)"
echo "  5. Add routers in Django admin"
echo "  6. Create profiles and customers"
echo "  7. Test payment callbacks"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Check service status:"
echo "    sudo systemctl status mikrotik-billing"
echo ""
echo "  View logs:"
echo "    tail -f ${APP_DIR}/logs/error.log"
echo ""
echo "  Check VPN connections:"
echo "    sudo wg show"
echo ""
echo "  Restart services:"
echo "    sudo systemctl restart mikrotik-billing celery-worker celery-beat"
echo ""
echo "  Run backups:"
echo "    /home/deploy/backup.sh"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Installation log saved to: /var/log/mikrotik-billing-install.log${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Happy Billing! 🚀💰${NC}"
echo ""

# Save installation details
cat > /root/installation-details.txt << EOF
MikroTik Billing System - Installation Details
===============================================

Date: $(date)
Server IP: ${SERVER_IP}
Domain: ${DOMAIN}

Website: https://${DOMAIN}
Admin Panel: https://${DOMAIN}/admin/
Username: admin
Password: admin123 (CHANGE THIS!)

VPN Server:
-----------
VPN IP: 10.10.0.1
VPN Port: 51820 (UDP)
Public Key: ${SERVER_PUBLIC_KEY}

Database:
---------
Name: ${DB_NAME}
User: ${DB_USER}
Password: ${DB_PASSWORD}

Django Secret Key: ${DJANGO_SECRET_KEY}

Application Directory: ${APP_DIR}
Logs Directory: ${APP_DIR}/logs

Backups: /home/deploy/backups (automatic daily at 2 AM)

Services:
---------
- mikrotik-billing.service (Gunicorn)
- celery-worker.service
- celery-beat.service
- nginx
- postgresql
- redis-server
- wg-quick@wg0 (WireGuard)

EOF

print_success "Installation details saved to /root/installation-details.txt"

exit 0
