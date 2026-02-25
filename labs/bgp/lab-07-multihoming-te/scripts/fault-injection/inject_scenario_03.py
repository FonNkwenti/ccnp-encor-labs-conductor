"""
BGP Lab 07 — Fault Injection: Scenario 03
Ticket: AS-path prepend not taking effect on 192.168.2.0/24 toward ISP-A

Fault:  Moves the AS-path prepend entry for PREFIX-192-168-2 in TE-TO-ISP-A
        to sequence 50 — placing it AFTER the catch-all permit at sequence 40.
        When IOS evaluates TE-TO-ISP-A, seq 40 matches first (permits everything),
        so seq 50 never fires. R2 receives 192.168.2.0/24 with a normal single-hop
        AS-path (just 65001) instead of the intended 4-entry prepended path.

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
    # Rebuild TE-TO-ISP-A with prepend entry placed after the catch-all
    "no route-map TE-TO-ISP-A",
    # seq 10: PREFIX-192-168-2 — now missing prepend (just MED)
    "route-map TE-TO-ISP-A permit 10",
    " match ip address prefix-list PREFIX-192-168-2",
    " set metric 100",
    " set community 65001:100 additive",
    # seq 20: PREFIX-192-168-1 with correct low MED
    "route-map TE-TO-ISP-A permit 20",
    " match ip address prefix-list PREFIX-192-168-1",
    " set metric 10",
    " set community 65001:100 additive",
    # seq 30: PREFIX-192-168-3 with medium MED
    "route-map TE-TO-ISP-A permit 30",
    " match ip address prefix-list PREFIX-192-168-3",
    " set metric 50",
    " set community 65001:100 additive",
    # seq 40: CATCH-ALL — this runs before the prepend entry
    "route-map TE-TO-ISP-A permit 40",
    " set community 65001:100 additive",
    # seq 50: prepend entry placed AFTER catch-all — will never match
    "route-map TE-TO-ISP-A permit 50",
    " match ip address prefix-list PREFIX-192-168-2",
    " set as-path prepend 65001 65001 65001",
    " set metric 100",
    "end",
]

print("Injecting Scenario 03: misplacing AS-path prepend entry in TE-TO-ISP-A on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 10.1.12.2 soft out")
print("Fault injected.")
print()
print("Verify the fault:")
print("  R1# show route-map TE-TO-ISP-A")
print("  (check: seq 50 has the prepend — placed after seq 40 catch-all)")
print("  R2# show ip bgp 192.168.2.0")
print("  (expect: AS-path 65001 — only 1 entry, prepend not applied)")
print("  (correct would be: AS-path 65001 65001 65001 65001 — 4 entries)")
