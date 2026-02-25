"""
BGP Lab 04 — Apply Full Solution
Restores R1 and R4 to the complete solved state for Lab 04.
Run this after any fault injection scenario to reset the lab.
"""
from netmiko import ConnectHandler
import time

devices = {
    "R1": {"device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5001,
            "username": "", "password": "", "secret": ""},
    "R4": {"device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5004,
            "username": "", "password": "", "secret": ""},
}

r1_solution = [
    # Clear any broken prefix-list entries first
    "no ip prefix-list FROM-ISP-A",
    "no ip prefix-list FROM-ISP-B",
    "no ip prefix-list TO-ISP-B",
    # Rebuild correct prefix-lists
    "ip prefix-list FROM-ISP-A seq 10 permit 198.51.100.0/24",
    "ip prefix-list FROM-ISP-A seq 20 deny 0.0.0.0/0 le 32",
    "ip prefix-list FROM-ISP-B seq 10 deny 203.0.115.0/24",
    "ip prefix-list FROM-ISP-B seq 20 permit 0.0.0.0/0 le 32",
    "ip prefix-list TO-ISP-B seq 10 permit 192.168.1.0/24",
    "ip prefix-list TO-ISP-B seq 20 deny 0.0.0.0/0 le 32",
    # Apply BGP neighbor policies
    "router bgp 65001",
    " neighbor 10.1.12.2 soft-reconfiguration inbound",
    " neighbor 10.1.12.2 prefix-list FROM-ISP-A in",
    " neighbor 10.1.13.2 soft-reconfiguration inbound",
    " neighbor 10.1.13.2 prefix-list FROM-ISP-B in",
    " neighbor 10.1.13.2 prefix-list TO-ISP-B out",
    "end",
]

r1_soft_resets = [
    "clear ip bgp 10.1.12.2 soft in",
    "clear ip bgp 10.1.13.2 soft",
]

r4_solution = [
    "no ip access-list standard ENTERPRISE-INTERNAL",
    "ip access-list standard ENTERPRISE-INTERNAL",
    " permit 10.4.1.0 0.0.0.255",
    " permit 10.4.2.0 0.0.0.255",
    "router bgp 65001",
    " neighbor 172.16.1.1 distribute-list ENTERPRISE-INTERNAL out",
    "end",
]

r4_soft_reset = "clear ip bgp 172.16.1.1 soft out"

print("Restoring Lab 04 to solved state...")

print("  Applying R1 solution...")
with ConnectHandler(**devices["R1"]) as conn:
    conn.enable()
    conn.send_config_set(r1_solution)
    for cmd in r1_soft_resets:
        conn.send_command(cmd)
        time.sleep(1)
print("  R1 done.")

print("  Applying R4 solution...")
with ConnectHandler(**devices["R4"]) as conn:
    conn.enable()
    conn.send_config_set(r4_solution)
    conn.send_command(r4_soft_reset)
print("  R4 done.")

print("\nSolution applied. Verify with:")
print("  R1# show ip bgp")
print("  R1# show ip bgp neighbors 10.1.12.2 routes")
print("  R1# show ip bgp neighbors 10.1.13.2 advertised-routes")
print("  R1# show ip bgp neighbors 172.16.4.4 received-routes")
