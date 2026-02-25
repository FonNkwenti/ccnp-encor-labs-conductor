# BGP Lab 05 — Challenge Exercises: AS-Path Manipulation & Route-Maps

These challenges extend the core lab. Complete the main workbook before attempting these.

---

## Challenge 1: Match Locally Originated Routes

Use an AS-path ACL with the `^$` (empty) pattern to match only routes originated locally (by this router) in the BGP table.

**Task:**
1. Configure `ip as-path access-list 10 permit ^$`
2. Run `show ip bgp regexp ^$` on R1
3. Explain what prefixes appear and why

**Expected:** Only routes originating from R1 itself (192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24, 172.16.1.1/32) appear — prefixes that R1 injected via `network` statements. Their AS-path is empty (they haven't transited any AS).

---

## Challenge 2: Conditional Route Advertisement Using advertise-map

Cisco IOS supports conditional BGP advertisement: advertise a route only if a condition route exists (or doesn't exist) in the BGP table.

**Task:**
1. Create a route-map `EXIST-MAP` that matches `198.51.100.0/24` (ISP-A's primary prefix)
2. Create a route-map `ADV-MAP` that matches `192.168.3.0/24` (enterprise secondary subnet)
3. Configure: `neighbor 10.1.13.2 advertise-map ADV-MAP exist-map EXIST-MAP`
4. Verify on R3 that `192.168.3.0/24` appears when `198.51.100.0/24` is present on R1

This simulates conditional advertisement: only announce the backup prefix if the primary ISP is reachable.

---

## Challenge 3: AS-Path Prepend Only Specific Prefixes

Modify the `PREPEND-TO-ISP-B` route-map to apply different prepend depths to different prefixes:
- `192.168.1.0/24` (primary): no prepend (R3 may use this path equally)
- `192.168.2.0/24` (secondary): prepend 1 extra hop
- `192.168.3.0/24` (tertiary): prepend 3 extra hops

**Task:** Create three separate prefix-lists and three route-map sequences:
```
route-map PREPEND-TO-ISP-B permit 5
 match ip address prefix-list PFX-192-168-1
 ! no set — advertise as-is
route-map PREPEND-TO-ISP-B permit 10
 match ip address prefix-list PFX-192-168-2
 set as-path prepend 65001
route-map PREPEND-TO-ISP-B permit 15
 match ip address prefix-list PFX-192-168-3
 set as-path prepend 65001 65001 65001
route-map PREPEND-TO-ISP-B permit 20
```

Verify on R3 that each enterprise prefix shows a different AS-path length.

---

## Challenge 4: Route-Map with Multiple Match Conditions

Build a route-map sequence that matches BOTH a prefix-list AND an AS-path ACL (both conditions must be true for the clause to match).

**Task:**
1. Create a route-map `STRICT-MATCH` with a sequence that:
   - Matches prefix-list `ENTERPRISE-PREFIXES` (192.168.x.x/24)
   - AND matches AS-path ACL for empty path (`^$`) — locally originated
2. Apply as outbound to R3
3. Explain the logic: only routes that are BOTH enterprise /24 subnets AND locally originated on R1 will match (not routes redistributed from elsewhere)

**Key concept:** Multiple `match` clauses in one route-map sequence are AND conditions. Separate sequences are OR conditions.

---

## Challenge 5: Audit Route-Map Effectiveness

After completing the lab, document the effectiveness of each route-map by examining match counters and comparing BGP tables before and after applying policies.

**Task:** For each route-map (`SET-LP-200-ISP-A`, `POLICY-ISP-B-IN`, `PREPEND-TO-ISP-B`):
1. Run `show route-map NAME` and record the match count for each sequence
2. Identify which sequences matched zero routes (potential misconfiguration or unnecessary rule)
3. Verify that `show ip bgp` on R3 confirms AS-path prepending is active for enterprise prefixes

This mirrors a real-world change validation process.
