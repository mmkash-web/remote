# MikroTik + Tailscale VPN Setup Guide

Complete guide to connect your MikroTik routers to Tailscale VPN mesh network.

---

## 📋 Prerequisites

- MikroTik RouterOS 7.6+ (for container support)
- Tailscale account (free): https://tailscale.com/
- SSH or Winbox access to router
- At least 128MB free disk space on router

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Enable Container Support on MikroTik

Connect to your MikroTik via SSH or Winbox terminal:

```bash
# Enable container feature
/system/device-mode/update container=yes

# Router will reboot - wait 2 minutes
```

After reboot, continue:

```bash
# Create a bridge for containers (if not exists)
/interface/bridge/add name=docker

# Add veth interface for container
/interface/veth/add name=veth1 address=172.17.0.2/24 gateway=172.17.0.1

# Add veth to bridge
/interface/bridge/port add bridge=docker interface=veth1

# Configure IP for bridge
/ip/address/add address=172.17.0.1/24 interface=docker

# Configure NAT for container internet access
/ip/firewall/nat/add chain=srcnat action=masquerade src-address=172.17.0.0/24

# Enable DNS for containers
/ip/dns/set allow-remote-requests=yes
```

### Step 2: Get Tailscale Auth Key

1. Go to https://login.tailscale.com/admin/settings/keys
2. Click **"Generate auth key"**
3. Check these options:
   - ✅ **Reusable**
   - ✅ **Ephemeral** (optional)
   - ✅ **Preauthorized**
4. Copy the key: `tskey-auth-xxxxxxxxxxxxxxxxxxxxx`

### Step 3: Install Tailscale Container on MikroTik

**Option A: Using Tailscale Official Image (Recommended)**

```bash
# Download Tailscale container image
/container/add remote-image=tailscale/tailscale:stable interface=veth1 \
    root-dir=disk1/tailscale logging=yes

# Set Tailscale auth key as environment variable
/container/envs/add name=tailscale_env key=TS_AUTHKEY value="tskey-auth-YOUR-KEY-HERE"
/container/envs/add name=tailscale_env key=TS_STATE_DIR value="/var/lib/tailscale"
/container/envs/add name=tailscale_env key=TS_USERSPACE value="true"
/container/envs/add name=tailscale_env key=TS_ACCEPT_DNS value="false"

# Assign environment to container
/container/set 0 envlist=tailscale_env

# Start the container
/container/start 0
```

**Option B: Manual Script Method (For older RouterOS)**

If your RouterOS doesn't support containers, use this script:

```bash
# Download and install Tailscale package
/tool fetch url=https://pkgs.tailscale.com/stable/tailscale_latest_mips.tgz

# Extract and install (manual process)
# Follow: https://tailscale.com/kb/1019/subnets/
```

---

## ✅ Verify Connection

### Check Container Status

```bash
# View container status
/container/print

# View container logs
/container/shell 0

# Inside container, check Tailscale status
tailscale status
```

### Get Router's Tailscale IP

```bash
# Check Tailscale IP address assigned to router
tailscale ip -4
```

Example output: `100.64.0.2`

### Test Connectivity

From your Scalingo app or another device on Tailscale network:

```bash
# Ping the router's Tailscale IP
ping 100.64.0.2

# Test MikroTik API connection
telnet 100.64.0.2 8728
```

---

## 🔧 Configure Each Router

Repeat the above steps for each MikroTik router. Each will get a unique Tailscale IP:

- **Router 1**: 100.64.0.2
- **Router 2**: 100.64.0.3
- **Router 3**: 100.64.0.4
- **Scalingo App**: 100.64.0.1

---

## 🌐 Access from Scalingo

In your Django app on Scalingo, use the Tailscale IPs:

```python
# routers/models.py
# When adding a router, use Tailscale IP:
# VPN IP: 100.64.0.2
# API Port: 8728
```

---

## 🔒 Enable MikroTik API

Don't forget to enable API service on each router:

```bash
# Enable API
/ip/service/set api address="" disabled=no port=8728

# Or enable API-SSL for security
/ip/service/set api-ssl address="" disabled=no port=8729 certificate=auto
```

---

## 📱 Alternative: Tailscale Without Containers

If your MikroTik doesn't support containers, use **EoIP + Tailscale on a tiny device**:

### Setup Raspberry Pi as Bridge:

```
MikroTik ←→ EoIP Tunnel ←→ Raspberry Pi ←→ Tailscale
```

**On Raspberry Pi:**
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Enable IP forwarding
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Start Tailscale
sudo tailscale up
```

**On MikroTik:**
```bash
# Create EoIP tunnel to Raspberry Pi
/interface/eoip/add name=eoip-tailscale remote-address=RASPBERRY_PI_LAN_IP tunnel-id=1

# Add IP address
/ip/address/add address=10.10.0.2/24 interface=eoip-tailscale

# Add route to Tailscale network via Raspberry Pi
/ip/route/add dst-address=100.64.0.0/10 gateway=RASPBERRY_PI_IP
```

---

## 🚨 Troubleshooting

### Container won't start
```bash
# Check if device-mode is enabled
/system/device-mode/print

# Verify disk space
/disk/print

# Check container logs
/log/print where topics~"container"
```

### Can't connect to Tailscale
```bash
# Restart container
/container/stop 0
/container/start 0

# Regenerate auth key if expired
# Get new key from Tailscale dashboard
```

### API connection fails
```bash
# Verify API is enabled
/ip/service/print

# Check firewall rules
/ip/firewall/filter/print

# Test local API access
/tool/api-test
```

---

## 📊 Monitoring

### View Tailscale Network

Visit: https://login.tailscale.com/admin/machines

You'll see all connected devices:
- ✅ mikrotikvpn-scalingo (Scalingo app)
- ✅ router1-mikrotik
- ✅ router2-mikrotik
- ✅ router3-mikrotik

---

## 💡 Tips

1. **Name Your Routers**: Set hostname for easy identification
   ```bash
   /system/identity/set name=router1-nairobi
   ```

2. **Keep Containers Updated**:
   ```bash
   /container/stop 0
   /container/remove 0
   # Re-download latest image
   /container/add remote-image=tailscale/tailscale:stable ...
   ```

3. **Backup Configuration**:
   ```bash
   /export file=backup-tailscale-config
   ```

4. **Monitor Logs**:
   ```bash
   /log/print where topics~"container"
   ```

---

## ✅ Success Checklist

- [ ] Container mode enabled on MikroTik
- [ ] Tailscale auth key obtained
- [ ] Container downloaded and started
- [ ] Router appears in Tailscale dashboard
- [ ] Tailscale IP assigned (100.64.0.x)
- [ ] API service enabled (port 8728)
- [ ] Can ping router from Scalingo app
- [ ] Can connect to MikroTik API via Tailscale IP
- [ ] Router added to Django billing system

---

**Your routers are now connected via Tailscale VPN!** 🎉

