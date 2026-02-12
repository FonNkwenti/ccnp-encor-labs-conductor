import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """MD5 Password Mismatch on R2"""
    commands = [
        "key chain SKYNET_MD5",
        " key 1",
        "  key-string WRONG_PASSWORD"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "Challenge 1")
    print("\nChallenge 1 fault injected successfully.")
    print("Refer to challenges.md for the symptom and goal.")

if __name__ == "__main__":
    inject()