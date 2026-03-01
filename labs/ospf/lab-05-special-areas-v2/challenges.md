# OSPF Lab 05 — Extension Challenges

These challenges extend the core lab tasks. Each is standalone and can be attempted independently after completing the main workbook.

---

## Challenge 1: Custom Default Route Metric in Area 2

By default, the ABR injects the default route into a stub area with a cost of 1. Change the cost of the default route advertised into Area 2 to 50. Verify that R7's routing table reflects the updated metric for `0.0.0.0/0`.

**Hint:** Look for an OSPF area subcommand that sets the cost of the auto-generated default route.

**Success criteria:** `show ip route` on R7 shows `O*IA 0.0.0.0/0 [110/51]` (cost 50 from R3 + 1 for the link).

---

## Challenge 2: Prevent R7 from Becoming DR

On the R3-R7 link (10.37.0.0/30), OSPF will elect a DR/BDR by default. Configure the link so that no DR/BDR election occurs — both ends should become OSPF neighbors without going through the DR/BDR election process.

**Hint:** The network type that eliminates DR election on point-to-point links requires a specific interface-level command.

**Success criteria:** `show ip ospf neighbor` on R3 shows R7 with a neighbor state of `FULL/ -` (no DR designation). `show ip ospf interface FastEthernet1/1` confirms the network type.

---

## Challenge 3: Area 2 with Two Internal Routers

Extend the topology by adding a second router (R8) in Area 2, connecting it to R7 via a new subnet (e.g., 10.78.0.0/30). Configure R8 as a stub router in Area 2. Verify:

1. R8 forms adjacency with R7 (both in Area 2, both stub).
2. R8's routing table contains only its connected routes and the default route — no inter-area routes.
3. R7 can reach R8's loopback, and R1 can reach R8 via the summary route.

**Success criteria:** `show ip ospf neighbor` on R7 shows both R3 and R8 in FULL state. `show ip route` on R8 contains only one OSPF route: `O*IA 0.0.0.0/0`.

---

## Challenge 4: Compare LSDB Size Across All Three Area Types

Capture and compare the LSDB on R7 across all three configurations:

| State              | `show ip ospf database` output | Number of LSAs |
|--------------------|-------------------------------|----------------|
| Normal Area 2      | (capture here)                | ?              |
| Stub Area 2        | (capture here)                | ?              |
| Totally Stubby 2   | (capture here)                | ?              |

Answer the following:

1. How many Type 3 Summary LSAs exist in each state?
2. Which configuration produces the fewest LSAs on R7?
3. If 100 external routes were redistributed into OSPF by an ASBR in Area 0, what would change in the Stub vs Normal comparison?

**Success criteria:** Table completed with accurate LSA counts. Written answers address all three questions.
