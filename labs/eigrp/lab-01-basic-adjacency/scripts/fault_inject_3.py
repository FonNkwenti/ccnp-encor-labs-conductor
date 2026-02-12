import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Passive Interface on transit link R2 Fa0/1"""
    commands = [
        "router eigrp 100",
        " passive-interface FastEthernet0/1"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "Challenge 3")
    print("\nChallenge 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()