#!/usr/bin/env python3
"""
Fault Injection Script: Broken IGP preventing BGP peering

Injects:     Removes OSPF network statement for physical link
Target:      R4
Fault Type:  IGP Failure

Breaks OSPF adjacency between R1 and R4. Without OSPF, R4 loses
reachability to R1's loopback, bringing down the entire iBGP session.
"""

import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R4"
CONSOLE_PORT = 5004

FAULT_COMMANDS = [
    "router ospf 1",
    "no network 10.1.14.0 0.0.0.3 area 0"
]

def inject_fault():
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Removing OSPF network statement for Fa0/0 — FAULT")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 3: IGP Failure"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Scenario 3 active: R4 loses OSPF adjacency with R1")
        print(f"[!] Note: BGP session will drop after the OSPF/BGP hold timers expire (~minutes).")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Broken IGP")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
