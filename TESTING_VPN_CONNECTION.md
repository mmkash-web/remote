# VPN Connection Testing & Verification Guide

Complete guide to verify your MikroTik VPN setup is working correctly.

---

## ✅ 5-Step Verification Process

### Step 1: Verify VPN Connection (Router → VPS/Scalingo)
### Step 2: Test Network Connectivity (Ping Tests)
### Step 3: Test MikroTik API Access
### Step 4: Test Django Connection
### Step 5: End-to-End Test (Create User via Django)

---

## 📋 Step 1: Verify VPN Connection

### For Tailscale:

#### On MikroTik Router:

```bash
# Check container status
/container/print detail

# Should show:
# name: tailscale
# status: running
```

✅ **Success indicators:**
- Status: `running`
- No error messages

#### Check Tailscale Dashboard:

1. Go to: https://login.tailscale.com/admin/machines
2. You should see:
   - ✅ Your Scalingo app (mikrotikvpn-scalingo)
   - ✅ Your MikroTik router (Router1-Billing)
   - Both showing as **"Connected"** with green indicators

#### Get Router's Tailscale IP:

```bash
# In container shell
/container/shell 0

# Inside container
tailscale ip -4
# Output: 100.64.0.2

exit
```

✅ **Success:** Router has IP like `100.64.0.2`

---

### For WireGuard:

#### On MikroTik Router:

```bash
# Check WireGuard interface
/interface/wireguard/print detail

# Should show:
# name: wg-vpn
# listen-port: 51820
# public-key: xxxxx
# private-key: xxxxx
```

```bash
# Check peer status
/interface/wireguard/peers/print detail

# Should show:
# interface: wg-vpn
# endpoint-address: YOUR_VPS_IP
# endpoint-port: 51820
# current-endpoint-address: YOUR_VPS_IP:51820  ← IMPORTANT
# current-endpoint-port: 51820
# last-handshake: 2m30s ago  ← Should be recent!
```

✅ **Success indicators:**
- `current-endpoint-address` is filled
- `last-handshake` is recent (< 5 minutes)

#### On VPS:

```bash
# Check WireGuard status
sudo wg show

# Should show:
# interface: wg0
#   public key: xxxxx
#   private key: (hidden)
#   listening port: 51820
#
# peer: <ROUTER_PUBLIC_KEY>
#   endpoint: <ROUTER_PUBLIC_IP>:51820
#   allowed ips: 10.10.0.2/32
#   latest handshake: 1 minute ago  ← Recent!
#   transfer: 2.50 MiB received, 1.80 MiB sent
```

✅ **Success indicators:**
- Peer is listed
- Latest handshake is recent
- Data transfer shows activity

---

### For L2TP:

#### On MikroTik Router:

```bash
# Check L2TP client status
/interface/l2tp-client/print detail

# Should show:
# name: vpn-billing
# connect-to: YOUR_VPS_IP
# user: router1
# running: yes  ← IMPORTANT!
```

```bash
# Monitor connection (real-time)
/interface/l2tp-client/monitor 0

# Should show:
# status: "connected"
# uptime: 5m30s
# encoding: MPPE128 stateless
# local-address: 10.10.0.2
# remote-address: 10.10.0.1
```

✅ **Success indicators:**
- `running: yes`
- `status: connected`
- `local-address` is assigned (10.10.0.2)

#### On VPS:

```bash
# Check connected L2TP clients
sudo tail -f /var/log/syslog | grep xl2tpd

# Should show recent connection logs:
# xl2tpd[xxxx]: Connection established to XX.XX.XX.XX
# xl2tpd[xxxx]: router1 connected

# Check active connections
ps aux | grep xl2tpd
```

✅ **Success:** Logs show successful connection

---

## 📡 Step 2: Test Network Connectivity

### Test 1: Ping from Router to Server

#### On MikroTik:

**For Tailscale:**
```bash
/ping 100.64.0.1 count=10

# Expected output:
# 100.64.0.1 64 byte ping: ttl=64 time=15 ms
# 100.64.0.1 64 byte ping: ttl=64 time=12 ms
# 100.64.0.1 64 byte ping: ttl=64 time=14 ms
# ...
# 10 packets transmitted, 10 packets received, 0% packet loss
```

**For WireGuard/L2TP:**
```bash
/ping 10.10.0.1 count=10

# Expected output:
# 10.10.0.1 64 byte ping: ttl=64 time=25 ms
# 10.10.0.1 64 byte ping: ttl=64 time=22 ms
# ...
# 10 packets transmitted, 10 packets received, 0% packet loss
```

