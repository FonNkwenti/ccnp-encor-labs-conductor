#!/usr/bin/env python3
"""
Fault Injection Script: Low Local Preference on R2 Routes

Injects:     route-map setting LP=50 applied inbound on R1's R2 neighbor
Target:      R1
Fault Type:  Incorrect Policy Direction / Wrong Attribute Value

Applies a route-map that sets local-preference=50 (below the default
of 100) for all routes received from R2. This makes R3 always win for
all prefixes, opposite of the intended primary/backup policy.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R1"
CONSOLE_PORT = 5001

FAULT_COMMANDS = [
    "route-map BROKEN_LP permit 10",
    "set local-preference 50",
    "exit",
    "router bgp 65001",
    "neighbor 10.1.12.2 route-map BROKEN_LP in",
]


def inject_fault():
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Applying LP=50 route-map inbound on R2 neighbor — FAULT")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 2: Low Local Preference"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Scenario 2 active: all R2 routes have LP=50 (below default 100)")
        print(f"[!] Run: clear ip bgp 10.1.12.2 soft in  on R1 to activate policy")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Low Local Preference on R2 Routes")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
