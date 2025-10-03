# Testing Guide - MikroTik Billing System

Complete guide to test the system locally before production deployment.

## 📋 Pre-Testing Checklist

Before you start testing:

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Admin user created (`python setup_admin.py`)
- [ ] Development server can start (`python manage.py runserver`)

## 🚀 Step-by-Step Testing

### Step 1: Verify Installation

```bash
# Run the setup verification script
python check_setup.py
```

This checks:
- Python version
- All required packages
- Database connection
- Migrations status
- Directory structure

**Expected Result**: All critical checks should pass ✓

---

### Step 2: Start the Development Server

```bash
# Activate virtual environment if not already
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start server
python manage.py runserver
```

**Expected Result**: Server starts on `http://127.0.0.1:8000` without errors

**Test**: Open browser and visit `http://127.0.0.1:8000`
- Should redirect to login page
- Login page should display properly with styling

---

### Step 3: Test Login System

1. **Navigate to**: `http://127.0.0.1:8000`
2. **Login with**:
   - Username: `admin`
   - Password: `admin123`

**Expected Result**:
- ✓ Login successful
- ✓ Redirected to dashboard
- ✓ Dashboard shows statistics cards
- ✓ Sidebar navigation visible
- ✓ No console errors

**Screenshot**: Dashboard should show:
- Total Customers: 0
- Active Customers: 0
- Routers Online: 0/0
- Revenue stats

---

### Step 4: Test Profile Management

#### Create a Profile

1. Click **Profiles** in sidebar
2. Click **Add New Profile**
3. Fill in:
   ```
   Name: 5Mbps Daily Test
   Description: Test profile for 5Mbps speed
   Download Speed: 5M
   Upload Speed: 5M
   Duration Value: 1
   Duration Unit: Days
   Price: 50
   Currency: KES
   Is Active: ✓
   Is Public: ✓
   ```
4. Click **Save Profile**

**Expected Result**:
- ✓ Success message appears
- ✓ Redirected to profile list
- ✓ New profile appears in list
- ✓ Profile details are correct

#### Test Profile List

- **Navigate to**: Profiles → View all
- **Expected**: Profile list shows created profile
- **Actions**: Edit, Delete buttons visible

---

### Step 5: Test Router Management

#### Option A: Test Without Real Router (Mock Test)

