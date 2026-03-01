# Fault Injection — OSPF Lab 08

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 project open with R1, R2, R3, and R6 powered on
- `setup_lab.py` run at least once to load initial configs
- Solution configs applied: `python3 scripts/fault-injection/apply_solution.py`
- `netmiko` installed: `pip install netmiko`

## Inject a Fault

```bash
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
```

## Restore

```bash
python3 apply_solution.py
```
