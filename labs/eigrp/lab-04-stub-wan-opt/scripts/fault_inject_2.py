import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Timer Mismatch on R1/R2"""
    commands = [
        "interface FastEthernet1/0",
        " ip hello-interval eigrp 100 60",
        " ip hold-time eigrp 100 70"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 2")
    print("\nChallenge 2 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()