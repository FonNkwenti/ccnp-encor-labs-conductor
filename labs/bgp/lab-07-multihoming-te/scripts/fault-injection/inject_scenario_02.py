"""
BGP Lab 07 — Fault Injection Scenario 02
Fault: MED values swapped on R1.
192.168.1.0/24 is advertised to ISP-A with MED=100 (should be MED=10)
and to ISP-B with MED=10 (but the entry was already set correctly — this
fault swaps the MED on TE-TO-ISP-A seq 20 to 100, and on TE-TO-ISP-B
seq 20 to 100, causing both ISPs to deprioritize their respective preferred
prefixes. Inbound traffic will arrive on the wrong ISP link.
"""
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
}

commands = [
    "no route-map TE-TO-ISP-A permit 20",
    "route-map TE-TO-ISP-A permit 20",
    " match ip address prefix-list PREFIX-192-168-1",
    " set metric 100",
    " set community 65001:100 additive",
    "no route-map TE-TO-ISP-B permit 20",
    "route-map TE-TO-ISP-B permit 20",
    " match ip address prefix-list PREFIX-192-168-2",
    " set metric 100",
    " set community 65001:100 additive",
]

print("Injecting Scenario 02: Swapping MED values on TE-TO-ISP-A and TE-TO-ISP-B...")
with ConnectHandler(**device) as net_connect:
    output = net_connect.send_config_set(commands)
    print(output)
print("Fault injected.")
print()
print("Expected symptom: 192.168.1.0/24 now has MED=100 to ISP-A (was 10).")
print("                  192.168.2.0/24 now has MED=100 to ISP-B (was 10).")
print("                  Both ISPs will prefer the wrong link for these prefixes.")
print("Verify with:")
print("  R2# show ip bgp 192.168.1.0     (expect MED=100, should be 10)")
print("  R3# show ip bgp 192.168.2.0     (expect MED=100, should be 10)")
print("  R1# show route-map TE-TO-ISP-A")
print("  R1# show route-map TE-TO-ISP-B")
