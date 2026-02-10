import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Extreme Delay on Primary Link"""
    print("Injecting Challenge 2: Primary Link Delay Inflation...")
    commands = [
        "interface FastEthernet1/0",
        " delay 100000"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Fa1/0 High Delay")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()