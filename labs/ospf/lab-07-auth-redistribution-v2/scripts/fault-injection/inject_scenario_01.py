#!/usr/bin/env python3
"""
inject_scenario_01.py — Fault injection for Ticket 1
Works with workbook.md Section 9: Ticket 1
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException

DEVICES = [
    {"name": "R2", "host": "127.0.0.1", "port": 5002},
    {"name": "R3", "host": "127.0.0.1", "port": 5003},
]

# Introduce a wrong key-string on R2 and R3 — key ID matches but string differs
FAULT_COMMANDS = {
    "R2": [
        "key chain OSPF_AUTH",
        " key 1",
        "  key-string WrongKey!XYZ",
        "  cryptographic-algorithm hmac-sha-256",
        "  exit",
        " exit",
    ],
    "R3": [
        "key chain OSPF_AUTH",
        " key 1",
        "  key-string WrongKey!XYZ",
        "  cryptographic-algorithm hmac-sha-256",
        "  exit",
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
    print("Injecting Fault: Ticket 1 — Area 0 auth key mismatch")
    print("=" * 60)
    for device in DEVICES:
        inject(device)
    print("Fault active. Work through Ticket 1 in workbook.md Section 9.")


if __name__ == "__main__":
    main()
