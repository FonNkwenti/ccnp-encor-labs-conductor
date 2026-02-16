import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """ABR Isolation on R2 (Remove Area 0)"""
    commands = [
        "router ospf 1",
        " no network 10.12.0.0 0.0.0.3 area 0",
        " no network 10.2.2.2 0.0.0.0 area 0"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "Challenge 2")
    print("
Scenario 2 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
