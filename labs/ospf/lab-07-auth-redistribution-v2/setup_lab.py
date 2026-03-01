#!/usr/bin/env python3
"""
setup_lab.py — OSPF Lab 07: Authentication & Redistribution
Loads initial-configs onto R1, R2, R3, R5 via GNS3 console (Netmiko telnet).
"""

import os
import sys
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

LAB_DIR = os.path.dirname(os.path.abspath(__file__))

DEVICES = [
    {"name": "R1", "host": "127.0.0.1", "port": 5001},
    {"name": "R2", "host": "127.0.0.1", "port": 5002},
    {"name": "R3", "host": "127.0.0.1", "port": 5003},
    {"name": "R5", "host": "127.0.0.1", "port": 5005},
]


def load_config(device: dict) -> None:
    name = device["name"]
    cfg_path = os.path.join(LAB_DIR, "initial-configs", f"{name}.cfg")

    if not os.path.exists(cfg_path):
        print(f"  [SKIP] {name}: config file not found at {cfg_path}")
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
        "session_log": None,
    }

    print(f"  [{name}] Connecting on port {device['port']}...")
    try:
        with ConnectHandler(**conn_params) as conn:
            conn.enable()
            conn.send_config_set(commands, cmd_verify=False)
            conn.send_command("write memory", expect_string=r"\[OK\]|#")
            print(f"  [{name}] Config loaded and saved.")
    except NetmikoTimeoutException:
        print(f"  [{name}] ERROR: Connection timed out. Is the router powered on in GNS3?")
    except NetmikoAuthenticationException:
        print(f"  [{name}] ERROR: Authentication failed.")
    except Exception as exc:
        print(f"  [{name}] ERROR: {exc}")


def main() -> None:
    print("=" * 60)
    print("OSPF Lab 07 — Authentication & Redistribution")
    print("Loading initial configurations...")
    print("=" * 60)

    for device in DEVICES:
        load_config(device)

    print("=" * 60)
    print("Done. Verify with: show ip ospf neighbor")
    print("=" * 60)


if __name__ == "__main__":
    main()
