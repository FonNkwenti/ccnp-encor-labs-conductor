"""
BGP Lab 05 — Fault Injection: Scenario 02
Ticket: PREPEND-TO-ISP-B applied 'in' (inbound) instead of 'out' (outbound)
        — AS-path prepend has no effect on routes advertised to R3
Fault: Apply PREPEND-TO-ISP-B route-map inbound from R3 instead of outbound
Target: R1 (port 5001)
"""
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
    "secret": "",
}

fault_commands = [
    # Ensure prerequisite config exists
    "ip prefix-list ENTERPRISE-PREFIXES seq 10 permit 192.168.0.0/16 ge 24 le 24",
    "route-map PREPEND-TO-ISP-B permit 10",
    " match ip address prefix-list ENTERPRISE-PREFIXES",
    " set as-path prepend 65001 65001 65001",
    "route-map PREPEND-TO-ISP-B permit 20",
    # Apply outbound policy for ISP-B inbound (policy-ISP-B-IN for inbound)
    "ip as-path access-list 2 permit ^65003$",
    "ip prefix-list DENY-203-115 seq 10 permit 203.0.115.0/24",
    "route-map POLICY-ISP-B-IN deny 5",
    " match ip address prefix-list DENY-203-115",
    "route-map POLICY-ISP-B-IN permit 10",
    " match as-path 2",
    " set local-preference 150",
    "route-map POLICY-ISP-B-IN permit 20",
    # Apply the fault: PREPEND-TO-ISP-B on the wrong direction (in instead of out)
    "router bgp 65001",
    " no neighbor 10.1.13.2 prefix-list FROM-ISP-B in",
    " no neighbor 10.1.13.2 prefix-list TO-ISP-B out",
    " neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in",
    " neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B in",   # WRONG direction — fault
    "end",
]

print("Injecting Scenario 02: PREPEND-TO-ISP-B applied 'in' instead of 'out' on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_config_set(fault_commands[:-1])
    conn.send_command("clear ip bgp 10.1.13.2 soft")
    print(output)
print("Fault injected.")
print("Verify on R3: 'show ip bgp 192.168.1.0' — R1 direct path should still be preferred (1 hop).")
print("Expected: no AS-path prepend visible because the route-map is applied inbound (wrong direction).")