✅ **Success:**
- 0% packet loss
- Ping time < 100ms (usually 10-50ms)

❌ **Failure:**
- "timeout" messages
- 100% packet loss
- → Check VPN configuration

---

### Test 2: Ping from Server to Router

#### On VPS:

**For WireGuard/L2TP:**
```bash
ping 10.10.0.2 -c 10

# Expected output:
# PING 10.10.0.2 (10.10.0.2) 56(84) bytes of data.
# 64 bytes from 10.10.0.2: icmp_seq=1 ttl=64 time=24.5 ms
# 64 bytes from 10.10.0.2: icmp_seq=2 ttl=64 time=22.1 ms
# ...
# 10 packets transmitted, 10 received, 0% packet loss
```

#### On Scalingo (with Tailscale):

```bash
# SSH to your Scalingo app
scalingo run bash

# Then ping router
ping 100.64.0.2 -c 5

# Expected: 0% packet loss
```

✅ **Success:** 0% packet loss, ping time < 100ms

---

## 🔌 Step 3: Test MikroTik API Access

### Test from VPS/Scalingo:

#### Method A: Using Telnet (Quick Test)

```bash
# Test if API port is reachable
telnet 10.10.0.2 8728

# Expected output:
# Trying 10.10.0.2...
# Connected to 10.10.0.2.
# Escape character is '^]'.

# Press Ctrl+] then type 'quit' to exit
```

✅ **Success:** "Connected to 10.10.0.2"
❌ **Failure:** "Connection refused" or "Connection timed out"

---

#### Method B: Using Python (Detailed Test)

Create test file `test_api.py`:

```python
#!/usr/bin/env python3
"""
Test MikroTik API Connection
"""
import sys

try:
    from librouteros import connect
    from librouteros.query import Key
except ImportError:
    print("❌ Error: librouteros not installed")
    print("Run: pip install librouteros")
    sys.exit(1)

# Configuration
ROUTER_IP = "10.10.0.2"  # Or 100.64.0.2 for Tailscale
ROUTER_PORT = 8728
ROUTER_USER = "admin"
ROUTER_PASS = "your-password"

print("=" * 50)
print("MikroTik API Connection Test")
print("=" * 50)
print(f"Testing connection to: {ROUTER_IP}:{ROUTER_PORT}")
print()

try:
    # Attempt connection
    print("→ Connecting to router...")
    api = connect(
        username=ROUTER_USER,
        password=ROUTER_PASS,
        host=ROUTER_IP,
        port=ROUTER_PORT,
        timeout=10
    )
    print("✅ Connected successfully!")
    print()
    
    # Test 1: Get router identity
    print("→ Getting router identity...")
    identity = list(api('/system/identity/print'))
    router_name = identity[0].get('name', 'Unknown')
    print(f"✅ Router Name: {router_name}")
    print()
    
    # Test 2: Get RouterOS version
    print("→ Getting RouterOS version...")
    resource = list(api('/system/resource/print'))
    version = resource[0].get('version', 'Unknown')
    board = resource[0].get('board-name', 'Unknown')
    print(f"✅ RouterOS Version: {version}")
    print(f"✅ Board: {board}")
    print()
    
    # Test 3: Count existing users
    print("→ Counting PPP secrets (users)...")
    secrets = list(api('/ppp/secret/print'))
    user_count = len(secrets)
    print(f"✅ Current Users: {user_count}")
    print()
    
    # Test 4: Get interfaces
    print("→ Getting interfaces...")
    interfaces = list(api('/interface/print'))
    print(f"✅ Interfaces found: {len(interfaces)}")
    for iface in interfaces[:3]:  # Show first 3
        name = iface.get('name', 'Unknown')
        itype = iface.get('type', 'Unknown')
        print(f"   - {name} ({itype})")
    print()
    
    # Close connection
    api.close()
    
    print("=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print()
    print("Your MikroTik API is working correctly!")
    print("You can now use this router in your Django app.")
    
except Exception as e:
    print("=" * 50)
    print("❌ CONNECTION FAILED!")
    print("=" * 50)
    print(f"Error: {str(e)}")
    print()
    print("Troubleshooting:")
    print("1. Check VPN is connected (ping test)")
    print("2. Verify API is enabled: /ip service print")
    print("3. Check username/password are correct")
    print("4. Verify router IP is correct")
    print("5. Check firewall rules on router")
    sys.exit(1)
```

