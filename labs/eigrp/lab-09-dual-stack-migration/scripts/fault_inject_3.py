import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Disable IPv6 on Tunnel interface on R6"""
    commands = [
        "interface Tunnel8",
        " no ipv6 enable",
        " no ipv6 address 2001:DB8:ACAD:16::2/64"
    ]
    injector = FaultInjector()
    injector.execute_commands(5006, commands, "Challenge 3")
    print("\nChallenge 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()