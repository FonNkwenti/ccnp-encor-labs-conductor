import sys
import os
import telnetlib
import time

# Add common tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))

class LabRefresher:
    def __init__(self, devices):
        self.devices = devices  # List of (name, port, config_path)

    def push_config(self, host, port, config_file):
        print(f"Refreshing {host}:{port} with {config_file}...")
        try:
            tn = telnetlib.Telnet(host, port, timeout=5)
            tn.write(b"\n")
            time.sleep(0.5)
            tn.write(b"enable\n")
            tn.write(b"configure terminal\n")
            
            with open(config_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('!'):
                        tn.write(line.encode('ascii') + b"\n")
                        time.sleep(0.1)
            
            tn.write(b"end\n")
            tn.write(b"write memory\n")
            tn.close()
            print(f"  Successfully refreshed.")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
            return False

    def run(self):
        for name, port, config in self.devices:
            config_path = os.path.join(os.path.dirname(__file__), "..", config)
            self.push_config("127.0.0.1", port, config_path)

if __name__ == "__main__":
    devices = [
        ("R1", 5001, "solutions/R1.cfg"),
        ("R2", 5002, "solutions/R2.cfg"),
        ("R3", 5003, "solutions/R3.cfg"),
        ("R7", 5007, "solutions/R7.cfg")
    ]
    refresher = LabRefresher(devices)
    refresher.run()
    print("\nLab 03 has been refreshed to the 'Solution' state.")