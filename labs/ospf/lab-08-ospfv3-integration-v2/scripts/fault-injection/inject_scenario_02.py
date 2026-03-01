#!/usr/bin/env python3
"""
inject_scenario_02.py — Fault injection for Ticket 2
Works with workbook.md Section 9: Ticket 2
"""

import sys
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException

DEVICES = [{"name": "R3", "host": "127.0.0.1", "port": 5003}]

# Remove ospfv3 ipv6 activation from R3 Loopback0 only — IPv4 loopback still works
FAULT_COMMANDS = {
    "R3": [
        "interface Loopback0",
        " no ospfv3 1 ipv6 area 1",
        " exit",
    ],
}


def inject(device: dict) -> None:
    name = device["name"]
    commands = FAULT_COMMANDS.get(name, [])
    if not commands:
        return

    conn_params = {
        "device_type": "cisco_ios_telnet",
        "host": device["host"],
        "port": device["port"],
        "username": "",
        "password": "",
        "secret": "",
        "timeout": 30,
    }

    print(f"  [{name}] Injecting fault...")
    try:
        with ConnectHandler(**conn_params) as conn:
            conn.enable()
            conn.send_config_set(commands, cmd_verify=False)
            print(f"  [{name}] Fault injected.")
    except NetmikoTimeoutException:
        print(f"  [{name}] ERROR: Timeout — is {name} running in GNS3?")
    except Exception as exc:
        print(f"  [{name}] ERROR: {exc}")


def main() -> None:
    print("=" * 60)
    print("Injecting Fault: Ticket 2 — R3 Lo0 IPv6 OSPFv3 activation removed")
    print("=" * 60)
    for device in DEVICES:
        inject(device)
    print("Fault active. Work through Ticket 2 in workbook.md Section 9.")


if __name__ == "__main__":
    main()
