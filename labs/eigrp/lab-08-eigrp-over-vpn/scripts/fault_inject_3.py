import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Destination Unreachable (Physical Link Down) on R1"""
    commands = [
        "interface GigabitEthernet3/0",
        " shutdown"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 3")
    print("\nChallenge 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()