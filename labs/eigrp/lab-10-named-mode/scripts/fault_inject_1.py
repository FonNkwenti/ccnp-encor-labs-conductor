import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """SHA-256 Password Mismatch on R6 Tunnel8"""
    commands = [
        "router eigrp SKYNET_CORE",
        " address-family ipv4 autonomous-system 100",
        "  af-interface Tunnel8",
        "   authentication mode hmac-sha-256 WRONG_PASSWORD",
        "  exit-af-interface"
    ]
    injector = FaultInjector()
    injector.execute_commands(5006, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()
