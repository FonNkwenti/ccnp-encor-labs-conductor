import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Passive-Interface on Wrong Interface (Fa1/0 instead of Lo0)"""
    commands = [
        "router eigrp SKYNET_CORE",
        " address-family ipv4 autonomous-system 100",
        "  af-interface Loopback0",
        "   no passive-interface",
        "  exit-af-interface",
        "  af-interface FastEthernet1/0",
        "   passive-interface",
        "  exit-af-interface"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "Challenge 3")
    print("\nChallenge 3 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
