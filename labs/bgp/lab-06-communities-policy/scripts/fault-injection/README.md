# Fault Injection — BGP Lab 06

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 lab running with all 5 routers powered on
- Lab 06 initial configurations loaded (`python3 setup_lab.py` from the lab root)
- Lab 06 solution configurations applied (`python3 scripts/fault-injection/apply_solution.py`)
- Python 3 with netmiko installed (`pip install netmiko`)

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
