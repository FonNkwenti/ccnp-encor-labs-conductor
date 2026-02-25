# BGP Lab 07 — Fault Injection Scenarios

This directory contains three fault injection scripts for BGP Lab 07: Multihoming & Traffic Engineering.
Each script introduces a targeted misconfiguration on R1 that breaks a specific traffic engineering behavior.
Run `apply_solution.py` at any time to restore all routers to the correct Lab 07 solution state.

---

## Prerequisites

- GNS3 topology for Lab 07 must be running.
- All routers must be at the Lab 07 solution state before injecting faults.
  If starting fresh, run `../../setup_lab.py` first, complete the lab tasks, then use these scripts.
- Python 3 with `netmiko` installed: `pip install netmiko`

---

## Scenario 01 — Conditional Default Route Broken

**Script:** `inject_scenario_01.py`

**Fault Description:**
The static `ip route 0.0.0.0 0.0.0.0 Null0` on R1 is removed, and the
`default-originate route-map COND-DEFAULT` statement is removed from R1's
iBGP neighbor config for R4 (172.16.4.4). Without the static route, the
COND-DEFAULT route-map condition can never be satisfied, so R1 stops
advertising a default route to R4 via iBGP.

**Symptom:**
R4 loses its 0.0.0.0/0 entry from BGP. The enterprise internal router has
no default route and cannot reach any internet destinations.

**Verification Commands:**
```
R4# show ip route 0.0.0.0
R4# show ip bgp 0.0.0.0
R1# show ip bgp neighbors 172.16.4.4 advertised-routes
R1# show ip route 0.0.0.0
```

**Run:**
```bash
python3 inject_scenario_01.py
```

---

## Scenario 02 — MED Values Swapped (Wrong Inbound Traffic Preference)

**Script:** `inject_scenario_02.py`

**Fault Description:**
The MED values in `TE-TO-ISP-A` and `TE-TO-ISP-B` are swapped for the
primary-preferred prefixes. Specifically:
- `TE-TO-ISP-A` seq 20: 192.168.1.0/24 gets MED=100 (should be MED=10)
- `TE-TO-ISP-B` seq 20: 192.168.2.0/24 gets MED=100 (should be MED=10)

The design intent is that 192.168.1.0/24 should attract inbound traffic via
ISP-A (low MED=10 advertised to ISP-A) and 192.168.2.0/24 should attract
traffic via ISP-B. With both MEDs set to 100, neither ISP has a reason to
prefer their designated path — inbound traffic distribution is broken.

**Symptom:**
ISP-A and ISP-B both see MED=100 for their designated preferred prefix.
Traffic engineering for inbound path selection is ineffective. Both prefixes
may arrive via whichever ISP wins on AS-path length or other attributes.

**Verification Commands:**
```
R2# show ip bgp 192.168.1.0        (expect MED=100, was 10 — indicates fault)
R3# show ip bgp 192.168.2.0        (expect MED=100, was 10 — indicates fault)
R1# show route-map TE-TO-ISP-A
R1# show route-map TE-TO-ISP-B
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
R1# show ip bgp neighbors 10.1.13.2 advertised-routes
```

**Run:**
```bash
python3 inject_scenario_02.py
```

---

## Scenario 03 — AS-Path Prepend Shadowed by Catch-All (Wrong Order)

**Script:** `inject_scenario_03.py`

**Fault Description:**
In `TE-TO-ISP-B`, the entry that applies 3x AS-path prepend to 192.168.1.0/24
(originally at seq 10) is deleted and re-added at seq 50. Because the catch-all
`route-map TE-TO-ISP-B permit 40` matches all prefixes before seq 50 is evaluated,
the prepend statement is effectively dead — it will never be reached.

ISP-B now receives 192.168.1.0/24 with a normal (unprepended) AS-path, making the
path look shorter and equally or more attractive than the ISP-A path. This undermines
the inbound TE design that intended ISP-A as the preferred entry point for 192.168.1.0/24.

**Symptom:**
R3 (ISP-B) sees 192.168.1.0/24 with AS-path `65001` instead of `65001 65001 65001 65001`.
If ISP-A and ISP-B are peers (they are — via 10.1.23.0/30), ISP-B may now prefer
its direct path to 192.168.1.0/24 over the ISP-A path, causing traffic to arrive
via ISP-B instead of the intended ISP-A uplink.

**Verification Commands:**
```
R3# show ip bgp 192.168.1.0        (expect AS-path: 65001 — no prepend, should be 4 hops)
R1# show route-map TE-TO-ISP-B     (seq 10 missing; seq 50 appears after seq 40 catch-all)
R1# show ip bgp neighbors 10.1.13.2 advertised-routes
R2# show ip bgp 192.168.1.0        (compare AS-path length received from R3 via peer link)
```

**Run:**
```bash
python3 inject_scenario_03.py
```

---

## Restoring to Solution State

To reset all routers to the correct Lab 07 solution configuration after any fault:

```bash
python3 apply_solution.py
```

This script rebuilds all modified route-maps on R1, restores the static Null0 route,
re-applies the conditional default-originate, and issues `clear ip bgp soft` commands
to propagate updated policy to all neighbors.
