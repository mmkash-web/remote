# MikroTik WireGuard VPN Configuration Script
# Router 1 - Import this file to your MikroTik (RouterOS 7.0+)
# 
# BEFORE IMPORTING:
# 1. Replace YOUR_VPS_IP with your VPS public IP
# 2. Replace VPS_PUBLIC_KEY with your VPS WireGuard public key
# 3. After running, copy the router's public key to VPS config
# 4. Upload this file to MikroTik Files
# 5. Run: /import file=router1-wireguard.rsc

:log info "=========================================="
:log info "Starting WireGuard VPN Configuration"
:log info "Router: Router1"
:log info "=========================================="

# Set router identity
/system identity set name="Router1-Billing"

# Remove existing WireGuard interfaces
:log info "Removing old WireGuard interfaces..."
:foreach i in=[/interface wireguard find] do={
    /interface wireguard remove $i
}

# Create WireGuard interface
:log info "Creating WireGuard interface..."
/interface wireguard add \
    name=wg-vpn \
    listen-port=51820 \
    comment="VPN to Billing Server"

# Get and display the public key (IMPORTANT: Save this!)
:delay 2s
:local wgpubkey [/interface wireguard get [find name=wg-vpn] public-key]
:log info "Router WireGuard Public Key: $wgpubkey"
:put "=========================================="
:put "⚠️  IMPORTANT: Copy this Public Key!"
:put "=========================================="
:put $wgpubkey
:put "=========================================="
:put "Add this key to your VPS /etc/wireguard/wg0.conf"
:put "Then restart WireGuard on VPS"
:put "=========================================="

# Add peer (VPS server)
:log info "Adding WireGuard peer (VPS)..."
/interface wireguard peers add \
    interface=wg-vpn \
    public-key="REPLACE_WITH_VPS_PUBLIC_KEY" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s \
    comment="VPS Server"

# Assign IP address
:log info "Assigning VPN IP address..."
/ip address add address=10.10.0.2/24 interface=wg-vpn

# Enable MikroTik API
:log info "Enabling API service..."
/ip service set api disabled=no port=8728

# Add firewall rule to allow API from VPN only
:log info "Configuring firewall..."
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    in-interface=wg-vpn \
    action=accept \
    comment="Allow API from VPN" \
    place-before=0

/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    action=drop \
    comment="Block API from outside"

# Wait for connection
:log info "Waiting for VPN connection (10 seconds)..."
:delay 10s

# Test connection
:log info "Testing VPN connection..."
:local pingresult [/ping 10.10.0.1 count=3]
:if ($pingresult > 0) do={
    :log info "✅ VPN Connected Successfully!"
    :put "=========================================="
    :put "✅ Configuration Complete!"
    :put "VPN Status: CONNECTED"
    :put "VPN IP: 10.10.0.2"
    :put "Gateway: 10.10.0.1"
    :put "API Port: 8728"
    :put "=========================================="
    :put "✅ Ping to VPS successful ($pingresult/3)"
    :put "=========================================="
} else={
    :log warning "⚠️  Cannot ping VPS yet"
    :put "=========================================="
    :put "⚠️  Configuration applied, but cannot ping VPS"
    :put "Make sure you:"
    :put "  1. Added router's public key to VPS"
    :put "  2. Restarted WireGuard on VPS"
    :put "  3. VPS firewall allows port 51820/udp"
    :put "=========================================="
}

:put ""
:put "Router Public Key (add to VPS):"
:put $wgpubkey

:log info "Configuration script completed"

