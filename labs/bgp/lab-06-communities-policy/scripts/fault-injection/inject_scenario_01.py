"""
BGP Lab 06 — Fault Injection: Scenario 01
Ticket: Communities not propagating to ISP-A (R2)
Fault:  Removes 'send-community' from R1's neighbor statement for R2 (10.1.12.2)
        Communities are then silently dropped and R2 never sees 65001:100 on
        enterprise prefixes.
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
    " no neighbor 10.1.12.2 send-community",
    "end",
]

print("Injecting Scenario 01: removing send-community from R1 neighbor 10.1.12.2...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 10.1.12.2 soft out")
print("Fault injected.")
print()
print("Verify the fault:")
print("  R1# show bgp neighbors 10.1.12.2 | include Community")
print("  (should show nothing, or 'Community attribute not sent')")
print("  R2# show ip bgp 192.168.1.0")
print("  (should show NO Community field)")
