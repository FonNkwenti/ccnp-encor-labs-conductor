from netmiko import ConnectHandler


class FaultInjector:
    def __init__(self, host="127.0.0.1"):
        self.host = host

    def _connect(self, port):
        """Create a Netmiko connection to a GNS3 console port."""
        device = {
            "device_type": "cisco_ios_telnet",
            "host": self.host,
            "port": port,
            "username": "",
            "password": "",
            "secret": "",
            "timeout": 10,
        }
        return ConnectHandler(**device)

    def execute_commands(self, port, commands, description="Injecting fault"):
        """
        Connects to a GNS3 console via Netmiko and executes IOS
        configuration commands.
        """
        try:
            conn = self._connect(port)
            output = conn.send_config_set(commands)
            conn.disconnect()
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False


if __name__ == "__main__":
    injector = FaultInjector()
    print("FaultInjector utility loaded.")
