import socket
import time
import sys

class FaultInjector:
    def __init__(self, host="127.0.0.1"):
        self.host = host

    def _handle_telnet_negotiation(self, sock):
        """Handle telnet protocol negotiation (IAC sequences)."""
        sock.settimeout(0.5)
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                # Look for telnet IAC (0xFF) sequences and ignore them
                # In a real implementation, we'd respond appropriately,
                # but for our use case we just drain the buffer
                if not data.startswith(b'\xff'):
                    # Got non-IAC data
                    break
        except socket.timeout:
            pass

    def _read_until_prompt(self, sock, timeout=2):
        """Read from socket until we get a prompt (# or >) or timeout."""
        sock.settimeout(timeout)
        data = b""
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Look for IOS prompt patterns
                lines = data.split(b'\n')
                for line in lines:
                    line = line.strip()
                    if line.endswith(b'#') or line.endswith(b'>'):
                        return data
        except socket.timeout:
            pass
        return data

    def execute_commands(self, port, commands, description="Injecting fault"):
        """
        Connects via Telnet and executes a list of configuration commands.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host, port))

            # Drain initial telnet negotiation/banner
            time.sleep(0.5)
            self._read_until_prompt(sock, 2)

            # Send newline to activate prompt
            sock.sendall(b"\n")
            time.sleep(0.2)
            self._read_until_prompt(sock, 1)

            # Enter enable mode
            sock.sendall(b"enable\n")
            time.sleep(0.2)
            self._read_until_prompt(sock, 1)

            # Enter config mode
            sock.sendall(b"configure terminal\n")
            time.sleep(0.3)
            self._read_until_prompt(sock, 1)

            # Execute each command with appropriate delays
            for cmd in commands:
                sock.sendall(cmd.encode('ascii') + b"\n")
                time.sleep(0.25)
                self._read_until_prompt(sock, 1)

            # Exit config mode
            sock.sendall(b"end\n")
            time.sleep(0.2)
            self._read_until_prompt(sock, 1)

            # Close connection gracefully
            sock.sendall(b"exit\n")
            time.sleep(0.1)
            sock.close()
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

if __name__ == "__main__":
    # Example usage (dry run check)
    injector = FaultInjector()
    print("FaultInjector utility loaded.")