# BGP Lab 07 — Multihoming & Traffic Engineering

> **Prerequisites:** BGP Lab 06 (Communities & Policy Control) must be complete.
> Initial configs for this lab are the Lab 06 solutions.

---

## 1. Concepts & Skills Covered

| Concept | Description |
|---|---|
| BGP Multihoming | Dual-ISP connectivity for redundancy and load distribution |
| Outbound Traffic Engineering | Local Preference per-prefix to steer egress traffic per ISP |
| Inbound Traffic Engineering | AS-Path prepending to influence remote ISP path selection |
| MED (Multi-Exit Discriminator) | Signaling preferred ingress point to directly connected ISPs |
| Conditional Default Route | `default-originate route-map` to inject 0/0 only when a condition is met |
| Route-Map Sequencing | Correct ordering of match/set clauses to avoid catch-all masking |
| Prefix-List Granularity | Per-prefix prefix-lists enabling prefix-specific TE policies |

### Key BGP Attributes Used in This Lab

- **Local Preference (LOCAL_PREF):** Influences outbound path selection within the AS. Higher is preferred. Set inbound.
- **AS-Path Prepend:** Artificially lengthens the AS-path. Used outbound to make a path less preferred by remote ASes.
- **MED (metric):** Suggests preferred ingress point to a directly connected AS. Lower is preferred. Compared only between routes from the same AS by default.
- **Conditional Default:** `neighbor X default-originate route-map Y` — sends 0.0.0.0/0 to neighbor X only if route-map Y matches something in the local BGP table.

---

## 2. Topology & Scenario

```
           AS 65002 (ISP-A)
               R2
              /  \
    Fa1/0 .1/    \.2 Fa1/0
           /      \
    Fa1/0.2        Fa0/0.2
      R1 ---------- R3
    Fa0/0           Fa1/0 .2
      |         AS 65003 (ISP-B)
    Fa0/0 .1        |
      R4           Fa1/1 .1
  (iBGP/OSPF)      |
                   R5
            AS 65004 (Downstream)
```

### Network Overview

**R1 (Enterprise Edge — AS 65001)** is dual-homed to two ISPs:
- **ISP-A (R2, AS 65002):** Primary uplink. Enterprise prefers ISP-A for internet egress on most prefixes.
- **ISP-B (R3, AS 65003):** Secondary uplink. Enterprise uses ISP-B as backup and for inbound traffic on selected prefixes.

**R4 (Enterprise Internal — AS 65001)** is an iBGP peer to R1. It receives a conditional default route from R1 only when ISP-A's 198.51.100.0/24 is reachable.

**Traffic Engineering Goals:**
1. Enterprise outbound traffic to ISP-A prefixes exits via ISP-A; outbound to ISP-B prefixes exits via ISP-B.
2. Inbound traffic to 192.168.1.0/24 prefers ISP-A as entry point; 192.168.2.0/24 prefers ISP-B.
3. MEDs signal preferred ingress to each ISP.
4. R4 gets a default route only while ISP-A's primary prefix (198.51.100.0/24) is present.

### IP Addressing Summary

| Link | Subnet | R1 | Peer |
|---|---|---|---|
| R1-R2 (ISP-A) | 10.1.12.0/30 | Fa1/0 .1 | R2 Fa0/0 .2 |
| R1-R3 (ISP-B) | 10.1.13.0/30 | Fa1/1 .1 | R3 Fa1/0 .2 |
| R1-R4 (internal) | 10.1.14.0/30 | Fa0/0 .1 | R4 Fa0/0 .2 |
| R2-R3 (ISP peering) | 10.1.23.0/30 | — | R2 Fa1/0 .1 / R3 Fa0/0 .2 |
| R3-R5 (customer) | 10.1.35.0/30 | — | R3 Fa1/1 .1 / R5 Fa0/0 .2 |

---

## 3. Hardware & Environment Specifications

### Device Platform Table

