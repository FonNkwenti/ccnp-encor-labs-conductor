#!/usr/bin/env python3
"""
Fault Injection Script: Passive Interface Misconfiguration

Injects: Passive Interface Default with Wrong Exclusion
Target Device: R3
Fault Type: Interface Configuration Error

This script connects to R3 via console and configures passive-interface default,
then incorrectly excludes Loopback0 instead of the transit interface, preventing
adjacency formation with R2.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

# Device Configuration
DEVICE_NAME = "R3"
CONSOLE_PORT = 5003

# Fault Configuration Commands (config-mode commands only)
FAULT_COMMANDS = [
    "router eigrp 100",
    "passive-interface default",
    "no passive-interface Loopback0",
]


def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Configuring passive-interface default (FAULT)")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 2: Passive Interface Misconfiguration"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 2: Passive Interface Misconfiguration is now active.")
        print(f"[!] R3 will NOT form adjacency with R2 (all interfaces passive)")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Passive Interface Misconfiguration")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
