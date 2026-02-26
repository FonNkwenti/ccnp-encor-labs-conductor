"""
Fault Injection — BGP Lab 07, Ticket 2
Moves the AS-path prepend for 192.168.2.0/24 from OUTBOUND-ISP-B to OUTBOUND-ISP-A.
R1 will now prepend toward ISP-A (wrong direction), causing inbound traffic for
192.168.2.0/24 to prefer the ISP-B path instead of ISP-A.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from lab_utils import inject_fault

FAULT_COMMANDS = {
    "R1": [
        # Remove correct prepend from OUTBOUND-ISP-B
        "no route-map OUTBOUND-ISP-B permit 10",
        "route-map OUTBOUND-ISP-B permit 10",
        "exit",
        # Add wrong prepend to OUTBOUND-ISP-A (192.168.2.0/24 prepended toward ISP-A)
        "no route-map OUTBOUND-ISP-A permit 10",
        "route-map OUTBOUND-ISP-A permit 10",
        "match ip address prefix-list ENTERPRISE-192-168-2",
        "set as-path prepend 65001 65001 65001",
        "exit",
        "clear ip bgp 10.1.12.2 soft out",
        "clear ip bgp 10.1.13.2 soft out",
    ]
}

if __name__ == "__main__":
    inject_fault(FAULT_COMMANDS, host="127.0.0.1", port_map={"R1": 5001})
    print("Scenario 02 injected: 192.168.2.0/24 AS-path prepend applied toward wrong ISP (ISP-A).")
    print("Symptom: inbound traffic for 192.168.2.0/24 enters via ISP-B instead of ISP-A.")