| Device | Role | Platform |
|---|---|---|
| R1 | Enterprise Edge | c7200 |
| R2 | ISP-A | c7200 |
| R3 | ISP-B | c7200 |
| R4 | Enterprise Internal | c3725 |
| R5 | Downstream Customer | c3725 |

### Console Access Table

| Device | Telnet Port |
|---|---|
| R1 | 5001 |
| R2 | 5002 |
| R3 | 5003 |
| R4 | 5004 |
| R5 | 5005 |

```bash
# Connect to any router console
telnet 127.0.0.1 5001   # R1
telnet 127.0.0.1 5002   # R2
telnet 127.0.0.1 5003   # R3
telnet 127.0.0.1 5004   # R4
telnet 127.0.0.1 5005   # R5
```

### Interface Assignments

**R1 (c7200):** fa0/0, fa1/0, fa1/1, Lo0–Lo3
**R2 (c7200):** fa0/0, fa1/0, Lo0–Lo3
**R3 (c7200):** fa0/0, fa1/0, fa1/1, Lo0–Lo3
**R4 (c3725):** fa0/0, Lo0–Lo2
**R5 (c3725):** fa0/0, Lo0–Lo2

---

## 4. Base Configuration

Load the Lab 06 solution configs as the starting point. These configs are pre-built into the `initial-configs/` directory.

```bash
python3 setup_lab.py
```

### What Is Already Configured

After loading the initial configs, the following is in place on R1:
- iBGP session to R4 (172.16.4.4) via OSPF-learned loopback
- eBGP sessions to R2 (10.1.12.2, AS 65002) and R3 (10.1.13.2, AS 65003)
- Community-list CUSTOMER-ROUTES matching 65003:500
- Route-maps: SET-LP-200-ISP-A, POLICY-ISP-B-IN, PREPEND-TO-ISP-B, SET-COMMUNITY-OUT
- Enterprise prefixes 192.168.1-3.0/24 advertised via BGP

### Verification: Confirm Starting State

```
R1# show ip bgp summary
R1# show ip bgp
R1# show ip bgp neighbors 10.1.12.2 | include route-map
R1# show ip bgp neighbors 10.1.13.2 | include route-map
```

All three BGP sessions should be Established before beginning the lab tasks.

---

## 5. Lab Challenge

### Overview

You will replace the coarse Lab 06 route-maps with granular, per-prefix traffic engineering policies on R1. R2, R3, R4, and R5 require no changes.

---

### Task 1: Per-Prefix Outbound Traffic Engineering via Local Preference

**Goal:** Replace the existing inbound route-maps with per-prefix LP policies so that:
- ISP-A prefixes (198.51.100-102.0/24) received via ISP-A get LP=200 (prefer ISP-A for those destinations)
- ISP-B prefixes (203.0.113-115.0/24) received via ISP-B get LP=200 (prefer ISP-B for those destinations)
- Customer routes tagged 65003:500 get LP=120
- All other routes get LP=150

**Step 1.1 — Create per-ISP prefix-lists on R1:**

```
ip prefix-list ISP-A-PREFIXES seq 10 permit 198.51.100.0/24
ip prefix-list ISP-A-PREFIXES seq 20 permit 198.51.101.0/24
ip prefix-list ISP-A-PREFIXES seq 30 permit 198.51.102.0/24
ip prefix-list ISP-B-PREFIXES seq 10 permit 203.0.113.0/24
ip prefix-list ISP-B-PREFIXES seq 20 permit 203.0.114.0/24
ip prefix-list ISP-B-PREFIXES seq 30 permit 203.0.115.0/24
```

**Step 1.2 — Create LP-FROM-ISP-A route-map (replaces SET-LP-200-ISP-A):**

```
route-map LP-FROM-ISP-A permit 10
 match ip address prefix-list ISP-A-PREFIXES
 set local-preference 200
route-map LP-FROM-ISP-A permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
route-map LP-FROM-ISP-A permit 30
 set local-preference 150
```

**Step 1.3 — Create LP-FROM-ISP-B route-map (replaces POLICY-ISP-B-IN):**