Run the test:

```bash
# On VPS
python3 test_api.py

# On Scalingo
scalingo run python test_api.py
```

✅ **Expected output:**
```
==================================================
MikroTik API Connection Test
==================================================
Testing connection to: 10.10.0.2:8728

→ Connecting to router...
✅ Connected successfully!

→ Getting router identity...
✅ Router Name: Router1-Billing

→ Getting RouterOS version...
✅ RouterOS Version: 7.11.2
✅ Board: RB3011

→ Counting PPP secrets (users)...
✅ Current Users: 0

→ Getting interfaces...
✅ Interfaces found: 12
   - ether1 (ether)
   - ether2 (ether)
   - vpn-billing (l2tp-out)

==================================================
🎉 ALL TESTS PASSED!
==================================================

Your MikroTik API is working correctly!
You can now use this router in your Django app.
```

---

## 🌐 Step 4: Test Django Connection

### Test from Django Shell:

```bash
# On local machine
python manage.py shell

# On Scalingo
scalingo run python manage.py shell
```

In Django shell:

```python
from routers.models import Router
from routers.services.mikrotik_api import MikroTikAPI

# Create a test router (or get existing one)
router = Router.objects.create(
    name="Test Router 1",
    vpn_ip="10.10.0.2",  # Or 100.64.0.2 for Tailscale
    api_username="admin",
    api_password="your-password",
    api_port=8728,
    is_active=True
)

# Test connection
api = MikroTikAPI(router)
result = api.test_connection()

print("Connection Result:", result)

# Get router info
if result['success']:
    identity = api.get_router_identity()
    print("Router Name:", identity.get('name'))
    
    users = api.list_users()
    print("Total Users:", len(users))
    
    print("\n✅ Django can communicate with MikroTik!")
else:
    print("\n❌ Connection failed:", result.get('error'))

# Clean up test
router.delete()
```

✅ **Expected output:**
```
Connection Result: {'success': True, 'message': 'Connected successfully'}
Router Name: Router1-Billing
Total Users: 0

✅ Django can communicate with MikroTik!
```

---

## 🔄 Step 5: End-to-End Test

### Complete workflow test:

#### 1. Add Router via Django UI:

```
1. Go to: http://127.0.0.1:8000/routers/create/
   (or https://your-app.osc-fr1.scalingo.io/routers/create/)

2. Fill in:
   - Name: Test Router 1
   - VPN IP: 10.10.0.2 (or 100.64.0.2)
   - Username: admin
   - Password: your-router-password
   - API Port: 8728

3. Click "Test Connection" button

4. Expected: ✅ "Connection successful!"
```

✅ **Success:** Green success message appears

---

#### 2. Create a Profile:

```
1. Go to: /profiles/create/
2. Fill in:
   - Name: Test 1GB Daily
   - Speed: 5M/5M
   - Duration: 1 day
   - Price: 50

3. Save
```

---

#### 3. Create a Test Customer:

```
1. Go to: /customers/create/
2. Fill in:
   - Username: testuser1
   - Password: test123
   - Full Name: Test User
   - Router: Test Router 1
   - Profile: Test 1GB Daily

3. Save
```

✅ **Expected:** User is created in Django AND on MikroTik router!

---

#### 4. Verify User on MikroTik:

On MikroTik terminal:

```bash
/ppp/secret/print

# Should show:
# name="testuser1" password="test123" service=any ...
```

✅ **Success:** User appears in PPP secrets!

---

#### 5. Enable Customer and Test:

```
1. In Django, go to customer detail page
2. Click "Enable" button
3. Expected: Customer status changes to "Active"
```

On MikroTik:

```bash
/ppp/secret/print where name=testuser1

# Should show: disabled=no
```

✅ **Success:** User is enabled on router!

---

## 🔍 Diagnostic Commands Reference

### Quick Status Check Script

Save as `check_vpn_status.sh`:

```bash
#!/bin/bash
echo "========================================"
echo "VPN Connection Status Check"
echo "========================================"
echo ""

# Check 1: Ping test
echo "1. Testing network connectivity..."
if ping -c 3 -W 2 10.10.0.2 > /dev/null 2>&1; then
    echo "   ✅ Ping successful"
else
    echo "   ❌ Ping failed"
fi
echo ""

# Check 2: API port test
echo "2. Testing API port (8728)..."
if timeout 3 bash -c "echo > /dev/tcp/10.10.0.2/8728" 2>/dev/null; then
    echo "   ✅ API port reachable"
else
    echo "   ❌ API port not reachable"
fi
echo ""

# Check 3: WireGuard status (if applicable)
echo "3. Checking WireGuard..."
if sudo wg show | grep -q "peer"; then
    echo "   ✅ WireGuard peers connected"
    sudo wg show | grep "latest handshake"
else
    echo "   ⚠️  No WireGuard peers (or not using WireGuard)"
fi
echo ""

echo "========================================"
echo "Status check complete!"
echo "========================================"
```

