#!/usr/bin/env python3
"""
Fault Injection Script: Missing Network Statements on R3

Injects:     Removes all BGP network statements from R3
Target:      R3
Fault Type:  Missing Configuration

Removes all network advertisement statements from R3's BGP process,
so R3 peers are Established but receive zero prefixes from AS 65003.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICE_NAME = "R3"
CONSOLE_PORT = 5003

FAULT_COMMANDS = [
    "router bgp 65003",
    "no network 172.16.3.3 mask 255.255.255.255",
    "no network 203.0.113.0 mask 255.255.255.0",
    "no network 203.0.114.0 mask 255.255.255.0",
    "no network 203.0.115.0 mask 255.255.255.0",
]


def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Injecting fault on {DEVICE_NAME} (port {CONSOLE_PORT})...")
    print(f"[*] Removing all network statements from R3's BGP (FAULT)")

    injector = FaultInjector()
    success = injector.execute_commands(
        CONSOLE_PORT,
        FAULT_COMMANDS,
        "Scenario 2: Missing Network Statements"
    )

    if success:
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 2: Missing Network Statements is now active.")
        print(f"[!] R3 will NOT advertise any prefixes to its BGP peers")
    else:
        print(f"[!] Failed to inject fault on {DEVICE_NAME}.")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Fault Injection: Missing Network Statements")
    print("=" * 60)
    inject_fault()
    print("=" * 60)
