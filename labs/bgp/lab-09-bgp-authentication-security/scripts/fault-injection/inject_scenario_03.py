"""
Fault Injection — BGP Lab 09, Ticket 3
Two-part fault:
  1. Removes the bogon deny clause (sequence 5) from ISP-A-IN on R1
  2. Adds a bogon loopback (10.99.0.0/24) on R2 and advertises it via BGP
Result: A private-space route appears in R1's BGP table.
"""
from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
}

R2 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5002,
    "username": "",
    "password": "",
}

R1_FAULT_COMMANDS = [
    "no route-map ISP-A-IN deny 5",
]

R2_FAULT_COMMANDS = [
    "interface Loopback99",
    "ip address 10.99.0.1 255.255.255.0",
    "no shutdown",
    "exit",
    "router bgp 65002",
    "network 10.99.0.0 mask 255.255.255.0",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 3 fault (part 1): removing bogon deny from ISP-A-IN on R1...")
    with ConnectHandler(**R1) as conn:
        conn.enable()
        output = conn.send_config_set(R1_FAULT_COMMANDS)
        print(output)

    print("[*] Injecting Ticket 3 fault (part 2): advertising bogon 10.99.0.0/24 from R2...")
    with ConnectHandler(**R2) as conn:
        conn.enable()
        output = conn.send_config_set(R2_FAULT_COMMANDS)
        print(output)

    print("[+] Fault injected. Soft-clear inbound on R1 to apply the missing filter:")
    print("    R1# clear ip bgp 10.1.12.2 soft in")
    print("    R1# show ip bgp | begin Network  --> 10.99.0.0/24 should appear")
    print("    The student must identify the missing bogon filter and restore it.")
