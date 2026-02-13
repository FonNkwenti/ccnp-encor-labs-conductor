import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Wide Metrics Removed from R6"""
    commands = [
        "router eigrp SKYNET_CORE",
        " address-family ipv4 autonomous-system 100",
        "  topology base",
        "   no metric version 64bit",
        "   no metric rib-scale 128",
        "  exit-af-topology"
    ]
    injector = FaultInjector()
    injector.execute_commands(5006, commands, "Challenge 2")
    print("\nChallenge 2 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
