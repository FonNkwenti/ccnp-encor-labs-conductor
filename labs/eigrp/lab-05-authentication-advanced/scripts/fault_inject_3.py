import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Route Map Tagging Removal on R3"""
    print("Injecting Challenge 3: Tagging Removal...")
    commands = [
        "router eigrp 100",
        " no redistribute connected route-map TAG_R5",
        " redistribute connected"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "R3 Remove Tagging")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()