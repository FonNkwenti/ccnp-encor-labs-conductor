# Troubleshooting Challenges: EIGRP Lab 03

These challenges are designed to test your diagnostic skills. Use the `scripts/fault_injector.py` script to inject a fault, then try to identify and resolve it.

## Challenge 1: The Null0 Blackhole
**Symptom:** R1 has a route for the summarized 172.16.0.0/16 regional network, but it's pointing to `Null0` instead of R7. Consequently, no one can reach the subnets behind R7.

**Goal:** Identify why R1 has locally generated a summary route for a prefix it should be learning from R7, and restore the correct path.

---

## Challenge 2: Summary AD Sabotage
**Symptom:** You've configured summarization on R3, but the summary route is not appearing in the routing tables of R2 or R1. R3's console shows that the neighbor relationship with R2 is stable.

**Goal:** Investigate the administrative distance settings for the summary on R3. Is the summary "too expensive" to be used?

---

## Challenge 3: Overly Aggressive Boundary
**Symptom:** R7 is configured to summarize 172.16.0.0/16, but it is also accidentally summarizing the 10.0.17.0/30 transit link. R1 and R7 have lost their EIGRP adjacency.

**Goal:** Correct the summarization mask or command on R7 to ensure that management and transit networks are not accidentally suppressed by the regional summary.
