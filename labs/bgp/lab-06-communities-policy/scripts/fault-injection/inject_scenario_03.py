"""
BGP Lab 06 — Fault Injection: Scenario 03
Ticket: R5 BGP session Established but no routes advertised
Fault:  Removes all network statements from R5's BGP config so it has nothing
        to advertise. The TCP/BGP session with R3 remains up (PfxRcvd stays 0).
Target: R5 (port 5005)
"""
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5005,
    "username": "",
    "password": "",
    "secret": "",
}

fault_commands = [
    "router bgp 65004",
    " no network 172.16.5.5 mask 255.255.255.255",
    " no network 10.5.1.0 mask 255.255.255.0",
    " no network 10.5.2.0 mask 255.255.255.0",
    "end",
]

print("Injecting Scenario 03: removing network statements from R5 BGP config...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
print("Fault injected.")
print()
print("Verify the fault:")
print("  R5# show ip bgp")
print("  (should be empty — no prefixes in BGP table)")
print("  R3# show ip bgp summary")
print("  (R5 neighbor should show PfxRcvd = 0, but session still Up)")
print("  R3# show ip bgp 10.5.1.0")
print("  (no entry)")
