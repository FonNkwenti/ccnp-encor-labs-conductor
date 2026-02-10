import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Offset-list to make direct link unattractive"""
    print("Injecting Challenge 3: Offset-list Metric Inflation...")
    commands = [
        "access-list 10 permit 3.3.3.3",
        "router eigrp 100",
        " offset-list 10 in 1000000 FastEthernet1/1"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Offset-list")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()