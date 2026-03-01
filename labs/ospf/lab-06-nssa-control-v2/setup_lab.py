from netmiko import ConnectHandler
import os

class LabSetup:
    def __init__(self, devices):
        self.devices = devices

    def push_config(self, host, port, config_file):
        print(f"Connecting to {host}:{port}...")
        try:
            if not os.path.exists(config_file):
                print(f"  Error: Config file {config_file} not found.")
                return False
            conn = ConnectHandler(
                device_type='cisco_ios_telnet',
                host=host,
                port=port,
                timeout=5,
            )
            with open(config_file, 'r') as f:
                commands = [
                    line.strip() for line in f
                    if line.strip() and not line.startswith('!')
                ]
            conn.send_config_set(commands)
            conn.send_command("write memory", read_timeout=10)
            print(f"  Successfully loaded {config_file}")
            conn.disconnect()
            return True
        except Exception as e:
            print(f"  Failed to connect or push config: {e}")
            return False

    def run(self):
        print("Starting Lab Setup Automation...")
        for name, port, config in self.devices:
            print(f"--- Setting up {name} ---")
            self.push_config("127.0.0.1", port, config)
        print("Lab Setup Complete.")


base_dir = os.path.dirname(os.path.abspath(__file__))
initial_configs = os.path.join(base_dir, "initial-configs")

devices = [
    ("R1", 5001, os.path.join(initial_configs, "R1.cfg")),
    ("R2", 5002, os.path.join(initial_configs, "R2.cfg")),
    ("R3", 5003, os.path.join(initial_configs, "R3.cfg")),
    ("R4", 5004, os.path.join(initial_configs, "R4.cfg")),
    ("R7", 5007, os.path.join(initial_configs, "R7.cfg")),
]

if __name__ == "__main__":
    lab = LabSetup(devices)
    lab.run()
