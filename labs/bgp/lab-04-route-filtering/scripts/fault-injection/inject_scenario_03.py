"""
BGP Lab 04 — Fault Injection: Scenario 03
Ticket: Outbound prefix filter TO-ISP-B not taking effect (missing soft out reset)
Fault: Apply TO-ISP-B prefix-list outbound to R3 but do NOT run 'clear ip bgp soft out'
       The existing BGP updates to R3 remain unchanged (all 3 enterprise prefixes sent)
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

# First, remove any existing outbound filter to start clean (simulating initial state)
# Then apply the correct prefix-list but intentionally skip the soft out reset
fault_commands = [
    # Remove outbound filter if applied (reset to unfiltered state)
    "router bgp 65001",
    " no neighbor 10.1.13.2 prefix-list TO-ISP-B out",
    "end",
    # Clear to push all prefixes (restore full advertisement to R3)
    "clear ip bgp 10.1.13.2 soft out",
]

fault_commands_part2 = [
    # Now re-apply the prefix-list but intentionally skip the soft reset
    "ip prefix-list TO-ISP-B seq 10 permit 192.168.1.0/24",
    "ip prefix-list TO-ISP-B seq 20 deny 0.0.0.0/0 le 32",
    "router bgp 65001",
    " neighbor 10.1.13.2 prefix-list TO-ISP-B out",
    "end",
    # Intentionally NOT running: clear ip bgp 10.1.13.2 soft out
]

import time

print("Injecting Scenario 03: Outbound filter applied but soft out reset NOT performed...")
with ConnectHandler(**device) as conn:
    conn.enable()
    # Step 1: remove existing filter, soft reset to push all 3 prefixes
    output = conn.send_config_set(fault_commands[:-1])
    conn.send_command(fault_commands[-1])
    print("Step 1: Restored full advertisement to R3.")
    time.sleep(2)
    # Step 2: re-apply filter without soft out reset (the fault)
    output2 = conn.send_config_set(fault_commands_part2)
    print(output2)

print("Fault injected.")
print("Run: show ip bgp neighbors 10.1.13.2 advertised-routes on R1")
print("Expected: All 3 enterprise prefixes still visible (filter not yet active)")
print("Fix: clear ip bgp 10.1.13.2 soft out")
