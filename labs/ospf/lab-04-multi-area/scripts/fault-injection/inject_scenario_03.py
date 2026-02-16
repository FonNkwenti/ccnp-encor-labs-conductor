import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Intra-Area instead of Inter-Area on R3 Loopback"""
    commands = [
        "router ospf 1",
        " no network 3.3.3.3 0.0.0.0 area 1",
        " network 3.3.3.3 0.0.0.0 area 0"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "Challenge 3")
    print("
Scenario 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
