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

## Challenge 2: Advanced Auth Anarchy (SHA-256)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** The new HMAC-SHA-256 authentication between R2 and R3 is not working. `show ip eigrp neighbors detail` shows no peers on the link.

**Goal:** Determine if the issue is a password mismatch or a configuration mode error, and fix it.

---

## Challenge 3: Tagging & Offsets Gone Wrong
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1 is successfully receiving routes from R5, but they are not being tagged with `555`, and consequently, the Offset List is not applying the expected metric penalty.

**Goal:** Find where the tagging process is failing (likely on R3) and ensure that R1 receives the routes with the correct tag.
