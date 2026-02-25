"""
BGP Lab 04 — Fault Injection: Scenario 02
Ticket: Cannot view received-routes from ISP-B (soft-reconfiguration missing)
Fault: Remove 'neighbor 10.1.13.2 soft-reconfiguration inbound' from R1
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
    "router bgp 65001",
    " no neighbor 10.1.13.2 soft-reconfiguration inbound",
    "end",
]

print("Injecting Scenario 02: Removing soft-reconfiguration inbound for R3 neighbor on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_config_set(fault_commands)
    print(output)
print("Fault injected.")
print("Run: show ip bgp neighbors 10.1.13.2 received-routes")
print("Expected error: % Inbound soft reconfiguration not enabled")
