# Fault Injection — BGP Lab 08

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 lab running with all six routers powered on
- Lab in a known-good state (run `setup_lab.py` or `apply_solution.py` first)
- Python 3 with Netmiko installed (`pip install netmiko`)

## Inject a Fault

```bash
cd scripts/fault-injection/
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
```

## Restore

```bash
python3 apply_solution.py
```

Work through the troubleshooting ticket in `workbook.md` Section 9 before running `apply_solution.py`.
