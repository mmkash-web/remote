# MikroTik + L2TP/IPSec VPN Setup Guide

Easiest VPN setup - great for beginners!

---

## 📋 Prerequisites

- VPS with Ubuntu/Debian
- MikroTik RouterOS (any version)
- Root access to VPS
- Basic MikroTik knowledge

---

## Part 1: Setup L2TP Server on VPS

### Step 1: Install L2TP Server

```bash
# SSH to VPS
ssh root@your-vps-ip

# Install packages
sudo apt update
sudo apt install xl2tpd strongswan -y
```

### Step 2: Configure IPSec

Edit `/etc/ipsec.conf`:

```bash
sudo nano /etc/ipsec.conf
```

Add this configuration:

```ini
config setup
    nat_traversal=yes
    virtual_private=%v4:10.10.0.0/16

conn L2TP-PSK
    authby=secret
    pfs=no
    auto=add
    keyingtries=3
    rekey=no
    ikelifetime=8h
    keylife=1h
    type=transport
    left=%defaultroute
    leftprotoport=17/1701
    right=%any
    rightprotoport=17/%any
```

### Step 3: Configure IPSec Secrets

Edit `/etc/ipsec.secrets`:

```bash
sudo nano /etc/ipsec.secrets
```

Add:

```
# VPS IP and Pre-Shared Key
YOUR_VPS_IP %any : PSK "YourStrongPSKPassword123"
```

### Step 4: Configure L2TP

Edit `/etc/xl2tpd/xl2tpd.conf`:

```bash
sudo nano /etc/xl2tpd/xl2tpd.conf
```

Add:

```ini
[global]
listen-addr = YOUR_VPS_IP

[lns default]
ip range = 10.10.0.2-10.10.0.254
local ip = 10.10.0.1
require chap = yes
refuse pap = yes
require authentication = yes
name = l2tpd
pppoptfile = /etc/ppp/options.xl2tpd
length bit = yes
```

### Step 5: Configure PPP Options

Edit `/etc/ppp/options.xl2tpd`:

```bash
sudo nano /etc/ppp/options.xl2tpd
```

Add:

```
require-mschap-v2
ms-dns 8.8.8.8
ms-dns 8.8.4.4
auth
mtu 1410
mru 1410
nodefaultroute
debug
lock
proxyarp
connect-delay 5000
```

### Step 6: Create VPN Users

Edit `/etc/ppp/chap-secrets`:

```bash
sudo nano /etc/ppp/chap-secrets
```

Add users (format: username * password IP):

```
# Router credentials
router1 * Router1Pass123 10.10.0.2
router2 * Router2Pass456 10.10.0.3
router3 * Router3Pass789 10.10.0.4
```

### Step 7: Enable IP Forwarding

```bash
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Step 8: Configure Firewall

```bash
# Enable L2TP and IPSec ports
sudo ufw allow 500/udp
sudo ufw allow 4500/udp
sudo ufw allow 1701/udp

# Enable NAT
sudo iptables -t nat -A POSTROUTING -s 10.10.0.0/24 -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -s 10.10.0.0/24 -j ACCEPT

# Save rules
sudo apt install iptables-persistent -y
sudo netfilter-persistent save
```

### Step 9: Start Services

```bash
# Restart IPSec
sudo systemctl restart strongswan

# Restart L2TP
sudo systemctl restart xl2tpd

# Enable on boot
sudo systemctl enable strongswan
sudo systemctl enable xl2tpd

# Check status
sudo systemctl status strongswan
sudo systemctl status xl2tpd
```

---

## Part 2: Configure MikroTik Router

### Step 1: Create L2TP Client

Connect to MikroTik via Winbox or SSH:

```bash
# Add L2TP client interface
/interface/l2tp-client/add \
    name=l2tp-vpn \
    connect-to=YOUR_VPS_PUBLIC_IP \
    user=router1 \
    password=Router1Pass123 \
    disabled=no \
    use-ipsec=yes \
    ipsec-secret=YourStrongPSKPassword123 \
    add-default-route=no

# Wait a few seconds for connection
/interface/l2tp-client/print
```

### Step 2: Verify Connection

```bash
# Check L2TP status (should show "connected")
/interface/l2tp-client/monitor 0

# Check if IP is assigned (should be 10.10.0.2)
/ip/address/print where interface=l2tp-vpn

# Ping VPS
/ping 10.10.0.1
```

### Step 3: Enable MikroTik API

```bash
# Enable API
/ip/service/set api disabled=no port=8728

# For security, use API-SSL
/ip/service/set api-ssl disabled=no port=8729
```

---

## ✅ Test Connection

### From VPS:

```bash
# Check connected clients
sudo xl2tpd-control list

