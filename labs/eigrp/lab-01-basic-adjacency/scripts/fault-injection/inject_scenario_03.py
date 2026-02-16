#!/usr/bin/env python3
"""
Fault Injection Script: Missing Network Statement

Injects: Missing EIGRP Network Advertisement
Target Device: R1
Fault Type: Route Advertisement Error

This script connects to R1 via console and removes the network statement
for the Loopback0 interface, preventing it from being advertised to neighbors.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

# Device Configuration
DEVICE_NAME = "R1"
CONSOLE_PORT = 5001

# Fault Configuration Commands (config-mode commands only)
FAULT_COMMANDS = [
    "router eigrp 100",
    "no network 1.1.1.1 0.0.0.0",
]


def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Removing Loopback0 network statement (FAULT)")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 3: Missing Network Statement"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 3: Missing Network Statement is now active.")
        print(f"[!] R1's Loopback0 (1.1.1.1/32) will NOT be advertised to neighbors")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Missing Network Statement")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
