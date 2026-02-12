import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """AS Number Mismatch for IPv6 AF on R2"""
    commands = [
        "router eigrp SKYNET_CORE",
        " no address-family ipv6 autonomous-system 100",
        " address-family ipv6 autonomous-system 666",
        "  topology base",
        "  exit-af-topology"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "Challenge 2")
    print("\nChallenge 2 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()