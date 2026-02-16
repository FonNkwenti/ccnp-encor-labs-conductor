#!/usr/bin/env python3
"""
Solution Restoration Script

Restores all devices to their correct EIGRP configuration,
removing all injected faults from troubleshooting scenarios.

This script connects to all active devices and applies the
correct configuration from the lab solutions.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

# Device Console Port Mappings
DEVICES = {
    "R1": 5001,
    "R2": 5002,
    "R3": 5003,
}

# Correct EIGRP Configuration per Device (config-mode commands only)
CONFIGS = {
    "R1": [
        "no router eigrp 200",
        "router eigrp 100",
        "eigrp router-id 1.1.1.1",
        "network 1.1.1.1 0.0.0.0",
        "network 10.0.12.0 0.0.0.3",
        "passive-interface Loopback0",
        "no auto-summary",
    ],
    "R2": [
        "no router eigrp 200",
        "router eigrp 100",
        "eigrp router-id 2.2.2.2",
        "network 2.2.2.2 0.0.0.0",
        "network 10.0.12.0 0.0.0.3",
        "network 10.0.23.0 0.0.0.3",
        "passive-interface Loopback0",
        "no auto-summary",
    ],
    "R3": [
        "router eigrp 100",
        "no passive-interface default",
        "eigrp router-id 3.3.3.3",
        "network 3.3.3.3 0.0.0.0",
        "network 10.0.23.0 0.0.0.3",
        "passive-interface Loopback0",
        "no auto-summary",
    ],
}


def main():
    """Restore all devices to correct configuration."""
    print("=" * 60)
    print("Solution Restoration: Removing All Faults")
    print("=" * 60)

    injector = FaultInjector()
    success_count = 0
    fail_count = 0

    for device_name, port in DEVICES.items():
        print(f"\n[*] Restoring {device_name} (port {port})...")
        success = injector.execute_commands(
            port,
            CONFIGS[device_name],
            f"Restore {device_name}"
        )
        if success:
            print(f"[+] {device_name} restored successfully!")
            success_count += 1
        else:
            print(f"[!] Failed to restore {device_name}.")
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"Restoration Complete: {success_count} succeeded, {fail_count} failed")
    print("=" * 60)

    if fail_count > 0:
        print("[!] Some devices could not be restored. Check GNS3 and try again.")
        sys.exit(1)
    else:
        print("[+] All devices restored to correct configuration!")
        print("[+] Lab is ready for normal operation.")


if __name__ == "__main__":
    main()
