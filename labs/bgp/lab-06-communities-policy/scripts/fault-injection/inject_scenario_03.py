"""
BGP Lab 06 — Fault Injection: Scenario 03
Ticket: DataStream reports receiving an ISP-B internal prefix marked confidential
Fault:  Remove the outbound route-map POLICY-TO-R5 from R3's R5 neighbor
        statement — 203.0.115.0/24 reaches R5 without the no-export community
Target: R3 (port 5003)
"""
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5003,
    "username": "",
    "password": "",
    "secret": "",
}

fault_commands = [
    "router bgp 65003",
    " no neighbor 10.1.35.2 route-map POLICY-TO-R5 out",
]

print("Injecting Scenario 03: removing POLICY-TO-R5 outbound policy on R3 toward R5...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 10.1.35.2 soft out")
print("Fault injected.")
print("Verify: 'show ip bgp 203.0.115.0' on R5 — Community line should be absent.")
