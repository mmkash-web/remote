# Quick Start Guide

Get your MikroTik Billing System up and running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- pip installed
- Basic knowledge of command line

## Installation Steps

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Run migrations
python manage.py migrate
```

### 3. Create Admin User & Sample Data

```bash
# Run setup script
python setup_admin.py
```

This creates:
- Admin user: `admin` / `admin123` (⚠️ Change in production!)
- Sample bandwidth profiles (5Mbps Daily, 10Mbps Weekly, 20Mbps Monthly)

### 4. Start Server

```bash
python manage.py runserver
```

### 5. Access the System

Open your browser and go to:
```
http://127.0.0.1:8000
```

Login with:
- **Username**: admin
- **Password**: admin123

## First-Time Configuration

### Add Your First Router

1. Click **Routers** in the sidebar
2. Click **Add Router**
3. Fill in:
   ```
   Name: MyRouter
   VPN IP: 10.10.0.2 (or your router's IP)
   Username: admin
   Password: your-router-password
   API Port: 8728
   ```
4. Click **Save Router**
5. Click **Test Connection** to verify

### Create Customers

1. Click **Customers** in the sidebar
2. Click **Add New Customer**
3. Fill in customer details
4. Select router and profile
5. Click **Save Customer**

The customer account is automatically created on the MikroTik router!

### Process Payment

**Option 1: Manual Payment**
1. Go to customer detail page
2. Click **Record Payment**
3. Enter amount and payment method
4. Customer is automatically activated

**Option 2: API Callback**
Configure your payment gateway to send callbacks to:
```
POST http://your-domain.com/api/payment/callback/
```

## Testing Payment Callback

Use curl or Postman:

```bash
curl -X POST http://127.0.0.1:8000/api/payment/callback/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST123",
    "customer_username": "customer1",
    "amount": 50.00,
    "currency": "KES",
    "status": "success",
    "payment_method": "MPESA"
  }'
```

## Optional: Enable Background Tasks

For automatic router checks and reports:

### Install Redis

```bash
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt install redis-server
# Mac: brew install redis
```

### Start Celery

```bash
# Terminal 1: Worker
celery -A mikrotik_billing worker -l info

# Terminal 2: Beat (scheduler)
celery -A mikrotik_billing beat -l info
```

## Common Issues

### Can't connect to router?

- Check if API is enabled: `/ip service set api disabled=no`
- Verify IP address and credentials
- Check firewall rules

### Static files not loading?

```bash
mkdir static staticfiles media
python manage.py collectstatic
```

### Database errors?

```bash
python manage.py migrate
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Configure payment gateways (M-Pesa, PayPal)
- Set up email notifications
- Generate vouchers for prepaid access
- View reports and analytics

## Production Deployment

See [README.md](README.md) for production deployment checklist including:
- Security configurations
- Database setup (PostgreSQL)
- HTTPS/SSL
- Backup strategy

---

Need help? Check the README.md or create an issue on GitHub.

Happy billing! 🎉

