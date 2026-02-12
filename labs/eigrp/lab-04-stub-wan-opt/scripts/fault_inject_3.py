import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Missing static keyword in stub config"""
    commands = [
        "ip route 192.168.99.0 255.255.255.0 Null0",
        "router eigrp 100",
        " redistribute static",
        " eigrp stub connected summary"
    ]
    injector = FaultInjector()
    injector.execute_commands(5005, commands, "Challenge 3")
    print("\nChallenge 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()