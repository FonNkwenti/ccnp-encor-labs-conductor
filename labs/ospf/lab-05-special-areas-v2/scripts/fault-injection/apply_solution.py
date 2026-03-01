"""
Restore all devices to the known-good (solution) state.
Run this after each troubleshooting ticket to reset the lab.
"""
from netmiko import ConnectHandler
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
solutions_dir = os.path.join(base_dir, "solutions")

devices = [
    ("R1", 5001, os.path.join(solutions_dir, "R1.cfg")),
    ("R2", 5002, os.path.join(solutions_dir, "R2.cfg")),
    ("R3", 5003, os.path.join(solutions_dir, "R3.cfg")),
    ("R7", 5007, os.path.join(solutions_dir, "R7.cfg")),
]

def restore(name, port, config_file):
    print(f"Restoring {name}...")
    try:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host="127.0.0.1",
            port=port,
            timeout=10,
        )
        with open(config_file, "r") as f:
            commands = [
                line.strip() for line in f
                if line.strip() and not line.startswith("!")
            ]
        conn.send_config_set(commands)
        conn.send_command("write memory", read_timeout=10)
        conn.disconnect()
        print(f"  {name} restored.")
    except Exception as e:
        print(f"  Failed to restore {name}: {e}")

if __name__ == "__main__":
    print("Restoring all devices to solution state...")
    for name, port, cfg in devices:
        restore(name, port, cfg)
    print("All devices restored.")
