"""
Fault Injection — Ticket 1
Removes the stub configuration from R3, creating an OSPF area type mismatch.
R7 retains its stub config; adjacency will not form.
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
    "no area 2 stub no-summary",
    "no area 2 stub",
]

def inject():
    print("Injecting Ticket 1 fault: removing stub config from R3...")
    conn = ConnectHandler(**R3)
    conn.send_config_set(fault_commands)
    conn.send_command("write memory", read_timeout=10)
    conn.disconnect()
    print("Fault injected. R3 Area 2 is now a normal area.")
    print("Expected symptom: R7 shows no OSPF neighbors.")

if __name__ == "__main__":
    inject()