```
route-map LP-FROM-ISP-B permit 10
 match ip address prefix-list ISP-B-PREFIXES
 set local-preference 200
route-map LP-FROM-ISP-B permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
route-map LP-FROM-ISP-B permit 30
 set local-preference 150
```

**Step 1.4 — Apply to BGP neighbors on R1:**

```
router bgp 65001
 no neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in
 neighbor 10.1.12.2 route-map LP-FROM-ISP-A in
 no neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in
 neighbor 10.1.13.2 route-map LP-FROM-ISP-B in
```

**Step 1.5 — Reset inbound updates:**

```
clear ip bgp 10.1.12.2 soft in
clear ip bgp 10.1.13.2 soft in
```

---

### Task 2: Inbound Traffic Engineering via AS-Path Prepending

**Goal:** Steer internet inbound traffic so that:
- 192.168.1.0/24 is preferred via ISP-A — prepend 3x on outbound to ISP-B
- 192.168.2.0/24 is preferred via ISP-B — prepend 3x on outbound to ISP-A

**Step 2.1 — Create per-enterprise prefix-lists on R1:**

```
ip prefix-list PREFIX-192-168-1 seq 10 permit 192.168.1.0/24
ip prefix-list PREFIX-192-168-2 seq 10 permit 192.168.2.0/24
ip prefix-list PREFIX-192-168-3 seq 10 permit 192.168.3.0/24
```

**Step 2.2 — Build TE-TO-ISP-A route-map** (192.168.2 gets prepended, 192.168.1 gets low MED as primary):
See Task 3 below — MED and prepend are configured together in the same route-map.

---

### Task 3: MED for Inbound Traffic Hints

**Goal:** Set MED values on outbound advertisements so each ISP understands which enterprise prefix is preferred inbound via which link:
- Via ISP-A: 192.168.1 preferred (MED=10), 192.168.3 secondary (MED=50), 192.168.2 deprioritized (MED=100 + prepend)
- Via ISP-B: 192.168.2 preferred (MED=10), 192.168.3 secondary (MED=50), 192.168.1 deprioritized (MED=100 + prepend)

**Step 3.1 — Create TE-TO-ISP-A route-map (replaces SET-COMMUNITY-OUT):**

```
route-map TE-TO-ISP-A permit 10
 match ip address prefix-list PREFIX-192-168-2
 set as-path prepend 65001 65001 65001
 set metric 100
route-map TE-TO-ISP-A permit 20
 match ip address prefix-list PREFIX-192-168-1
 set metric 10
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 40
 set community 65001:100 additive
```

**Step 3.2 — Create TE-TO-ISP-B route-map (replaces PREPEND-TO-ISP-B):**

```
route-map TE-TO-ISP-B permit 10
 match ip address prefix-list PREFIX-192-168-1
 set as-path prepend 65001 65001 65001
 set metric 100
route-map TE-TO-ISP-B permit 20
 match ip address prefix-list PREFIX-192-168-2
 set metric 10
 set community 65001:100 additive
route-map TE-TO-ISP-B permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
route-map TE-TO-ISP-B permit 40
 set community 65001:100 additive
```

**Step 3.3 — Apply outbound route-maps on R1:**

```
router bgp 65001
 no neighbor 10.1.12.2 route-map SET-COMMUNITY-OUT out
 neighbor 10.1.12.2 route-map TE-TO-ISP-A out
 no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out
 neighbor 10.1.13.2 route-map TE-TO-ISP-B out
```

**Step 3.4 — Reset outbound updates:**

```
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out
```

---

### Task 4: Conditional Default Route Origination

**Goal:** R1 should advertise a default route (0.0.0.0/0) to R4 only while ISP-A's primary prefix 198.51.100.0/24 is present in R1's BGP table. If ISP-A goes down and 198.51.100.0/24 disappears, R4 loses its default route.

**Step 4.1 — Create the condition prefix-list:**

```
ip prefix-list COND-DEFAULT-CHECK seq 10 permit 198.51.100.0/24
```

**Step 4.2 — Create the condition route-map:**

