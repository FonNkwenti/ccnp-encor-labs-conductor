# Troubleshooting Challenges: OSPF Lab 03

These challenges are designed to test your diagnostic skills.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Inconsistent Backbone
**Script:** `scripts/fault_inject_1.py`
**Symptom:** After a maintenance window, R1 reports a cost of **21** to reach R3's loopback (10.3.3.3/32) via R2. However, R2 appears to be advertising its FastEthernet links with a cost of **1** instead of **10**, creating an inconsistent cost view across the OSPF domain.

**Goal:** Identify which router has a mismatched reference bandwidth configuration and correct it. Verify that all routers share the same `auto-cost reference-bandwidth` value.

---

## Challenge 2: The Vanishing Shortcut
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1's direct link to R3 (Fa1/1) is up and OSPF-adjacent, but the cost to reach R3 via this link has become absurdly high. All traffic to R3 is forced through R2 even for prefixes that should prefer the direct path. The cost on Fa1/1 appears to be **65535**.

**Goal:** Find the excessive manual cost configuration on R1's interface and restore it to the intended value of 50.

---

## Challenge 3: The Backbone Bottleneck
**Script:** `scripts/fault_inject_3.py`
**Symptom:** After a junior engineer's change, R1 is sending all traffic (including R2-bound traffic) via the direct link to R3 (Fa1/1). The Backbone Router (R2) appears unreachable via its primary link, and traffic to 10.2.2.2/32 is taking the long path R1 -> R3 -> R2.

**Goal:** Investigate the cost configuration on R1's Fa1/0 interface (link to R2). The manual cost has been applied to the wrong interface, causing the backbone link to be deprioritized.
