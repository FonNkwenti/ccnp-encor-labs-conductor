# BGP Lab 08: Challenges — Route Reflectors & iBGP Scaling

These challenges extend the core lab. Each is standalone — restore the solution state with
`python3 scripts/fault-injection/apply_solution.py` before starting each one.

---

## Challenge 1: Non-Client iBGP Peer

**Scenario:** The enterprise is adding a fourth BGP speaker (hypothetical R7, AS 65001) that must NOT be an RR client — it will be a non-client iBGP peer of R1.

**Task:** Without adding a physical router, model this scenario by understanding the design constraint:

1. Explain in writing (or in a text file) why a non-client peer still requires a full mesh among all non-client peers if there are multiple non-clients
2. On R1, simulate this by temporarily removing `route-reflector-client` from R4 (do NOT change R6's designation)
3. Run `show bgp 192.168.6.0` on R4 — observe that R4 no longer receives R6's prefix
4. Run `show bgp 10.4.1.0` on R6 — observe that R6 still receives R4's prefix (because R6 is still a client)
5. Explain the asymmetry: why does the route flow in one direction but not the other?
6. Restore `route-reflector-client` on R4 and verify symmetric route propagation is restored

**Success criteria:** You can clearly articulate the difference between RR-client and non-client iBGP behavior, and have verified the asymmetry experimentally.

---

## Challenge 2: Hierarchical Route Reflectors

**Scenario:** The enterprise is planning to scale to 50 BGP speakers across multiple data centers. A single RR will become a bottleneck. The team wants to understand hierarchical RR design.

**Task:**

1. On R4 (currently an RR client), configure it as a second Route Reflector in a different cluster (cluster-id 2) — it will serve as an RR for hypothetical downstream clients
2. Add R4 as a client of R1 (R4 is simultaneously a client of R1's cluster 1 AND an RR for cluster 2)
3. Verify that R4 still receives reflected routes from R1 with cluster-list = 0.0.0.1
4. Examine `show bgp 192.168.6.0` on R4 — confirm R4 can see R6's prefix via cluster 1 reflection
5. Explain why hierarchical RRs use different cluster-ids and what would happen if both R1 and R4 used cluster-id 1

**Success criteria:** R4 has `bgp cluster-id 2` configured. `show bgp` on R4 shows routes with cluster-list = 0.0.0.1 (from R1). You can explain the loop prevention role of cluster-id in a hierarchical design.

---

## Challenge 3: RR Redundancy with Two Route Reflectors

**Scenario:** The operations team wants to eliminate the single point of failure on R1. They plan to configure R6 as a second Route Reflector in the same cluster (cluster-id 1), creating a redundant RR pair.

**Task:**

1. Configure R6 as a second Route Reflector with `bgp cluster-id 1` (same cluster as R1)
2. On R6, add R4 as a route-reflector-client (172.16.4.4, update-source Loopback0, next-hop-self)
3. Verify R4 now has two iBGP sessions: one to R1 and one to R6 (both must be Established)
4. On R4, run `show bgp 192.168.6.0` — R4 should now receive two copies of the route (one from each RR); BGP will select one as best
5. Simulate R1 failure by shutting R1's Fa0/0 interface (`shutdown`) and verify R4 still has a valid route to R6's prefix via R6
6. Restore R1's interface and return R6 to its original non-RR client configuration

**Success criteria:** R4 receives routes from both RR1 (R1) and RR2 (R6). When R1's link to R4 is down, R4 continues to learn routes via R6. `show bgp 192.168.6.0` on R4 shows two paths before the failure.

---

## Challenge 4: Prefix Filtering on a Route Reflector

**Scenario:** The security team requires that R4 (Enterprise Internal) must NEVER receive ISP prefixes directly in its BGP table — it should only use the default route originated by R1. However, R6 (Enterprise Edge 2) should receive full ISP routes for policy decisions.

**Task:**

1. Create an outbound prefix-list on R1 for the neighbor R4 that permits only the default route (0.0.0.0/0) and denies all ISP prefixes (198.51.100.0/22 and 203.0.113.0/22 le 24)
2. Apply the prefix-list as a distribute-list outbound to neighbor 172.16.4.4
3. Perform a soft-reset outbound on R1 toward R4
4. Verify on R4: `show bgp` must NOT contain any 198.51.x.x or 203.0.x.x prefixes; it must contain the 0.0.0.0/0 default route
5. Verify on R6: `show bgp` must still contain all ISP prefixes (the filter only applies to R4)
6. Confirm that R4 still has enterprise-internal prefixes from R6 via reflection (192.168.6.0/24 must be present)

**Success criteria:** R4's BGP table contains zero ISP prefixes and a valid default route. R6's BGP table is unchanged. The prefix-list does not affect R6 or the eBGP sessions on R1.
