"""
BGP Lab 07 — Apply Full Solution
Restores all 5 routers to the complete solved state for Lab 07.
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
    # Static default route for conditional default-originate
    "ip route 0.0.0.0 0.0.0.0 Null0",
    # Community-list (from Lab 06)
    "no ip community-list standard CUSTOMER-ROUTES",
    "ip community-list standard CUSTOMER-ROUTES permit 65003:500",
    # Ensure ISP-A prefix-list present
    "no ip prefix-list ISP-A-PREFIXES",
    "ip prefix-list ISP-A-PREFIXES seq 10 permit 198.51.100.0/24",
    "ip prefix-list ISP-A-PREFIXES seq 20 permit 198.51.101.0/24",
    "ip prefix-list ISP-A-PREFIXES seq 30 permit 198.51.102.0/24",
    # Ensure ISP-B prefix-list present
    "no ip prefix-list ISP-B-PREFIXES",
    "ip prefix-list ISP-B-PREFIXES seq 10 permit 203.0.113.0/24",
    "ip prefix-list ISP-B-PREFIXES seq 20 permit 203.0.114.0/24",
    "ip prefix-list ISP-B-PREFIXES seq 30 permit 203.0.115.0/24",
    # Ensure per-enterprise prefix-lists present
    "no ip prefix-list PREFIX-192-168-1",
    "ip prefix-list PREFIX-192-168-1 seq 10 permit 192.168.1.0/24",
    "no ip prefix-list PREFIX-192-168-2",
    "ip prefix-list PREFIX-192-168-2 seq 10 permit 192.168.2.0/24",
    "no ip prefix-list PREFIX-192-168-3",
    "ip prefix-list PREFIX-192-168-3 seq 10 permit 192.168.3.0/24",
    # Ensure conditional default prefix-list present
    "no ip prefix-list COND-DEFAULT-CHECK",
    "ip prefix-list COND-DEFAULT-CHECK seq 10 permit 198.51.100.0/24",
    # Rebuild LP-FROM-ISP-A
    "no route-map LP-FROM-ISP-A",
    "route-map LP-FROM-ISP-A permit 10",
    " match ip address prefix-list ISP-A-PREFIXES",
    " set local-preference 200",
    "route-map LP-FROM-ISP-A permit 20",
    " match community CUSTOMER-ROUTES",
    " set local-preference 120",
    "route-map LP-FROM-ISP-A permit 30",
    " set local-preference 150",
    # Rebuild LP-FROM-ISP-B
    "no route-map LP-FROM-ISP-B",
    "route-map LP-FROM-ISP-B permit 10",
    " match ip address prefix-list ISP-B-PREFIXES",
    " set local-preference 200",
    "route-map LP-FROM-ISP-B permit 20",
    " match community CUSTOMER-ROUTES",
    " set local-preference 120",
    "route-map LP-FROM-ISP-B permit 30",
    " set local-preference 150",
    # Rebuild TE-TO-ISP-A
    "no route-map TE-TO-ISP-A",
    "route-map TE-TO-ISP-A permit 10",
    " match ip address prefix-list PREFIX-192-168-2",
    " set as-path prepend 65001 65001 65001",
    " set metric 100",
    "route-map TE-TO-ISP-A permit 20",
    " match ip address prefix-list PREFIX-192-168-1",
    " set metric 10",
    " set community 65001:100 additive",
    "route-map TE-TO-ISP-A permit 30",
    " match ip address prefix-list PREFIX-192-168-3",
    " set metric 50",
    " set community 65001:100 additive",
    "route-map TE-TO-ISP-A permit 40",
    " set community 65001:100 additive",
    # Rebuild TE-TO-ISP-B
    "no route-map TE-TO-ISP-B",
    "route-map TE-TO-ISP-B permit 10",
    " match ip address prefix-list PREFIX-192-168-1",
    " set as-path prepend 65001 65001 65001",
    " set metric 100",
    "route-map TE-TO-ISP-B permit 20",
    " match ip address prefix-list PREFIX-192-168-2",
    " set metric 10",
    " set community 65001:100 additive",
    "route-map TE-TO-ISP-B permit 30",
    " match ip address prefix-list PREFIX-192-168-3",
    " set metric 50",
    " set community 65001:100 additive",
    "route-map TE-TO-ISP-B permit 40",
    " set community 65001:100 additive",
    # Rebuild COND-DEFAULT
    "no route-map COND-DEFAULT",
    "route-map COND-DEFAULT permit 10",
    " match ip address prefix-list COND-DEFAULT-CHECK",
    # Apply BGP neighbor config
    "router bgp 65001",
    " neighbor 10.1.12.2 send-community",
    " neighbor 10.1.12.2 route-map LP-FROM-ISP-A in",
    " neighbor 10.1.12.2 route-map TE-TO-ISP-A out",
    " neighbor 10.1.13.2 send-community",
    " neighbor 10.1.13.2 route-map LP-FROM-ISP-B in",
    " neighbor 10.1.13.2 route-map TE-TO-ISP-B out",
    " neighbor 172.16.4.4 send-community",
    " neighbor 172.16.4.4 default-originate route-map COND-DEFAULT",
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
    "no route-map TAG-CUSTOMER-IN",
    "route-map TAG-CUSTOMER-IN permit 10",
    " set community 65003:500 additive",
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
    "no route-map SET-NO-EXPORT",
    "route-map SET-NO-EXPORT permit 10",
    " match ip address ENTERPRISE-INTERNAL",
    " set community no-export additive",
    "route-map SET-NO-EXPORT permit 20",
    "router bgp 65001",
    " neighbor 172.16.1.1 send-community",
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

print("\nAll devices restored to Lab 07 solution state.")
print()
print("Verify with:")
print("  R1# show ip bgp summary              (3 BGP sessions active)")
print("  R1# show ip bgp 198.51.100.0         (expect Local preference: 200 via ISP-A)")
print("  R1# show ip bgp 203.0.113.0          (expect Local preference: 200 via ISP-B)")
print("  R2# show ip bgp 192.168.2.0          (expect AS-path: 65001 65001 65001 65001)")
print("  R2# show ip bgp 192.168.1.0          (expect Metric: 10)")
print("  R3# show ip bgp 192.168.1.0          (expect AS-path: 65001 65001 65001 65001)")
print("  R3# show ip bgp 192.168.2.0          (expect Metric: 10)")
print("  R4# show ip bgp                      (expect 0.0.0.0/0 default route present)")
