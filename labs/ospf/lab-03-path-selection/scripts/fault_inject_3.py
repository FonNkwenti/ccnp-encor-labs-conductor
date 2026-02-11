import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Cost Applied to Wrong Interface"""
    print("Injecting Challenge 3: Cost on Wrong Interface...")
    commands_remove = [
        "interface FastEthernet1/1",
        " no ip ospf cost"
    ]
    commands_add = [
        "interface FastEthernet1/0",
        " ip ospf cost 50"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands_remove, "R1 Fa1/1 Remove Cost")
    injector.execute_commands(5001, commands_add, "R1 Fa1/0 Add Cost")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()
