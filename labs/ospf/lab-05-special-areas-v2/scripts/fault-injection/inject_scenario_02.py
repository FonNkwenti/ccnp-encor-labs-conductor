"""
Fault Injection — Ticket 2
Removes the Area 2 network statement from R3's OSPF process.
R3's Fa1/1 interface is no longer part of OSPF — R7 cannot form adjacency.
"""
from netmiko import ConnectHandler

R3 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5003,
    "timeout": 10,
}

fault_commands = [
    "router ospf 1",
    "no network 10.37.0.0 0.0.0.3 area 2",
]

def inject():
    print("Injecting Ticket 2 fault: removing Area 2 network statement from R3...")
    conn = ConnectHandler(**R3)
    conn.send_config_set(fault_commands)
    conn.send_command("write memory", read_timeout=10)
    conn.disconnect()
    print("Fault injected. R3's Fa1/1 subnet is no longer in OSPF.")
    print("Expected symptom: R7 has no neighbors, routing table shows only connected routes.")

if __name__ == "__main__":
    inject()
