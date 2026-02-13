import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Route Map Tagging Removal on R3"""
    commands = [
        "router eigrp 100",
        " no distribute-list route-map TAG_R5 out FastEthernet0/0",
        " redistribute connected"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "Challenge 2")
    print("\nChallenge 2 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
