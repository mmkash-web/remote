# MikroTik VPN Configuration Scripts

Ready-to-use configuration scripts for connecting MikroTik routers to your billing system via VPN.

---

## 📁 Files Included

- `router1-l2tp.rsc` - L2TP/IPSec VPN configuration (easiest)
- `router1-wireguard.rsc` - WireGuard VPN configuration (fastest)
- `router-template.rsc` - Template for additional routers

---

## 🚀 Quick Start

### Method 1: L2TP (Recommended for Beginners)

**Step 1:** Edit `router1-l2tp.rsc`

Replace these values:
```
YOUR_VPS_IP → your actual VPS IP (e.g., 203.0.113.45)
Router1Pass123 → your chosen password
YourStrongPSKPassword123 → your IPSec pre-shared key
```

**Step 2:** Upload to MikroTik

Using Winbox:
1. Click **Files** on left menu
2. Drag and drop `router1-l2tp.rsc` into Files window
3. Wait for upload to complete

Or using FTP:
```bash
ftp 192.168.88.1
# Login with admin credentials
put router1-l2tp.rsc
```

**Step 3:** Import Configuration

Open MikroTik Terminal (Winbox → New Terminal) and run:
```
/import file=router1-l2tp.rsc
```

**Step 4:** Verify Connection

```
/interface l2tp-client monitor 0
/ping 10.10.0.1
```

---

### Method 2: WireGuard (Recommended for Speed)

**Step 1:** Edit `router1-wireguard.rsc`

Replace these values:
```
YOUR_VPS_IP → your VPS public IP
REPLACE_WITH_VPS_PUBLIC_KEY → VPS WireGuard public key
```

**Step 2:** Upload and Import

```bash
# Upload file to MikroTik
# Then in MikroTik terminal:
/import file=router1-wireguard.rsc
```

**Step 3:** Copy Router's Public Key

The script will display the router's public key. Copy it!

**Step 4:** Add Key to VPS

On your VPS, edit `/etc/wireguard/wg0.conf`:
```bash
sudo nano /etc/wireguard/wg0.conf

# Add:
[Peer]
PublicKey = <PASTE_ROUTER_PUBLIC_KEY>
AllowedIPs = 10.10.0.2/32

# Restart WireGuard
sudo wg-quick down wg0
sudo wg-quick up wg0
```

**Step 5:** Verify Connection

```
/ping 10.10.0.1
/interface wireguard print
```

---

## 🔧 Configuring Additional Routers

### For Router 2:

1. Copy `router1-l2tp.rsc` to `router2-l2tp.rsc`
2. Change these values:
```
name="Router1-Billing" → name="Router2-Billing"
user=router1 → user=router2
address=10.10.0.2/24 → address=10.10.0.3/24
```
3. Import to Router 2

### For Router 3:

Same process, use:
- `user=router3`
- `address=10.10.0.4/24`

---

## 📝 Manual Configuration (No Script)

### L2TP Setup Commands:

```bash
# Create L2TP client
/interface l2tp-client add \
    name=vpn-billing \
    connect-to=YOUR_VPS_IP \
    user=router1 \
    password=YOUR_PASSWORD \
    use-ipsec=yes \
    ipsec-secret=YOUR_PSK \
    disabled=no

# Enable API
/ip service set api disabled=no port=8728

# Check status
/interface l2tp-client monitor 0
```

### WireGuard Setup Commands:

```bash
# Create interface
/interface wireguard add name=wg-vpn listen-port=51820

# Get public key
/interface wireguard print

# Add peer
/interface wireguard peers add \
    interface=wg-vpn \
    public-key="VPS_PUBLIC_KEY" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s

# Add IP
/ip address add address=10.10.0.2/24 interface=wg-vpn

# Enable API
/ip service set api disabled=no port=8728
```

---

## ✅ Post-Configuration Checklist

After importing the configuration:

- [ ] VPN interface is running
- [ ] VPN IP is assigned (10.10.0.x)
- [ ] Can ping VPS (10.10.0.1)
- [ ] API service is enabled (port 8728)
- [ ] Firewall allows API from VPN
- [ ] Router appears in billing system

---

## 🚨 Troubleshooting

### Connection fails?

```bash
# Check logs
/log print where topics~"l2tp,wireguard"

# Verify credentials
/interface l2tp-client print detail

# Test ping
/ping 10.10.0.1 count=5
```

### API not accessible?

```bash
# Check API service
/ip service print

# Check firewall
/ip firewall filter print where chain=input
```

### Need to reset?

```bash
# Remove L2TP
/interface l2tp-client remove [find name=vpn-billing]

# Remove WireGuard
/interface wireguard remove [find name=wg-vpn]

# Then re-import script
```

---

## 📊 What These Scripts Do

1. ✅ Set router identity (name)
2. ✅ Remove old VPN configurations
3. ✅ Create VPN connection (L2TP or WireGuard)
4. ✅ Assign VPN IP address
5. ✅ Enable MikroTik API (port 8728)
6. ✅ Configure firewall (allow API from VPN only)
7. ✅ Test connection and display status
8. ✅ Show diagnostics and next steps

---

## 🔐 Security Features

- API accessible only from VPN network
- Unnecessary services disabled
- Firewall rules applied
- Encrypted VPN tunnel
- Strong authentication

---

## 💡 Tips

1. **Test locally first** - Configure one router on your desk before deploying
2. **Label your routers** - Use descriptive names (location, branch)
3. **Keep credentials safe** - Store passwords securely
4. **Backup configs** - Run `/export file=backup` before changes
5. **Monitor logs** - Check `/log print` regularly

---

## 📞 Support

For detailed guides, see:
- `MIKROTIK_L2TP_SETUP.md` - Complete L2TP guide
- `MIKROTIK_WIREGUARD_SETUP.md` - Complete WireGuard guide
- `MIKROTIK_TAILSCALE_SETUP.md` - Tailscale guide (for Scalingo)

---

**Happy configuring!** 🚀