```
route-map COND-DEFAULT permit 10
 match ip address prefix-list COND-DEFAULT-CHECK
```

**Step 4.3 — Add static default pointing to Null0 (required for IOS conditional default-originate):**

```
ip route 0.0.0.0 0.0.0.0 Null0
```

**Step 4.4 — Apply conditional default to the R4 neighbor:**

```
router bgp 65001
 neighbor 172.16.4.4 default-originate route-map COND-DEFAULT
```

**Step 4.5 — Verify R4 receives the default:**

```
R4# show ip bgp
R4# show ip route 0.0.0.0
```

---

## 6. Verification & Analysis

### Task 1 Verification: Outbound LP Policy

```
R1# show ip bgp 198.51.100.0
R1# show ip bgp 203.0.113.0
```

Expected:
- 198.51.100.0/24 via R2 (ISP-A): Local preference = 200
- 203.0.113.0/24 via R3 (ISP-B): Local preference = 200
- Routes from the non-native ISP: Local preference = 150

```
R1# show ip bgp | include 198.51
R1# show ip bgp | include 203.0
```

Confirm that for each ISP's own prefixes, the path via that ISP has the highest LP.

### Task 2 Verification: AS-Path Prepend

```
R2# show ip bgp 192.168.2.0
R3# show ip bgp 192.168.1.0
```

Expected:
- R2 sees 192.168.2.0/24 with AS-path: 65001 65001 65001 65001 (4 entries — 3 prepends + originating AS)
- R3 sees 192.168.1.0/24 with AS-path: 65001 65001 65001 65001 (4 entries)

```
R2# show ip bgp 192.168.1.0
```

Expected: AS-path for 192.168.1.0/24 from R1 shows just 65001 (no prepend — this is the preferred path via ISP-A).

### Task 3 Verification: MED Values

```
R2# show ip bgp 192.168.1.0
R2# show ip bgp 192.168.2.0
R3# show ip bgp 192.168.1.0
R3# show ip bgp 192.168.2.0
```

Expected on R2 (ISP-A):
- 192.168.1.0/24: Metric = 10 (low — preferred ingress via ISP-A)
- 192.168.2.0/24: Metric = 100 (high — ISP-B is preferred ingress for this prefix)

Expected on R3 (ISP-B):
- 192.168.2.0/24: Metric = 10 (low — preferred ingress via ISP-B)
- 192.168.1.0/24: Metric = 100 (high — ISP-A is preferred ingress for this prefix)

### Task 4 Verification: Conditional Default

```
R4# show ip bgp
R4# show ip route 0.0.0.0
```

Expected: R4 has a BGP default route 0.0.0.0/0 with next-hop 172.16.1.1.

To test the conditional: On R2, remove the 198.51.100.0 network statement and observe R4 losing its default route.

```
R1# show ip bgp 198.51.100.0
(After R2 withdraws it — should disappear from R1's table)
R4# show ip route 0.0.0.0
(Should no longer be present)
```

---

## 7. Verification Cheatsheet

### Quick Reference Commands

| Purpose | Command |
|---|---|
| BGP summary | `show ip bgp summary` |
| Full BGP table | `show ip bgp` |
| Specific prefix detail | `show ip bgp 192.168.1.0` |
| LP of all ISP-A prefixes | `show ip bgp \| include 198.51` |
| LP of all ISP-B prefixes | `show ip bgp \| include 203.0` |
| AS-path seen by ISP-A | R2# `show ip bgp 192.168.2.0` |
| MED seen by ISP-A | R2# `show ip bgp 192.168.1.0` |
| Default route on R4 | R4# `show ip route 0.0.0.0` |
| BGP default from R1 | R4# `show ip bgp 0.0.0.0` |
| Neighbor route-map applied | `show ip bgp neighbors 10.1.12.2 \| include route-map` |
| Outbound advertised routes | `show ip bgp neighbors 10.1.12.2 advertised-routes` |
| Inbound received routes | `show ip bgp neighbors 10.1.12.2 received-routes` |
| Prefix-list summary | `show ip prefix-list` |
| Route-map detail | `show route-map LP-FROM-ISP-A` |
| Static routes | `show ip route static` |

