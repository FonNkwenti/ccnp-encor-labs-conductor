import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Summary AD Sabotage on R3"""
    print("Injecting Challenge 2: Summary AD Sabotage on R3...")
    commands = [
        "interface FastEthernet0/0",
        " ip summary-address eigrp 100 192.168.0.0 255.255.0.0 255"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "R3 Summary AD 255")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()