"""
BGP Lab 05 — Fault Injection: Scenario 03
Ticket: SET-LP-200-ISP-A uses 'set weight 200' instead of 'set local-preference 200'
        — R1 path selection works locally, but R4 cannot see the preference
Fault: Replace 'set local-preference 200' with 'set weight 200' in SET-LP-200-ISP-A
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
    # Ensure prerequisite exists
    "ip as-path access-list 1 permit ^65002$",
    # Remove the correct set local-preference sequence
    "no route-map SET-LP-200-ISP-A 10",
    # Rebuild with set weight instead (the fault)
    "route-map SET-LP-200-ISP-A permit 10",
    " match as-path 1",
    " set weight 200",
    # Keep the pass-through
    "route-map SET-LP-200-ISP-A permit 20",
    # Apply inbound
    "router bgp 65001",
    " no neighbor 10.1.12.2 weight 100",
    " no neighbor 10.1.12.2 prefix-list FROM-ISP-A in",
    " neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in",
    "end",
]

print("Injecting Scenario 03: 'set weight 200' instead of 'set local-preference 200' on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_config_set(fault_commands[:-1])
    conn.send_command("clear ip bgp 10.1.12.2 soft in")
    print(output)
print("Fault injected.")
print("Verify on R1: 'show ip bgp 198.51.100.0' — shows weight 200 but local-pref 100.")
print("Verify on R4: 'show ip bgp' — all routes show LocPrf 100 (no preference visible from R4).")
