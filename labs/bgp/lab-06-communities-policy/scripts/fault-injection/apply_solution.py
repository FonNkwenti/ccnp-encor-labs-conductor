"""
BGP Lab 06 — Apply Full Solution
Restores R1, R3, and R5 to the complete solved state for Lab 06.
Run this after any fault injection scenario to reset the lab.
"""
from netmiko import ConnectHandler
import time

r1 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
    "secret": "",
}

r3 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5003,
    "username": "",
    "password": "",
    "secret": "",
}

r5 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5005,
    "username": "",
    "password": "",
    "secret": "",
}

r1_solution = [
    # Prefix-list for ISP-A internal prefix
    "ip prefix-list ISP-A-INTERNAL seq 10 permit 198.51.102.0/24",
    # Rebuild SET-LP-200-ISP-A with local-AS community sequence
    "no route-map SET-LP-200-ISP-A",
    "route-map SET-LP-200-ISP-A permit 10",
    " match ip address prefix-list ISP-A-INTERNAL",
    " set local-preference 200",
    " set community local-AS",
    "route-map SET-LP-200-ISP-A permit 15",
    " match as-path 1",
    " set local-preference 200",
    "route-map SET-LP-200-ISP-A permit 20",
    # Outbound to ISP-A — community tag 65001:100
    "no route-map TAG-ISP-A-OUT",
    "route-map TAG-ISP-A-OUT permit 10",
    " match ip address prefix-list ENTERPRISE-PREFIXES",
    " set community 65001:100",
    "route-map TAG-ISP-A-OUT permit 20",
    # Outbound to ISP-B — community tag 65001:200 + prepend
    "no route-map TAG-AND-PREPEND-ISP-B",
    "route-map TAG-AND-PREPEND-ISP-B permit 10",
    " match ip address prefix-list ENTERPRISE-PREFIXES",
    " set community 65001:200",
    " set as-path prepend 65001 65001 65001",
    "route-map TAG-AND-PREPEND-ISP-B permit 20",
    # Apply to BGP neighbors
    "router bgp 65001",
    " neighbor 10.1.12.2 send-community",
    " neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in",
    " neighbor 10.1.12.2 route-map TAG-ISP-A-OUT out",
    " neighbor 10.1.13.2 send-community",
    " no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out",
    " neighbor 10.1.13.2 route-map TAG-AND-PREPEND-ISP-B out",
    "end",
]

r3_solution = [
    # Prefix-list and community-list
    "ip prefix-list ISP-B-INTERNAL seq 10 permit 203.0.115.0/24",
    "ip community-list standard R5-PREFERRED permit 65004:100",
    # Rebuild outbound policy to R5
    "no route-map POLICY-TO-R5",
    "route-map POLICY-TO-R5 permit 10",
    " match ip address prefix-list ISP-B-INTERNAL",
    " set community no-export",
    "route-map POLICY-TO-R5 permit 20",
    # Rebuild inbound policy from R5
    "no route-map POLICY-FROM-R5",
    "route-map POLICY-FROM-R5 permit 10",
    " match community R5-PREFERRED",
    " set local-preference 180",
    "route-map POLICY-FROM-R5 permit 20",
    # Apply to BGP neighbor R5
    "router bgp 65003",
    " neighbor 10.1.35.2 remote-as 65004",
    " neighbor 10.1.35.2 soft-reconfiguration inbound",
    " neighbor 10.1.35.2 send-community",
    " neighbor 10.1.35.2 route-map POLICY-FROM-R5 in",
    " neighbor 10.1.35.2 route-map POLICY-TO-R5 out",
    "end",
]

r5_solution = [
    # Prefix-list and route-map for community tagging
    "ip prefix-list R5-CUSTOMER-ROUTES seq 10 permit 10.4.1.0/24",
    "ip prefix-list R5-CUSTOMER-ROUTES seq 20 permit 10.4.2.0/24",
    "no route-map SET-COMM-OUT",
    "route-map SET-COMM-OUT permit 10",
    " match ip address prefix-list R5-CUSTOMER-ROUTES",
    " set community 65004:100",
    "route-map SET-COMM-OUT permit 20",
    # BGP process
    "router bgp 65004",
    " bgp router-id 172.16.5.5",
    " neighbor 10.1.35.1 remote-as 65003",
    " neighbor 10.1.35.1 soft-reconfiguration inbound",
    " neighbor 10.1.35.1 send-community",
    " neighbor 10.1.35.1 route-map SET-COMM-OUT out",
    " network 172.16.5.5 mask 255.255.255.255",
    " network 10.4.1.0 mask 255.255.255.0",
    " network 10.4.2.0 mask 255.255.255.0",
    "end",
]

print("Restoring Lab 06 to solved state...")

print("  Restoring R1...")
with ConnectHandler(**r1) as conn:
    conn.enable()
    conn.send_config_set(r1_solution[:-1])
    time.sleep(1)
    conn.send_command("clear ip bgp 10.1.12.2 soft in")
    time.sleep(1)
    conn.send_command("clear ip bgp 10.1.12.2 soft out")
    time.sleep(1)
    conn.send_command("clear ip bgp 10.1.13.2 soft out")

print("  Restoring R3...")
with ConnectHandler(**r3) as conn:
    conn.enable()
    conn.send_config_set(r3_solution[:-1])
    time.sleep(1)
    conn.send_command("clear ip bgp 10.1.35.2 soft")

print("  Restoring R5...")
with ConnectHandler(**r5) as conn:
    conn.enable()
    conn.send_config_set(r5_solution[:-1])
    time.sleep(1)
    conn.send_command("clear ip bgp 10.1.35.1 soft out")

print("Done.")
print("\nVerify with:")
print("  R2# show ip bgp 192.168.1.0         (expect Community: 65001:100)")
print("  R3# show ip bgp 192.168.1.0         (expect Community: 65001:200)")
print("  R5# show ip bgp 203.0.115.0         (expect Community: no-export)")
print("  R3# show ip bgp 10.4.1.0            (expect localpref 180, Community: 65004:100)")
print("  R1# show ip bgp 198.51.102.0        (expect Community: local-AS, localpref 200)")
print("  R3# show ip bgp 198.51.102.0        (expect: Network not in table)")
