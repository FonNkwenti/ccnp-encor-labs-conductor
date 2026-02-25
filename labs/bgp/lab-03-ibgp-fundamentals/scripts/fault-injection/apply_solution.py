#!/usr/bin/env python3
"""
Solution Restoration Script

Restores all devices to their correct BGP configuration,
removing all injected faults from troubleshooting scenarios.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

DEVICES = {
    "R1": 5001,
    "R4": 5004,
}

CONFIGS = {
    "R1": [
        # Scenario 1 fix: Add missing update-source loopback0
        "router bgp 65001",
        "neighbor 172.16.4.4 update-source loopback0",
        # Scenario 2 fix: Add missing next-hop-self
        "neighbor 172.16.4.4 next-hop-self",
    ],
    "R4": [
        # Scenario 3 fix: Add missing OSPF network statement
        "router ospf 1",
        "network 10.1.14.0 0.0.0.3 area 0",
    ],
}


def main():
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
