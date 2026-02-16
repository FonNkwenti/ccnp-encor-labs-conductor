import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def apply():
    """Restore all devices to correct OSPF Multi-Area configuration"""
    print("Restoring lab configuration...")
    
    # R2 Corrections
    r2_commands = [
        "router ospf 1",
        " network 10.12.0.0 0.0.0.3 area 0",
        " network 10.2.2.2 0.0.0.0 area 0",
        " network 10.23.0.0 0.0.0.3 area 1"
    ]
    
    # R3 Corrections
    r3_commands = [
        "router ospf 1",
        " no network 10.23.0.0 0.0.0.3 area 100",
        " no network 3.3.3.3 0.0.0.0 area 0",
        " network 10.23.0.0 0.0.0.3 area 1",
        " network 3.3.3.3 0.0.0.0 area 1"
    ]
    
    injector = FaultInjector()
    injector.execute_commands(5002, r2_commands, "Restore R2")
    injector.execute_commands(5003, r3_commands, "Restore R3")
    
    print("
Lab configuration restored successfully.")

if __name__ == "__main__":
    apply()
