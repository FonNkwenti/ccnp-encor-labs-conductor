import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Excessive Manual Cost on Direct Link"""
    print("Injecting Challenge 2: Excessive Cost on R1 Fa1/1...")
    commands = [
        "interface FastEthernet1/1",
        " ip ospf cost 65535"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Fa1/1 Max Cost")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()
