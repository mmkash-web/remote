# MikroTik + WireGuard VPN Setup Guide

Complete guide to connect MikroTik routers to your VPS via WireGuard VPN.

---

## 📋 Prerequisites

- MikroTik RouterOS 7.0+ (WireGuard built-in)
- VPS with WireGuard server installed
- VPS public IP address
- SSH access to both VPS and MikroTik

---

## Part 1: Setup WireGuard Server on VPS

### Step 1: Install WireGuard on VPS

```bash
# SSH to your VPS
ssh root@your-vps-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install WireGuard
sudo apt install wireguard -y

# Enable IP forwarding
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Step 2: Generate Server Keys

```bash
# Navigate to WireGuard directory
cd /etc/wireguard

# Generate server keys
wg genkey | tee server_private.key | wg pubkey > server_public.key

# Set permissions
chmod 600 server_private.key
```

### Step 3: Configure WireGuard Server

Create `/etc/wireguard/wg0.conf`:

```bash
sudo nano /etc/wireguard/wg0.conf
```

Add this configuration:

```ini
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = <PASTE_SERVER_PRIVATE_KEY_HERE>

# Save traffic rules
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Router 1 (MikroTik)
[Peer]
PublicKey = <ROUTER1_PUBLIC_KEY_WILL_BE_ADDED>
AllowedIPs = 10.10.0.2/32

# Router 2 (MikroTik)
[Peer]
PublicKey = <ROUTER2_PUBLIC_KEY_WILL_BE_ADDED>
AllowedIPs = 10.10.0.3/32

# Router 3 (MikroTik)
[Peer]
PublicKey = <ROUTER3_PUBLIC_KEY_WILL_BE_ADDED>
AllowedIPs = 10.10.0.4/32
```

**Important:** Replace `eth0` with your actual network interface:
```bash
ip a  # Find your interface (eth0, ens3, etc.)
```

### Step 4: Configure Firewall on VPS

```bash
# Allow WireGuard port
sudo ufw allow 51820/udp

# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### Step 5: Start WireGuard Server

```bash
# Start WireGuard
sudo wg-quick up wg0

# Enable on boot
sudo systemctl enable wg-quick@wg0

# Check status
sudo wg show
```

---

## Part 2: Configure MikroTik Router (Client)

### Step 1: Connect to MikroTik

Use Winbox or SSH:
```bash
ssh admin@192.168.88.1
```

### Step 2: Generate Router Keys

```bash
# Generate WireGuard keys on MikroTik
/interface/wireguard/add name=wg-vpn listen-port=51820

# Get the public key (save this - you'll need it for VPS config)
/interface/wireguard/print
```

Copy the **Public Key** from the output.

### Step 3: Configure WireGuard Interface

```bash
# Add WireGuard peer (connect to VPS server)
/interface/wireguard/peers/add \
    interface=wg-vpn \
    public-key="<PASTE_VPS_SERVER_PUBLIC_KEY>" \
    endpoint-address=YOUR_VPS_PUBLIC_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s

# Assign IP address to WireGuard interface
/ip/address/add address=10.10.0.2/24 interface=wg-vpn

# Add route (optional - for routing all traffic through VPN)
# /ip/route/add dst-address=0.0.0.0/0 gateway=10.10.0.1
```

### Step 4: Add Router's Public Key to VPS

Go back to your VPS and add the router's public key:

```bash
# On VPS, edit WireGuard config
sudo nano /etc/wireguard/wg0.conf

# Add/update the peer section with router's public key:
[Peer]
PublicKey = <PASTE_ROUTER_PUBLIC_KEY_HERE>
AllowedIPs = 10.10.0.2/32

# Restart WireGuard
sudo wg-quick down wg0
sudo wg-quick up wg0
```

---

## Part 3: Enable MikroTik API

```bash
# Enable API service
/ip/service/set api disabled=no address="" port=8728

# Or use API-SSL for security
/ip/service/set api-ssl disabled=no port=8729 certificate=auto
```

