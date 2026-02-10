import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Receive-Only Stub on R5"""
    print("Injecting Challenge 1: Receive-Only Stub on R5...")
    commands = [
        "router eigrp 100",
        " eigrp stub receive-only"
    ]
    injector = FaultInjector()
    injector.execute_commands(5005, commands, "R5 Receive-Only")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()