"""
BGP Lab 04 — Fault Injection: Scenario 01
Ticket: Prefix-list blocks ALL routes from ISP-A (deny/permit inverted)
Fault: FROM-ISP-A has 'deny 198.51.100.0/24' instead of 'permit 198.51.100.0/24'
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
    # Remove the correct permit entry and replace with deny
    "no ip prefix-list FROM-ISP-A seq 10",
    "ip prefix-list FROM-ISP-A seq 10 deny 198.51.100.0/24",
    # Ensure the catch-all deny remains
    "ip prefix-list FROM-ISP-A seq 20 deny 0.0.0.0/0 le 32",
    # Apply the broken inbound filter
    "router bgp 65001",
    " neighbor 10.1.12.2 soft-reconfiguration inbound",
    " neighbor 10.1.12.2 prefix-list FROM-ISP-A in",
    "end",
    "clear ip bgp 10.1.12.2 soft in",
]

print("Injecting Scenario 01: Inverted deny/permit in FROM-ISP-A prefix-list on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_config_set(fault_commands[:-1])
    conn.send_command(fault_commands[-1])
    print(output)
print("Fault injected. Run 'show ip bgp' on R1 — no ISP-A prefixes should appear.")
