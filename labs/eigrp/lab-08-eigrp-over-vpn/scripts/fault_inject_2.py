import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """MTU Mismatch / Too Large on R6"""
    commands = [
        "interface Tunnel8",
        " no ip mtu",
        " ip mtu 1500"
    ]
    injector = FaultInjector()
    injector.execute_commands(5006, commands, "Challenge 2")
    print("\nChallenge 2 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()