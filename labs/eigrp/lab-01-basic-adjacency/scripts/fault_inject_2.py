import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """K-Value Mismatch on R3"""
    print("Injecting Challenge 2: K-Value Mismatch...")
    commands = [
        "router eigrp 100",
        " metric weights 0 1 1 1 1 1"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "R3 K-Value Mismatch")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()