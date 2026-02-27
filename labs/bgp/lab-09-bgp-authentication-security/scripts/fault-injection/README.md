# Fault Injection — BGP Lab 09

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 lab running with all six routers (R1–R6) powered on
- `setup_lab.py` has been run and the lab is in a known-good state
- Python 3 with `netmiko` installed (`pip install netmiko`)

## Inject a Fault

```
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
```

## Restore

```
python3 apply_solution.py
```
