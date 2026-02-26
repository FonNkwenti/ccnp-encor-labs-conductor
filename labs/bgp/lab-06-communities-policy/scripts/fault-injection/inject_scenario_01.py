"""
BGP Lab 06 — Fault Injection: Scenario 01
Ticket: R5's routes arrive at R3 but local-preference is 100, not 180
Fault:  Remove the community-list R5-PREFERRED on R3, breaking the
        match community clause in POLICY-FROM-R5 (sequences fall through
        to the permit-all tail; LP remains at default 100)
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
    "no ip community-list standard R5-PREFERRED",
]

print("Injecting Scenario 01: removing R5-PREFERRED community-list on R3...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 10.1.35.2 soft in")
print("Fault injected.")
print("Verify: 'show ip bgp 10.4.1.0' on R3 — local-pref should drop to 100.")
