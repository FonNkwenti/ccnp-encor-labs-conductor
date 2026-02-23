---
name: fault-injector
description: Generates Python fault-injection scripts (inject_scenario_NN.py, apply_solution.py) and a README that push Cisco misconfigurations into live GNS3 routers via Netmiko telnet for troubleshooting practice. Use when asked to "inject faults", "create troubleshooting scenarios", "generate fault scripts", "add a troubleshooting challenge", or automatically after lab-workbook-creator completes a lab.
metadata:
  author: CCNP ENCOR Labs Conductor
  version: 2.0.0
  category: workflow-automation
  tags: [ccnp, encor, gns3, cisco, troubleshooting, netmiko, fault-injection]
---

# Fault Injector Skill

## Purpose
This skill automatically generates Python scripts that inject the troubleshooting scenarios defined in lab workbooks into the live GNS3 environment. It enables instructors and students to quickly set up fault conditions for troubleshooting practice without manual configuration.

## When to Use
- Automatically called by `lab-workbook-creator` skill after workbook generation
- Manually invoked to generate/regenerate fault injection scripts for existing labs
- When updating troubleshooting scenarios in a workbook

## Input Requirements
The skill requires:
1. **Workbook path**: Path to the lab's `workbook.md` file
2. **Console Access Table**: Device-to-port mappings (parsed from workbook)
3. **Troubleshooting Scenarios**: At least 3 scenarios from Section 8 of the workbook

## Output Structure
Creates the following in the lab directory:

```
labs/[chapter]/[lab-XX]/
├── workbook.md
├── scripts/
│   └── fault-injection/
│       ├── README.md                    # Instructions for using scripts
│       ├── inject_scenario_01.py        # Scenario 1 fault injection
│       ├── inject_scenario_02.py        # Scenario 2 fault injection
│       ├── inject_scenario_03.py        # Scenario 3 fault injection
│       └── apply_solution.py            # Restore correct configuration
```

## Script Requirements

### Each Fault Injection Script Must:
1. **Connect via Netmiko**: Use `ConnectHandler` with `device_type="cisco_ios_telnet"` to connect to localhost:[console_port]
2. **Handle IOS CLI**: Netmiko handles enable mode, config mode, and command timing automatically
3. **Apply Fault Configuration**: Use `send_config_set()` to inject the specific misconfiguration
4. **Provide Feedback**: Clear console output showing progress
5. **Error Handling**: Gracefully handle connection failures
6. **Self-Documenting**: Include docstring explaining what fault is injected

### Standard Script Structure:
```python
#!/usr/bin/env python3
"""
Fault Injection Script: [Scenario Name]

Injects: [Description of fault]
Target Device: [Device name]
Fault Type: [Category - e.g., AS Mismatch, Passive Interface, etc.]

This script connects to the device via console and applies the
misconfiguration described in Troubleshooting Scenario X.
"""

from netmiko import ConnectHandler
import sys

# Device Configuration
DEVICE_NAME = "R2"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5002

# Fault Configuration Commands
FAULT_COMMANDS = [
    "no router eigrp 100",
    "router eigrp 200",
    "eigrp router-id 2.2.2.2",
    # ... more commands
]

def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Connecting to {DEVICE_NAME}...")

    try:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host=CONSOLE_HOST,
            port=CONSOLE_PORT,
            username="",
            password="",
            secret="",
            timeout=10,
        )
        print(f"[+] Connected to {DEVICE_NAME}")

        # Apply fault commands
        print(f"[*] Injecting fault configuration...")
        output = conn.send_config_set(FAULT_COMMANDS)
        print(output)

        conn.disconnect()

        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario X is now active.")

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("Fault Injection: [Scenario Name]")
    print("="*60)
    inject_fault()
    print("="*60)
```

## README.md Template

The skill generates a README.md in the `scripts/fault-injection/` directory:

```markdown
# Fault Injection Scripts

This directory contains automated fault injection scripts for troubleshooting practice.

## Prerequisites
- GNS3 project must be running
- All devices must be accessible via console ports
- Python 3.x installed
- `netmiko` library installed (`pip install netmiko`)

## Available Scenarios

### Scenario 1: [Name]
**Fault**: [Description]
**Target Device**: [Device]
**Command**: `python3 inject_scenario_01.py`

### Scenario 2: [Name]
**Fault**: [Description]
**Target Device**: [Device]
**Command**: `python3 inject_scenario_02.py`

### Scenario 3: [Name]
**Fault**: [Description]
**Target Device**: [Device]
**Command**: `python3 inject_scenario_03.py`

## Usage

1. Ensure your GNS3 lab is running
2. Run a fault injection script:
   ```bash
   cd scripts/fault-injection
   python3 inject_scenario_01.py
   ```
3. Practice troubleshooting using the workbook
4. Restore correct configuration:
   ```bash
   python3 apply_solution.py
   ```

## Restoring Configuration

The `apply_solution.py` script restores all devices to their correct configuration,
removing all injected faults.
```

## Workbook Integration

### Add to Workbook Section 8
After each troubleshooting scenario, include:

```markdown
#### Running This Scenario

To automatically inject this fault into your lab:

\`\`\`bash
cd scripts/fault-injection
python3 inject_scenario_01.py
\`\`\`

To restore the correct configuration:

\`\`\`bash
python3 apply_solution.py
\`\`\`
```

## Parsing Troubleshooting Scenarios

The skill must extract from the workbook:
1. **Scenario Number**: From heading (e.g., "Scenario 1: AS Mismatch")
2. **Target Device**: From Problem Statement or Mission
3. **Fault Type**: Categorize the misconfiguration
4. **Commands to Inject**: Parse from the Solution section

### Example Mapping:

| Scenario | Device | Fault Commands |
|----------|--------|----------------|
| AS Mismatch | R2 | `no router eigrp 100`, `router eigrp 200`, ... |
| Passive Interface | R3 | `passive-interface default`, `no passive-interface Loopback0` |
| Missing Network | R1 | `router eigrp 100`, `no network 1.1.1.1 0.0.0.0` |

## Console Access Table Parsing

Extract from workbook section "Console Access Table":

```markdown
| Device | Port | Connection Command |
|--------|------|-------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
```

Parse into:
```python
DEVICE_CONSOLE_MAP = {
    "R1": 5001,
    "R2": 5002,
    "R3": 5003,
}
```

## Error Handling

Scripts should handle:
- Connection timeouts
- Device not responding
- Invalid console ports
- Netmiko authentication exceptions
- IOS command errors

## Best Practices

1. **Idempotent Scripts**: Running script multiple times should be safe
2. **Clear Feedback**: Print what's happening at each step
3. **Timeout Management**: Don't hang indefinitely
4. **State Verification**: Optionally verify fault was applied
5. **Documentation**: Each script self-documents what it does

## Integration with Lab Workbook Creator

The `lab-workbook-creator` skill should:
1. Generate the workbook with troubleshooting scenarios
2. Call the `fault-injector` skill
3. Pass workbook path and parsed scenarios
4. Fault-injector generates all Python scripts
5. Updates workbook with instructions for running scripts
