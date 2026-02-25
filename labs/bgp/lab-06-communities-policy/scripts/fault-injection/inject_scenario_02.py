"""
BGP Lab 06 — Fault Injection: Scenario 02
Ticket: Community-list not matching — customer routes getting wrong local-preference
Fault:  Replaces the correct CUSTOMER-ROUTES community-list (65003:500) with a
        wrong value (65003:999), so route-map POLICY-ISP-B-IN sequence 8 never
        matches and customer routes fall through to sequence 10 (LP 150).
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
    # Remove the correct community-list
    "no ip community-list standard CUSTOMER-ROUTES",
    # Install a broken one with wrong community number
    "ip community-list standard CUSTOMER-ROUTES permit 65003:999",
    "end",
]

print("Injecting Scenario 02: misconfiguring CUSTOMER-ROUTES community-list on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 10.1.13.2 soft in")
print("Fault injected.")
print()
print("Verify the fault:")
print("  R1# show ip community-list")
print("  (should show: permit 65003:999  — wrong value)")
print("  R1# show ip bgp 10.5.1.0")
print("  (should show Local preference: 150 instead of 120)")
