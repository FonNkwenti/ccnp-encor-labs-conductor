import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Passive Interface on transit link R2 Fa0/1"""
    print("Injecting Challenge 3: Passive Transit Interface...")
    commands = [
        "router eigrp 100",
        " passive-interface FastEthernet0/1"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 Passive Fa0/1")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()