**Create a test router** (won't connect, but tests the UI):

1. Click **Routers** → **Add Router**
2. Fill in:
   ```
   Name: TestRouter
   Description: Test router for development
   VPN IP: 192.168.1.1 (any IP)
   API Port: 8728
   Username: admin
   Password: test123
   Is Active: ✓
   ```
3. Click **Save Router**

**Expected Result**:
- ✓ Router created successfully
- ✓ Shown in router list
- ✓ Status shows "UNKNOWN" or "OFFLINE" (normal, no real connection)

**Note**: Connection test will fail (expected), but you verified the UI works!

#### Option B: Test With Real/Virtual MikroTik Router

If you have access to a MikroTik router or CHR (Cloud Hosted Router):

**1. Configure MikroTik:**
```routeros
# Enable API
/ip service set api disabled=no port=8728

# Create test user
/user add name=billing-test password=test123 group=full
```

**2. Add Router in Web Panel:**
- Use router's actual IP (or VPN IP)
- Username: `billing-test`
- Password: `test123`

**3. Test Connection:**
- Click **Test Connection** button
- **Expected**: "Router is ONLINE" message

**4. Check Router Details:**
- Navigate to router detail page
- **Expected**: Shows router model, version, uptime

---

### Step 6: Test Customer Management

#### Create a Customer

**Requirements**: At least one Profile and one Router must exist

1. Click **Customers** → **Add New Customer**
2. Fill in:
   ```
   Username: testuser1
   Password: password123
   Full Name: Test User One
   Email: test@example.com
   Phone: +254712345678
   Router: [Select your test router]
   Profile: [Select your test profile]
   Notes: Test customer for system verification
   Send Notifications: ✓
   ```
3. Click **Save Customer**

**Expected Result**:
- ✓ Customer created in database
- ✓ Success message appears
- ✓ Redirected to customer detail page

**If Router is Real**:
- ✓ Customer is created on MikroTik router
- ✓ Can verify in router with: `/ppp secret print`

**If Router is Mock**:
- ✓ Warning message: "Failed to create on router" (expected)
- ✓ Customer still created in database

#### View Customer Details

- **Navigate to**: Customer detail page
- **Expected to see**:
  - Customer info (username, name, email, phone)
  - Status: PENDING (no payment yet)
  - Profile information
  - Router assignment
  - Payment history (empty)
  - Session history (empty)
  - Action buttons (Edit, Enable, Disable, Delete, Record Payment)

---

### Step 7: Test Payment Processing

#### Test Manual Payment

1. Go to customer detail page
2. Click **Record Payment** button
3. Fill in:
   ```
   Amount: 50
   Payment Method: CASH
   Reference: TEST001
   Notes: Test payment
   ```
4. Click **Submit**

**Expected Result**:
- ✓ Success message: "Payment recorded successfully"
- ✓ Customer status changes to "ACTIVE"
- ✓ Expires date is set (1 day from now)
- ✓ Payment appears in payment history
- ✓ Last payment date updated

#### Test Payment API Callback

**Open a new terminal** and run:

```bash
curl -X POST http://127.0.0.1:8000/api/payment/callback/ ^
  -H "Content-Type: application/json" ^
  -d "{\"transaction_id\":\"TEST002\",\"customer_username\":\"testuser1\",\"amount\":50.00,\"currency\":\"KES\",\"status\":\"success\",\"payment_method\":\"MPESA\"}"
```

**For PowerShell (Windows):**
```powershell
$body = @{
    transaction_id = "TEST002"
    customer_username = "testuser1"
    amount = 50.00
    currency = "KES"
    status = "success"
    payment_method = "MPESA"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/payment/callback/" -Method Post -Body $body -ContentType "application/json"
```

**For Python:**
```python
import requests
import json

data = {
    "transaction_id": "TEST002",
    "customer_username": "testuser1",
    "amount": 50.00,
    "currency": "KES",
    "status": "success",
    "payment_method": "MPESA"
}

response = requests.post(
    "http://127.0.0.1:8000/api/payment/callback/",
    json=data
)
print(response.json())
```

**Expected Result**:
- ✓ API returns: `{"status": "success", "message": "Payment processed successfully"}`
- ✓ New payment record created
- ✓ Customer subscription extended
- ✓ Payment appears in customer's payment history

---

### Step 8: Test Voucher System

#### Create Voucher Batch

1. Click **Vouchers** → **Create Batch**
2. Fill in:
   ```
   Name: Test Voucher Batch
   Description: 100 test vouchers
   Profile: [Select a profile]
   Router: [Select a router]
   Quantity: 10
   Price per Voucher: 50
   ```
3. Click **Create Batch**

**Expected Result**:
- ✓ Success message: "Created batch with 10 vouchers"
- ✓ Redirected to batch detail page
- ✓ Shows 10 vouchers with unique codes (format: XXXX-XXXX-XXXX)
- ✓ All vouchers show status "Available"

#### Test Voucher Redemption

1. Copy a voucher code from the batch
2. Navigate to **Vouchers** → **Redeem**
3. Fill in:
   ```
   Voucher Code: [Paste copied code]
   Customer: [Select testuser1]
   ```
4. Click **Redeem**

**Expected Result**:
- ✓ Success message: "Voucher redeemed successfully"
- ✓ Customer subscription extended
- ✓ Voucher status changes to "Used"
- ✓ Voucher shows "Used by: testuser1"

#### Export Vouchers

1. Go to voucher batch detail
2. Click **Export to CSV**

**Expected Result**:
- ✓ CSV file downloads
- ✓ Contains all voucher codes
- ✓ Shows status for each voucher

---

### Step 9: Test Reports & Analytics

#### View Dashboard

- Navigate to main **Dashboard**
- **Expected to see**:
  - Statistics updated with your test data
  - Customer count showing
  - Payment records visible
  - Recent activity log

#### View Revenue Report

1. Click **Reports** → **Revenue Report**
2. **Expected to see**:
   - Total revenue from test payments
   - Payment breakdown by method
   - Payment breakdown by profile
   - List of recent payments

#### View Customer Report

1. Click **Reports** → **Customer Report**
2. **Expected to see**:
   - Total customers count
   - Active vs expired breakdown
   - Customers by router
   - Customers by profile

---

### Step 10: Test Customer Actions

#### Enable/Disable Customer

**On Real Router:**
1. Go to customer detail
2. Click **Disable**
   - **Expected**: Success message, customer disabled on router
3. Click **Enable**
   - **Expected**: Success message, customer enabled on router

**On Mock Router:**
- May show errors (expected without real router)
- Database status still updates

#### Extend Subscription

1. Go to customer detail
2. Click **Extend Subscription**
3. Choose option:
   - Use profile duration
   - OR custom days: 7
4. Click **Extend**

**Expected Result**:
- ✓ Success message
- ✓ Expiry date extended
- ✓ Customer remains active

#### View Active Sessions

- Navigate to **Active Sessions**
- **On Real Router**: Shows connected customers
- **On Mock Router**: Shows empty list (expected)

---

### Step 11: Test Activity Logging

1. Navigate to **Admin Panel** (if superuser)
2. Go to **Core** → **Activity Logs**

**Expected to see**:
- ✓ All actions logged (CREATE, UPDATE, ENABLE, DISABLE, PAYMENT)
- ✓ Each log shows: User, Action, Description, IP, Timestamp
- ✓ Recent test actions visible

---

### Step 12: Test Admin Panel

1. Navigate to: `http://127.0.0.1:8000/admin/`
2. Login with admin credentials

**Test each section**:
- ✓ **Routers**: View, Edit routers
- ✓ **Customers**: View, Edit customers
- ✓ **Profiles**: View, Edit profiles
- ✓ **Payments**: View payment records
- ✓ **Vouchers**: View vouchers and batches
- ✓ **Activity Logs**: View all logs
- ✓ **Notifications**: View notifications

**Expected**: All admin pages load without errors

---

## 🧪 Advanced Testing (Optional)

### Test Celery Background Tasks

**If you have Redis installed:**

**Terminal 1 - Start Celery Worker:**
```bash
celery -A mikrotik_billing worker -l info
```

**Terminal 2 - Test Manual Task:**
```bash
python manage.py shell
```

Then in shell:
```python
from routers.tasks import check_router_status
from routers.models import Router

# Get first router
router = Router.objects.first()

# Trigger status check
result = check_router_status.delay(str(router.id))
print(f"Task ID: {result.id}")

# Check result (wait a few seconds)
print(result.get(timeout=10))
```

**Expected**: Task executes successfully

---

## ✅ Complete Testing Checklist

Use this checklist to verify everything:

### Basic Functionality
- [ ] Server starts without errors
- [ ] Login page displays correctly
- [ ] Can login with admin account
- [ ] Dashboard loads with statistics
- [ ] Navigation sidebar works
- [ ] All menu items accessible

### Profile Management
- [ ] Can create new profile
- [ ] Profile appears in list
- [ ] Can edit profile
- [ ] Can view profile details
- [ ] Can delete profile (if no customers)

### Router Management
- [ ] Can add new router
- [ ] Router appears in list
- [ ] Can view router details
- [ ] Can edit router
- [ ] Can test connection (if real router)
- [ ] Status updates correctly

### Customer Management
- [ ] Can create new customer
- [ ] Customer created in database
- [ ] Customer created on router (if real)
- [ ] Can view customer details
- [ ] Can edit customer information
- [ ] Can enable/disable customer
- [ ] Can extend subscription
- [ ] Can delete customer

### Payment System
- [ ] Can record manual payment
- [ ] Payment activates customer
- [ ] Payment API callback works
- [ ] Payment history displays correctly
- [ ] Transaction logging works

### Voucher System
- [ ] Can create voucher batch
- [ ] Vouchers generated with unique codes
- [ ] Can view voucher list
- [ ] Can redeem voucher
- [ ] Voucher extends customer subscription
- [ ] Can export vouchers to CSV

### Reports & Analytics
- [ ] Dashboard shows correct statistics
- [ ] Revenue report displays
- [ ] Customer report displays
- [ ] Router report displays
- [ ] Charts/graphs render (if implemented)

### Security & Logging
- [ ] Activity logs record actions
- [ ] Notifications appear
- [ ] Unauthorized access blocked
- [ ] CSRF protection works
- [ ] Admin panel secured

### UI/UX
- [ ] Pages load quickly
- [ ] No console errors
- [ ] Responsive design works on mobile
- [ ] Forms validate input
- [ ] Success/error messages display
- [ ] Icons and styling correct

---

## 🐛 Common Issues & Solutions

### Issue: Server won't start
**Solution**:
```bash
python check_setup.py
python manage.py migrate
```

### Issue: "ModuleNotFoundError"
**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: Can't connect to router
**Solutions**:
- Verify router IP is accessible: `ping 10.10.0.2`
- Check API is enabled: `/ip service print`
- Verify port 8728 is open
- Check username/password
- Try from MikroTik: `/user print`

### Issue: Static files not loading
**Solution**:
```bash
python manage.py collectstatic
```

### Issue: Payment callback fails
**Solutions**:
- Check URL is correct
- Verify JSON format
- Check customer username exists
- Review error in console/logs

### Issue: Database locked (SQLite)
**Solution**:
```bash
# Close all connections
# Restart server
python manage.py runserver
```

---

## 📊 Test Data Summary

After completing all tests, you should have:

- **Profiles**: 1-3 test profiles (5Mbps, 10Mbps, etc.)
- **Routers**: 1 test router (may be offline if mock)
- **Customers**: 2-3 test customers
- **Payments**: 2-3 test payment records
- **Vouchers**: 1 batch with 10 vouchers (1 used, 9 available)
- **Activity Logs**: 15+ log entries
- **Sessions**: 0 (unless real router with active connections)

---

## 🎯 Performance Testing

### Basic Load Test

**Using Apache Bench (if installed):**
```bash
ab -n 100 -c 10 http://127.0.0.1:8000/
```

**Expected**: 
- All requests should complete
- No 500 errors
- Average response time < 500ms

---

## 📸 Visual Testing

### Take Screenshots

Document your test results by taking screenshots of:
1. Dashboard with data
2. Router list
3. Customer list
4. Payment history
5. Voucher batch
6. Reports page

Compare with expected layouts to verify UI works correctly.

---

## ✨ Final Verification

Before deployment, ensure:

- [ ] All checklist items completed
- [ ] No critical errors in console
- [ ] All major features tested
- [ ] Test data can be cleared (for production)
- [ ] Documentation reviewed
- [ ] Backup created

### Clear Test Data (Before Production)

```bash
# Option 1: Delete test objects manually in admin panel

# Option 2: Reset database (CAUTION: Deletes everything!)
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚀 You're Ready!

If all tests pass, you're ready to:
1. Deploy to staging environment
2. Test with real MikroTik router
3. Configure production settings
4. Deploy to production server

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment steps.

---

## 📞 Need Help?

If any tests fail:
1. Check error messages carefully
2. Review logs: Check terminal output
3. Run `python check_setup.py`
4. Check [README.md](README.md) troubleshooting section
5. Review [COMMANDS.md](COMMANDS.md) for useful commands

**Happy Testing!** 🧪✨

