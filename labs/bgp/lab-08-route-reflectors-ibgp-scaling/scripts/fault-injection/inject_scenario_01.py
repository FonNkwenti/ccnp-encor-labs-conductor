"""
Fault Injection — BGP Lab 08, Ticket 1
Removes next-hop-self from R1's neighbor statement for R6.
R1 continues to reflect ISP routes to R6, but the next-hop remains
the original eBGP peer address (10.1.12.2 or 10.1.13.2), which R6
cannot reach — causing R6's routing table to have no valid path to
ISP prefixes despite a populated BGP table.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from lab_utils import inject_fault

FAULT_COMMANDS = {
    "R1": [
        "router bgp 65001",
        "no neighbor 172.16.6.6 next-hop-self",
        "end",
        "clear ip bgp 172.16.6.6 soft out",
    ]
}

if __name__ == "__main__":
    inject_fault(FAULT_COMMANDS, host="127.0.0.1", port_map={"R1": 5001})
    print("Scenario 01 injected: next-hop-self removed for R6 on R1.")
    print("Symptom: R6 BGP table shows ISP routes but routing table has no valid path to internet.")
