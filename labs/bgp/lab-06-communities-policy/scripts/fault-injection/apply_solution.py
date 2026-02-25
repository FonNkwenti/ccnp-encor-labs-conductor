"""
BGP Lab 06 — Apply Full Solution
Restores all 5 routers to the complete solved state for Lab 06.
Run this after any fault injection scenario to reset the lab.
"""
from netmiko import ConnectHandler
import time


def connect(port):
    return ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=port,
        username="",
        password="",
        secret="",
    )


# ── R1 ──────────────────────────────────────────────────────────────────────
r1_commands = [
    # Community-list
    "no ip community-list standard CUSTOMER-ROUTES",
    "ip community-list standard CUSTOMER-ROUTES permit 65003:500",
    # Prefix-lists (ensure present)
    "ip prefix-list ENTERPRISE-PREFIXES seq 10 permit 192.168.0.0/16 ge 24 le 24",
    "ip prefix-list DENY-203-115 seq 10 permit 203.0.115.0/24",
    "ip prefix-list LOOPBACK-PREFIX seq 10 permit 172.16.1.1/32",
    # Rebuild SET-COMMUNITY-OUT
    "no route-map SET-COMMUNITY-OUT",
    "route-map SET-COMMUNITY-OUT permit 10",
    " match ip address prefix-list ENTERPRISE-PREFIXES",
    " set community 65001:100 additive",
    "route-map SET-COMMUNITY-OUT permit 20",
    # Rebuild POLICY-ISP-B-IN with community match at seq 8
    "no route-map POLICY-ISP-B-IN",
    "route-map POLICY-ISP-B-IN deny 5",
    " match ip address prefix-list DENY-203-115",
    "route-map POLICY-ISP-B-IN permit 8",
    " match community CUSTOMER-ROUTES",
    " set local-preference 120",
    "route-map POLICY-ISP-B-IN permit 10",
    " match as-path 2",
    " set local-preference 150",
    "route-map POLICY-ISP-B-IN permit 20",
    # Apply BGP neighbor config
    "router bgp 65001",
    " neighbor 10.1.12.2 send-community",
    " neighbor 10.1.12.2 route-map SET-COMMUNITY-OUT out",
    " neighbor 10.1.13.2 send-community",
    " neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in",
    " neighbor 172.16.4.4 send-community",
    "end",
]

# ── R2 ──────────────────────────────────────────────────────────────────────
r2_commands = [
    "router bgp 65002",
    " neighbor 10.1.12.1 send-community",
    " neighbor 10.1.23.2 send-community",
    "end",
]

# ── R3 ──────────────────────────────────────────────────────────────────────
r3_commands = [
    # Rebuild TAG-CUSTOMER-IN
    "no route-map TAG-CUSTOMER-IN",
    "route-map TAG-CUSTOMER-IN permit 10",
    " set community 65003:500 additive",
    # BGP neighbor config
    "router bgp 65003",
    " neighbor 10.1.13.1 send-community",
    " neighbor 10.1.23.1 send-community",
    " neighbor 10.1.35.2 remote-as 65004",
    " neighbor 10.1.35.2 send-community",
    " neighbor 10.1.35.2 soft-reconfiguration inbound",
    " neighbor 10.1.35.2 route-map TAG-CUSTOMER-IN in",
    "end",
]

# ── R4 ──────────────────────────────────────────────────────────────────────
r4_commands = [
    # Rebuild SET-NO-EXPORT
    "no route-map SET-NO-EXPORT",
    "route-map SET-NO-EXPORT permit 10",
    " match ip address ENTERPRISE-INTERNAL",
    " set community no-export additive",
    "route-map SET-NO-EXPORT permit 20",
    # BGP neighbor config
    "router bgp 65001",
    " neighbor 172.16.1.1 send-community",
    " no neighbor 172.16.1.1 distribute-list ENTERPRISE-INTERNAL out",
    " neighbor 172.16.1.1 route-map SET-NO-EXPORT out",
    "end",
]

# ── R5 ──────────────────────────────────────────────────────────────────────
r5_commands = [
    "router bgp 65004",
    " bgp router-id 172.16.5.5",
    " neighbor 10.1.35.1 remote-as 65003",
    " neighbor 10.1.35.1 send-community",
    " network 172.16.5.5 mask 255.255.255.255",
    " network 10.5.1.0 mask 255.255.255.0",
    " network 10.5.2.0 mask 255.255.255.0",
    "end",
]


def restore(name, port, commands, soft_resets=None):
    print(f"\nRestoring {name} (port {port})...")
    with connect(port) as conn:
        conn.enable()
        conn.send_config_set(commands)
        time.sleep(1)
        if soft_resets:
            for cmd in soft_resets:
                conn.send_command(cmd)
                time.sleep(0.5)
    print(f"  {name} done.")


restore("R1", 5001, r1_commands, [
    "clear ip bgp 10.1.12.2 soft",
    "clear ip bgp 10.1.13.2 soft",
    "clear ip bgp 172.16.4.4 soft",
])
restore("R2", 5002, r2_commands)
restore("R3", 5003, r3_commands, ["clear ip bgp 10.1.35.2 soft in"])
restore("R4", 5004, r4_commands, ["clear ip bgp 172.16.1.1 soft out"])
restore("R5", 5005, r5_commands)

print("\nAll devices restored to Lab 06 solution state.")
print()
print("Verify with:")
print("  R1# show ip bgp summary              (5 sessions — 4 on R1 side)")
print("  R2# show ip bgp 192.168.1.0          (expect Community: 65001:100)")
print("  R1# show ip bgp 10.4.1.0             (expect Community: no-export)")
print("  R3# show ip bgp 10.5.1.0             (expect Community: 65003:500)")
print("  R1# show ip bgp 10.5.1.0             (expect Local preference: 120)")
print("  R1# show ip bgp 198.51.100.0         (expect Local preference: 200)")
