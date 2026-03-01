# OSPF Lab 08 — Extended Challenges

These four exercises extend the core lab. Complete them after finishing the main workbook tasks. No step-by-step guidance is provided.

---

## Challenge 1: OSPFv3 Authentication with IPsec

OSPFv3 does not support MD5 or SHA key-chain authentication at the interface level like OSPFv2 does. Instead, it relies on IPsec AH (Authentication Header) to authenticate OSPFv3 packets. Configure IPsec AH-SHA1 authentication for OSPFv3 Area 0 on R1 and R2, then verify the adjacency is authenticated.

**Acceptance criteria:**
- `show ospfv3 interface FastEthernet1/0` on R1 confirms the authentication type (AH SHA1)
- `show ospfv3 neighbor` shows R2 remains `FULL` after authentication is applied
- R3 (Area 1, no IPsec) is unaffected

**Hint:** Use `ospfv3 authentication ipsec spi <value> sha1 <key>` on the interface. Both ends of the link must use identical SPI values and keys. IOS 15.x requires `crypto engine accelerator` or software crypto support.

---

## Challenge 2: OSPFv3 Stub Area for R6

R6 is a leaf router with only one uplink to R1. Reconfigure the R1–R6 connection so that Area 0 is split: move the R1–R6 link into a new **Area 3** and configure Area 3 as a stub area. R6 should receive a default route from R1 instead of the full OSPF topology.

**Acceptance criteria:**
- `show ospfv3` on R6 shows Area 3 as stub
- `show ipv6 route` on R6 shows a default route (`OI ::/0`) pointing to R1
- `show ospfv3 database` on R6 shows no external or inter-area LSAs for specific prefixes (only the default)
- Ping from R6 to `2001:DB8:3::3` still succeeds (via the default route)

**Hint:** Configure `area 3 stub` under OSPFv3 process on both R1 and R6. Deactivate the Gi3/0 interfaces from Area 0 and re-activate them in Area 3.

---

## Challenge 3: OSPFv3 Reference Bandwidth Drift

A new engineer accidentally reconfigured `auto-cost reference-bandwidth 100` (instead of 1000) in R2's `ipv6 unicast` address family only. This creates a split-brain situation where IPv4 and IPv6 have different costs for the same links.

Starting from the solution state: manually introduce this fault on R2, then diagnose it from R3's routing table by comparing IPv4 and IPv6 metrics to the same destination, and fix it.

**Acceptance criteria:**
- Before fix: R3's `show ip route 10.2.2.2` and `show ipv6 route 2001:DB8:2::2` show different metrics
- After fix: Both show metric `21` (cost 10 R3→R2 via Area 1 + cost 11 on R2's Lo0, reference bandwidth 1000)
- `show ospfv3` on all routers confirms `auto-cost reference-bandwidth 1000` in both AFs

**Hint:** Use `show ospfv3` on each router to confirm the reference bandwidth setting per AF. An inconsistency creates asymmetric metrics between IPv4 and IPv6 for the same physical path.

---

## Challenge 4: Dual-Stack Default Route Origination

R6 is meant to serve as the IPv4 and IPv6 default gateway for the domain. Configure R6 to originate a default route into OSPFv3 for both address families, so that R1, R2, and R3 see a default route pointing to R6.

**Acceptance criteria:**
- `show ip route` on R1 shows `O*E2 0.0.0.0/0` via `10.16.0.2`
- `show ipv6 route` on R1 shows `OE2 ::/0` via R6's link-local on Gi3/0
- `show ip route` and `show ipv6 route` on R3 also show the default routes (propagated via inter-area)
- Existing specific routes are still present (default route does not replace them)

**Hint:** Under the OSPFv3 process on R6, add `default-information originate always` inside both the `address-family ipv4 unicast` and `address-family ipv6 unicast` blocks. The `always` keyword forces origination even if R6 has no default route of its own.
