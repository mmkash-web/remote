# MikroTik L2TP VPN Configuration Script
# Router 1 - Import this file to your MikroTik
# 
# BEFORE IMPORTING:
# 1. Replace YOUR_VPS_IP with your actual VPS public IP
# 2. Replace passwords with your actual credentials
# 3. Upload this file to MikroTik Files
# 4. Run: /import file=router1-l2tp.rsc

:log info "=========================================="
:log info "Starting MikroTik VPN Configuration"
:log info "Router: Router1"
:log info "=========================================="

# Set router identity
/system identity set name="Router1-Billing"

# Remove existing L2TP connections if any
:log info "Removing old L2TP connections..."
:foreach i in=[/interface l2tp-client find] do={
    /interface l2tp-client remove $i
}

# Configure L2TP VPN Client
:log info "Creating L2TP VPN connection..."
/interface l2tp-client add \
    name=vpn-billing \
    connect-to=YOUR_VPS_IP \
    user=router1 \
    password=Router1Pass123 \
    use-ipsec=yes \
    ipsec-secret=YourStrongPSKPassword123 \
    disabled=no \
    add-default-route=no \
    comment="VPN to Billing Server"

# Wait for connection to establish
:log info "Waiting for VPN connection (15 seconds)..."
:delay 15s

# Enable MikroTik API
:log info "Enabling API service..."
/ip service set api disabled=no port=8728

# Optional: Enable API-SSL for security
# /ip service set api-ssl disabled=no port=8729

# Disable unnecessary services (optional)
:log info "Disabling unnecessary services..."
/ip service set telnet disabled=yes
/ip service set ftp disabled=yes
/ip service set www disabled=no

# Add firewall rule to allow API from VPN only
:log info "Configuring firewall for API access..."
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    src-address=10.10.0.0/24 \
    action=accept \
    comment="Allow API from VPN" \
    place-before=0

/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    action=drop \
    comment="Block API from outside"

# Check VPN status
:log info "Checking VPN connection status..."
:if ([/interface l2tp-client get [find name=vpn-billing] running] = true) do={
    :local vpnip [/ip address get [find interface=vpn-billing] address]
    :log info "✅ VPN Connected Successfully!"
    :log info "VPN IP: $vpnip"
    :put "=========================================="
    :put "✅ Configuration Complete!"
    :put "VPN Status: CONNECTED"
    :put "VPN IP: $vpnip"
    :put "API Port: 8728"
    :put "=========================================="
} else={
    :log error "❌ VPN Connection FAILED!"
    :put "=========================================="
    :put "❌ VPN Connection Failed!"
    :put "Check:"
    :put "  1. VPS IP address correct"
    :put "  2. Username/password correct"
    :put "  3. IPSec PSK correct"
    :put "  4. VPS L2TP server running"
    :put "=========================================="
}

:log info "Configuration script completed"

