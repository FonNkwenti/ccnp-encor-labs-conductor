import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Offset-list to make direct link unattractive"""
    commands = [
        "access-list 10 permit 3.3.3.3",
        "router eigrp 100",
        " offset-list 10 in 1000000 FastEthernet1/1"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 3")
    print("\nChallenge 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()