Run it:
```bash
chmod +x check_vpn_status.sh
./check_vpn_status.sh
```

---

## 📊 Connection Status Matrix

| Test | What it Checks | Success Indicator | Failure Action |
|------|---------------|-------------------|----------------|
| **VPN Status** | VPN connection active | Interface running | Restart VPN service |
| **Ping Test** | Network reachability | 0% packet loss | Check VPN config |
| **Telnet Test** | API port open | "Connected" message | Enable API service |
| **API Login** | Authentication works | Gets router info | Check credentials |
| **Django Test** | Full integration | Creates user on router | Check firewall |

---

## ✅ Complete Success Checklist

Print this and check off as you verify:

```
VPN CONNECTION:
□ VPN interface shows "running" status
□ VPN IP address is assigned (10.10.0.x or 100.64.0.x)
□ Last handshake/connection time is recent

NETWORK TESTS:
□ Can ping from router to server (0% loss)
□ Can ping from server to router (0% loss)
□ Ping time is reasonable (< 100ms)

API TESTS:
□ Telnet to port 8728 succeeds
□ Python API test script passes all checks
□ Can read router identity via API
□ Can list interfaces via API

DJANGO INTEGRATION:
□ Can add router in Django admin
□ "Test Connection" button works
□ Can create profile
□ Can create customer
□ Customer appears on MikroTik router
□ Can enable/disable customer
□ Changes sync to router instantly

END-TO-END:
□ Create test user via Django
□ User exists on MikroTik (/ppp/secret/print)
□ User can connect to hotspot
□ Django shows user as "Active"
□ Can extend user expiry
□ Payment callback works
```

---

## 🚨 Troubleshooting Common Issues

### Issue 1: Ping works, but API doesn't

**Cause:** API service not enabled or firewall blocking

**Solution:**
```bash
# On MikroTik
/ip/service/set api disabled=no port=8728
/ip/firewall/filter/print where chain=input
```

---

### Issue 2: API works locally, not from Django

**Cause:** Wrong VPN IP in Django configuration

**Solution:**
- Check actual VPN IP: `/ip/address/print`
- Update router VPN IP in Django
- Use VPN IP, not public IP!

---

### Issue 3: VPN connects but drops frequently

**Cause:** Keepalive not configured

**Solution:**
```bash
# For WireGuard
/interface/wireguard/peers/set 0 persistent-keepalive=25s

# For L2TP
/interface/l2tp-client/set 0 keepalive-timeout=60
```

---

### Issue 4: Can't reach router from Scalingo

**Cause:** Tailscale not configured properly

**Solution:**
```bash
# Check Tailscale is in buildpacks
cat .buildpacks

# Verify auth key is set
scalingo env | grep TAILSCALE

# Check Scalingo has Tailscale IP
scalingo run tailscale ip -4
```

---

## 📞 Quick Verification Commands

### One-Line Test Commands:

```bash
# Test VPN + API in one command
ping -c 1 10.10.0.2 && echo "VPN OK" && timeout 2 bash -c "echo > /dev/tcp/10.10.0.2/8728" && echo "API OK"

# WireGuard status
sudo wg show | grep -E "interface|peer|handshake"

# L2TP status
sudo tail -20 /var/log/syslog | grep xl2tpd

# Django API test
echo "from routers.services.mikrotik_api import MikroTikAPI; from routers.models import Router; r=Router.objects.first(); print(MikroTikAPI(r).test_connection())" | python manage.py shell
```

---

## 🎉 Final Verification

**Everything is working if:**

1. ✅ You can ping router from server
2. ✅ Telnet to API port succeeds
3. ✅ Python API test passes all checks
4. ✅ Django "Test Connection" button shows success
5. ✅ Creating a customer in Django creates user on MikroTik
6. ✅ `/ppp/secret/print` on MikroTik shows the user

**If all above pass: 🎊 Your setup is complete and working!**

---

**Save this guide and use it every time you add a new router!** 📋✅

