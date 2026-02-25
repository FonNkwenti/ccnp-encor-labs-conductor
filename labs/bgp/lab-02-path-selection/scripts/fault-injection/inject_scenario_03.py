#!/usr/bin/env python3
"""
Fault Injection Script: MED Route-Map Applied Inbound Instead of Outbound

Injects:     MED route-maps applied 'in' instead of 'out' on R1's neighbors
Target:      R1
Fault Type:  Incorrect Policy Direction (in vs out)

Applies SET_MED_LOW and SET_MED_HIGH route-maps in the INBOUND direction
on R1's neighbor sessions. This modifies how R1 processes received routes
instead of setting MED on routes R1 advertises to the ISPs. Result: ISPs
see no MED values from R1.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R1"
CONSOLE_PORT = 5001

FAULT_COMMANDS = [
    "route-map SET_MED_LOW permit 10",
    "set metric 10",
    "exit",
    "route-map SET_MED_HIGH permit 10",
    "set metric 100",
    "exit",
    "router bgp 65001",
    "neighbor 10.1.12.2 route-map SET_MED_LOW in",
    "neighbor 10.1.13.2 route-map SET_MED_HIGH in",
    "no neighbor 10.1.12.2 route-map SET_MED_LOW out",
    "no neighbor 10.1.13.2 route-map SET_MED_HIGH out",
]


def inject_fault():
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Applying MED route-maps INBOUND instead of outbound — FAULT")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 3: MED Applied Inbound"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Scenario 3 active: MED route-maps applied inbound (wrong direction)")
        print(f"[!] R2 and R3 will see Enterprise prefixes with metric=0")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: MED Route-Map Applied Inbound")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