# Ping router
ping 10.10.0.2

# Test API
telnet 10.10.0.2 8728
```

### From MikroTik:

```bash
# Check L2TP status
/interface/l2tp-client/print detail

# Ping VPS
/ping 10.10.0.1 count=5

# Check routes
/ip/route/print where gateway=10.10.0.1
```

---

## 📝 Quick Configuration for Additional Routers

### Router 2 Setup:

```bash
# On Router 2
/interface/l2tp-client/add \
    name=l2tp-vpn \
    connect-to=YOUR_VPS_IP \
    user=router2 \
    password=Router2Pass456 \
    use-ipsec=yes \
    ipsec-secret=YourStrongPSKPassword123 \
    disabled=no

/ip/service/set api disabled=no port=8728
```

**Don't forget to add router2 credentials in VPS `/etc/ppp/chap-secrets`!**

---

## 🔧 Ready-to-Use MikroTik Script

Save this as `l2tp-setup.rsc` and import to MikroTik:

```
# L2TP VPN Client Configuration
# Replace YOUR_VPS_IP and credentials

:log info "Starting L2TP VPN Setup"

# Remove existing L2TP if any
:if ([/interface l2tp-client find name=l2tp-vpn] != "") do={
    /interface l2tp-client remove [find name=l2tp-vpn]
}

# Add L2TP client
/interface l2tp-client add \
    name=l2tp-vpn \
    connect-to=YOUR_VPS_PUBLIC_IP \
    user=router1 \
    password=Router1Pass123 \
    use-ipsec=yes \
    ipsec-secret=YourStrongPSKPassword123 \
    disabled=no \
    add-default-route=no \
    comment="VPN to Billing Server"

# Enable API
/ip service set api disabled=no port=8728

# Wait for connection
:delay 10s

# Check status
:if ([/interface l2tp-client get [find name=l2tp-vpn] running] = true) do={
    :log info "L2TP VPN Connected Successfully!"
    :put "✅ VPN Connected!"
} else={
    :log error "L2TP VPN Connection Failed!"
    :put "❌ VPN Failed! Check credentials."
}

:log info "L2TP VPN Setup Complete"
```

### Import script to MikroTik:

1. Upload `l2tp-setup.rsc` to MikroTik Files
2. Run: `/import file=l2tp-setup.rsc`

---

## 🚨 Troubleshooting

### L2TP won't connect?

**On VPS, check logs:**
```bash
sudo tail -f /var/log/syslog | grep xl2tpd
sudo tail -f /var/log/syslog | grep ipsec
```

**On MikroTik:**
```bash
/log print where topics~"l2tp"
/interface l2tp-client monitor 0
```

### IPSec fails?

```bash
# On VPS, check IPSec status
sudo ipsec status

# Restart IPSec
sudo systemctl restart strongswan

# On MikroTik, check IPSec policies
/ip ipsec policy print
```

### Can't connect to API?

```bash
# On MikroTik, verify service
/ip service print

# Check firewall
/ip firewall filter print where chain=input
```

---

## 📊 Network Diagram

```
┌──────────────────────────────────────┐
│  VPS (Django Billing System)        │
│  Public IP: XX.XX.XX.XX              │
│  VPN IP: 10.10.0.1                   │
│  L2TP Server (ports 500,1701,4500)  │
└───────────────┬──────────────────────┘
                │
                │ L2TP/IPSec VPN
                │
        ┌───────┴────────┬──────────────┐
        │                │              │
┌───────▼──────┐  ┌──────▼──────┐  ┌───▼────────┐
│ Router 1     │  │ Router 2    │  │ Router 3   │
│ 10.10.0.2    │  │ 10.10.0.3   │  │ 10.10.0.4  │
│ user:router1 │  │ user:router2│  │user:router3│
└──────────────┘  └─────────────┘  └────────────┘
```

---

## ✅ Success Checklist

- [ ] L2TP server installed on VPS
- [ ] IPSec configured
- [ ] User credentials added
- [ ] Firewall ports opened
- [ ] Services started and enabled
- [ ] L2TP client created on MikroTik
- [ ] IPSec enabled with PSK
- [ ] Connection established
- [ ] VPN IP assigned (10.10.0.x)
- [ ] Can ping VPS from router
- [ ] API enabled on MikroTik
- [ ] API accessible from VPS

---

## 💡 Advantages of L2TP

- ✅ Easy to setup
- ✅ Works on any RouterOS version
- ✅ Built-in encryption (IPSec)
- ✅ Reliable connection
- ✅ Username/password authentication
- ✅ No container support needed

---

**Your MikroTik routers are now connected via L2TP/IPSec VPN!** 🎉