### Expected End-State Summary

| Prefix | Via ISP-A: LP | Via ISP-B: LP | Outbound to ISP-A: MED | Outbound to ISP-B: MED |
|---|---|---|---|---|
| 198.51.100.0/24 | 200 | 150 | — | — |
| 203.0.113.0/24 | 150 | 200 | — | — |
| 192.168.1.0/24 | — | — | 10 | 100+prepend |
| 192.168.2.0/24 | — | — | 100+prepend | 10 |
| 192.168.3.0/24 | — | — | 50 | 50 |

---

## 8. Solutions

<details>
<summary>Task 1 Complete Solution — Per-Prefix Local Preference</summary>

```
! On R1:
ip prefix-list ISP-A-PREFIXES seq 10 permit 198.51.100.0/24
ip prefix-list ISP-A-PREFIXES seq 20 permit 198.51.101.0/24
ip prefix-list ISP-A-PREFIXES seq 30 permit 198.51.102.0/24
ip prefix-list ISP-B-PREFIXES seq 10 permit 203.0.113.0/24
ip prefix-list ISP-B-PREFIXES seq 20 permit 203.0.114.0/24
ip prefix-list ISP-B-PREFIXES seq 30 permit 203.0.115.0/24
!
route-map LP-FROM-ISP-A permit 10
 match ip address prefix-list ISP-A-PREFIXES
 set local-preference 200
route-map LP-FROM-ISP-A permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
route-map LP-FROM-ISP-A permit 30
 set local-preference 150
!
route-map LP-FROM-ISP-B permit 10
 match ip address prefix-list ISP-B-PREFIXES
 set local-preference 200
route-map LP-FROM-ISP-B permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
route-map LP-FROM-ISP-B permit 30
 set local-preference 150
!
router bgp 65001
 no neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in
 neighbor 10.1.12.2 route-map LP-FROM-ISP-A in
 no neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in
 neighbor 10.1.13.2 route-map LP-FROM-ISP-B in
!
clear ip bgp 10.1.12.2 soft in
clear ip bgp 10.1.13.2 soft in
```

Key point: Sequence 10 catches ISP-native prefixes first (LP=200), sequence 20 catches customer routes (LP=120), and the catch-all sequence 30 applies LP=150 to all remaining routes. Ordering is critical — if the catch-all was first, all routes would get LP=150 regardless.

</details>

<details>
<summary>Task 2 Complete Solution — AS-Path Prepending</summary>

```
! On R1:
ip prefix-list PREFIX-192-168-1 seq 10 permit 192.168.1.0/24
ip prefix-list PREFIX-192-168-2 seq 10 permit 192.168.2.0/24
ip prefix-list PREFIX-192-168-3 seq 10 permit 192.168.3.0/24
!
! TE-TO-ISP-A: prepend 192.168.2 (want ISP-B ingress for it)
route-map TE-TO-ISP-A permit 10
 match ip address prefix-list PREFIX-192-168-2
 set as-path prepend 65001 65001 65001
 set metric 100
route-map TE-TO-ISP-A permit 20
 match ip address prefix-list PREFIX-192-168-1
 set metric 10
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 40
 set community 65001:100 additive
!
! TE-TO-ISP-B: prepend 192.168.1 (want ISP-A ingress for it)
route-map TE-TO-ISP-B permit 10
 match ip address prefix-list PREFIX-192-168-1
 set as-path prepend 65001 65001 65001
 set metric 100
route-map TE-TO-ISP-B permit 20
 match ip address prefix-list PREFIX-192-168-2
 set metric 10
 set community 65001:100 additive
route-map TE-TO-ISP-B permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
route-map TE-TO-ISP-B permit 40
 set community 65001:100 additive
!
router bgp 65001
 no neighbor 10.1.12.2 route-map SET-COMMUNITY-OUT out
 neighbor 10.1.12.2 route-map TE-TO-ISP-A out
 no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out
 neighbor 10.1.13.2 route-map TE-TO-ISP-B out
!
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out
```

