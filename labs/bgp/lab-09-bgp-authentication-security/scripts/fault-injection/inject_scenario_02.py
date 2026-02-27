"""
Fault Injection — BGP Lab 09, Ticket 2
Sets maximum-prefix limit to 1 on R1's R2 neighbor,
causing the session to tear down when R2 advertises more than 1 prefix.
"""
from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
}

FAULT_COMMANDS = [
    "router bgp 65001",
    "no neighbor 10.1.12.2 maximum-prefix 200 80",
    "neighbor 10.1.12.2 maximum-prefix 1",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 2 fault: maximum-prefix set to 1 on R1 for R2 neighbor...")
    with ConnectHandler(**R1) as conn:
        conn.enable()
        output = conn.send_config_set(FAULT_COMMANDS)
        print(output)
    print("[+] Fault injected. The R1-R2 BGP session will tear down immediately.")
    print("    R1# show ip bgp summary  --> 10.1.12.2 should show 'Idle' (PfxCt)")
    print("    R1# show ip bgp neighbors 10.1.12.2 | include Maximum")
