# Fault Injection — OSPF Lab 06 (NSSA & Route Control)

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 lab running with R1, R2, R3, R4, R7 powered on
- `setup_lab.py` has been run and initial configs loaded
- Lab tasks completed (solutions applied) — fault scripts break a working config
- Python 3 + netmiko installed: `pip install netmiko`

## Inject a Fault

```bash
cd scripts/fault-injection
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
```

## Restore

```bash
python3 apply_solution.py
```

Run `apply_solution.py` between tickets to return all devices to the working state.
