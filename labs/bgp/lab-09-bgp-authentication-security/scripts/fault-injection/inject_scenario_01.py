"""
Fault Injection — BGP Lab 09, Ticket 1
Injects a password mismatch on R2's BGP session to R1.
"""
from netmiko import ConnectHandler

R2 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5002,
    "username": "",
    "password": "",
}

FAULT_COMMANDS = [
    "router bgp 65002",
    "neighbor 10.1.12.1 password WRONG_KEY",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 1 fault: MD5 password mismatch on R2 for R1 neighbor...")
    with ConnectHandler(**R2) as conn:
        conn.enable()
        output = conn.send_config_set(FAULT_COMMANDS)
        print(output)
    print("[+] Fault injected. Wait ~30 seconds for the BGP session to drop.")
    print("    R1# show ip bgp summary  --> 10.1.12.2 should show 'Active' state")
