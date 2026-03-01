#!/usr/bin/env python3
"""
apply_solution.py — Restore all devices to known-good (solution) state.
Loads solutions/ configs onto R1, R2, R3, R5.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException

LAB_DIR = os.path.join(os.path.dirname(__file__), "../..")

DEVICES = [
    {"name": "R1", "host": "127.0.0.1", "port": 5001},
    {"name": "R2", "host": "127.0.0.1", "port": 5002},
    {"name": "R3", "host": "127.0.0.1", "port": 5003},
    {"name": "R5", "host": "127.0.0.1", "port": 5005},
]


def restore(device: dict) -> None:
    name = device["name"]
    cfg_path = os.path.join(LAB_DIR, "solutions", f"{name}.cfg")

    if not os.path.exists(cfg_path):
        print(f"  [SKIP] {name}: solution file not found at {cfg_path}")
        return

    with open(cfg_path) as f:
        commands = [
            line.rstrip()
            for line in f
            if line.strip() and not line.startswith("!")
        ]

    conn_params = {
        "device_type": "cisco_ios_telnet",
        "host": device["host"],
        "port": device["port"],
        "username": "",
        "password": "",
        "secret": "",
        "timeout": 30,
    }

    print(f"  [{name}] Restoring solution config...")
    try:
        with ConnectHandler(**conn_params) as conn:
            conn.enable()
            conn.send_config_set(commands, cmd_verify=False)
            conn.send_command("write memory", expect_string=r"\[OK\]|#")
            print(f"  [{name}] Restored and saved.")
    except NetmikoTimeoutException:
        print(f"  [{name}] ERROR: Timeout — is {name} running in GNS3?")
    except Exception as exc:
        print(f"  [{name}] ERROR: {exc}")


def main() -> None:
    print("=" * 60)
    print("OSPF Lab 07 — Restoring to Solution State")
    print("=" * 60)
    for device in DEVICES:
        restore(device)
    print("=" * 60)
    print("Restore complete. Verify: show ip ospf neighbor")
    print("=" * 60)


if __name__ == "__main__":
    main()
