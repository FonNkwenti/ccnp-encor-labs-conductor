# Fault Injection Scripts — BGP Lab 05: AS-Path Manipulation & Route-Maps

## Prerequisites

- GNS3 lab running with R1, R2, R3, R4 at console ports 5001–5004
- `setup_lab.py` has been run to push Lab 04 initial configs
- Python packages: `netmiko`

## Workflow

```bash
# 1. Push initial configs (Lab 04 state — prefix-list filtering active)
python3 setup_lab.py

# 2. Inject a fault scenario
python3 scripts/fault-injection/inject_scenario_01.py

# 3. Diagnose and fix (see workbook Section 9)

# 4. Restore to solved state
python3 scripts/fault-injection/apply_solution.py
```

## Scenarios

| Script | Ticket | Fault Description | Target |
|--------|--------|-------------------|--------|
| `inject_scenario_01.py` | Ticket 1 | `SET-LP-200-ISP-A` uses `deny 10` instead of `permit 10` — ALL ISP-A routes blocked | R1 |
| `inject_scenario_02.py` | Ticket 2 | `PREPEND-TO-ISP-B` applied `in` (inbound) instead of `out` (outbound) — prepend has no effect | R1 |
| `inject_scenario_03.py` | Ticket 3 | `set weight 200` used instead of `set local-preference 200` — R4 cannot distinguish ISP preference | R1 |
| `apply_solution.py` | Restore | Applies complete Lab 05 solution to R1 | R1 |

## Key Diagnostic Commands

```bash
# Check AS-path access-lists
R1# show ip as-path-access-list

# Filter BGP table by AS-path pattern
R1# show ip bgp regexp ^65002$
R1# show ip bgp regexp ^65003$

# Check route-map definitions and match counters
R1# show route-map

# Check full path details for a specific prefix (local-pref, weight, AS-path)
R1# show ip bgp 198.51.100.0
R3# show ip bgp 192.168.1.0

# Check R4 sees correct local-preference values via iBGP
R4# show ip bgp
```

## Connection Details

| Device | Console Port | Telnet Command |
|--------|-------------|----------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
