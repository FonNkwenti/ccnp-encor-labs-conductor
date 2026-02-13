import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Wrong Tag Match in MATCH_TAG Route-Map on R1"""
    commands = [
        "route-map MATCH_TAG permit 10",
        " no match tag 555",
        " match tag 999"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 3")
    print("\nChallenge 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
