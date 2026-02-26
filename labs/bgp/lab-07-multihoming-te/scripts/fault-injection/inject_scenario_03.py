"""
Fault Injection — BGP Lab 07, Ticket 3
Changes the Local Preference set in ISP-A-IN route-map from 200 to 50 for ISP-A prefixes.
R1 now assigns LP=50 to ISP-A-origin prefixes, making them LESS preferred than the
LP=100 default applied to ISP-B paths. All traffic exits via ISP-B regardless of destination.
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from lab_utils import inject_fault

FAULT_COMMANDS = {
    "R1": [
        # Change LP from 200 to 50 for ISP-A prefixes in ISP-A-IN
        "route-map ISP-A-IN permit 10",
        "set local-preference 50",
        "exit",
        "clear ip bgp 10.1.12.2 soft in",
    ]
}

if __name__ == "__main__":
    inject_fault(FAULT_COMMANDS, host="127.0.0.1", port_map={"R1": 5001})
    print("Scenario 03 injected: ISP-A-IN sets LP=50 (inverted — lower than default LP=100).")
    print("Symptom: all outbound traffic exits via ISP-B regardless of destination prefix.")
