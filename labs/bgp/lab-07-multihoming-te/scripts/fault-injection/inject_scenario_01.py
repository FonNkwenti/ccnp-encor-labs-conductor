"""
Fault Injection — BGP Lab 07, Ticket 1
Injects a misconfigured sentinel prefix-list for the conditional default route.
The CHECK-ISP-UP route-map now references a non-existent prefix (198.51.110.0/24),
so R1 will never send the default route to R4 even when ISP sessions are active.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from lab_utils import inject_fault

FAULT_COMMANDS = {
    "R1": [
        "no ip prefix-list ISP-A-REACHABILITY",
        "ip prefix-list ISP-A-REACHABILITY seq 10 permit 198.51.110.0/24",
        "clear ip bgp 172.16.4.4 soft out",
    ]
}

if __name__ == "__main__":
    inject_fault(FAULT_COMMANDS, host="127.0.0.1", port_map={"R1": 5001})
    print("Scenario 01 injected: conditional default sentinel prefix-list misconfigured on R1.")
    print("Symptom: R4 has no default route even though ISP sessions are Established.")
