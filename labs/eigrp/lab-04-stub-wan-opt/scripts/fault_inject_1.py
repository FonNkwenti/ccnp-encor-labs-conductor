import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Receive-Only Stub on R5"""
    commands = [
        "router eigrp 100",
        " eigrp stub receive-only"
    ]
    injector = FaultInjector()
    injector.execute_commands(5005, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()