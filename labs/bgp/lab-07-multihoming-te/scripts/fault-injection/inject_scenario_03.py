"""
BGP Lab 07 — Fault Injection Scenario 03
Fault: AS-path prepend entry moved after catch-all in TE-TO-ISP-B.
Removes seq 10 (which prepends 3x AS-path for 192.168.1.0/24 to ISP-B)
and re-adds it as seq 50 — after the catch-all at seq 40. The catch-all
permits everything first, so the prepend statement never fires.
ISP-B will no longer see the longer AS-path for 192.168.1.0/24 and may
prefer that path incorrectly, causing suboptimal inbound routing.
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
    "no route-map TE-TO-ISP-B permit 10",
    "route-map TE-TO-ISP-B permit 50",
    " match ip address prefix-list PREFIX-192-168-1",
    " set as-path prepend 65001 65001 65001",
    " set metric 100",
]

print("Injecting Scenario 03: Moving AS-path prepend entry after catch-all in TE-TO-ISP-B...")
with ConnectHandler(**device) as net_connect:
    output = net_connect.send_config_set(commands)
    print(output)
print("Fault injected.")
print()
print("Expected symptom: 192.168.1.0/24 is advertised to ISP-B without AS-path prepend.")
print("                  ISP-B sees a shorter AS-path and may prefer this path incorrectly.")
print("Verify with:")
print("  R3# show ip bgp 192.168.1.0     (expect normal AS-path 65001, no prepend)")
print("  R1# show route-map TE-TO-ISP-B  (seq 10 missing, seq 50 after catch-all)")
print("  R1# show ip bgp neighbors 10.1.13.2 advertised-routes")
