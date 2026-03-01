#!/usr/bin/env python3
"""
inject_scenario_02.py — Fault injection for Ticket 2
Works with workbook.md Section 9: Ticket 2
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException

DEVICES = [
    {"name": "R2", "host": "127.0.0.1", "port": 5002},
]

# Remove the redistribute statement from OSPF on R2
FAULT_COMMANDS = {
    "R2": [
        "router ospf 1",
        " no redistribute eigrp 100 subnets route-map EIGRP_TO_OSPF",
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
    print("Injecting Fault: Ticket 2 — Redistribution removed from R2")
    print("=" * 60)
    for device in DEVICES:
        inject(device)
    print("Fault active. Work through Ticket 2 in workbook.md Section 9.")


if __name__ == "__main__":
    main()
