import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """SHA-256 Mode Error on R3"""
    print("Injecting Challenge 2: SHA-256 Mode Error...")
    # Change mode to MD5 on one side while other side is SHA-256
    commands = [
        "interface FastEthernet0/0",
        " no ip authentication mode eigrp 100 hmac-sha-256",
        " ip authentication mode eigrp 100 md5"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "R3 SHA-256 -> MD5")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()