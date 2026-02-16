import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Area ID Mismatch on R3"""
    commands = [
        "router ospf 1",
        " no network 10.23.0.0 0.0.0.3 area 1",
        " network 10.23.0.0 0.0.0.3 area 100"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "Challenge 1")
    print("
Scenario 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
