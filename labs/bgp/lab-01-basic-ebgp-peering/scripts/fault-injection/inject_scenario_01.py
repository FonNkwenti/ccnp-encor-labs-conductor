#!/usr/bin/env python3
"""
Fault Injection Script: Wrong Remote-AS on R2

Injects:     Incorrect remote-as for R1 neighbor on R2
Target:      R2
Fault Type:  Parameter Mismatch

Changes R2's neighbor statement for R1 from remote-as 65001 to 65003,
causing the eBGP OPEN message validation to fail.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R2"
CONSOLE_PORT = 5002

FAULT_COMMANDS = [
    "router bgp 65002",
    "no neighbor 10.1.12.1 remote-as 65001",
    "neighbor 10.1.12.1 remote-as 65003",
]


def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Changing R2's remote-as for R1 from 65001 to 65003 (FAULT)")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 1: Wrong Remote-AS"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 1: Wrong Remote-AS is now active.")
        print(f"[!] R1-R2 eBGP session will NOT establish (AS mismatch in OPEN)")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Wrong Remote-AS")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
