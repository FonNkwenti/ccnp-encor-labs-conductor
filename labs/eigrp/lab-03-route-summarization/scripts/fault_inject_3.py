import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Overly Aggressive Boundary on R7"""
    print("Injecting Challenge 3: Overly Aggressive Summary on R7...")
    commands = [
        "interface FastEthernet0/0",
        " no ip summary-address eigrp 100 172.16.0.0 255.255.0.0",
        " ip summary-address eigrp 100 0.0.0.0 0.0.0.0"
    ]
    injector = FaultInjector()
    injector.execute_commands(5007, commands, "R7 Default Route Summary")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()