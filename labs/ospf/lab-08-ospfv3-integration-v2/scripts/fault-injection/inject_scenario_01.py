#!/usr/bin/env python3
"""
inject_scenario_01.py — Fault injection for Ticket 1
Works with workbook.md Section 9: Ticket 1
"""

import sys
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException

DEVICES = [{"name": "R6", "host": "127.0.0.1", "port": 5006}]

# Remove ipv6 unicast-routing from R6 — kills all IPv6 OSPFv3 adjacency
FAULT_COMMANDS = {
    "R6": ["no ipv6 unicast-routing"],
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
    print("Injecting Fault: Ticket 1 — ipv6 unicast-routing removed from R6")
    print("=" * 60)
    for device in DEVICES:
        inject(device)
    print("Fault active. Work through Ticket 1 in workbook.md Section 9.")


if __name__ == "__main__":
    main()
