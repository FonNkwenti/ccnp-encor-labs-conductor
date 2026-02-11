import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Reference Bandwidth Mismatch on R2"""
    print("Injecting Challenge 1: Reference Bandwidth Mismatch...")
    commands = [
        "router ospf 1",
        " no auto-cost reference-bandwidth"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 Reference BW Reset")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()
