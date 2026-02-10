import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """AS Number Mismatch on R2"""
    print("Injecting Challenge 1: AS Number Mismatch...")
    commands = [
        "no router eigrp 100",
        "router eigrp 200",
        " network 2.2.2.2 0.0.0.0",
        " network 10.0.12.0 0.0.0.3",
        " network 10.0.23.0 0.0.0.3"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 AS Mismatch")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()