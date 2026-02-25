# BGP Lab 07 — Fault Injection Scripts

This directory contains fault injection and solution restoration scripts for
BGP Lab 07: Multihoming & Traffic Engineering.

All scripts use `device_type="cisco_ios_telnet"` and connect to `127.0.0.1`
(GNS3 localhost). Each router's console port is listed below.

## Console Port Reference

| Device | Role | Port |
|---|---|---|
| R1 | Enterprise Edge | 5001 |
| R2 | ISP-A | 5002 |
| R3 | ISP-B | 5003 |
| R4 | Enterprise Internal | 5004 |
| R5 | Downstream Customer | 5005 |

## Prerequisites

```bash
pip install netmiko
```

GNS3 must be running with all 5 routers loaded and in the **Lab 07 solution state**
before injecting any fault. Use `apply_solution.py` to restore that state.

---

## Scenario 01 — Conditional Default Not Received by R4

**File:** `inject_scenario_01.py`
**Target:** R1 (port 5001)

**What it breaks:**
- Removes the `ip route 0.0.0.0 0.0.0.0 Null0` static default route from R1
- Replaces the COND-DEFAULT route-map to reference a non-existent prefix-list
  (`COND-DEFAULT-WRONG` instead of `COND-DEFAULT-CHECK`)

**Symptom:** R4 has no default route. `show ip route 0.0.0.0` on R4 returns
`% Network not in table`.

**Root Causes to Find:**
1. Missing static default (`ip route 0.0.0.0 0.0.0.0 Null0`) — IOS will not
   originate a conditional default without a local 0/0 entry.
2. COND-DEFAULT route-map references a non-existent prefix-list, so the condition
   never matches and R1 never sends the default even if the static existed.

**Run:**
```bash
python3 inject_scenario_01.py
```

---

## Scenario 02 — MED Values Causing Wrong Inbound Path Selection

**File:** `inject_scenario_02.py`
**Target:** R1 (port 5001)

**What it breaks:**
- Swaps MED metric values in TE-TO-ISP-A:
  - PREFIX-192-168-2 (should be MED=100) gets MED=10
  - PREFIX-192-168-1 (should be MED=10) gets MED=100
- Removes the AS-path prepend on PREFIX-192-168-2

**Symptom:** R2 (ISP-A) sees 192.168.2.0/24 with Metric=10 (preferred ingress
via ISP-A) and 192.168.1.0/24 with Metric=100 (deprioritized) — exactly backwards
from the intended policy. Inbound traffic for 192.168.1.0/24 enters via ISP-B
instead of ISP-A.

**Root Cause to Find:**
TE-TO-ISP-A has MED values inverted between PREFIX-192-168-1 and PREFIX-192-168-2.
Check with `show route-map TE-TO-ISP-A` and compare seq 10 and seq 20 match/set clauses.

**Run:**
```bash
python3 inject_scenario_02.py
```

---

## Scenario 03 — AS-Path Prepend Not Taking Effect

**File:** `inject_scenario_03.py`
**Target:** R1 (port 5001)

**What it breaks:**
- Moves the AS-path prepend entry for PREFIX-192-168-2 in TE-TO-ISP-A from
  sequence 10 to sequence 50 — placing it after the catch-all permit at sequence 40.
- The catch-all (seq 40, no match clause) accepts all routes first, so seq 50
  with the prepend never fires.

**Symptom:** R2 receives 192.168.2.0/24 with AS-path `65001` (1 entry) instead
of the expected `65001 65001 65001 65001` (4 entries). Inbound traffic for
192.168.2.0/24 may enter via ISP-A instead of ISP-B as intended.

**Root Cause to Find:**
`show route-map TE-TO-ISP-A` will reveal that seq 50 contains the prepend but
seq 40 (no match = permit all) comes before it. The fix is to remove the route-map
and rebuild it with the prepend entry at seq 10 (before the catch-all at seq 40).

**Run:**
```bash
python3 inject_scenario_03.py
```

---

## Apply Solution — Restore All Routers to Lab 07 Solution State

**File:** `apply_solution.py`
**Targets:** R1 (5001), R2 (5002), R3 (5003), R4 (5004), R5 (5005)

Restores all 5 routers to the complete Lab 07 solved configuration. Run this
after any fault injection scenario to reset the lab for the next exercise.

**What it restores on R1:**
- `ip route 0.0.0.0 0.0.0.0 Null0` static route
- All prefix-lists: ISP-A-PREFIXES, ISP-B-PREFIXES, PREFIX-192-168-1/2/3,
  COND-DEFAULT-CHECK
- Route-maps: LP-FROM-ISP-A, LP-FROM-ISP-B, TE-TO-ISP-A, TE-TO-ISP-B, COND-DEFAULT
- BGP neighbor policies: LP inbound, TE outbound, conditional default to R4

**What it restores on R2, R3, R4, R5:** send-community statements and existing
route-maps (unchanged from Lab 06 baseline).

**Run:**
```bash
python3 apply_solution.py
```

**Post-restore verification:**
```
R1# show ip bgp summary
R2# show ip bgp 192.168.2.0   (expect AS-path: 65001 65001 65001 65001)
R2# show ip bgp 192.168.1.0   (expect Metric: 10)
R4# show ip bgp               (expect 0.0.0.0/0 present)
```
