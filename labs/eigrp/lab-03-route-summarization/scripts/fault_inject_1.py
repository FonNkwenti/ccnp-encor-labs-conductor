import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Local Summary Blackhole on R1"""
    print("Injecting Challenge 1: Local Summary Blackhole on R1...")
    commands = [
        "interface FastEthernet1/0",
        " ip summary-address eigrp 100 172.16.0.0 255.255.0.0"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Local Summary (Blackhole)")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()