# MikroTik WireGuard VPN Configuration
# For: remote.netbill.site
# Router 1 - VPN IP: 10.10.0.2
#
# BEFORE IMPORTING:
# 1. Replace YOUR_VPS_IP with actual IP (get from: https://remote.netbill.site or server)
# 2. Replace VPS_PUBLIC_KEY with actual key (get from VPS: sudo cat /etc/wireguard/server_public.key)
# 3. Upload this file to MikroTik Files
# 4. Import: /import file=router1-netbill.rsc

:log info "=========================================="
:log info "NetBill VPN Configuration - Router 1"
:log info "Domain: remote.netbill.site"
:log info "=========================================="

# Set router identity
/system identity set name="Router1-NetBill"

# Remove existing WireGuard interfaces
:log info "Removing old WireGuard interfaces..."
:foreach i in=[/interface wireguard find] do={
    /interface wireguard remove $i
}

# Create WireGuard interface
:log info "Creating WireGuard interface..."
/interface wireguard add \
    name=wg-netbill \
    listen-port=51820 \
    comment="VPN to remote.netbill.site"

# Get and display router's public key
:delay 2s
:local wgpubkey [/interface wireguard get [find name=wg-netbill] public-key]
:log info "Router WireGuard Public Key: $wgpubkey"

:put "=========================================="
:put "⚠️  IMPORTANT: Copy this Public Key!"
:put "=========================================="
:put $wgpubkey
:put "=========================================="
:put "Add this key to VPS:"
:put "1. SSH to VPS"
:put "2. sudo nano /etc/wireguard/wg0.conf"
:put "3. Add:"
:put "[Peer]"
:put "PublicKey = $wgpubkey"
:put "AllowedIPs = 10.10.0.2/32"
:put "4. sudo wg-quick down wg0 && sudo wg-quick up wg0"
:put "=========================================="

# Add peer (VPS server)
:log info "Adding WireGuard peer (remote.netbill.site)..."
/interface wireguard peers add \
    interface=wg-netbill \
    public-key="REPLACE_WITH_VPS_PUBLIC_KEY" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s \
    comment="remote.netbill.site VPS"

# Assign IP address
:log info "Assigning VPN IP address..."
/ip address add address=10.10.0.2/24 interface=wg-netbill comment="NetBill VPN IP"

# Enable MikroTik API
:log info "Enabling API service..."
/ip service set api disabled=no port=8728

# Configure firewall to allow API only from VPN
:log info "Configuring firewall..."

# Allow API from VPN network
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    src-address=10.10.0.0/24 \
    action=accept \
    comment="Allow API from NetBill VPN" \
    place-before=0

# Block API from everywhere else
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    action=drop \
    comment="Block API from outside"

# Disable unnecessary services for security
:log info "Disabling unnecessary services..."
/ip service set telnet disabled=yes
/ip service set ftp disabled=yes

# Wait for connection
:log info "Waiting for VPN connection (10 seconds)..."
:delay 10s

# Test connection
:log info "Testing VPN connection..."
:local pingresult [/ping 10.10.0.1 count=5]

:if ($pingresult > 0) do={
    :log info "✅ VPN Connected Successfully!"
    :put "=========================================="
    :put "✅ Configuration Complete!"
    :put "VPN Status: CONNECTED"
    :put "VPN IP: 10.10.0.2"
    :put "Gateway: 10.10.0.1"
    :put "Server: remote.netbill.site"
    :put "API Port: 8728"
    :put "=========================================="
    :put "✅ Ping to VPS successful ($pingresult/5)"
    :put "=========================================="
    :put ""
    :put "Next Steps:"
    :put "1. Login to https://remote.netbill.site/admin/"
    :put "2. Go to Routers → Add Router"
    :put "3. Enter:"
    :put "   - Name: Router1-NetBill"
    :put "   - VPN IP: 10.10.0.2"
    :put "   - Username: admin"
    :put "   - Password: (your router password)"
    :put "   - Port: 8728"
    :put "4. Click 'Test Connection'"
    :put "=========================================="
} else={
    :log warning "⚠️  Cannot ping VPS yet"
    :put "=========================================="
    :put "⚠️  Configuration applied, but cannot ping VPS"
    :put ""
    :put "Troubleshooting:"
    :put "  1. Verify VPS_PUBLIC_KEY is correct"
    :put "  2. Check YOUR_VPS_IP is correct"
    :put "  3. Make sure you added router's key to VPS"
    :put "  4. Check VPS firewall: sudo ufw status"
    :put "  5. Check WireGuard on VPS: sudo wg show"
    :put "=========================================="
}

:put ""
:put "Router Public Key (for VPS config):"
:put $wgpubkey
:put ""

:log info "Configuration script completed"

