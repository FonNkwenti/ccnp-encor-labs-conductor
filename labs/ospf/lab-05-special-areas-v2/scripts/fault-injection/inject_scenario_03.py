"""
Fault Injection — Ticket 3
Removes totally-stubby config from R3, reverting Area 2 to a regular stub.
R7 now receives all inter-area Type 3 LSAs — routing table grows unexpectedly.
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
    "area 2 stub",
]

def inject():
    print("Injecting Ticket 3 fault: removing no-summary from R3 (Area 2 reverts to stub)...")
    conn = ConnectHandler(**R3)
    conn.send_config_set(fault_commands)
    conn.send_command("write memory", read_timeout=10)
    conn.disconnect()
    print("Fault injected. Area 2 is now a regular stub — all inter-area Type 3 LSAs flood in.")
    print("Expected symptom: R7 routing table contains many O IA routes instead of just the default.")

if __name__ == "__main__":
    inject()
