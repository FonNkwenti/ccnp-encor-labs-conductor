# Troubleshooting Challenges: EIGRP Lab 05

These challenges are designed to test your diagnostic skills.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The "Secret" Mismatch (MD5)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 and R2 are physically connected, but the EIGRP adjacency has dropped. `show ip eigrp neighbors` is empty on both sides. Console logs on R1 show "authentication bad key".

**Goal:** Identify why MD5 authentication is failing and restore the secure adjacency.

---

## Challenge 2: Tagging & Offsets Gone Wrong
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1 is successfully receiving routes from R5, but they are not being tagged with `555`, and consequently, the Offset List is not applying the expected metric penalty.

**Goal:** Find where the tagging process is failing (likely on R3) and ensure that R1 receives the routes with the correct tag.

---

## Challenge 3: The Phantom Penalty
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1's offset list appears to be active, but the metric penalty is being applied to the wrong routes. Routes from R5 that should be penalized are unaffected, while other routes are unexpectedly inflated.

**Goal:** Investigate the route-map `MATCH_TAG` on R1. Determine if the tag value being matched is correct (should be `555`), and fix the mismatch.
