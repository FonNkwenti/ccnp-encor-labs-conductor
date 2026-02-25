"""
BGP Lab 07 — Fault Injection: Scenario 02
Ticket: MED values are causing wrong inbound path selection

Fault:  Swaps the MED metric values in TE-TO-ISP-A route-map so that:
        - PREFIX-192-168-2 (which should be MED=100 — deprioritized via ISP-A) gets MED=10
        - PREFIX-192-168-1 (which should be MED=10 — preferred via ISP-A) gets MED=100
        This makes ISP-A believe that 192.168.2.0/24 is the preferred ingress via
        ISP-A rather than 192.168.1.0/24 — the opposite of the intended policy.
        The AS-path prepend on PREFIX-192-168-2 is also removed to make the MED
        the only differentiator.

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
    # Rebuild TE-TO-ISP-A with swapped MEDs and no prepend on PREFIX-192-168-2
    "no route-map TE-TO-ISP-A",
    "route-map TE-TO-ISP-A permit 10",
    " match ip address prefix-list PREFIX-192-168-2",
    " set metric 10",
    " set community 65001:100 additive",
    "route-map TE-TO-ISP-A permit 20",
    " match ip address prefix-list PREFIX-192-168-1",
    " set metric 100",
    " set community 65001:100 additive",
    "route-map TE-TO-ISP-A permit 30",
    " match ip address prefix-list PREFIX-192-168-3",
    " set metric 50",
    " set community 65001:100 additive",
    "route-map TE-TO-ISP-A permit 40",
    " set community 65001:100 additive",
    "end",
]

print("Injecting Scenario 02: swapping MED values in TE-TO-ISP-A on R1...")
with ConnectHandler(**device) as conn:
    conn.enable()
    conn.send_config_set(fault_commands)
    conn.send_command("clear ip bgp 10.1.12.2 soft out")
print("Fault injected.")
print()
print("Verify the fault:")
print("  R1# show route-map TE-TO-ISP-A")
print("  (check: PREFIX-192-168-2 now has metric 10, PREFIX-192-168-1 has metric 100)")
print("  R2# show ip bgp 192.168.1.0")
print("  (expect: Metric = 100 — WRONG, should be 10)")
print("  R2# show ip bgp 192.168.2.0")
print("  (expect: Metric = 10 — WRONG, should be 100 with prepend)")