---

## ✅ Test Connection

### From VPS:

```bash
# Ping MikroTik router via VPN
ping 10.10.0.2

# Test API connection
telnet 10.10.0.2 8728

# Check WireGuard status
sudo wg show
```

### From MikroTik:

```bash
# Ping VPS via VPN
/ping 10.10.0.1

# Check WireGuard status
/interface/wireguard/print
/interface/wireguard/peers/print
```

---

## 📝 Quick Configuration Script for Additional Routers

### Router 2 Configuration:

```bash
# On Router 2 MikroTik
/interface/wireguard/add name=wg-vpn listen-port=51820
/interface/wireguard/print  # Copy public key

/interface/wireguard/peers/add \
    interface=wg-vpn \
    public-key="<VPS_SERVER_PUBLIC_KEY>" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s

/ip/address/add address=10.10.0.3/24 interface=wg-vpn
/ip/service/set api disabled=no port=8728
```

**Don't forget to add Router 2's public key to VPS `/etc/wireguard/wg0.conf`!**

---

## 🔧 Complete Setup for Multiple Routers

### VPS WireGuard Config (wg0.conf):

```ini
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]  # Router 1 - Nairobi
PublicKey = abcd1234...
AllowedIPs = 10.10.0.2/32

[Peer]  # Router 2 - Mombasa
PublicKey = efgh5678...
AllowedIPs = 10.10.0.3/32

[Peer]  # Router 3 - Kisumu
PublicKey = ijkl9012...
AllowedIPs = 10.10.0.4/32
```

---

## 🚨 Troubleshooting

### Connection not working?

**Check VPS firewall:**
```bash
sudo ufw status
sudo wg show
sudo journalctl -u wg-quick@wg0 -f
```

**Check MikroTik logs:**
```bash
/log/print where topics~"wireguard"
```

**Verify keys:**
```bash
# On VPS
sudo wg show

# On MikroTik
/interface/wireguard/print
/interface/wireguard/peers/print
```

### Can't ping across VPN?

```bash
# On VPS, check IP forwarding
cat /proc/sys/net/ipv4/ip_forward  # Should output: 1

# Check iptables rules
sudo iptables -L -n -v
```

### API connection fails?

```bash
# On MikroTik, verify API service
/ip/service/print

# Test from VPS
telnet 10.10.0.2 8728
```

---

## 📊 Network Diagram

```
┌─────────────────────────────────────┐
│  VPS (Your Django App)              │
│  Public IP: XX.XX.XX.XX             │
│  VPN IP: 10.10.0.1                  │
│  WireGuard Server (port 51820)     │
└───────────────┬─────────────────────┘
                │
                │ WireGuard VPN Tunnel
                │
        ┌───────┴───────┬─────────────┐
        │               │             │
┌───────▼──────┐ ┌──────▼─────┐ ┌────▼──────┐
│ Router 1     │ │ Router 2   │ │ Router 3  │
│ 10.10.0.2    │ │ 10.10.0.3  │ │ 10.10.0.4 │
│ Nairobi      │ │ Mombasa    │ │ Kisumu    │
└──────────────┘ └────────────┘ └───────────┘
```

---

## ✅ Success Checklist

- [ ] WireGuard installed on VPS
- [ ] Server keys generated
- [ ] wg0.conf configured
- [ ] Firewall rules added
- [ ] WireGuard server started
- [ ] MikroTik WireGuard interface created
- [ ] Router keys generated
- [ ] Peer configured on MikroTik
- [ ] Router's public key added to VPS
- [ ] VPN IP assigned to router
- [ ] Can ping VPS from router
- [ ] Can ping router from VPS
- [ ] API enabled on MikroTik
- [ ] API accessible via VPN IP

---

**Your MikroTik routers are now connected via WireGuard VPN!** 🎉

