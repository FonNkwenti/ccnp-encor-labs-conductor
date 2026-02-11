import telnetlib
import sys
import time
import os

class LabSetup:
    def __init__(self, devices):
        self.devices = devices

    def push_config(self, host, port, config_file):
        print(f"Connecting to {host}:{port}...")
        try:
            tn = telnetlib.Telnet(host, port, timeout=5)
            tn.write(b"\n")
            time.sleep(1)
            tn.write(b"enable\n")
            tn.write(b"configure terminal\n")
            if not os.path.exists(config_file):
                print(f"  Error: Config file {config_file} not found.")
                return False
            with open(config_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('!'):
                        tn.write(line.encode('ascii') + b"\n")
                        time.sleep(0.1)
            tn.write(b"end\n")
            tn.write(b"write memory\n")
            print(f"  Successfully loaded {config_file}")
            tn.close()
            return True
        except Exception as e:
            print(f"  Failed to connect or push config: {e}")
            return False

    def run(self):
        print("Starting Lab Setup Automation...")
        for name, port, config in self.devices:
            print(f"--- Setting up {name} ---")
            config_path = os.path.join(os.path.dirname(__file__), config)
            self.push_config("127.0.0.1", port, config_path)
        print("Lab Setup Complete.")

if __name__ == "__main__":
    devices = [("R1", 5001, "initial-configs/R1.cfg"), ("R2", 5002, "initial-configs/R2.cfg"), ("R3", 5003, "initial-configs/R3.cfg")]
    LabSetup(devices).run()
