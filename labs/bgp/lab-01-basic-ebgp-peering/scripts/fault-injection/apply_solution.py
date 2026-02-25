#!/usr/bin/env python3
"""
Solution Restoration Script

Restores all devices to their correct BGP configuration,
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

# Correct BGP Configuration per Device (config-mode commands only)
CONFIGS = {
    "R1": [
        "interface Loopback1",
        "ip address 192.168.1.1 255.255.255.0",
        "no shutdown",
        "interface Loopback2",
        "ip address 192.168.2.1 255.255.255.0",
        "no shutdown",
        "interface Loopback3",
        "ip address 192.168.3.1 255.255.255.0",
        "no shutdown",
        "router bgp 65001",
        "bgp router-id 172.16.1.1",
        "neighbor 10.1.12.2 remote-as 65002",
        "neighbor 10.1.13.2 remote-as 65003",
        "network 172.16.1.1 mask 255.255.255.255",
        "network 192.168.1.0 mask 255.255.255.0",
        "network 192.168.2.0 mask 255.255.255.0",
        "network 192.168.3.0 mask 255.255.255.0",
    ],
    "R2": [
        "router bgp 65002",
        "bgp router-id 172.16.2.2",
        "no neighbor 10.1.12.1 remote-as 65003",
        "neighbor 10.1.12.1 remote-as 65001",
        "neighbor 10.1.23.2 remote-as 65003",
        "network 172.16.2.2 mask 255.255.255.255",
        "network 198.51.100.0 mask 255.255.255.0",
        "network 198.51.101.0 mask 255.255.255.0",
        "network 198.51.102.0 mask 255.255.255.0",
    ],
    "R3": [
        "router bgp 65003",
        "bgp router-id 172.16.3.3",
        "neighbor 10.1.13.1 remote-as 65001",
        "neighbor 10.1.23.1 remote-as 65002",
        "network 172.16.3.3 mask 255.255.255.255",
        "network 203.0.113.0 mask 255.255.255.0",
        "network 203.0.114.0 mask 255.255.255.0",
        "network 203.0.115.0 mask 255.255.255.0",
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
