import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Local Summary Blackhole on R1"""
    commands = [
        "interface FastEthernet1/0",
        " ip summary-address eigrp 100 172.16.0.0 255.255.0.0"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()