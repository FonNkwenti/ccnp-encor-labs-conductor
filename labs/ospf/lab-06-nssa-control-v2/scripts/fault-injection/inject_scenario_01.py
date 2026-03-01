"""
Fault Injection — Ticket 1
Removes the NSSA configuration from R4, creating an area type mismatch.
R1 retains nssa; R4 reverts to normal area. Adjacency drops.
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
    "no area 14 nssa",
]

def inject():
    print("Injecting Ticket 1 fault: removing NSSA config from R4...")
    conn = ConnectHandler(**R4)
    conn.send_config_set(fault_commands)
    conn.send_command("write memory", read_timeout=10)
    conn.disconnect()
    print("Fault injected. R4 Area 14 is now a normal area.")
    print("Expected symptom: R4 shows no OSPF neighbors (N-bit mismatch with R1).")

if __name__ == "__main__":
    inject()
