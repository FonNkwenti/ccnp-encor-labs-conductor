#!/usr/bin/env python3
"""
Fault Injection Script: Shutdown Loopback Interfaces on R1

Injects:     Shuts down Loopback1, Loopback2, Loopback3 on R1
Target:      R1
Fault Type:  Interface State

Shuts down the loopback interfaces that originate the Enterprise
prefixes (192.168.X.0/24). The connected routes disappear from
the routing table, causing BGP network statements to become inactive.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R1"
CONSOLE_PORT = 5001

FAULT_COMMANDS = [
    "interface Loopback1",
    "shutdown",
    "interface Loopback2",
    "shutdown",
    "interface Loopback3",
    "shutdown",
]


def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Shutting down Loopback1/2/3 on R1 (FAULT)")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 3: Shutdown Loopbacks"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 3: Shutdown Loopbacks is now active.")
        print(f"[!] R1 will NOT advertise Enterprise prefixes (192.168.X.0/24)")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Shutdown Loopbacks")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
