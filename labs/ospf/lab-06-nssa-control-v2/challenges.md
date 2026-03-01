# OSPF Lab 06 — Extension Challenges

These challenges extend the core lab tasks. Each is standalone and can be attempted independently after completing the main workbook.

---

## Challenge 1: Type 7 Metric Types — E1 vs E2

By default, `redistribute connected subnets` on R4 generates Type 7 LSAs with metric type E2 (flat external metric). Reconfigure the redistribution to use metric type E1 (cost-accumulating). Verify how the metric for `172.16.4.0/24` changes as seen from R2 vs. R3.

**Hint:** Look for the `metric-type` keyword on the redistribution command.

**Success criteria:** `show ip route ospf` on R2 shows `O E1 172.16.4.0/24` with a metric that reflects the accumulated cost from R4 to R2. The metric on R3 is higher than on R2 because R3 is further from R4.

---

## Challenge 2: NSSA without Automatic Default Route

In a regular NSSA (not Totally NSSA), the ABR does NOT automatically inject a default route. Verify this by removing `no-summary` from R1 (revert to regular NSSA) and checking whether R4 still has a default route. Then manually force the ABR to originate a default route into Area 14.

**Hint:** There is an OSPF area subcommand that forces default-information origination into an NSSA even without `no-summary`.

**Success criteria:** After removing `no-summary`, `show ip route` on R4 confirms no default route. After applying the fix, `O*IA 0.0.0.0/0` reappears in R4's routing table.

---

## Challenge 3: Multiple ASBRs in Area 14 — Translation Election

Add a second router (R5) into Area 14 as a second ASBR, connected to R1 via a new subnet. R5 should also redistribute a connected loopback (e.g., 192.168.5.0/24). Configure R5 with a higher router ID than R4.

Verify:
1. Both R4 and R5 generate Type 7 LSAs for their respective subnets.
2. Only ONE of the two ABRs translates Type 7 → Type 5 (the one with the highest router ID among the ABRs connecting Area 14 to Area 0 — in this topology, only R1 is ABR).
3. Both external subnets appear as Type 5 in the backbone.

**Success criteria:** `show ip ospf database external` on R2 lists both 172.16.4.0 and 192.168.5.0. Both have R1 as the advertising router.

---

## Challenge 4: Trace the Full LSA Lifecycle

Without making any configuration changes, capture and document the complete lifecycle of the 172.16.4.0/24 prefix as it propagates through the OSPF domain:

| Stage | Router | LSA Type | Command to Verify | ADV Router |
|-------|--------|----------|-------------------|------------|
| Origination | R4 | Type 7 | | |
| Translation | R1 | Type 5 | | |
| Backbone propagation | R2 | Type 5 | | |
| Stub area | R7 | N/A (blocked) | | |

Answer: Why does R7 not see the 172.16.4.0/24 external route, even though it's reachable from the backbone? What mechanism prevents it from entering Area 2?

**Success criteria:** Table completed with correct LSA types and advertising routers at each stage. Written explanation of why Area 2 (Totally Stubby) blocks the external route.
