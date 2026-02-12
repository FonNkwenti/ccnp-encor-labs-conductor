import socket
import time
import sys

class FaultInjector:
    def __init__(self, host="127.0.0.1"):
        self.host = host

    def execute_commands(self, port, commands, description="Injecting fault"):
        """
        Connects via Telnet and executes a list of configuration commands.
        """
        try:
            tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tn.settimeout(5)
            tn.connect((self.host, port))
            
            # Ensure prompt
            tn.sendall(b"\n")
            time.sleep(1)
            
            tn.sendall(b"enable\n")
            tn.sendall(b"configure terminal\n")
            time.sleep(0.5)

            for cmd in commands:
                tn.sendall(cmd.encode('ascii') + b"\n")
                time.sleep(0.2)
            
            tn.sendall(b"end\n")
            tn.sendall(b"exit\n")
            tn.close()
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

if __name__ == "__main__":
    # Example usage (dry run check)
    injector = FaultInjector()
    print("FaultInjector utility loaded.")