"""
BGP Lab 07 — Fault Injection: Scenario 01
Ticket: Conditional default route not being received by R4

Fault:  Removes the ip route 0.0.0.0 0.0.0.0 Null0 static route from R1 and
        replaces the COND-DEFAULT route-map with one that references a non-existent
        prefix-list (COND-DEFAULT-WRONG). Without the static default, IOS will not
        originate 0/0 even if the condition route-map matches. Additionally, the
        wrong prefix-list name ensures the route-map never matches.

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
    # Remove the static default route (required for conditional default-originate)
    "no ip route 0.0.0.0 0.0.0.0 Null0",
    # Replace COND-DEFAULT with a broken version referencing a non-existent prefix-list
    "no route-map COND-DEFAULT",
    "route-map COND-DEFAULT permit 10",
    " match ip address prefix-list COND-DEFAULT-WRONG",
    "end",
]

print("Injecting Scenario 01: breaking conditional default route on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 172.16.4.4 soft out")
print("Fault injected.")
print()
print("Verify the fault:")
print("  R1# show ip route static")
print("  (should show NO static 0.0.0.0 route)")
print("  R1# show route-map COND-DEFAULT")
print("  (should show match against COND-DEFAULT-WRONG — a non-existent prefix-list)")
print("  R4# show ip bgp")
print("  (should show NO 0.0.0.0/0 default route)")
print("  R4# show ip route 0.0.0.0")
print("  (should return: % Network not in table)")
