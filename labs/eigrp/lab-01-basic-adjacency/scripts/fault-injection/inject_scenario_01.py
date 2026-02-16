#!/usr/bin/env python3
"""
Fault Injection Script: AS Number Mismatch

Injects: EIGRP AS Number Mismatch
Target Device: R2
Fault Type: Protocol Parameter Mismatch

This script connects to R2 via console and changes the EIGRP AS number
from 100 to 200, preventing adjacency formation with R1.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

# Device Configuration
DEVICE_NAME = "R2"
CONSOLE_PORT = 5002

# Fault Configuration Commands (config-mode commands only)
FAULT_COMMANDS = [
    "no router eigrp 100",
    "router eigrp 200",
    "eigrp router-id 2.2.2.2",
    "network 2.2.2.2 0.0.0.0",
    "network 10.0.12.0 0.0.0.3",
    "network 10.0.23.0 0.0.0.3",
    "passive-interface Loopback0",
    "no auto-summary",
]


def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Changing EIGRP AS from 100 to 200 (FAULT)")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 1: AS Number Mismatch"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 1: AS Number Mismatch is now active.")
        print(f"[!] R2 will NOT form adjacency with R1 (AS mismatch)")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: AS Number Mismatch")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
