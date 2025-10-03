# MikroTik WireGuard VPN Configuration
# For: remote.netbill.site
# Router 3 - VPN IP: 10.10.0.4

:log info "NetBill VPN Configuration - Router 3"

/system identity set name="Router3-NetBill"

:foreach i in=[/interface wireguard find] do={
    /interface wireguard remove $i
}

/interface wireguard add \
    name=wg-netbill \
    listen-port=51820 \
    comment="VPN to remote.netbill.site"

:delay 2s
:local wgpubkey [/interface wireguard get [find name=wg-netbill] public-key]

:put "Router 3 Public Key: $wgpubkey"

/interface wireguard peers add \
    interface=wg-netbill \
    public-key="REPLACE_WITH_VPS_PUBLIC_KEY" \
    endpoint-address=YOUR_VPS_IP \
    endpoint-port=51820 \
    allowed-address=0.0.0.0/0 \
    persistent-keepalive=25s \
    comment="remote.netbill.site VPS"

/ip address add address=10.10.0.4/24 interface=wg-netbill comment="NetBill VPN IP"
/ip service set api disabled=no port=8728

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
    :put "✅ Router 3 Connected! VPN IP: 10.10.0.4"
}

:put "Add to VPS: [Peer] PublicKey=$wgpubkey AllowedIPs=10.10.0.4/32"

