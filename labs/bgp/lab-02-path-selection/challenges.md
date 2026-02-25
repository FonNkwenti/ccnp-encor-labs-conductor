# BGP Lab 02: BGP Path Selection Algorithm — Challenge Exercises

These standalone challenges test your ability to apply path selection
manipulation without step-by-step guidance. Complete the core lab first.

---

## Challenge 1: Attribute Interaction — Weight Beats Local Preference

**Scenario:** Configure LP=200 on routes from R2 AND Weight=100 on routes from R3. Which attribute wins? Verify your answer with `show ip bgp 203.0.113.0/24`.

**Expected outcome:** Weight is evaluated first. Routes from R3 with weight=100 beat routes from R2 with weight=0 — even though LP=200 is set on R2's routes. LP is evaluated second only when weights are equal.

---

## Challenge 2: Per-Prefix Weight Using Route-Maps

**Scenario:** Rather than applying weight to all routes from a neighbor, create a route-map that sets weight=500 only for the 172.16.2.2/32 loopback prefix from R2, and weight=0 for all other routes from R2. Verify that only 172.16.2.2/32 shows weight=500.

**Success criteria:**
- `show ip bgp 172.16.2.2/32` shows `weight 500` on the R2 path
- `show ip bgp 198.51.100.0/24` shows default `weight 0` on the R2 path

---

## Challenge 3: Understand MED Non-Transitivity

**Scenario:** On R1, configure MED=50 when advertising to R2. Verify that R2 shows MED=50. Now check R3's BGP table for the same Enterprise prefixes — specifically look at the path R3 receives via R2 (if any). Does R3 see MED=50?

**Expected outcome:** R3 does NOT see MED=50. When R2 forwards the Enterprise prefix to R3, R2 strips the MED (sets it to 0) because MED is non-transitive and is not propagated to other ASes.

---

## Challenge 4: AS-Path Prepend Asymmetry

**Scenario:** Configure R1 to prepend AS 65001 three times when advertising to R3. Verify that R3 now sees Enterprise prefixes with AS-path `65001 65001 65001 65001` (4 hops). Also verify that R2 still sees `65001` (1 hop) — prepending only affects the specified neighbor.

**Success criteria:**
- R3: `show ip bgp 192.168.1.0/24` → AS-path `65001 65001 65001 65001`
- R2: `show ip bgp 192.168.1.0/24` → AS-path `65001`
