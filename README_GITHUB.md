# 🚀 MikroTik VPN Billing System

**Complete automated billing and customer management system for MikroTik routers with VPN support.**

Perfect for ISPs, VPN providers, and network administrators managing multiple MikroTik routers.

[![Deploy](https://img.shields.io/badge/Deploy-One%20Click-blue)](https://github.com/mmkash-web/remote)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green)](https://www.djangoproject.com/)

---

## ⚡ Quick Deploy (5 Minutes)

Deploy the complete system on your VPS with **one command**:

```bash
curl -sSL https://raw.githubusercontent.com/mmkash-web/remote/main/quick-install.sh | sudo bash
```

That's it! The installer will:
- ✅ Set up PostgreSQL database
- ✅ Install Redis for caching  
- ✅ Configure Nginx web server
- ✅ Install SSL certificate (Let's Encrypt)
- ✅ Set up Django application
- ✅ Create systemd services
- ✅ Configure firewall
- ✅ Start everything automatically

**[📖 Read the Quick Installation Guide](QUICK_VPS_INSTALL.md)**

---

## 🎯 Features

### Customer Management
- ✅ Add/edit/delete customers
- ✅ Automatic expiry tracking
- ✅ Bulk operations
- ✅ Import/export customers
- ✅ Customer profiles and groups
- ✅ Active session monitoring

### Payment Integration
- 💳 **M-Pesa** (Kenya)
- 💰 **PayPal** (International)
- 💵 Manual payments
- 📊 Payment history & reports
- 🔔 Payment notifications

### Voucher System
- 🎫 Generate voucher batches
- 🖨️ Print voucher cards
- 🔐 Unique secure codes
- ✅ Redeem & track usage
- 📈 Voucher analytics

### Router Management
- 🌐 Multiple MikroTik routers
- 🔄 Auto-sync with RouterOS
- 📡 Real-time connection monitoring
- ⚙️ Profile management
- 🔧 Remote configuration

### Reports & Analytics
- 📊 Revenue reports
- 👥 Customer statistics
- 🌐 Router performance
- 📈 Usage trends
- 📥 Export to CSV/PDF

### API Access
- 🔌 RESTful API
- 🔑 Token authentication
- 📡 Webhooks (M-Pesa, PayPal)
- 📚 Complete documentation
- 🧪 Postman collection

---

## 📸 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Customer Management
![Customers](docs/screenshots/customers.png)

### Reports
![Reports](docs/screenshots/reports.png)

---

## 🛠️ Tech Stack

- **Backend:** Django 4.2+, Python 3.8+
- **Database:** PostgreSQL 12+
- **Cache:** Redis
- **Web Server:** Nginx + Gunicorn
- **Task Queue:** Celery
- **API:** Django REST Framework
- **Frontend:** TailwindCSS + Alpine.js
- **Router API:** librouteros

---

## 📋 Requirements

### For VPS Installation

- **OS:** Ubuntu 22.04 LTS (recommended)
- **RAM:** 1GB minimum (2GB recommended)
- **CPU:** 1 core minimum
- **Storage:** 20GB minimum
- **Domain:** Optional but recommended

### For Local Development

- Python 3.8+
- PostgreSQL 12+
- Redis
- MikroTik router (optional for testing)

---

## 🚀 Installation Methods

### 1. Quick VPS Install (Recommended)

**For production deployment on a VPS:**

```bash
curl -sSL https://raw.githubusercontent.com/mmkash-web/remote/main/quick-install.sh | sudo bash
```

**[📖 Detailed Guide](QUICK_VPS_INSTALL.md)**

### 2. Manual Installation

**For development or custom setup:**

```bash
# Clone repository
git clone https://github.com/mmkash-web/remote.git
cd remote

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

**[📖 Complete Manual Guide](VPS_COMPLETE_DEPLOYMENT.md)**

### 3. Docker Installation (Coming Soon)

```bash
docker-compose up -d
```

---

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=mikrotik_billing
DATABASE_USER=billing_user
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0

# M-Pesa (Optional)
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_PASSKEY=your-passkey
MPESA_SHORTCODE=your-shortcode

# PayPal (Optional)
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret
PAYPAL_MODE=sandbox  # or 'live'
```

### 2. MikroTik Router Setup

**Enable API on your MikroTik:**

```bash
/ip service set api address=YOUR_VPS_IP port=8728
```

**Create PPP profile:**

```bash
/ppp profile add name="1Mbps-30Days" local-address=10.10.10.1 remote-address=dhcp-pool
/ip pool add name=dhcp-pool ranges=10.10.10.2-10.10.10.254
```

**[📖 Complete MikroTik Setup Guide](MIKROTIK_VPN_QUICKSTART.md)**

---

## 📚 Documentation

- **[Quick VPS Installation](QUICK_VPS_INSTALL.md)** - 5-minute setup guide
- **[Complete VPS Deployment](VPS_COMPLETE_DEPLOYMENT.md)** - Detailed production setup
- **[MikroTik Configuration](MIKROTIK_VPN_QUICKSTART.md)** - Router setup guide
- **[API Documentation](docs/API.md)** - REST API reference
- **[Testing Guide](TESTING_GUIDE.md)** - How to test the system
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues & solutions

---

## 🎓 Video Tutorials

Coming soon! Subscribe for updates:

- ✅ Quick VPS Installation
- ✅ MikroTik Router Setup
- ✅ Customer Management
- ✅ Payment Integration
- ✅ Voucher System

---

## 🔧 Management

### Check Status

```bash
sudo systemctl status mikrotik-billing
sudo systemctl status mikrotik-celery
sudo systemctl status nginx
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
```

### Update Application

```bash
cd /home/deploy/mikrotikvpn
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart mikrotik-billing mikrotik-celery
```

---

## 🆘 Support

- **Documentation:** [https://github.com/mmkash-web/remote](https://github.com/mmkash-web/remote)
- **Issues:** [https://github.com/mmkash-web/remote/issues](https://github.com/mmkash-web/remote/issues)
- **Email:** admin@netbill.site
- **Community:** [Join our Discord](#) (coming soon)

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework
- [MikroTik](https://mikrotik.com/) - Router OS
- [TailwindCSS](https://tailwindcss.com/) - UI framework
- [librouteros](https://github.com/luqasz/librouteros) - MikroTik API library

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=mmkash-web/remote&type=Date)](https://star-history.com/#mmkash-web/remote&Date)

---

## 📞 Contact

**Project Maintainer:** Emmanuel Mmkash  
**Email:** admin@netbill.site  
**GitHub:** [@mmkash-web](https://github.com/mmkash-web)

---

**Made with ❤️ for the ISP community**

