# OSPF Lab 07 — Extended Challenges

These four exercises extend the core lab. Each is standalone — complete them after finishing the main workbook tasks. No step-by-step guidance is provided.

---

## Challenge 1: Key Rollover Without Dropping Adjacencies

OSPF key-chains support multiple keys simultaneously, which allows you to perform live key rollovers without dropping adjacencies. Your task is to add a second key (key ID `2`) with a new key-string to the `OSPF_AUTH` key-chain on all three Area 0 routers (R1, R2, R3), and then remove key ID `1` — all without ever losing an OSPF neighbor relationship.

**Acceptance criteria:**
- `show ip ospf neighbor` shows no state changes during the rollover (FULL throughout)
- `show ip ospf interface` on each Area 0 interface shows key ID `2` as the active key
- Key ID `1` is absent from `show key chain`

**Hint:** OSPF will use the highest-numbered key that is valid on both ends of a link. Add key 2 to all routers first before removing key 1.

---

## Challenge 2: Redistribute a Connected Loopback with Metric Seeding

R5 has two research loopbacks being redistributed via EIGRP. Add a third subnet `172.16.200.0/24` as a new loopback on R5, but this time redistribute it **directly as a connected route** on R2 (not via EIGRP) with a seed metric of `50` and metric type E1. Verify that R3 sees this route with a metric of `60` (seed 50 + cost 10 from R3 to R2).

**Acceptance criteria:**
- `show ip ospf database external` on R1 shows `172.16.200.0` with metric 50, type-1
- `show ip route ospf` on R3 shows `O E1 172.16.200.0/24 [110/60]`
- The existing `172.16.5.0/24` (E1) and `172.16.105.0/24` (E2) routes are unaffected

**Hint:** Use a separate `redistribute connected subnets` statement with a different route-map clause and a `set metric` statement alongside `set metric-type type-1`.

---

## Challenge 3: Filter External Routes from Reaching Area 1

The security team wants to prevent the partner research subnets from being installed in R3's routing table while R1 should still see them. Configure a distribute-list or OSPF filter on R3 to block `172.16.0.0/16` (summary) from being installed, while keeping all internal OSPF routes intact.

**Acceptance criteria:**
- `show ip route` on R3 shows **no** `O E1` or `O E2` entries for the `172.16.x.x` space
- `show ip route ospf` on R1 shows both external routes unchanged
- All OSPF internal routes (loopbacks, point-to-point links) remain reachable from R3

**Hint:** Use `ip ospf distribute-list prefix <list> in` on R3's OSPF process to filter LSA installation into the RIB without affecting LSA propagation.

---

## Challenge 4: Dual-ASBR Redistribution with E2 Tie-Breaking

Add a second ASBR scenario. Configure R1 to also peer with R5 via a new loopback-to-loopback link (use `10.15.0.0/30`), and redistribute the same `172.16.5.0/24` subnet from R1 as E2 with seed metric `20`. Now both R1 and R2 are advertising the same E2 prefix. Predict and verify which ASBR R3 prefers, then explain why.

**Acceptance criteria:**
- `show ip ospf database external` shows two LSAs for `172.16.5.0` (one from R1, one from R2)
- `show ip route 172.16.5.0` on R3 shows one next-hop (the preferred ASBR)
- You can articulate the E2 tie-breaking rule in your own words

**Hint:** With identical E2 metrics, OSPF selects the path to the ASBR with the lowest internal cost. R3's OSPF cost to each ASBR determines the winner. Manipulate interface costs to force a specific outcome and validate your understanding.
