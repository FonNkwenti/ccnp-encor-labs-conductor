import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """MD5 Password Mismatch on R2"""
    print("Injecting Challenge 1: MD5 Password Mismatch...")
    commands = [
        "key chain SKYNET_MD5",
        " key 1",
        "  key-string WRONG_PASSWORD"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 MD5 Mismatch")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()