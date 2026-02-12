import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Feasibility Condition Failure"""
    commands = [
        "interface Loopback0",
        " delay 20000"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()