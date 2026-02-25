"""
BGP Lab 05 — Fault Injection: Scenario 01
Ticket: Route-map SET-LP-200-ISP-A uses 'deny 10' instead of 'permit 10'
        — blocks ALL ISP-A routes from being accepted by R1
Fault: Replace permit sequence 10 with deny sequence 10 in SET-LP-200-ISP-A
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
    # Ensure AS-path ACL exists
    "ip as-path access-list 1 permit ^65002$",
    # Remove the correct permit sequence
    "no route-map SET-LP-200-ISP-A 10",
    # Add a deny sequence instead (the fault)
    "route-map SET-LP-200-ISP-A deny 10",
    " match as-path 1",
    # Remove the pass-through sequence so all non-matching routes are also denied
    "no route-map SET-LP-200-ISP-A 20",
    # Apply the broken route-map inbound from R2
    "router bgp 65001",
    " no neighbor 10.1.12.2 weight 100",
    " no neighbor 10.1.12.2 prefix-list FROM-ISP-A in",
    " neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in",
    "end",
]

print("Injecting Scenario 01: deny instead of permit in SET-LP-200-ISP-A on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_config_set(fault_commands[:-1])
    conn.send_command("clear ip bgp 10.1.12.2 soft in")
    print(output)
print("Fault injected.")
print("Verify: 'show ip bgp summary' on R1 — R2 neighbor should show 0 prefixes received.")
