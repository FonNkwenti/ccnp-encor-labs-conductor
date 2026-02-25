# BGP Lab 06 — Fault Injection Scripts

These scripts inject deliberate faults into the running GNS3 lab to simulate the troubleshooting scenarios in Section 9 of the workbook. Run them after the lab is fully set up and all BGP sessions are Established.

All scripts connect via Netmiko using `device_type="cisco_ios_telnet"` to `127.0.0.1`.

---

## Prerequisites

- GNS3 lab is running with all 5 routers booted
- `setup_lab.py` has been run (or initial configs have been manually loaded)
- All BGP sessions are Established (verify with `show ip bgp summary`)
- The full solution configuration is in place before injecting a fault

```bash
pip install netmiko
```

---

## Fault Scenarios

### Scenario 01 — Missing send-community (Ticket 1)

**Script:** `inject_scenario_01.py`
**Target:** R1 (port 5001)

**Fault Injected:**
Removes `send-community` from R1's neighbor statement for R2 (10.1.12.2). BGP communities are then silently dropped and ISP-A never receives the `65001:100` enterprise community on inbound prefixes.

**Symptom:**
```
R2# show ip bgp 192.168.1.0
(no Community field shown)
```

**Run:**
```bash
python3 inject_scenario_01.py
```

---

### Scenario 02 — Wrong Community-List Value (Ticket 2)

**Script:** `inject_scenario_02.py`
**Target:** R1 (port 5001)

**Fault Injected:**
Replaces the `CUSTOMER-ROUTES` community-list with an incorrect value (`65003:999` instead of `65003:500`). Route-map POLICY-ISP-B-IN sequence 8 never matches, and customer routes from R5 fall through to sequence 10, receiving local-preference 150 instead of the correct 120.

**Symptom:**
```
R1# show ip bgp 10.5.1.0
  Local preference: 150   (should be 120)
  Community: 65003:500
```

**Run:**
```bash
python3 inject_scenario_02.py
```

---

### Scenario 03 — R5 Advertising No Routes (Ticket 3)

**Script:** `inject_scenario_03.py`
**Target:** R5 (port 5005)

**Fault Injected:**
Removes all `network` statements from R5's BGP configuration. The BGP session with R3 remains Established (TCP is up) but R5 has no prefixes to advertise, so R3 receives 0 routes from R5.

**Symptom:**
```
R3# show ip bgp summary
10.1.35.2   4 65004 ...  0   (PfxRcvd = 0, session still Up)

R5# show ip bgp
(empty)
```

**Run:**
```bash
python3 inject_scenario_03.py
```

---

## Restore All Devices to Solution State

After completing a troubleshooting scenario (or to reset between scenarios):

```bash
python3 apply_solution.py
```

This pushes the full solution configuration to all 5 routers and performs soft BGP resets to ensure the routing table converges to the correct state.
