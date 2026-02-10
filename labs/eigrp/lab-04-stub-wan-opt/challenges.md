# Troubleshooting Challenges: EIGRP Lab 04

These challenges are designed to test your diagnostic skills. Use the `scripts/fault_injector.py` script to inject a fault, then try to identify and resolve it.

## Challenge 1: The "Receive-Only" Silence
**Symptom:** R3 is adjacent with R5, but R1 and R2 no longer have any routes to the 10.5.x.x networks located behind R5. R5's neighbor status on R3 shows it is a "Stub Peer".

**Goal:** Identify why R5 has stopped advertising its connected networks and restore reachability while keeping R5 as a stub.

---

## Challenge 2: The WAN Timeout
**Symptom:** The EIGRP adjacency between R1 and R2 is constantly flapping. You see logs indicating that the neighbor has been "reset" due to "hold timer expired". You've verified the physical link is stable.

**Goal:** Compare the EIGRP hello and hold timers on both sides of the R1-R2 WAN link and ensure they are consistent and appropriate for a slow leased line.

---

## Challenge 3: Forgotten Static Routes
**Symptom:** R5 has a static route to a legacy server at 192.168.99.1. Management wants this route to be shared with the rest of the company, but despite having `eigrp stub connected summary`, the static route is not appearing in R1's routing table.

**Goal:** Modify the stub configuration on R5 to allow the advertisement of static routes, without removing the stub protection.
