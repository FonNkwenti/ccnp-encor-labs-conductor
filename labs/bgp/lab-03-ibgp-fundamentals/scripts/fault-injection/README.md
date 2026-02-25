# Fault Injection — BGP Lab 03

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 project running with all routers started
- All devices accessible via console ports (R1=5001, R2=5002, R3=5003, R4=5004)
- Python 3.x with `netmiko` installed (`pip install netmiko`)
- Lab solution configs applied (run `setup_lab.py` first, then complete the lab)

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
