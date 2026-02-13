# Troubleshooting Challenges: EIGRP Lab 10

These challenges are designed to test your diagnostic skills.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Auth Asymmetry
**Script:** `scripts/fault_inject_1.py`
**Symptom:** After configuring SHA-256 authentication on both R1 and R6 for Tunnel8, the EIGRP adjacency over the tunnel drops. `show eigrp address-family ipv4 neighbors` no longer shows the tunnel peer. Debug output mentions "authentication failure".

**Goal:** Investigate the SHA-256 password configured on R6's `af-interface Tunnel8`. Determine if there is a password mismatch and restore the authenticated adjacency.

---

## Challenge 2: The Metric Mismatch
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1 and R6 have an active EIGRP adjacency, but R1 reports routes from R6 with unexpectedly different metric values. The `show eigrp address-family ipv4 topology` output on R1 shows classic 32-bit metrics for R6 routes, while R1's local routes use 64-bit wide metrics.

**Goal:** Check whether wide metrics (`metric version 64bit`) are still enabled on R6. A version mismatch between peers causes metric translation issues. Restore consistent wide metrics on both sides.

---

## Challenge 3: The Silent Interface
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1 suddenly loses its EIGRP adjacency with R2 over FastEthernet1/0. `show eigrp address-family ipv4 neighbors` no longer shows R2 as a neighbor. However, R1 can still ping R2's interface address.

**Goal:** Check R1's `af-interface` configuration. Determine if `passive-interface` was accidentally applied to `FastEthernet1/0` instead of `Loopback0`, and correct the configuration.
