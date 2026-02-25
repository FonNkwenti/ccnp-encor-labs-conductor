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
    "R2": 5002,
    "R3": 5003,
}

CONFIGS = {
    "R1": [
        # Remove any fault-injected weight on R3
        "router bgp 65001",
        "no neighbor 10.1.13.2 weight 200",
        # Remove BROKEN_LP route-map if applied
        "no neighbor 10.1.12.2 route-map BROKEN_LP in",
        # Remove inbound MED route-maps if applied
        "no neighbor 10.1.12.2 route-map SET_MED_LOW in",
        "no neighbor 10.1.13.2 route-map SET_MED_HIGH in",
        # Restore correct permanent weight on R2 (Lab 02 solution)
        "neighbor 10.1.12.2 weight 100",
    ],
    "R2": [
        # Remove any prepend route-maps if they were applied
        "router bgp 65002",
        "no neighbor 10.1.12.1 route-map PREPEND_TO_R1 out",
    ],
    "R3": [
        # No changes needed for R3 in Lab 02 troubleshooting
        "do show ip bgp summary",
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