Verify on ISP-A (R2):
```
R2# show ip bgp 192.168.2.0
(Expect AS-path: 65001 65001 65001 65001 — 3 prepends visible)
R2# show ip bgp 192.168.1.0
(Expect AS-path: 65001 — no prepend, this is the preferred path)
```

</details>

<details>
<summary>Task 3 Complete Solution — MED Values</summary>

MED is set within the same TE-TO-ISP-A and TE-TO-ISP-B route-maps created in Task 2. No additional configuration is needed beyond what was done in Task 2 steps above.

Verify the MED values are visible on the ISP routers:

```
R2# show ip bgp 192.168.1.0
! Expect: Metric 10 (low — ISP-A is preferred ingress for 192.168.1.0)

R2# show ip bgp 192.168.2.0
! Expect: Metric 100 (high — ISP-B is preferred ingress for 192.168.2.0)

R3# show ip bgp 192.168.2.0
! Expect: Metric 10 (low — ISP-B is preferred ingress for 192.168.2.0)

R3# show ip bgp 192.168.1.0
! Expect: Metric 100 (high — ISP-A is preferred ingress for 192.168.1.0)
```

Important: MED is only compared between routes from the **same neighboring AS**. Since R2 and R3 are different ASes, R2 will not compare its MED against R3's MED without `bgp always-compare-med`. This lab uses MED as a hint to the directly connected ISP about which of **its own** entry points is preferred.

</details>

<details>
<summary>Task 4 Complete Solution — Conditional Default Route</summary>

```
! On R1:
ip prefix-list COND-DEFAULT-CHECK seq 10 permit 198.51.100.0/24
!
route-map COND-DEFAULT permit 10
 match ip address prefix-list COND-DEFAULT-CHECK
!
ip route 0.0.0.0 0.0.0.0 Null0
!
router bgp 65001
 neighbor 172.16.4.4 default-originate route-map COND-DEFAULT
```

How it works:
1. The `ip route 0.0.0.0 0.0.0.0 Null0` creates a static default in the routing table. This is required by IOS for `default-originate route-map` to function — the router needs 0/0 to exist locally before it can originate it.
2. The route-map COND-DEFAULT checks whether 198.51.100.0/24 exists in the BGP table.
3. If the match succeeds (198.51.100.0 is present), R1 sends 0.0.0.0/0 to R4.
4. If R2 withdraws 198.51.100.0/24 (ISP-A down), the route-map no longer matches, and R1 withdraws the default from R4.

Verify:
```
R4# show ip bgp
! Expect: 0.0.0.0/0 with next-hop 172.16.1.1

R4# show ip route 0.0.0.0
! Expect: B* 0.0.0.0/0 [200/0] via 172.16.1.1

R1# show ip bgp neighbors 172.16.4.4 advertised-routes | include 0.0.0.0
! Expect: 0.0.0.0 0.0.0.0
```

</details>

---

## 9. Troubleshooting Scenarios

### Ticket 1

**Symptom:** R4 is not receiving any default route from R1, even though ISP-A is up and 198.51.100.0/24 is visible in R1's BGP table.

**Verification commands:**

```
R1# show ip bgp neighbors 172.16.4.4 advertised-routes | include 0.0.0.0
R1# show ip route static
R4# show ip bgp
R4# show ip route 0.0.0.0
```

**What to look for:**
- R1's BGP neighbor 172.16.4.4 is not advertising 0.0.0.0/0
- R1's routing table has no static default route (`show ip route static` returns empty or no 0.0.0.0)
- R1 does have 198.51.100.0/24 in BGP table

**Root Cause and Fix:**

<details>
<summary>Ticket 1 Solution</summary>

The root cause is one of the following:

**Cause A:** The `ip route 0.0.0.0 0.0.0.0 Null0` static route is missing. IOS requires a local 0/0 entry in the routing table before it will originate a default via `default-originate route-map`.

Fix:
```
R1(config)# ip route 0.0.0.0 0.0.0.0 Null0
```

