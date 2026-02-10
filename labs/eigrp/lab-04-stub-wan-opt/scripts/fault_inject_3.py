import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Missing static keyword in stub config"""
    print("Injecting Challenge 3: Missing Static in Stub...")
    commands = [
        "ip route 192.168.99.0 255.255.255.0 Null0",
        "router eigrp 100",
        " redistribute static",
        " eigrp stub connected summary"
    ]
    injector = FaultInjector()
    injector.execute_commands(5005, commands, "R5 Redistribute Static but Stub restricted")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()