"""
Fault Injection — Ticket 2
Removes the redistribution from R4's OSPF process.
R4 still has adjacency with R1 but no longer originates Type 7 LSA for 172.16.4.0/24.
The research subnet becomes unreachable from the backbone.
"""
from netmiko import ConnectHandler

R4 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5004,
    "timeout": 10,
}

fault_commands = [
    "router ospf 1",
    "no redistribute connected subnets",
]

def inject():
    print("Injecting Ticket 2 fault: removing redistribution from R4...")
    conn = ConnectHandler(**R4)
    conn.send_config_set(fault_commands)
    conn.send_command("write memory", read_timeout=10)
    conn.disconnect()
    print("Fault injected. R4 no longer redistributes connected interfaces.")
    print("Expected symptom: 172.16.4.0/24 absent from R2 routing table. Type 7 LSA gone.")

if __name__ == "__main__":
    inject()
