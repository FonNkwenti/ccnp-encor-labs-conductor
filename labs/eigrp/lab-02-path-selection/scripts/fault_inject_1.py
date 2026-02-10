import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Feasibility Condition Failure"""
    print("Injecting Challenge 1: Feasibility Condition Failure...")
    commands = [
        "interface Loopback0",
        " delay 20000"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "R3 Loopback Delay (Feasibility)")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()