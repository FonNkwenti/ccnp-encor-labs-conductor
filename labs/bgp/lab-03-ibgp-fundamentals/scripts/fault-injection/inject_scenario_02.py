#!/usr/bin/env python3
"""
Fault Injection Script: Inaccessible next-hop

Injects:     Removes neighbor next-hop-self
Target:      R1
Fault Type:  Missing Configuration

Causes R1 to advertise external routes to R4 without changing the
next-hop attribute. R4 cannot route to the ISP physical IPs, so
the BGP routes remain invalid and are not installed in the RIB.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R1"
CONSOLE_PORT = 5001

FAULT_COMMANDS = [
    "router bgp 65001",
    "no neighbor 172.16.4.4 next-hop-self",
    "exit",
    "clear ip bgp 172.16.4.4 soft out"
]

def inject_fault():
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Removing 'next-hop-self' for neighbor R4 — FAULT")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 2: Inaccessible Next-Hop"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Scenario 2 active: R4 receives external routes with inaccessible next-hops")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Inaccessible Next-Hop")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
