# MikroTik VPN Quick Start Guide

**⚡ Get your routers connected in 15 minutes!**

---

## 🎯 Choose Your Method (30 seconds)

| I'm using... | Use this VPN |
|--------------|--------------|
| **Scalingo / Heroku** | → Tailscale |
| **Regular VPS** | → WireGuard or L2TP |
| **First time with VPN** | → L2TP |
| **Want fastest speed** | → WireGuard |

---

## 🚀 Method 1: Tailscale (Easiest for Scalingo)

### VPS/Server Side (5 minutes):

```bash
# Already using Scalingo? Just add this:
scalingo env-set TAILSCALE_AUTHKEY="tskey-auth-xxxxx"

# Get auth key from: https://login.tailscale.com/admin/settings/keys
```

### MikroTik Side (10 minutes):

1. **Enable containers** (RouterOS 7.6+ only):
```bash
/system/device-mode/update container=yes
# Router will reboot
```

2. **Setup network for container**:
```bash
/interface/bridge/add name=docker
/interface/veth/add name=veth1 address=172.17.0.2/24 gateway=172.17.0.1
/interface/bridge/port add bridge=docker interface=veth1
/ip/address/add address=172.17.0.1/24 interface=docker
/ip/firewall/nat/add chain=srcnat action=masquerade src-address=172.17.0.0/24
```

3. **Install Tailscale**:
```bash
/container/add remote-image=tailscale/tailscale:stable interface=veth1 \
    root-dir=disk1/tailscale logging=yes

/container/envs/add name=tailscale_env key=TS_AUTHKEY \
    value="tskey-auth-YOUR-KEY-HERE"

/container/set 0 envlist=tailscale_env
/container/start 0
```

4. **Enable API**:
```bash
/ip/service/set api disabled=no port=8728
```

5. **Get Tailscale IP**:
```bash
# Check in Tailscale dashboard: https://login.tailscale.com/admin/machines
# Your router will show as: 100.64.0.2 (example)
```

✅ **Done!** Use `100.64.0.2` as VPN IP in your Django app!

---

## 🔐 Method 2: WireGuard (Fastest)

### VPS Side (10 minutes):

```bash
# Install WireGuard
sudo apt update && sudo apt install wireguard -y

# Generate server keys
cd /etc/wireguard
wg genkey | tee server_private.key | wg pubkey > server_public.key

# Create config
sudo nano /etc/wireguard/wg0.conf
```

Add this (replace keys):
```ini
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = <ROUTER_PUBLIC_KEY_WILL_ADD_LATER>
AllowedIPs = 10.10.0.2/32
```

```bash
# Enable IP forwarding
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Open firewall
sudo ufw allow 51820/udp

# Start WireGuard
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0

# Get server public key
sudo cat /etc/wireguard/server_public.key
```

### MikroTik Side (5 minutes):

```bash
# Create WireGuard interface
/interface/wireguard/add name=wg-vpn listen-port=51820

# Get router public key (SAVE THIS!)
/interface/wireguard/print

# Add VPS as peer
/interface/wireguard/peers/add \
    interface=wg-vpn \
    public-key="<VPS_SERVER_PUBLIC_KEY>" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s

# Assign IP
/ip/address/add address=10.10.0.2/24 interface=wg-vpn

# Enable API
/ip/service/set api disabled=no port=8728

# Test
/ping 10.10.0.1
```

**Don't forget:** Add router's public key to VPS config and restart WireGuard!

✅ **Done!** Use `10.10.0.2` as VPN IP in Django!

---

## 🎯 Method 3: L2TP (Easiest for VPS)

### VPS Side (15 minutes):

```bash
# Install packages
sudo apt update
sudo apt install xl2tpd strongswan -y

# Configure IPSec
sudo nano /etc/ipsec.conf
```

Add:
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

```bash
# Set PSK
sudo nano /etc/ipsec.secrets
```

Add:
```
YOUR_VPS_IP %any : PSK "YourStrongPassword123"
```

```bash
# Configure L2TP
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

```bash
# Create user
sudo nano /etc/ppp/chap-secrets
```

Add:
```
router1 * Router1Pass123 10.10.0.2
```

```bash
# Enable IP forwarding
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Firewall
sudo ufw allow 500/udp
sudo ufw allow 4500/udp
sudo ufw allow 1701/udp

