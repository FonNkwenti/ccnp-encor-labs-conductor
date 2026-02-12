import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Prefix-List Gap on R1"""
    commands = [
        "ip prefix-list AUTHORIZED_NETS deny 10.0.12.0/30",
        "ip prefix-list AUTHORIZED_NETS seq 5 permit 2.2.2.2/32",
        "ip prefix-list AUTHORIZED_NETS seq 10 permit 3.3.3.3/32"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()