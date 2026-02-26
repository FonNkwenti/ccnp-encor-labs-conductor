"""
Fault Injection — BGP Lab 08, Ticket 3
Removes update-source Loopback0 from R6's BGP neighbor statement for R1.
R6 will attempt to source the iBGP TCP session from its GigabitEthernet3/0
interface (10.1.16.2) instead of Loopback0 (172.16.6.6).
R1 expects connections from 172.16.6.6 and will reject the mismatched
source, leaving R6's session stuck in Active state.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from lab_utils import inject_fault

FAULT_COMMANDS = {
    "R6": [
        "router bgp 65001",
        "no neighbor 172.16.1.1 update-source Loopback0",
        "end",
        "clear ip bgp 172.16.1.1",
    ]
}

if __name__ == "__main__":
    inject_fault(FAULT_COMMANDS, host="127.0.0.1", port_map={"R6": 5006})
    print("Scenario 03 injected: update-source Loopback0 removed on R6.")
    print("Symptom: R6 BGP session to R1 (172.16.1.1) stuck in Active state.")
