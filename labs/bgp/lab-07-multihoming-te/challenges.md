# BGP Lab 07 — Challenge Exercises

These challenges extend the core lab tasks. Each challenge is self-contained and builds on the completed Lab 07 solution state.

---

## Challenge 1: Weight-Based Local TE for a Single Admin Station

**Background:** BGP Weight is a Cisco-proprietary attribute that is locally significant (not propagated). It takes precedence over Local Preference.

**Challenge:** Configure R1 so that all routes received from ISP-B (R3) that match 203.0.115.0/24 are given a Weight of 50000 on R1. All other routes from ISP-B retain their existing LP policy. Verify that R1 selects 203.0.115.0/24 via ISP-B even if ISP-B's LP for that prefix drops below ISP-A's LP.

**Hints:**
- Weight is set via `set weight` in a route-map
- Weight is evaluated before Local Preference in the BGP path selection order
- You will need a new route-map sequence or a separate route-map on the ISP-B inbound neighbor

**Verification:**
```
R1# show ip bgp 203.0.115.0
(Expect: Weight = 50000, path via R3)
```

---

## Challenge 2: Prefix-Specific Backup via ISP-B with Failover

**Background:** The conditional default in Task 4 protects R4 when ISP-A goes down. But what about individual enterprise prefixes?

**Challenge:** Configure R1 so that 192.168.3.0/24 is advertised outbound to both ISP-A and ISP-B with equal MEDs (MED=50). Then simulate ISP-A failure by shutting R1's Fa1/0 interface. Verify that:
1. R1 withdraws all ISP-A routes from its BGP table
2. R4 loses its conditional default route
3. Traffic from R3 (ISP-B) continues to reach 192.168.3.0/24 via R1's Fa1/1

**Steps:**
1. Confirm 192.168.3.0/24 is advertised with MED=50 to both ISPs (already done in Lab 07)
2. Simulate ISP-A failure: `interface FastEthernet1/0` → `shutdown`
3. Observe BGP reconvergence on R1 and R4

**Verification:**
```
R1# show ip bgp summary
R4# show ip route 0.0.0.0
R3# show ip bgp 192.168.3.0
```

---

## Challenge 3: MED Propagation via ISP Peering

**Background:** R2 (ISP-A) and R3 (ISP-B) have an eBGP peering (10.1.23.0/30). By default, MED is reset to 0 when a route is re-advertised to a third AS. However, ISPs sometimes preserve MED within their own network.

**Challenge:** Configure R2 to preserve the MED received from R1 (65001) when advertising those routes to R3. Then observe what R3 sees for enterprise prefixes. Enable `bgp always-compare-med` on R3 and observe how it changes R3's path selection for enterprise prefixes when received from both R2 and directly from R1.

**Hints:**
- Use `neighbor 10.1.23.2 metric-out` or check if R2 passes MED by default
- `bgp always-compare-med` on R3 enables cross-AS MED comparison

**Verification:**
```
R3# show ip bgp 192.168.1.0
(Compare paths — which path does R3 prefer?)
```

---

## Challenge 4: Outbound Policy Using BGP Communities from ISP-A

**Background:** Real ISPs often accept community values from customers to trigger policy actions (e.g., blackholing, LP adjustment). In this challenge, you simulate ISP-A (R2) implementing a community-based policy for its customer (R1).

**Challenge:**
1. On R2, configure a community-list that matches community 65001:200
2. If a route from R1 carries community 65001:200, R2 sets LP=50 for that route (making it a last-resort path within ISP-A's network)
3. On R1, tag 192.168.3.0/24 with community 65001:200 in the TE-TO-ISP-A route-map
4. Verify R2 has reduced LP on 192.168.3.0/24

**Verification:**
```
R2# show ip bgp 192.168.3.0
(Expect: Local preference 50)
```

---

## Challenge 5: Selective Route Advertisement with Default-Only to R4

**Challenge:** Rather than advertising all internet prefixes to R4 via iBGP, configure R1 to send only the conditional default route to R4. Remove all other iBGP route advertisements to R4 so that R4's routing table is clean: it has only the default route pointing to R1 for internet access.

**Hints:**
- Use a route-map on `neighbor 172.16.4.4` outbound that only permits 0.0.0.0/0
- Or use a prefix-list filtering all routes except 0/0 on the outbound direction to R4

**Verification:**
```
R4# show ip bgp
(Expect: Only 0.0.0.0/0 and internally redistributed routes)
R4# show ip route bgp
```

---

## Challenge 6: AS-Path Prepend Asymmetry — Inbound vs. Outbound Traffic Mismatch

**Background:** Inbound TE (prepending) and outbound TE (LP) can create routing asymmetry where traffic enters via one ISP and exits via another.

**Challenge:** Analyze the current routing configuration and answer:
1. For a flow from R2 (ISP-A) to 192.168.1.0/24: Which ISP does R2 use to reach R1? (ISP-A direct — no prepend on ISP-A side for 192.168.1.0)
2. For the return traffic from R1 (to reach R2's 198.51.100.0/24): Which path does R1 use? (ISP-A — LP=200)
3. Is this flow symmetric or asymmetric?

Then: Introduce an asymmetry by prepending 192.168.1.0/24 outbound to BOTH ISPs. Observe how path selection changes on R2 and R3.

**Document your findings as a table:**

| Traffic Direction | Source | Destination | Entry ISP | Exit ISP | Symmetric? |
|---|---|---|---|---|---|
| Internet to Enterprise | R2 | 192.168.1.0/24 | ISP-A | — | — |
| Enterprise to Internet | R1 | 198.51.100.0/24 | — | ISP-A | — |

---

## Challenge 7: Atomic Aggregate and Route Summarization

**Background:** R1 currently advertises individual /24 prefixes. In production, summarization is common to reduce BGP table size.

**Challenge:**
1. On R1, add a summary prefix 192.168.0.0/22 using `aggregate-address 192.168.0.0 255.255.252.0 summary-only`
2. Observe that the individual /24s are suppressed from being advertised
3. Note the `atomic-aggregate` attribute that IOS automatically sets on the summary
4. Re-enable specific prefix advertisement by removing `summary-only` and adding `suppress-map` to only suppress 192.168.2.0/24

**Verification:**
```
R2# show ip bgp 192.168.0.0
(Expect: Atomic-aggregate attribute, 192.168.0.0/22 summary)
R2# show ip bgp 192.168.1.0
(With summary-only: not present. Without: present)
R1# show ip bgp
(Expect: s> for suppressed routes)
```
