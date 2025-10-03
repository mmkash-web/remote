# Quick Testing Checklist

Use this checklist to quickly verify the system is working before deployment.

## ⚡ Quick Start Testing (10 Minutes)

### 1. Installation Check ✓
```bash
python check_setup.py
```
- [ ] All critical checks pass
- [ ] No red X marks for critical items

### 2. Start Server ✓
```bash
python manage.py runserver
```
- [ ] Server starts without errors
- [ ] Accessible at http://127.0.0.1:8000

### 3. Login Test ✓
- [ ] Login page displays properly
- [ ] Can login with admin/admin123
- [ ] Dashboard loads successfully

### 4. Create Test Profile ✓
Navigate: **Profiles → Add New Profile**
```
Name: 5Mbps Test
Download: 5M
Upload: 5M
Duration: 1 Day
Price: 50 KES
```
- [ ] Profile created successfully
- [ ] Appears in profile list

### 5. Create Test Router ✓
Navigate: **Routers → Add Router**
```
Name: TestRouter
VPN IP: 192.168.1.1
Username: admin
Password: test123
Port: 8728
```
- [ ] Router created successfully
- [ ] Appears in router list
- [ ] Status shows (may be offline - OK for testing)

### 6. Create Test Customer ✓
Navigate: **Customers → Add New Customer**
```
Username: testuser1
Password: password123
Full Name: Test User
Email: test@test.com
Router: [Select TestRouter]
Profile: [Select 5Mbps Test]
```
- [ ] Customer created successfully
- [ ] Appears in customer list

### 7. Record Payment ✓
From customer detail page:
```
Amount: 50
Method: CASH
Reference: TEST001
```
- [ ] Payment recorded
- [ ] Customer status changes to ACTIVE
- [ ] Expiry date set

### 8. Test Payment API ✓
Run in terminal:
```powershell
$body = @{
    transaction_id = "TEST-API-001"
    customer_username = "testuser1"
    amount = 50.00
    currency = "KES"
    status = "success"
    payment_method = "MPESA"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/payment/callback/" `
    -Method Post -Body $body -ContentType "application/json"
```
- [ ] Returns success response
- [ ] Payment created in system
- [ ] Customer subscription extended

### 9. Create Vouchers ✓
Navigate: **Vouchers → Create Batch**
```
Name: Test Batch
Quantity: 10
Profile: [Select 5Mbps Test]
Router: [Select TestRouter]
Price: 50
```
- [ ] Batch created
- [ ] 10 vouchers generated
- [ ] Codes display correctly (XXXX-XXXX-XXXX)

### 10. Redeem Voucher ✓
Navigate: **Vouchers → Redeem**
- Copy a voucher code
- Select testuser1
- Click Redeem
- [ ] Voucher redeemed successfully
- [ ] Customer subscription extended
- [ ] Voucher marked as used

### 11. Check Dashboard ✓
Navigate to main Dashboard
- [ ] Statistics show correct counts
- [ ] Recent activity displays
- [ ] Quick actions work
- [ ] No console errors

### 12. Check Reports ✓
Navigate: **Reports → Dashboard**
- [ ] Revenue stats display
- [ ] Customer breakdown shows
- [ ] Payment methods chart works
- [ ] No errors

---

## 🔬 Automated Testing

### Run Automated Tests
```bash
python run_tests.py
```
**Expected Result:**
```
✓ All tests passed!
Success Rate: 100%
```

### What It Tests:
- [ ] Database connectivity
- [ ] All models can be created
- [ ] Methods work correctly
- [ ] API imports successful
- [ ] Admin site configured
- [ ] Background tasks importable

---

## 🎯 Pass/Fail Criteria

### ✅ PASS if:
- All checklist items completed
- No critical errors in console
- Can create routers, customers, profiles
- Payments process successfully
- API callback works
- Automated tests pass

### ❌ FAIL if:
- Server won't start
- Can't login
- Can't create basic records
- Payment API returns errors
- Multiple console errors
- Automated tests fail

---

## 🚀 Ready for Deployment?

### Before Production:
- [ ] All tests passed
- [ ] Tested with real MikroTik router (recommended)
- [ ] Payment integration configured
- [ ] .env file configured
- [ ] Security settings reviewed
- [ ] Backup strategy planned
- [ ] Documentation reviewed

### Clear Test Data:
```bash
# Option 1: Delete via admin panel
# Option 2: Reset database
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 Test Results Template

**Date**: _____________
**Tester**: _____________

| Test | Pass | Fail | Notes |
|------|------|------|-------|
| Installation Check | ☐ | ☐ | |
| Server Start | ☐ | ☐ | |
| Login | ☐ | ☐ | |
| Create Profile | ☐ | ☐ | |
| Create Router | ☐ | ☐ | |
| Create Customer | ☐ | ☐ | |
| Record Payment | ☐ | ☐ | |
| API Callback | ☐ | ☐ | |
| Create Vouchers | ☐ | ☐ | |
| Redeem Voucher | ☐ | ☐ | |
| Dashboard | ☐ | ☐ | |
| Reports | ☐ | ☐ | |
| Automated Tests | ☐ | ☐ | |

**Overall Result**: PASS / FAIL

**Notes**:
_____________________________________________
_____________________________________________
_____________________________________________

---

## 💡 Quick Tips

1. **Use automated tests first**: `python run_tests.py`
2. **Follow the order**: Each step builds on previous steps
3. **Take screenshots**: Document working features
4. **Note issues**: Record any warnings or errors
5. **Test incrementally**: Don't skip steps
6. **Use mock router**: Real router not required for basic testing

---

## 📞 Support

If tests fail:
1. Check error messages in console
2. Run `python check_setup.py`
3. Review [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed help
4. Check [README.md](README.md) troubleshooting section

---

**Time Required**: 10-15 minutes for quick tests, 30-45 minutes for complete manual testing.

**Ready?** Start with Step 1! 🚀

