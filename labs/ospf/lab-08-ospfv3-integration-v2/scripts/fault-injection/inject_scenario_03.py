#!/usr/bin/env python3
"""
inject_scenario_03.py — Fault injection for Ticket 3
Works with workbook.md Section 9: Ticket 3
"""

import sys
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException

DEVICES = [{"name": "R6", "host": "127.0.0.1", "port": 5006}]

# Remove ospfv3 ipv4 activation from R6 Gi3/0 — IPv6 AF works, IPv4 routes missing
FAULT_COMMANDS = {
    "R6": [
        "interface GigabitEthernet3/0",
        " no ospfv3 1 ipv4 area 0",
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
    print("Injecting Fault: Ticket 3 — R6 Gi3/0 IPv4 OSPFv3 activation removed")
    print("=" * 60)
    for device in DEVICES:
        inject(device)
    print("Fault active. Work through Ticket 3 in workbook.md Section 9.")


if __name__ == "__main__":
    main()