**Cause B:** The COND-DEFAULT route-map references a wrong or non-existent prefix-list name. For example, it might reference `COND-DEFAULT-CHK` instead of `COND-DEFAULT-CHECK`.

Fix:
```
R1# show route-map COND-DEFAULT
! Check the match statement

R1(config)# no route-map COND-DEFAULT permit 10
R1(config)# route-map COND-DEFAULT permit 10
R1(config-route-map)# match ip address prefix-list COND-DEFAULT-CHECK
```

After fixing, verify:
```
R1# show ip bgp neighbors 172.16.4.4 advertised-routes | include 0.0.0.0
R4# show ip bgp
```

</details>

---

### Ticket 2

**Symptom:** R2 and R3 are both advertising the same MED values for 192.168.1.0/24 and 192.168.2.0/24, causing unpredictable inbound path selection. Or: MED values appear correct on R2/R3, but the ISP is not preferring the expected ingress point.

**Verification commands:**

```
R2# show ip bgp 192.168.1.0
R2# show ip bgp 192.168.2.0
R3# show ip bgp 192.168.1.0
R3# show ip bgp 192.168.2.0
R1# show route-map TE-TO-ISP-A
R1# show route-map TE-TO-ISP-B
```

**What to look for:**
- 192.168.1.0 showing Metric=100 on R2 (wrong — should be 10 on R2/ISP-A side)
- 192.168.2.0 showing Metric=10 on R2 (wrong — should be 100 on R2/ISP-A side)
- MEDs are swapped: R1 is steering inbound traffic the wrong way

**Root Cause and Fix:**

<details>
<summary>Ticket 2 Solution</summary>

The MED values are inverted in the route-maps. TE-TO-ISP-A has MED=10 on PREFIX-192-168-2 (which should have MED=100+prepend) and MED=100 on PREFIX-192-168-1 (which should have MED=10).

The correct TE-TO-ISP-A logic is:
- seq 10: PREFIX-192-168-2 → MED=100 + prepend (this is the deprioritized prefix via ISP-A)
- seq 20: PREFIX-192-168-1 → MED=10 (this is the preferred ingress via ISP-A)

Fix on R1:
```
no route-map TE-TO-ISP-A
route-map TE-TO-ISP-A permit 10
 match ip address prefix-list PREFIX-192-168-2
 set as-path prepend 65001 65001 65001
 set metric 100
route-map TE-TO-ISP-A permit 20
 match ip address prefix-list PREFIX-192-168-1
 set metric 10
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 40
 set community 65001:100 additive
```

Similarly verify and fix TE-TO-ISP-B if swapped.

After fix:
```
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out
R2# show ip bgp 192.168.1.0
! Expect: Metric 10
R2# show ip bgp 192.168.2.0
! Expect: Metric 100
```

Note: Even with correct MEDs, ISPs only compare MED between routes from the same neighboring AS. If ISP-A also receives the prefix from ISP-B (via R2-R3 peering), it uses AS-path length as a tiebreaker. The prepend ensures ISP-A prefers its own direct path to 192.168.1.0/24.

</details>

---

### Ticket 3

**Symptom:** R2 is receiving 192.168.2.0/24 from R1 with a normal 1-hop AS-path (just 65001) instead of the expected 4-hop prepended path. Inbound traffic for 192.168.2.0/24 is not being steered away from ISP-A as intended.

**Verification commands:**

```
R2# show ip bgp 192.168.2.0
R1# show route-map TE-TO-ISP-A
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
```

**What to look for:**
- R2 shows 192.168.2.0/24 with AS-path: 65001 (no prepend)
- R1's TE-TO-ISP-A route-map shows seq 10 does NOT match PREFIX-192-168-2
- Either the prepend entry is placed after the catch-all (seq 40), or the prefix-list name is wrong

**Root Cause and Fix:**

<details>
<summary>Ticket 3 Solution</summary>

The root cause is a route-map sequencing error. The AS-path prepend for PREFIX-192-168-2 has been placed at seq 50 (or any sequence after the seq 40 permit-all catch-all). When IOS evaluates the route-map, seq 40 matches first (permit everything), so seq 50 never fires.

