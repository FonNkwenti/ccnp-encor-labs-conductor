import sys
import os
import socket
import time

# Add common tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))

class LabRefresher:
    def __init__(self, devices):
        self.devices = devices  # List of (name, port, config_path)

    def push_config(self, host, port, config_file):
        print(f"Refreshing {host}:{port} with {config_file}...")
        try:
            tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tn.settimeout(5)
            tn.connect((host, port))
            tn.sendall(b"\r\n")
            time.sleep(0.5)
            tn.sendall(b"enable\r\n")
            time.sleep(0.3)
            tn.sendall(b"configure terminal\r\n")
            
            with open(config_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('!'):
                        tn.sendall(line.encode('ascii') + b"\r\n")
                        time.sleep(0.1)
            
            tn.sendall(b"end\r\n")
            tn.sendall(b"write memory\r\n")
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
        ("R4", 5004, "solutions/R4.cfg"),
        ("R5", 5005, "solutions/R5.cfg"),
        ("R6", 5006, "solutions/R6.cfg"),
        ("R7", 5007, "solutions/R7.cfg")
    ]
    refresher = LabRefresher(devices)
    refresher.run()
    print("\nLab 09 has been refreshed to the 'Solution' state.")