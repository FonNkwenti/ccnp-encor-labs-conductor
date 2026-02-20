Generate fault injection scripts for troubleshooting scenarios in: $ARGUMENTS

## Purpose
Create automated Python scripts that inject the troubleshooting scenarios defined in a lab workbook into the live GNS3 environment.

## Workflow

1. **Read the workbook** at the specified lab path (e.g., `labs/eigrp/lab-06-filtering-control/workbook.md`)

2. **Parse from the workbook:**
   - Console Access Table (device → port mappings)
   - Troubleshooting Scenarios (Section 8) — at least 3 scenarios
   - For each scenario: target device, fault type, commands to inject, solution commands

3. **Generate scripts** in `<lab-path>/scripts/fault-injection/`:
   - `inject_scenario_01.py` — injects first fault
   - `inject_scenario_02.py` — injects second fault
   - `inject_scenario_03.py` — injects third fault (and more if scenarios exist)
   - `apply_solution.py` — restores all devices to correct configuration
   - `README.md` — usage instructions

4. **Script requirements:**
   - Use Netmiko `ConnectHandler` with `device_type="cisco_ios_telnet"`
   - Connect to `127.0.0.1:<console_port>` from the Console Access Table
   - Use `send_config_set()` to inject misconfiguration commands
   - Include docstring explaining what fault is injected
   - Clear console output showing progress
   - Graceful error handling for connection failures
   - Scripts must be idempotent (safe to run multiple times)

5. **Update the workbook** to add "Automated Fault Injection" subsections to each troubleshooting scenario with run instructions.

## Arguments format
Provide the lab path, e.g.: `labs/ospf/lab-05-special-areas`
