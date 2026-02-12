import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Implicit Deny on R2 Route-Map"""
    commands = [
        "no route-map RM_FILTER_R3 permit 20",
        "route-map RM_FILTER_R3 deny 10",
        " match ip address prefix-list R1_LOOP"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "Challenge 2")
    print("\nChallenge 2 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()