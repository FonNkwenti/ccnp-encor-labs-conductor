#!/usr/bin/env python3
"""
Fault Injection Script: BGP active state due to missing update-source

Injects:     Removes neighbor update-source loopback0
Target:      R1
Fault Type:  Missing Configuration

Causes R1 to source BGP packets from its physical interface instead
of its Loopback0 interface, leading to a TCP session failure with
R4 (which expects packets from 172.16.1.1).
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R1"
CONSOLE_PORT = 5001

FAULT_COMMANDS = [
    "router bgp 65001",
    "no neighbor 172.16.4.4 update-source Loopback0"
]

def inject_fault():
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Removing 'update-source Loopback0' for neighbor R4 — FAULT")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 1: Missing Update-Source"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Scenario 1 active: R1 BGP session with R4 will stay in Active state")
        print(f"[!] Run: clear ip bgp * soft  on R1 to speed up TCP failure if needed")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Missing Update-Source")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
