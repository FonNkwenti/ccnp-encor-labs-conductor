#!/usr/bin/env python3
"""
Fault Injection Script: Weight on Wrong Neighbor

Injects:     weight 200 on R3 neighbor (10.1.13.2) on R1
Target:      R1
Fault Type:  Incorrect Path Selection Policy

Sets weight=200 for all routes received from R3, overriding the
shorter AS-path from R2. R1 now prefers R3 for all prefixes including
ISP-A prefixes that have a shorter direct path via R2.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R1"
CONSOLE_PORT = 5001

FAULT_COMMANDS = [
    "router bgp 65001",
    "neighbor 10.1.13.2 weight 200",
]


def inject_fault():
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Setting weight=200 on neighbor R3 (10.1.13.2) — FAULT")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 1: Weight on Wrong Neighbor"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Scenario 1 active: R1 will prefer R3 for ALL prefixes (weight override)")
        print(f"[!] Run: clear ip bgp 10.1.13.2 soft  on R1 to trigger best-path recalculation")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Weight on Wrong Neighbor")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
