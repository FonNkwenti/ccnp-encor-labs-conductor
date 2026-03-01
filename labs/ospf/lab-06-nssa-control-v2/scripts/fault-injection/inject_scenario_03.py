"""
Fault Injection — Ticket 3
Removes no-summary from R1, reverting Area 14 from Totally NSSA to regular NSSA.
R4 begins receiving all inter-area Type 3 LSAs — routing table grows unexpectedly.
"""
from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "timeout": 10,
}

fault_commands = [
    "router ospf 1",
    "no area 14 nssa no-summary",
    "area 14 nssa",
]

def inject():
    print("Injecting Ticket 3 fault: removing no-summary from R1 (Area 14 reverts to regular NSSA)...")
    conn = ConnectHandler(**R1)
    conn.send_config_set(fault_commands)
    conn.send_command("write memory", read_timeout=10)
    conn.disconnect()
    print("Fault injected. Area 14 is now regular NSSA — all inter-area Type 3 LSAs flood in.")
    print("Expected symptom: R4 routing table contains many O IA routes instead of just the default.")

if __name__ == "__main__":
    inject()