# Start services
sudo systemctl restart strongswan xl2tpd
sudo systemctl enable strongswan xl2tpd
```

### MikroTik Side (2 minutes):

```bash
/interface/l2tp-client/add \
    name=vpn-billing \
    connect-to=YOUR_VPS_IP \
    user=router1 \
    password=Router1Pass123 \
    use-ipsec=yes \
    ipsec-secret=YourStrongPassword123 \
    disabled=no

/ip/service/set api disabled=no port=8728

# Check status
/interface/l2tp-client/monitor 0
/ping 10.10.0.1
```

✅ **Done!** Use `10.10.0.2` as VPN IP in Django!

---

## 📁 Using Configuration Scripts

**Even Easier!** Just import our ready-made scripts:

1. Download from `mikrotik-configs/` folder
2. Edit VPS IP and passwords
3. Upload to MikroTik Files
4. Run: `/import file=router1-l2tp.rsc` (or wireguard)

**That's it!** Script does everything automatically!

---

## ✅ Verify Connection

### From Django/VPS:

```bash
# Ping router
ping 10.10.0.2

# Test API
telnet 10.10.0.2 8728

# If above works, add router in Django:
# - Name: Router1
# - VPN IP: 10.10.0.2
# - Port: 8728
```

### From MikroTik:

```bash
# Ping VPS
/ping 10.10.0.1

# Check VPN status
/interface print  # Look for vpn-billing or wg-vpn
/ip address print  # Should see 10.10.0.2
```

---

## 🆘 Troubleshooting (1 minute)

### Can't connect?

**Check these:**
```bash
# On VPS
sudo systemctl status <wireguard/xl2tpd>
sudo ufw status  # Firewall ports open?

# On MikroTik
/log print where topics~"vpn,wireguard,l2tp"
/ping YOUR_VPS_IP  # Internet connection OK?
```

### API not working?

```bash
# On MikroTik
/ip/service/print  # API enabled?
/ping 10.10.0.1    # VPN connected?
```

---

## 📊 Connection Matrix

| Setup | VPN IP Range | Your Router IP | VPS/Server IP |
|-------|--------------|----------------|---------------|
| **Tailscale** | 100.64.0.0/10 | 100.64.0.2 | 100.64.0.1 |
| **WireGuard** | 10.10.0.0/24 | 10.10.0.2 | 10.10.0.1 |
| **L2TP** | 10.10.0.0/24 | 10.10.0.2 | 10.10.0.1 |

---

## 🎯 Next Steps

After VPN is working:

1. **Add router in Django**:
   - Go to http://127.0.0.1:8000/routers/
   - Click "Add Router"
   - Enter VPN IP (10.10.0.2 or 100.64.0.2)
   - Port: 8728

2. **Create a profile**:
   - Go to Profiles → Add Profile
   - Set bandwidth limits and price

3. **Add a customer**:
   - Go to Customers → Add Customer
   - Select router and profile
   - Customer automatically created on MikroTik!

4. **Test payment flow**:
   - Use payment callback API
   - Customer gets enabled automatically

---

## 📚 Full Guides Available

For detailed step-by-step instructions:

- `MIKROTIK_TAILSCALE_SETUP.md` - Complete Tailscale guide
- `MIKROTIK_WIREGUARD_SETUP.md` - Complete WireGuard guide
- `MIKROTIK_L2TP_SETUP.md` - Complete L2TP guide
- `VPN_COMPARISON_GUIDE.md` - Which VPN to choose?
- `SCALINGO_DEPLOYMENT.md` - Deploy to Scalingo
- `mikrotik-configs/README.md` - Ready-to-use scripts

---

## 💡 Pro Tips

1. **Test locally first** - Configure one router on your desk before remote deployment
2. **Use scripts** - Import our `.rsc` files for instant configuration
3. **Label routers** - Give them meaningful names (location, branch)
4. **Backup configs** - Run `/export file=backup` before changes
5. **Monitor logs** - Check `/log print` regularly

---

**🎉 That's it! Your routers are now connected via secure VPN!**

**Having issues?** Check the detailed guides or troubleshooting sections!

**Want to add more routers?** Just repeat the "MikroTik Side" steps with different IPs (10.10.0.3, 10.10.0.4, etc.)

**Ready to deploy?** Follow `SCALINGO_DEPLOYMENT.md` for production setup!

---

**Happy billing!** 💰🚀

