"""
BGP Lab 06 — Fault Injection: Scenario 02
Ticket: R2 is receiving enterprise prefixes without a community tag
Fault:  Remove the outbound route-map TAG-ISP-A-OUT from R1's R2
        neighbor statement — enterprise prefixes reach R2 untagged
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
    " no neighbor 10.1.12.2 route-map TAG-ISP-A-OUT out",
]

print("Injecting Scenario 02: removing TAG-ISP-A-OUT outbound policy on R1 toward R2...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 10.1.12.2 soft out")
print("Fault injected.")
print("Verify: 'show ip bgp 192.168.1.0' on R2 — Community line should be absent.")
