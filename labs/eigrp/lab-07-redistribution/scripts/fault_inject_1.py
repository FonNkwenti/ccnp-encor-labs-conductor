import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Missing Seed Metric for EIGRP"""
    commands = [
        "router eigrp 100",
        " no redistribute ospf 1",
        " redistribute ospf 1"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()