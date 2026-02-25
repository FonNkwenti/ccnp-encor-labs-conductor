"""
BGP Lab 07 — Fault Injection Scenario 01
Fault: Conditional default not reaching R4.
Removes the static Null0 route that the COND-DEFAULT route-map depends on,
and removes the default-originate statement from the iBGP neighbor config.
R4 will lose its default route and have no path to the internet.
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
    "no ip route 0.0.0.0 0.0.0.0 Null0",
    "router bgp 65001",
    "no neighbor 172.16.4.4 default-originate route-map COND-DEFAULT",
]

print("Injecting Scenario 01: Breaking conditional default route...")
with ConnectHandler(**device) as net_connect:
    output = net_connect.send_config_set(commands)
    print(output)
print("Fault injected.")
print()
print("Expected symptom: R4 loses the 0.0.0.0/0 route from BGP.")
print("Verify with:")
print("  R4# show ip route 0.0.0.0")
print("  R4# show ip bgp 0.0.0.0")
