# MikroTik Billing Management System

A comprehensive, professional web-based billing management panel for MikroTik routers built with Django (Python). This system provides complete router management, customer billing, payment integration, voucher generation, and detailed reporting capabilities.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Django](https://img.shields.io/badge/django-4.2-green.svg)

## 🚀 Features

### Core Features
- **Router Management**: Add, monitor, and manage multiple MikroTik routers
- **Real-time Status Monitoring**: Check router online/offline status with automatic health checks
- **Customer Management**: Full CRUD operations for end-user accounts
- **Profile Management**: Create bandwidth profiles with pricing and duration
- **Payment Integration**: Mock payment callbacks ready for M-Pesa, PayPal, and other gateways
- **Voucher System**: Generate and manage prepaid access codes/vouchers
- **Session Tracking**: Monitor active connections and customer sessions
- **Reports & Analytics**: Revenue reports, customer analytics, and automated daily reports

### Advanced Features
- **Activity Logging**: Complete audit trail of all system actions
- **Notifications System**: In-app notifications for important events
- **Background Tasks**: Celery-based task queue for health checks and automated processes
- **API Endpoints**: RESTful API for payment callbacks and integrations
- **Multi-router Support**: Manage unlimited routers from a single panel
- **Auto-expiry Management**: Automatically disable expired accounts
- **Data Export**: Export vouchers and reports to CSV
- **Professional UI**: Modern, responsive interface built with TailwindCSS

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite/PostgreSQL/MySQL database
- Redis (optional, for Celery tasks)
- MikroTik router(s) with API enabled
- VPN tunnel to routers (if managing remote routers)

## 🛠️ Installation

### 1. Clone the Repository

```bash
cd C:\Users\A\Desktop\mikrotikvpn
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root (or copy from `.env.example`):

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (SQLite by default)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# For PostgreSQL (recommended for production)
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=mikrotik_billing
# DATABASE_USER=postgres
# DATABASE_PASSWORD=yourpassword
# DATABASE_HOST=localhost
# DATABASE_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password

# Celery (Optional - for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Payment Gateway Settings
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-mpesa-passkey

PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=sandbox
```

### 5. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 6. Create Static Files Directory

```bash
mkdir static
mkdir staticfiles
mkdir media
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` and login with your superuser credentials.

## 🔧 MikroTik Router Configuration

### 1. Enable API on Your MikroTik Router

```routeros
/ip service
set api address=0.0.0.0/0 disabled=no port=8728
```

### 2. Create Admin User (if needed)

```routeros
/user add name=billing-admin password=SecurePassword123 group=full
```

### 3. Configure VPN Tunnel (for remote routers)

If your routers are remote, set up a VPN tunnel (e.g., WireGuard, OpenVPN, or IPSec) and note the VPN IP addresses (e.g., 10.10.0.x).

### 4. Add Router to System

1. Login to the web panel
2. Navigate to **Routers** → **Add New Router**
3. Fill in:
   - **Name**: Router1
   - **VPN IP**: 10.10.0.2 (or LAN IP for local)
   - **Username**: billing-admin
   - **Password**: SecurePassword123
   - **API Port**: 8728 (default)
4. Click **Test Connection** to verify

## 📚 Usage Guide

### Adding a Customer

1. Go to **Customers** → **Add New Customer**
2. Fill in customer details (username, password, name, contact)
3. Select router and profile
4. Click **Save Customer**
   - User is automatically created on the selected MikroTik router

### Creating Profiles

1. Go to **Profiles** → **Add New Profile**
2. Configure:
   - **Name**: e.g., "5Mbps Daily"
   - **Download/Upload Speed**: 5M (MikroTik format)
   - **Duration**: 1 Day
   - **Price**: 50 KES
3. Save profile

### Processing Payments

#### Manual Payment:
1. Go to customer detail page
2. Click **Record Payment**
3. Enter amount and payment method
4. Customer is automatically activated/extended

#### Automatic Payment (API Callback):
Payment gateways should POST to:
```
POST http://your-domain.com/api/payment/callback/
Content-Type: application/json

{
    "transaction_id": "ABC123XYZ",
    "customer_username": "customer1",
    "amount": 50.00,
    "currency": "KES",
    "status": "success",
    "payment_method": "MPESA"
}
```

### Generating Vouchers

1. Go to **Vouchers** → **Create Batch**
2. Configure:
   - **Name**: December Vouchers
   - **Profile**: Select profile
   - **Router**: Select router
   - **Quantity**: 100
   - **Price per Voucher**: 50
3. Vouchers are generated automatically
4. Export to CSV for printing/distribution

### Redeeming Vouchers

1. Go to **Vouchers** → **Redeem**
2. Enter voucher code
3. Select customer
4. Customer is automatically extended

## 🔄 Background Tasks (Optional)

### Start Celery Worker

```bash
# In a separate terminal
celery -A mikrotik_billing worker -l info
```

### Start Celery Beat (Scheduler)

```bash
# In another terminal
celery -A mikrotik_billing beat -l info
```

**Scheduled Tasks:**
- Router status check: Every 5 minutes
- Check expired users: Daily at midnight
- Generate daily reports: Daily at 11:55 PM

## 🎨 UI Customization

The system uses TailwindCSS via CDN. For production, compile your own Tailwind build:

1. Install Node.js and npm
2. Configure `tailwind.config.js`
3. Build CSS: `npx tailwindcss -o static/css/tailwind.css --minify`
4. Update templates to use local CSS

## 🔐 Security Considerations

### For Production:

1. **Change DEBUG to False**:
   ```env
   DEBUG=False
   ```

2. **Use Strong SECRET_KEY**:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

3. **Use PostgreSQL/MySQL** instead of SQLite

4. **Enable HTTPS** with SSL certificate

5. **Configure Firewall**:
   - Only allow API port (8728) from billing server to routers
   - Use VPN tunnel for remote router access

6. **Secure Payment Callbacks**:
   - Verify webhook signatures
   - Use IP whitelisting

7. **Regular Backups**:
   ```bash
   python manage.py dumpdata > backup.json
   ```

## 📊 API Endpoints

### Payment Callback (Generic)
```
POST /api/payment/callback/
```

### M-Pesa Callback
```
POST /api/payment/mpesa/callback/
```

### PayPal Callback
```
POST /api/payment/paypal/callback/
```

### Payment Initiation
```
POST /api/payment/initiate/
```

## 🐛 Troubleshooting

### Connection to Router Fails

1. Check VPN/network connectivity
2. Verify API is enabled on router
3. Check username/password
4. Ensure port 8728 is not blocked by firewall

### librouteros Installation Issues

```bash
# If you encounter issues, try:
pip install librouteros --upgrade
```

### Static Files Not Loading

```bash
python manage.py collectstatic
```

### Database Errors

```bash
# Reset database (CAUTION: destroys all data)
python manage.py flush
python manage.py migrate
```

## 📁 Project Structure

```
mikrotikvpn/
├── manage.py
├── requirements.txt
├── README.md
├── .env (create this)
├── mikrotik_billing/      # Main project config
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── core/                  # Core utilities
│   ├── models.py         # ActivityLog, Notification
│   ├── context_processors.py
│   └── admin.py
├── routers/              # Router management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services/
│   │   └── mikrotik_api.py
│   ├── tasks.py
│   └── admin.py
├── customers/            # Customer management
│   ├── models.py
│   ├── views.py
│   └── forms.py
├── profiles/             # Bandwidth profiles
│   ├── models.py
│   └── views.py
├── payments/             # Payment processing
│   ├── models.py
│   ├── views.py
│   └── api_views.py     # Payment callbacks
├── vouchers/             # Voucher system
│   ├── models.py
│   └── views.py
├── reports/              # Analytics & reports
│   ├── models.py
│   └── views.py
├── dashboard/            # Main dashboard
│   └── views.py
└── templates/            # HTML templates
    ├── base.html
    ├── auth/
    ├── dashboard/
    └── partials/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 💬 Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Email: support@example.com

## 🙏 Acknowledgments

- **Django Framework** - Web framework
- **librouteros** - MikroTik API library
- **TailwindCSS** - UI framework
- **Alpine.js** - JavaScript framework
- **Font Awesome** - Icons

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-03  
**Author**: MikroTik Billing Team

## 🚦 Getting Started Checklist

- [ ] Install Python and dependencies
- [ ] Create virtual environment
- [ ] Configure `.env` file
- [ ] Run migrations
- [ ] Create superuser
- [ ] Configure MikroTik router API
- [ ] Add first router to system
- [ ] Create bandwidth profiles
- [ ] Add test customer
- [ ] Test payment callback (optional)
- [ ] Set up Celery (optional)
- [ ] Configure production settings (if deploying)

## 📈 Roadmap

- [ ] SMS notification integration
- [ ] Customer self-service portal
- [ ] Multi-currency support
- [ ] Advanced bandwidth throttling
- [ ] Usage-based billing
- [ ] Invoice generation
- [ ] Mobile app (Flutter/React Native)
- [ ] Multi-tenancy support

Enjoy managing your MikroTik billing with ease! 🎉

