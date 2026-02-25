"""
BGP Lab 05 — Apply Full Solution
Restores R1 to the complete solved state for Lab 05.
Run this after any fault injection scenario to reset the lab.
"""
from netmiko import ConnectHandler
import time

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
    "secret": "",
}

r1_solution = [
    # AS-path ACLs
    "ip as-path access-list 1 permit ^65002$",
    "ip as-path access-list 2 permit ^65003$",
    "ip as-path access-list 3 permit _65002_",
    # Prefix-lists for route-map matching
    "ip prefix-list ENTERPRISE-PREFIXES seq 10 permit 192.168.0.0/16 ge 24 le 24",
    "ip prefix-list DENY-203-115 seq 10 permit 203.0.115.0/24",
    # Rebuild SET-LP-200-ISP-A correctly (permit + local-preference)
    "no route-map SET-LP-200-ISP-A",
    "route-map SET-LP-200-ISP-A permit 10",
    " match as-path 1",
    " set local-preference 200",
    "route-map SET-LP-200-ISP-A permit 20",
    # Rebuild POLICY-ISP-B-IN
    "no route-map POLICY-ISP-B-IN",
    "route-map POLICY-ISP-B-IN deny 5",
    " match ip address prefix-list DENY-203-115",
    "route-map POLICY-ISP-B-IN permit 10",
    " match as-path 2",
    " set local-preference 150",
    "route-map POLICY-ISP-B-IN permit 20",
    # Rebuild PREPEND-TO-ISP-B
    "no route-map PREPEND-TO-ISP-B",
    "route-map PREPEND-TO-ISP-B permit 10",
    " match ip address prefix-list ENTERPRISE-PREFIXES",
    " set as-path prepend 65001 65001 65001",
    "route-map PREPEND-TO-ISP-B permit 20",
    # Apply to BGP neighbors
    "router bgp 65001",
    " no neighbor 10.1.12.2 weight 100",
    " no neighbor 10.1.12.2 prefix-list FROM-ISP-A in",
    " no neighbor 10.1.13.2 prefix-list FROM-ISP-B in",
    " no neighbor 10.1.13.2 prefix-list TO-ISP-B out",
    " no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B in",
    " neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in",
    " neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in",
    " neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out",
    "end",
]

print("Restoring Lab 05 to solved state on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(r1_solution)
    time.sleep(1)
    conn.send_command("clear ip bgp 10.1.12.2 soft in")
    time.sleep(1)
    conn.send_command("clear ip bgp 10.1.13.2 soft")
print("Done.")
print("\nVerify with:")
print("  R1# show route-map")
print("  R1# show ip bgp 198.51.100.0    (expect Local preference: 200)")
print("  R1# show ip bgp 203.0.113.0     (expect Local preference: 150)")
print("  R3# show ip bgp 192.168.1.0     (expect 4-hop via R1, 2-hop via R2 preferred)")
print("  R4# show ip bgp                 (expect LocPrf 200 for ISP-A, 150 for ISP-B)")