Fix — rebuild TE-TO-ISP-A with correct sequence ordering:
```
no route-map TE-TO-ISP-A
route-map TE-TO-ISP-A permit 10
 match ip address prefix-list PREFIX-192-168-2
 set as-path prepend 65001 65001 65001
 set metric 100
route-map TE-TO-ISP-A permit 20
 match ip address prefix-list PREFIX-192-168-1
 set metric 10
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
route-map TE-TO-ISP-A permit 40
 set community 65001:100 additive
```

The `no route-map TE-TO-ISP-A` removes all sequences at once. Then rebuild from scratch to guarantee correct ordering.

After fix:
```
clear ip bgp 10.1.12.2 soft out
R2# show ip bgp 192.168.2.0
! Expect: AS-path 65001 65001 65001 65001
```

Also check whether the prefix-list name in seq 10 is correct:
```
R1# show route-map TE-TO-ISP-A
! Look for: Match clauses: ip address prefix-lists: PREFIX-192-168-2
```

If it shows a wrong prefix-list name (e.g., PREFIX-192-168-TWO):
```
route-map TE-TO-ISP-A permit 10
 no match ip address prefix-list PREFIX-192-168-TWO
 match ip address prefix-list PREFIX-192-168-2
```

</details>

---

## 10. Lab Completion Checklist

### Task Completion

- [ ] **Task 1:** Prefix-lists ISP-A-PREFIXES and ISP-B-PREFIXES created on R1
- [ ] **Task 1:** Route-map LP-FROM-ISP-A applied inbound on neighbor 10.1.12.2
- [ ] **Task 1:** Route-map LP-FROM-ISP-B applied inbound on neighbor 10.1.13.2
- [ ] **Task 1:** R1 BGP table shows LP=200 for 198.51.100.0/24 (via ISP-A)
- [ ] **Task 1:** R1 BGP table shows LP=200 for 203.0.113.0/24 (via ISP-B)
- [ ] **Task 2:** Prefix-lists PREFIX-192-168-1, PREFIX-192-168-2, PREFIX-192-168-3 created
- [ ] **Task 2:** Route-map TE-TO-ISP-A applied outbound on neighbor 10.1.12.2
- [ ] **Task 2:** Route-map TE-TO-ISP-B applied outbound on neighbor 10.1.13.2
- [ ] **Task 2:** R2 sees 192.168.2.0/24 with 4-hop AS-path (3 prepends)
- [ ] **Task 2:** R3 sees 192.168.1.0/24 with 4-hop AS-path (3 prepends)
- [ ] **Task 3:** R2 sees 192.168.1.0/24 with MED=10
- [ ] **Task 3:** R2 sees 192.168.2.0/24 with MED=100
- [ ] **Task 3:** R3 sees 192.168.2.0/24 with MED=10
- [ ] **Task 3:** R3 sees 192.168.1.0/24 with MED=100
- [ ] **Task 4:** ip route 0.0.0.0 0.0.0.0 Null0 present on R1
- [ ] **Task 4:** COND-DEFAULT route-map referencing COND-DEFAULT-CHECK prefix-list
- [ ] **Task 4:** R4 receives BGP default route 0.0.0.0/0 from R1
- [ ] **Task 4:** When 198.51.100.0/24 removed from R2, R4 loses default route

### Verification Commands Quick Run

```bash
# On R1
show ip bgp summary
show ip bgp 198.51.100.0
show ip bgp 203.0.113.0
show ip route static
show route-map LP-FROM-ISP-A
show route-map TE-TO-ISP-A
show ip bgp neighbors 10.1.12.2 advertised-routes
show ip bgp neighbors 172.16.4.4 advertised-routes | include 0.0.0.0

# On R2
show ip bgp 192.168.1.0
show ip bgp 192.168.2.0

# On R3
show ip bgp 192.168.1.0
show ip bgp 192.168.2.0

# On R4
show ip bgp
show ip route 0.0.0.0
```
