# MikroTik WireGuard VPN Configuration
# For: remote.netbill.site
# Router 2 - VPN IP: 10.10.0.3
#
# BEFORE IMPORTING:
# 1. Replace YOUR_VPS_IP with actual IP
# 2. Replace VPS_PUBLIC_KEY with actual key
# 3. Upload to MikroTik and import

:log info "=========================================="
:log info "NetBill VPN Configuration - Router 2"
:log info "Domain: remote.netbill.site"
:log info "=========================================="

/system identity set name="Router2-NetBill"

:log info "Removing old WireGuard interfaces..."
:foreach i in=[/interface wireguard find] do={
    /interface wireguard remove $i
}

:log info "Creating WireGuard interface..."
/interface wireguard add \
    name=wg-netbill \
    listen-port=51820 \
    comment="VPN to remote.netbill.site"

:delay 2s
:local wgpubkey [/interface wireguard get [find name=wg-netbill] public-key]

:put "=========================================="
:put "Router 2 Public Key:"
:put $wgpubkey
:put "=========================================="

:log info "Adding WireGuard peer..."
/interface wireguard peers add \
    interface=wg-netbill \
    public-key="REPLACE_WITH_VPS_PUBLIC_KEY" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s \
    comment="remote.netbill.site VPS"

:log info "Assigning VPN IP..."
/ip address add address=10.10.0.3/24 interface=wg-netbill comment="NetBill VPN IP"

:log info "Enabling API..."
/ip service set api disabled=no port=8728

:log info "Configuring firewall..."
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    src-address=10.10.0.0/24 \
    action=accept \
    comment="Allow API from NetBill VPN" \
    place-before=0

/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=8728 \
    action=drop \
    comment="Block API from outside"

/ip service set telnet disabled=yes
/ip service set ftp disabled=yes

:delay 10s

:local pingresult [/ping 10.10.0.1 count=5]
:if ($pingresult > 0) do={
    :put "✅ Router 2 Connected! VPN IP: 10.10.0.3"
} else={
    :put "⚠️  Check VPS configuration"
}

:put ""
:put "Add to VPS: [Peer] PublicKey=$wgpubkey AllowedIPs=10.10.0.3/32"

