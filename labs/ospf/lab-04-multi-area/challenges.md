# Troubleshooting Challenges: OSPF Lab 04

These challenges are designed to test your diagnostic skills in a Multi-Area OSPF environment.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault-injection/inject_scenario_01.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Area Mismatch
**Script:** `scripts/fault-injection/inject_scenario_01.py`
**Symptom:** R2 and R3 were recently moved to Area 1, but the adjacency between them has failed. R2 shows `FastEthernet0/1` in Area 1, while R3's `FastEthernet0/0` appears to be in a different area. Pings between physical interfaces still work.

**Goal:** Correct the area ID mismatch on the link between R2 and R3 to restore the adjacency.

#### Automated Fault Injection
To automatically inject this fault into your lab environment:
```bash
python3 scripts/fault-injection/inject_scenario_01.py
```
To restore the correct configuration:
```bash
python3 scripts/fault-injection/apply_solution.py
```

---

## Challenge 2: The Isolated Branch
**Script:** `scripts/fault-injection/inject_scenario_02.py`
**Symptom:** R3 has lost all reachability to the backbone (R1). While R2 and R3 are adjacent in Area 1, R1 reports no routes to R3's loopback (10.3.3.3/32). R2 does not appear to be performing its role as an Area Border Router (ABR) for R3's prefixes.

**Goal:** Identify why R2 is not advertising Area 1 routes into Area 0. Ensure R2 has at least one active interface in the backbone area (Area 0).

#### Automated Fault Injection
To automatically inject this fault into your lab environment:
```bash
python3 scripts/fault-injection/inject_scenario_02.py
```
To restore the correct configuration:
```bash
python3 scripts/fault-injection/apply_solution.py
```

---

## Challenge 3: Type 3 Troubleshooting
**Script:** `scripts/fault-injection/inject_scenario_03.py`
**Symptom:** R1 sees R3's loopback (10.3.3.3/32) as an `O` (Intra-Area) route instead of an `O IA` (Inter-Area) route. This indicates that the hierarchy is not being enforced as intended, and R3's prefix is still being advertised as if it were in the backbone area.

**Goal:** Find the configuration error on R3 that is keeping its loopback in Area 0 instead of the new Area 1.

#### Automated Fault Injection
To automatically inject this fault into your lab environment:
```bash
python3 scripts/fault-injection/inject_scenario_03.py
```
To restore the correct configuration:
```bash
python3 scripts/fault-injection/apply_solution.py
```
