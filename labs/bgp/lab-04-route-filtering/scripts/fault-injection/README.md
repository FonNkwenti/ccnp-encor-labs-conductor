# Fault Injection Scripts — BGP Lab 04: Route Filtering with Prefix-Lists

## Prerequisites

- GNS3 lab running with R1, R2, R3, R4 at console ports 5001–5004
- `setup_lab.py` has been run to push initial configs
- Python packages: `netmiko`

## Workflow

```bash
# 1. Push initial configs (Lab 03 state — no filters)
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
| `inject_scenario_01.py` | Ticket 1 | `FROM-ISP-A` prefix-list has `deny` instead of `permit` for `198.51.100.0/24` — blocks ALL ISP-A routes | R1 |
| `inject_scenario_02.py` | Ticket 2 | `soft-reconfiguration inbound` removed from R3 neighbor — `received-routes` command fails | R1 |
| `inject_scenario_03.py` | Ticket 3 | `TO-ISP-B` outbound filter applied but `clear ip bgp soft out` not run — filter inactive | R1 |
| `apply_solution.py` | Restore | Applies complete Lab 04 solution to R1 and R4 | R1, R4 |

## Key Diagnostic Commands

```bash
# Check what prefixes are actually being received (pre-policy)
R1# show ip bgp neighbors 10.1.12.2 received-routes

# Check what prefixes are accepted after inbound filter
R1# show ip bgp neighbors 10.1.12.2 routes

# Check what is being advertised to ISP-B
R1# show ip bgp neighbors 10.1.13.2 advertised-routes

# View prefix-list definitions and match counts
R1# show ip prefix-list

# View ACL match counts for distribute-list
R4# show ip access-lists ENTERPRISE-INTERNAL
```

## Connection Details

| Device | Console Port | Telnet Command |
|--------|-------------|----------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
