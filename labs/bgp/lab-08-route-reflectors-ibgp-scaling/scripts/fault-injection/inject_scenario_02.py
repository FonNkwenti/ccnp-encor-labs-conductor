"""
Fault Injection — BGP Lab 08, Ticket 2
Removes the route-reflector-client designation from R4 on R1.
R4 becomes a non-client iBGP peer. Under iBGP split-horizon,
R1 cannot re-advertise routes learned from R6 (an iBGP peer) to
R4 (also an iBGP peer) unless R4 is an RR client.
R4 loses all routes from R6; R6 continues to receive R4's routes
because R6 is still an RR client.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from lab_utils import inject_fault

FAULT_COMMANDS = {
    "R1": [
        "router bgp 65001",
        "no neighbor 172.16.4.4 route-reflector-client",
        "end",
        "clear ip bgp 172.16.4.4 soft out",
    ]
}

if __name__ == "__main__":
    inject_fault(FAULT_COMMANDS, host="127.0.0.1", port_map={"R1": 5001})
    print("Scenario 02 injected: route-reflector-client removed for R4 on R1.")
    print("Symptom: R4 cannot reach R6 prefixes (192.168.6.0/24, 172.16.6.6/32).")
