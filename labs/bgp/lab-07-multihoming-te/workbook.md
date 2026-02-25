# BGP Lab 07 — Multihoming & Traffic Engineering

**Chapter:** BGP | **Lab Number:** 07 | **Difficulty:** Advanced | **Estimated Time:** 90 minutes

---

## 1. Concepts & Skills Covered

This lab builds on the community and policy infrastructure established in Lab 06 and focuses on practical dual-ISP traffic engineering. You will implement outbound and inbound traffic control using the full set of BGP policy tools available in IOS, and learn how the tools interact and complement one another.

### Core Topics

| Topic | Description |
|---|---|
| BGP Multihoming | Connecting a single AS to two or more upstream ISPs for redundancy and load distribution |
| Outbound Traffic Engineering | Using Local Preference to control which ISP the enterprise uses for each traffic class |
| Inbound Traffic Engineering | Using AS-path prepending and MED to influence how the internet reaches the enterprise |
| Local Preference (LP) | An iBGP attribute (not sent to eBGP peers) that sets preference for outbound exit paths |
| Per-destination LP policy | Applying different LP values based on prefix-list matching rather than a single flat policy |
| AS-Path Prepending | Artificially lengthening the AS-path to make a path less attractive to remote ASes |
| MED (Multi-Exit Discriminator) | A soft metric sent to directly connected eBGP peers as a hint for inbound path preference |
| MED vs. Prepending | Understanding when MED works and when prepending is required for multi-hop influence |
| Conditional Default Origination | Advertising a default route to internal peers only when an upstream prefix is reachable |
| `default-originate route-map` | IOS mechanism for conditional default route advertisement based on BGP table state |
| Dual-homed design principles | Designing policy so each prefix has a primary and a backup ISP path |

### CCNP ENCOR Exam Relevance

Traffic engineering in a dual-homed design is a core 350-401 topic. Expect exam questions on:
- Which BGP attributes control outbound vs inbound traffic
- Why Local Preference does not propagate to eBGP peers
- Why MED is only compared between routes from the same AS by default
- How AS-path prepending is the only portable inbound TE tool that works across multiple hops
- The exact syntax and behavior of `default-originate route-map`

---

## 2. Topology & Scenario

### Scenario

You are the network engineer for an enterprise (AS 65001). Your edge router R1 has dual connections — one to ISP-A (R2, AS 65002) and one to ISP-B (R3, AS 65003). The enterprise advertises three /24 prefixes to both ISPs. R4 is an internal router that depends on R1 for internet access via a default route. R5 (AS 65004) is a downstream customer connected to ISP-B.

Management requires a traffic engineering policy that steers specific destination groups toward the preferred ISP for outbound traffic, and steers specific source prefixes through the preferred ISP for inbound traffic. The default route to R4 must only be advertised when ISP-A is confirmed reachable — protecting R4 from a black-hole condition during an ISP-A outage.

The starting configuration is the Lab 06 solution. Community infrastructure, eBGP and iBGP sessions, and a basic LP policy are already in place. This lab replaces the flat LP policy with a per-destination policy and adds per-prefix outbound prepending.

### Topology Diagram

```
                  AS 65002 (ISP-A)
                      R2
                 172.16.2.2
              Fa0/0        Fa1/0
              .2                .1
    10.1.12.0/30          10.1.23.0/30
              .1                .2
           Fa1/0            Fa0/0
  AS 65001      R1        R3          AS 65003 (ISP-B)
  Enterprise  172.16.1.1  172.16.3.3
  Edge        Fa1/1    Fa1/0          Fa1/1
               .1        .2             .1
         10.1.13.0/30              10.1.35.0/30
                                         .2
               Fa0/0                  Fa0/0
                 .1                    R5
            10.1.14.0/30         172.16.5.5
                 .2             AS 65004
               Fa0/0       (Downstream Customer)
                 R4
            172.16.4.4
         AS 65001 (Internal)
```

### Addressing Summary

| Device | Interface | IP Address | Description |
|---|---|---|---|
| R1 | Loopback0 | 172.16.1.1/32 | Router-ID |
| R1 | Loopback1 | 192.168.1.1/24 | Enterprise subnet 1 |
| R1 | Loopback2 | 192.168.2.1/24 | Enterprise subnet 2 |
| R1 | Loopback3 | 192.168.3.1/24 | Enterprise subnet 3 |
| R1 | Fa0/0 | 10.1.14.1/30 | Link to R4 |
| R1 | Fa1/0 | 10.1.12.1/30 | Link to R2 (ISP-A) |
| R1 | Fa1/1 | 10.1.13.1/30 | Link to R3 (ISP-B) |
| R2 | Loopback0 | 172.16.2.2/32 | Router-ID |
| R2 | Loopback1 | 198.51.100.1/24 | ISP-A prefix |
| R2 | Loopback2 | 198.51.101.1/24 | ISP-A prefix |
| R2 | Loopback3 | 198.51.102.1/24 | ISP-A prefix |
| R2 | Fa0/0 | 10.1.12.2/30 | Link to R1 |
| R2 | Fa1/0 | 10.1.23.1/30 | Link to R3 |
| R3 | Loopback0 | 172.16.3.3/32 | Router-ID |
| R3 | Loopback1 | 203.0.113.1/24 | ISP-B prefix |
| R3 | Loopback2 | 203.0.114.1/24 | ISP-B prefix |
| R3 | Loopback3 | 203.0.115.1/24 | ISP-B prefix |
| R3 | Fa0/0 | 10.1.23.2/30 | Link to R2 |
| R3 | Fa1/0 | 10.1.13.2/30 | Link to R1 |
| R3 | Fa1/1 | 10.1.35.1/30 | Link to R5 |
| R4 | Loopback0 | 172.16.4.4/32 | Router-ID |
| R4 | Loopback1 | 10.4.1.1/24 | Enterprise internal subnet |
| R4 | Loopback2 | 10.4.2.1/24 | Enterprise internal subnet |
| R4 | Fa0/0 | 10.1.14.2/30 | Link to R1 |
| R5 | Loopback0 | 172.16.5.5/32 | Router-ID |
| R5 | Loopback1 | 10.5.1.1/24 | Customer subnet |
| R5 | Loopback2 | 10.5.2.1/24 | Customer subnet |
| R5 | Fa0/0 | 10.1.35.2/30 | Link to R3 |

### BGP Session Summary

| Session | Type | AS Pair | Interface |
|---|---|---|---|
| R1 — R2 | eBGP | 65001 — 65002 | 10.1.12.0/30 |
| R1 — R3 | eBGP | 65001 — 65003 | 10.1.13.0/30 |
| R1 — R4 | iBGP | 65001 (loopback) | via OSPF |
| R2 — R3 | eBGP | 65002 — 65003 | 10.1.23.0/30 |
| R3 — R5 | eBGP | 65003 — 65004 | 10.1.35.0/30 |

---

## 3. Hardware & Environment Specifications

### GNS3 Device Table

| Device | Role | Platform | AS | Loopback | Console Port |
|---|---|---|---|---|---|
| R1 | Enterprise Edge | c7200 | 65001 | 172.16.1.1/32 | 5001 |
| R2 | ISP-A | c7200 | 65002 | 172.16.2.2/32 | 5002 |
| R3 | ISP-B | c7200 | 65003 | 172.16.3.3/32 | 5003 |
| R4 | Enterprise Internal | c3725 | 65001 | 172.16.4.4/32 | 5004 |
| R5 | Downstream Customer | c3725 | 65004 | 172.16.5.5/32 | 5005 |

### Console Access Table

| Device | Console Port | Telnet Command |
|---|---|---|
| R1 | 5001 | telnet 127.0.0.1 5001 |
| R2 | 5002 | telnet 127.0.0.1 5002 |
| R3 | 5003 | telnet 127.0.0.1 5003 |
| R4 | 5004 | telnet 127.0.0.1 5004 |
| R5 | 5005 | telnet 127.0.0.1 5005 |

### Platform Notes

- **c7200**: Used for R1, R2, R3. Supports Fa0/0, Fa1/0, Fa1/1, Gi3/0, s2/0-s2/3.
- **c3725**: Used for R4, R5. Supports Fa0/0, Fa0/1, Fa1/0-Fa1/15 (switch), s2/0-s2/3.
- All routers run Cisco IOS 12.4 or 12.4T.
- Local Preference is an iBGP-only attribute — it is never advertised to eBGP peers.
- MED is only compared between routes from the same neighboring AS unless `bgp always-compare-med` is configured.

---

## 4. Base Configuration

The initial configuration for this lab is the complete solution from Lab 06 (Communities & Policy Control). All BGP infrastructure — sessions, community tagging, and the initial LP policy — is already in place.

### What is already configured

**R1 (inherited from Lab 06):**
- Interface IP addressing on all interfaces
- OSPF area 0 with R4 (for iBGP loopback reachability)
- eBGP sessions: R1-R2 (10.1.12.2), R1-R3 (10.1.13.2)
- iBGP session: R1-R4 (172.16.4.4, loopback-sourced, next-hop-self)
- Route-maps: `SET-LP-200-ISP-A`, `POLICY-ISP-B-IN`, `PREPEND-TO-ISP-B`, `SET-COMMUNITY-OUT`
- Prefix-lists: `ENTERPRISE-PREFIXES`, `DENY-203-115`
- Community-list: `CUSTOMER-ROUTES` (permits 65003:500)
- `send-community` enabled on all neighbors
- `soft-reconfiguration inbound` enabled on eBGP neighbors
- Networks advertised: 172.16.1.1/32, 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24

**R2 (ISP-A):**
- eBGP to R1 and R3
- Loopback prefixes 198.51.100-102.0/24 advertised into BGP
- `send-community` enabled

**R3 (ISP-B):**
- eBGP to R1, R2, and R5
- Loopback prefixes 203.0.113-115.0/24 advertised into BGP
- Route-map `TAG-CUSTOMER-IN` tagging R5 routes with community 65003:500
- `send-community` enabled

**R4 (Enterprise Internal):**
- iBGP to R1 via loopback
- Internal prefixes 10.4.1.0/24 and 10.4.2.0/24 with `no-export` community

**R5 (Downstream Customer):**
- eBGP to R3
- Customer prefixes 10.5.1.0/24 and 10.5.2.0/24 advertised

### Load Initial Configs

```bash
# Option 1: Automated setup (recommended)
python3 labs/bgp/lab-07-multihoming-te/setup_lab.py

# Option 2: Manual — paste each router's initial-configs/*.cfg via console
```

### Verify Base State

After loading, confirm the Lab 06 BGP state is intact on R1:

```
R1# show ip bgp summary
R1# show ip bgp
R1# show ip ospf neighbor
```

Confirm the existing LP policy is in place:

```
R1# show route-map SET-LP-200-ISP-A
R1# show route-map POLICY-ISP-B-IN
```

Expected: R1 BGP table shows ISP-A routes with LP=200, ISP-B routes with LP=150 or LP=120.

---

## 5. Lab Challenge

Complete all four tasks in order. Each task builds on the previous one.

---

### Task 1 — Outbound Traffic Engineering via Local Preference

**Objective:** Replace the existing flat LP route-maps with per-destination-group LP policies so that each ISP is preferred for the destinations it originates.

**Background:** The current policy applies LP=200 to all ISP-A routes. This is a blunt instrument — ISP-B is always secondary regardless of where the destination lives. The improved design assigns LP=200 to the ISP that originates the destination, making ISP-A preferred for ISP-A prefixes (198.51.x.x) and ISP-B preferred for ISP-B prefixes (203.0.x.x). Customer routes (tagged 65003:500) are deprioritized at LP=120 on both ISPs.

**Step 1: Create prefix-lists for per-destination matching**

```
ip prefix-list ISP-A-PREFIXES seq 10 permit 198.51.100.0/24
ip prefix-list ISP-A-PREFIXES seq 20 permit 198.51.101.0/24
ip prefix-list ISP-A-PREFIXES seq 30 permit 198.51.102.0/24

ip prefix-list ISP-B-PREFIXES seq 10 permit 203.0.113.0/24
ip prefix-list ISP-B-PREFIXES seq 20 permit 203.0.114.0/24
ip prefix-list ISP-B-PREFIXES seq 30 permit 203.0.115.0/24
```

**Step 2: Build the LP-FROM-ISP-A route-map (applied inbound from R2)**

```
route-map LP-FROM-ISP-A permit 10
 match ip address prefix-list ISP-A-PREFIXES
 set local-preference 200
!
route-map LP-FROM-ISP-A permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
!
route-map LP-FROM-ISP-A permit 30
 set local-preference 150
```

Sequence 10 catches ISP-A's own prefixes and marks them highest priority.
Sequence 20 catches customer routes (65003:500) that arrived via ISP-A and deprioritizes them.
Sequence 30 is the catch-all — all other ISP-A routes receive LP=150.

**Step 3: Build the LP-FROM-ISP-B route-map (applied inbound from R3)**

```
route-map LP-FROM-ISP-B permit 10
 match ip address prefix-list ISP-B-PREFIXES
 set local-preference 200
!
route-map LP-FROM-ISP-B permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
!
route-map LP-FROM-ISP-B permit 30
 set local-preference 150
```

Sequence 10 catches ISP-B's own prefixes and marks them highest priority.
Sequence 20 catches customer routes and deprioritizes them.
Sequence 30 is the catch-all at LP=150.

**Step 4: Apply the new route-maps, replacing the old ones**

```
router bgp 65001
 no neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in
 no neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in
 neighbor 10.1.12.2 route-map LP-FROM-ISP-A in
 neighbor 10.1.13.2 route-map LP-FROM-ISP-B in
```

**Step 5: Soft-reset inbound sessions to apply the new policy**

```
R1# clear ip bgp 10.1.12.2 soft in
R1# clear ip bgp 10.1.13.2 soft in
```

**Expected outcome:** ISP-A prefixes (198.51.x.x) show LP=200 via R2. ISP-B prefixes (203.0.x.x) show LP=200 via R3. Customer routes (10.5.x.x) show LP=120 on both paths.

---

### Task 2 — Inbound Traffic Engineering via AS-Path Prepending

**Objective:** Engineer which ISP the internet uses to reach each enterprise prefix by applying per-prefix AS-path prepending and MED values to outbound advertisements.

**Background:** The three enterprise prefixes serve different traffic profiles. Prefix 192.168.1.0/24 should be reached primarily via ISP-A. Prefix 192.168.2.0/24 should be reached primarily via ISP-B. Prefix 192.168.3.0/24 is load-balanced across both ISPs (equal MED). By prepending the AS-path on the non-preferred ISP and setting a lower MED on the preferred ISP, the internet is steered toward the desired ingress.

**Step 1: Create per-prefix prefix-lists**

```
ip prefix-list PREFIX-192-168-1 seq 10 permit 192.168.1.0/24
ip prefix-list PREFIX-192-168-2 seq 10 permit 192.168.2.0/24
ip prefix-list PREFIX-192-168-3 seq 10 permit 192.168.3.0/24
```

**Step 2: Build the TE-TO-ISP-A route-map (applied outbound to R2)**

```
route-map TE-TO-ISP-A permit 10
 match ip address prefix-list PREFIX-192-168-2
 set as-path prepend 65001 65001 65001
 set metric 100
!
route-map TE-TO-ISP-A permit 20
 match ip address prefix-list PREFIX-192-168-1
 set metric 10
 set community 65001:100 additive
!
route-map TE-TO-ISP-A permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
!
route-map TE-TO-ISP-A permit 40
 set community 65001:100 additive
```

Sequence 10: 192.168.2.0/24 is prepended three times and given MED=100 — the internet should reach this prefix via ISP-B, not ISP-A. The long AS-path discourages any path via ISP-A.
Sequence 20: 192.168.1.0/24 gets MED=10 (low MED = preferred) — ISP-A is the preferred ingress for this prefix.
Sequence 30: 192.168.3.0/24 gets MED=50 — balanced between the two ISPs.
Sequence 40: Pass-through for all other prefixes, applying enterprise community tag.

**Step 3: Build the TE-TO-ISP-B route-map (applied outbound to R3)**

```
route-map TE-TO-ISP-B permit 10
 match ip address prefix-list PREFIX-192-168-1
 set as-path prepend 65001 65001 65001
 set metric 100
!
route-map TE-TO-ISP-B permit 20
 match ip address prefix-list PREFIX-192-168-2
 set metric 10
 set community 65001:100 additive
!
route-map TE-TO-ISP-B permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
!
route-map TE-TO-ISP-B permit 40
 set community 65001:100 additive
```

Sequence 10: 192.168.1.0/24 is prepended three times — the internet should not use ISP-B to reach this prefix.
Sequence 20: 192.168.2.0/24 gets MED=10 — ISP-B is the preferred ingress for this prefix.
Sequence 30: 192.168.3.0/24 gets MED=50 — balanced.
Sequence 40: Pass-through for all other prefixes.

**Step 4: Apply the new outbound TE route-maps, replacing the old PREPEND-TO-ISP-B**

```
router bgp 65001
 no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out
 no neighbor 10.1.12.2 route-map SET-COMMUNITY-OUT out
 neighbor 10.1.12.2 route-map TE-TO-ISP-A out
 neighbor 10.1.13.2 route-map TE-TO-ISP-B out
```

**Step 5: Soft-reset outbound sessions**

```
R1# clear ip bgp 10.1.12.2 soft out
R1# clear ip bgp 10.1.13.2 soft out
```

**Expected outcome:** R2's BGP table shows 192.168.2.0/24 with a 3-hop prepended AS-path and MED=100. R3's BGP table shows 192.168.1.0/24 with a 3-hop prepended AS-path and MED=100.

---

### Task 3 — MED for Inbound Traffic Hints

**Objective:** Understand the relationship between MED and AS-path prepending and verify that MED values appear in the BGP tables of the directly connected ISPs.

**Background:** MED (Multi-Exit Discriminator) is a soft inbound traffic hint. When an enterprise is connected to a single ISP at two physical locations, MED tells that ISP which entrance the enterprise prefers. However, MED has a critical limitation: by default, IOS only compares MED values between routes received from the **same neighboring AS**. If ISP-A learns of 192.168.1.0/24 from both R1 directly (low MED) and via ISP-B (different AS), IOS does not compare those MED values unless `bgp always-compare-med` is configured on ISP-A.

AS-path prepending, by contrast, is visible to all ASes along the path — it changes the fundamental path length attribute, which all BGP speakers compare regardless of origin AS. For true multi-hop inbound traffic engineering, prepending is the reliable tool. MED is a supplementary hint for the directly connected ISP only.

**Verify MED values appear in R2's table for advertised routes:**

```
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
```

Expected output (relevant lines):

```
Network          Next Hop         Metric  LocPrf  Weight  Path
*> 192.168.1.0   0.0.0.0              10                  32768 i
*> 192.168.2.0   0.0.0.0             100                  32768 65001 65001 65001 i
*> 192.168.3.0   0.0.0.0              50                  32768 i
```

The Metric column shows the MED value. Confirm that R2 sees the MED values and the prepended AS-path for 192.168.2.0/24.

**Verify on R2:**

```
R2# show ip bgp 192.168.2.0
```

Expected: AS-path shows `65001 65001 65001 65001` (four instances — original plus three prepended) and MED=100.

```
R2# show ip bgp 192.168.1.0
```

Expected: AS-path shows `65001` (no prepend), MED=10.

No additional configuration is required for this task. It is a verification and conceptual task that confirms the work from Task 2.

---

### Task 4 — Conditional Default Route Origination

**Objective:** Configure R1 to advertise a default route 0.0.0.0/0 to R4 only when ISP-A is confirmed reachable (198.51.100.0/24 is present in R1's BGP table).

**Background:** Without a conditional check, R1 would always advertise a default route to R4 — even during an ISP-A failure. If ISP-B is also down, R4 would forward all traffic toward R1 and into a black hole. The `default-originate route-map` feature makes the default advertisement conditional: R1 checks its local BGP table for a specific prefix (the condition), and only originates the default if that prefix is present.

**Step 1: Create the null static route (required for origination)**

```
ip route 0.0.0.0 0.0.0.0 Null0
```

This static route does not affect forwarding — it provides the BGP process with a route to originate. The conditional route-map controls whether it is actually sent to R4.

**Step 2: Create the condition prefix-list**

```
ip prefix-list COND-DEFAULT-CHECK seq 10 permit 198.51.100.0/24
```

This prefix-list matches the ISP-A reachability indicator. If 198.51.100.0/24 is in R1's BGP table, the condition is satisfied.

**Step 3: Create the conditional route-map**

```
route-map COND-DEFAULT permit 10
 match ip address prefix-list COND-DEFAULT-CHECK
```

The route-map matches only when the condition prefix is present. The BGP process evaluates this route-map against the local BGP table — if any prefix in the table matches, the default is advertised to R4.

**Step 4: Apply conditional default-originate to the iBGP neighbor**

```
router bgp 65001
 neighbor 172.16.4.4 default-originate route-map COND-DEFAULT
```

**Step 5: Soft-reset the iBGP session**

```
R1# clear ip bgp 172.16.4.4 soft out
```

**Expected outcome:** R4 receives a default route from R1 when ISP-A is up. If 198.51.100.0/24 is removed from R1's BGP table (simulating ISP-A failure), the default route is withdrawn from R4 within the BGP hold-down timer.

---

## 6. Verification & Analysis

### Task 1 Verification — Local Preference Policy

**Step 1: Verify LP hierarchy on R1**

```
R1# show ip bgp
```

Expected output (key columns):

```
   Network          Next Hop     Metric  LocPrf  Weight  Path
*> 198.51.100.0/24  10.1.12.2       0      200      0   65002 i
*> 198.51.101.0/24  10.1.12.2       0      200      0   65002 i
*> 198.51.102.0/24  10.1.12.2       0      200      0   65002 i
*> 203.0.113.0/24   10.1.13.2       0      200      0   65003 i
*> 203.0.114.0/24   10.1.13.2       0      200      0   65003 i
*> 203.0.115.0/24   10.1.13.2       0      200      0   65003 i
*  198.51.100.0/24  10.1.13.2       0      150      0   65003 65002 i
*  203.0.113.0/24   10.1.12.2       0      150      0   65002 65003 i
*> 10.5.1.0/24      10.1.13.2       0      120      0   65003 65004 i
*> 10.5.2.0/24      10.1.13.2       0      120      0   65003 65004 i
```

The `>` marker indicates best path. ISP-A prefixes should be best via 10.1.12.2. ISP-B prefixes should be best via 10.1.13.2. Customer routes should show LP=120 via 10.1.13.2.

**Step 2: Verify route-map is applied**

```
R1# show route-map LP-FROM-ISP-A
R1# show route-map LP-FROM-ISP-B
```

Expected: Both route-maps exist with three sequences. Match counts increment after the soft-reset.

**Step 3: Verify a specific prefix**

```
R1# show ip bgp 198.51.100.0
```

Expected: Best path via 10.1.12.2 with local preference 200. Alternate path via 10.1.13.2 with local preference 150.

```
R1# show ip bgp 203.0.113.0
```

Expected: Best path via 10.1.13.2 with local preference 200. Alternate path via 10.1.12.2 with local preference 150.

```
R1# show ip bgp 10.5.1.0
```

Expected: Local preference 120 on the path via 10.1.13.2.

---

### Task 2 Verification — Inbound Traffic Engineering

**Step 1: Verify advertised routes to ISP-A (R2)**

```
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
```

Expected output (relevant lines):

```
Network          Next Hop         Metric  LocPrf  Weight  Path
*> 192.168.1.0   0.0.0.0              10                  32768 i
*> 192.168.2.0   0.0.0.0             100                  32768 65001 65001 65001 i
*> 192.168.3.0   0.0.0.0              50                  32768 i
```

192.168.2.0/24 must show the 3x prepend (AS-path length 4) and MED=100.
192.168.1.0/24 must show no prepend and MED=10.

**Step 2: Verify advertised routes to ISP-B (R3)**

```
R1# show ip bgp neighbors 10.1.13.2 advertised-routes
```

Expected output:

```
Network          Next Hop         Metric  LocPrf  Weight  Path
*> 192.168.1.0   0.0.0.0             100                  32768 65001 65001 65001 i
*> 192.168.2.0   0.0.0.0              10                  32768 i
*> 192.168.3.0   0.0.0.0              50                  32768 i
```

192.168.1.0/24 must show the 3x prepend and MED=100 to ISP-B.
192.168.2.0/24 must show no prepend and MED=10 to ISP-B.

**Step 3: Verify on R2 that the AS-path prepend is visible**

```
R2# show ip bgp 192.168.2.0
```

Expected: AS-path `65001 65001 65001 65001` (four hops — the remote AS sees your full prepended path).

```
R2# show ip bgp 192.168.1.0
```

Expected: AS-path `65001` (single hop, no prepend, preferred ingress via ISP-A).

**Step 4: Verify on R3 that the AS-path prepend is visible**

```
R3# show ip bgp 192.168.1.0
```

Expected: AS-path `65001 65001 65001 65001` (prepended — ISP-B is steered away from this prefix).

---

### Task 3 Verification — MED Values

**Step 1: Confirm MED values in advertised routes**

```
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
R1# show ip bgp neighbors 10.1.13.2 advertised-routes
```

The Metric column in the output corresponds to the MED sent to that peer. Both commands should show the MED values assigned in the TE-TO-ISP-A and TE-TO-ISP-B route-maps.

**Step 2: Understand MED comparison scope on R2**

```
R2# show ip bgp 192.168.3.0
```

R2 receives 192.168.3.0/24 from both R1 (MED=50, AS-path 65001) and from R3 (MED=50 but arriving via 65003 65001). By default, IOS will not compare MEDs between routes from different neighboring ASes. R2 selects best path based on AS-path length or router-id, not MED, for this cross-AS comparison.

To force MED comparison across different neighboring ASes (for testing purposes only):

```
R2(config)# router bgp 65002
R2(config-router)# bgp always-compare-med
```

Note: `bgp always-compare-med` must be consistent across all routers in an AS. Inconsistent configuration causes routing loops.

---

### Task 4 Verification — Conditional Default Route

**Step 1: Verify R4 receives the default route**

```
R4# show ip route 0.0.0.0
```

Expected:

```
B*   0.0.0.0/0 [20/0] via 172.16.1.1, 00:XX:XX
```

The `B*` indicates a BGP-learned default route.

**Step 2: Verify the default is in R1's BGP table**

```
R1# show ip bgp 0.0.0.0
```

Expected:

```
BGP routing table entry for 0.0.0.0/0
  Paths: (1 available, best #1)
    Local
      0.0.0.0 from 0.0.0.0 (172.16.1.1)
        Origin IGP, metric 0, localpref 100, weight 32768, valid, sourced, local, best
```

The `weight 32768` confirms this is a locally originated route.

**Step 3: Verify the condition prefix-list**

```
R1# show ip prefix-list COND-DEFAULT-CHECK
```

Expected:

```
ip prefix-list COND-DEFAULT-CHECK: 1 entries
   seq 10 permit 198.51.100.0/24
```

**Step 4: Simulate an ISP-A failure and verify default withdrawal**

On R2, temporarily shut the interface toward R1:

```
R2(config)# interface Fa0/0
R2(config-if)# shutdown
```

Wait for the BGP session to drop (hold timer: up to 90 seconds by default), then verify on R1:

```
R1# show ip bgp 198.51.100.0
```

Expected: Route is no longer present. Then verify on R4:

```
R4# show ip route 0.0.0.0
```

Expected: No default route. R4 correctly has no internet path.

Restore R2 afterward:

```
R2(config)# interface Fa0/0
R2(config-if)# no shutdown
```

---

## 7. Verification Cheatsheet

### Quick Reference Commands

| Goal | Command | Where to Run |
|---|---|---|
| BGP table with LP values | `show ip bgp` | R1 |
| Best path details for a prefix | `show ip bgp <prefix>` | R1, R2, R3 |
| Routes advertised to a peer | `show ip bgp neighbors <IP> advertised-routes` | R1 |
| Routes received from a peer | `show ip bgp neighbors <IP> received-routes` | R1 |
| Route-map match/set details | `show route-map <name>` | R1 |
| Prefix-list contents | `show ip prefix-list <name>` | R1 |
| BGP session status | `show ip bgp summary` | All routers |
| Default route on R4 | `show ip route 0.0.0.0` | R4 |
| Default route in BGP table | `show ip bgp 0.0.0.0` | R1 |
| Verify conditional default config | `show ip bgp neighbors 172.16.4.4 \| include default` | R1 |
| Soft-reset inbound policy | `clear ip bgp <IP> soft in` | R1 |
| Soft-reset outbound policy | `clear ip bgp <IP> soft out` | R1 |
| AS-path prepend verification | `show ip bgp <prefix>` | R2, R3 |
| MED value verification | `show ip bgp neighbors <IP> advertised-routes` | R1 |
| Community-list contents | `show ip community-list` | R1 |

### Expected LP Values on R1

| Prefix Range | Via | Local Preference | Reason |
|---|---|---|---|
| 198.51.100-102.0/24 | ISP-A (R2) | 200 | ISP-A originates these — preferred via ISP-A |
| 203.0.113-115.0/24 | ISP-B (R3) | 200 | ISP-B originates these — preferred via ISP-B |
| 198.51.100-102.0/24 | ISP-B (R3) | 150 | ISP-A prefixes arriving via ISP-B — catch-all |
| 203.0.113-115.0/24 | ISP-A (R2) | 150 | ISP-B prefixes arriving via ISP-A — catch-all |
| 10.5.1-2.0/24 | Either ISP | 120 | Customer routes (tagged 65003:500) |

### Expected MED and AS-Path on R2 (Advertised by R1)

| Prefix | MED | AS-Path Prepend | Preferred Ingress |
|---|---|---|---|
| 192.168.1.0/24 | 10 | None | ISP-A (low MED, short path) |
| 192.168.2.0/24 | 100 | 65001 65001 65001 | ISP-B (high MED, long path) |
| 192.168.3.0/24 | 50 | None | Load balanced |

### Troubleshooting One-Liners

```
# LP not changing after route-map applied?
R1# clear ip bgp 10.1.12.2 soft in
R1# show ip bgp 198.51.100.0   (check LocPrf column)

# Prepend not visible on R2?
R1# clear ip bgp 10.1.12.2 soft out
R2# show ip bgp 192.168.2.0    (check AS-path field)

# MED not appearing in advertised routes?
R1# show route-map TE-TO-ISP-A (check that set metric sequences exist)

# Default route not on R4?
R1# show ip bgp 198.51.100.0   (condition must be present)
R1# show ip bgp neighbors 172.16.4.4 | include default
R4# show ip bgp summary        (iBGP session must be up)

# Default appearing even when ISP-A is down?
R1# show ip prefix-list COND-DEFAULT-CHECK  (verify correct prefix: 198.51.100.0/24)
R1# show ip bgp 198.51.100.0   (must be absent for default to be withdrawn)
```

---

## 8. Solutions

### Task 1 Solution — Outbound TE via Local Preference

<details>
<summary>Task 1 Solution — Outbound TE via Local Preference</summary>

```
ip prefix-list ISP-A-PREFIXES seq 10 permit 198.51.100.0/24
ip prefix-list ISP-A-PREFIXES seq 20 permit 198.51.101.0/24
ip prefix-list ISP-A-PREFIXES seq 30 permit 198.51.102.0/24
!
ip prefix-list ISP-B-PREFIXES seq 10 permit 203.0.113.0/24
ip prefix-list ISP-B-PREFIXES seq 20 permit 203.0.114.0/24
ip prefix-list ISP-B-PREFIXES seq 30 permit 203.0.115.0/24
!
route-map LP-FROM-ISP-A permit 10
 match ip address prefix-list ISP-A-PREFIXES
 set local-preference 200
!
route-map LP-FROM-ISP-A permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
!
route-map LP-FROM-ISP-A permit 30
 set local-preference 150
!
route-map LP-FROM-ISP-B permit 10
 match ip address prefix-list ISP-B-PREFIXES
 set local-preference 200
!
route-map LP-FROM-ISP-B permit 20
 match community CUSTOMER-ROUTES
 set local-preference 120
!
route-map LP-FROM-ISP-B permit 30
 set local-preference 150
!
router bgp 65001
 no neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in
 no neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in
 neighbor 10.1.12.2 route-map LP-FROM-ISP-A in
 neighbor 10.1.13.2 route-map LP-FROM-ISP-B in
```

After applying:

```
R1# clear ip bgp 10.1.12.2 soft in
R1# clear ip bgp 10.1.13.2 soft in
```

Verify:

```
R1# show ip bgp 198.51.100.0
  Local preference: 200 (via 10.1.12.2)

R1# show ip bgp 203.0.113.0
  Local preference: 200 (via 10.1.13.2)

R1# show ip bgp 10.5.1.0
  Local preference: 120
```

</details>

---

### Task 2 Solution — Inbound TE via AS-Path Prepending

<details>
<summary>Task 2 Solution — Inbound TE via AS-Path Prepending</summary>

```
ip prefix-list PREFIX-192-168-1 seq 10 permit 192.168.1.0/24
ip prefix-list PREFIX-192-168-2 seq 10 permit 192.168.2.0/24
ip prefix-list PREFIX-192-168-3 seq 10 permit 192.168.3.0/24
!
route-map TE-TO-ISP-A permit 10
 match ip address prefix-list PREFIX-192-168-2
 set as-path prepend 65001 65001 65001
 set metric 100
!
route-map TE-TO-ISP-A permit 20
 match ip address prefix-list PREFIX-192-168-1
 set metric 10
 set community 65001:100 additive
!
route-map TE-TO-ISP-A permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
!
route-map TE-TO-ISP-A permit 40
 set community 65001:100 additive
!
route-map TE-TO-ISP-B permit 10
 match ip address prefix-list PREFIX-192-168-1
 set as-path prepend 65001 65001 65001
 set metric 100
!
route-map TE-TO-ISP-B permit 20
 match ip address prefix-list PREFIX-192-168-2
 set metric 10
 set community 65001:100 additive
!
route-map TE-TO-ISP-B permit 30
 match ip address prefix-list PREFIX-192-168-3
 set metric 50
 set community 65001:100 additive
!
route-map TE-TO-ISP-B permit 40
 set community 65001:100 additive
!
router bgp 65001
 no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out
 no neighbor 10.1.12.2 route-map SET-COMMUNITY-OUT out
 neighbor 10.1.12.2 route-map TE-TO-ISP-A out
 neighbor 10.1.13.2 route-map TE-TO-ISP-B out
```

After applying:

```
R1# clear ip bgp 10.1.12.2 soft out
R1# clear ip bgp 10.1.13.2 soft out
```

Verify:

```
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
(192.168.2.0 shows metric 100 and path 65001 65001 65001)

R2# show ip bgp 192.168.2.0
(AS-path: 65001 65001 65001 65001)

R3# show ip bgp 192.168.1.0
(AS-path: 65001 65001 65001 65001)
```

</details>

---

### Task 3 Solution — MED for Inbound Traffic Hints

<details>
<summary>Task 3 Solution — MED for Inbound Traffic Hints</summary>

Task 3 requires no additional configuration beyond what was applied in Task 2. The `set metric` commands in TE-TO-ISP-A and TE-TO-ISP-B embed MED values into the advertised routes.

Verify:

```
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
```

Expected output (Metric column = MED value):

```
Network          Next Hop         Metric  LocPrf  Weight  Path
*> 192.168.1.0   0.0.0.0              10                  32768 i
*> 192.168.2.0   0.0.0.0             100                  32768 65001 65001 65001 i
*> 192.168.3.0   0.0.0.0              50                  32768 i
```

```
R1# show ip bgp neighbors 10.1.13.2 advertised-routes
```

Expected:

```
Network          Next Hop         Metric  LocPrf  Weight  Path
*> 192.168.1.0   0.0.0.0             100                  32768 65001 65001 65001 i
*> 192.168.2.0   0.0.0.0              10                  32768 i
*> 192.168.3.0   0.0.0.0              50                  32768 i
```

Key concepts to understand:
- MED is honored only by the directly connected ISP (the AS that receives the advertisement).
- MED is only compared between routes received from the same neighboring AS unless `bgp always-compare-med` is enabled.
- AS-path prepending propagates the length change to all ASes globally.
- For inbound TE that must work beyond the directly connected ISP, prepending is the correct and only portable mechanism.

</details>

---

### Task 4 Solution — Conditional Default Route Origination

<details>
<summary>Task 4 Solution — Conditional Default Route Origination</summary>

```
ip route 0.0.0.0 0.0.0.0 Null0
!
ip prefix-list COND-DEFAULT-CHECK seq 10 permit 198.51.100.0/24
!
route-map COND-DEFAULT permit 10
 match ip address prefix-list COND-DEFAULT-CHECK
!
router bgp 65001
 neighbor 172.16.4.4 default-originate route-map COND-DEFAULT
```

After applying:

```
R1# clear ip bgp 172.16.4.4 soft out
```

Verify default route advertised to R4:

```
R4# show ip route 0.0.0.0
B*   0.0.0.0/0 [20/0] via 172.16.1.1, 00:00:XX
```

Verify condition check on R1:

```
R1# show ip bgp neighbors 172.16.4.4 | include default
  Default information originate, default sent
```

Failure simulation (ISP-A down):

```
R2(config)# interface Fa0/0
R2(config-if)# shutdown
```

Wait for session to drop, then:

```
R1# show ip bgp 198.51.100.0
(route absent — condition fails)

R4# show ip route 0.0.0.0
(no output — default withdrawn)
```

Restore:

```
R2(config)# interface Fa0/0
R2(config-if)# no shutdown
```

</details>

---

## 9. Troubleshooting Scenarios

### Ticket 1

**Problem:** R4 is not receiving a default route from R1. The `show ip route 0.0.0.0` command on R4 returns no output. The iBGP session between R1 and R4 is confirmed Established. ISP-A (R2) is up and the BGP session R1-R2 is in the Established state.

**Your Mission:** Diagnose why the default route is not propagating to R4 and restore the expected behavior.

**Symptoms:**

```
R4# show ip route 0.0.0.0
(no output)

R4# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
172.16.1.1      4 65001      XX      XX        X    0    0  HH:MM:SS       8
(session is up, R4 is receiving 8 prefixes but no default)

R1# show ip bgp neighbors 172.16.4.4 | include default
  Default information originate, default not sent
```

**Diagnostic Hint:** Check three things in order:
1. Is the static null route present?
2. Is the condition prefix (198.51.100.0/24) actually in R1's BGP table?
3. Does the prefix-list COND-DEFAULT-CHECK reference the correct prefix?

<details>
<summary>Solution</summary>

**Root Cause:**

The `ip prefix-list COND-DEFAULT-CHECK` references `198.51.200.0/24` instead of `198.51.100.0/24`. The condition never evaluates to true because the wrong prefix is being checked, so the default route is never sent to R4.

**Diagnosis:**

```
R1# show ip prefix-list COND-DEFAULT-CHECK
ip prefix-list COND-DEFAULT-CHECK: 1 entries
   seq 10 permit 198.51.200.0/24

R1# show ip bgp 198.51.200.0
(no entry — this prefix does not exist in the BGP table)
```

The BGP process evaluates the route-map COND-DEFAULT against the BGP table. Because 198.51.200.0/24 is absent, the route-map returns no match, and `default-originate` does not generate an advertisement.

**Fix:**

```
R1(config)# no ip prefix-list COND-DEFAULT-CHECK seq 10
R1(config)# ip prefix-list COND-DEFAULT-CHECK seq 10 permit 198.51.100.0/24
R1(config)# end
R1# clear ip bgp 172.16.4.4 soft out
```

**Verify:**

```
R1# show ip prefix-list COND-DEFAULT-CHECK
   seq 10 permit 198.51.100.0/24

R1# show ip bgp neighbors 172.16.4.4 | include default
  Default information originate, default sent

R4# show ip route 0.0.0.0
B*   0.0.0.0/0 [20/0] via 172.16.1.1, 00:00:XX
```

**Key Lesson:** Always verify prefix-list contents character by character against the actual BGP table when conditional features (`default-originate route-map`, `advertise-map`) are not behaving as expected. A single wrong octet causes the condition to silently fail with no error message.

</details>

---

### Ticket 2

**Problem:** MED values appear correct in `show ip bgp neighbors <IP> advertised-routes` on R1, confirming that 192.168.3.0/24 is being advertised with MED=50 to both ISP-A and ISP-B. However, when looking at R2's BGP table, R2 consistently prefers the path it received via R3 (65002 65003 65001) over the direct path from R1 (65001) for 192.168.3.0/24 — even though the direct path from R1 has a shorter AS-path. The operations team suspects MED is the culprit but is not sure why.

**Your Mission:** Explain and fix the path selection issue so R2 prefers its direct eBGP path from R1 for 192.168.3.0/24.

**Symptoms:**

```
R2# show ip bgp 192.168.3.0
BGP routing table entry for 192.168.3.0/24
  Paths: (2 available, best #2)
    65003 65001
      10.1.23.2 from 10.1.23.2 (172.16.3.3)
        Origin IGP, metric 50, localpref 100, valid, external
        (this is the longer AS-path — via R3 — but R2 has selected it as best???)
  * 65001
      10.1.12.1 from 10.1.12.1 (172.16.1.1)
        Origin IGP, metric 50, localpref 100, valid, external, best
```

Wait — reread the symptom. R2 has the direct path as best. The issue is that R2 is not using the MED to discriminate and the operations team cannot explain why the MED=50 from R1 is not being respected over the MED=50 from R3 (same value, different AS).

Actually the real fault scenario: R1's TE-TO-ISP-A route-map sequences are inverted — the `set metric` for 192.168.3.0/24 is at sequence 50, but a catch-all `permit` without a set metric was added at sequence 40, causing 192.168.3.0/24 to match the catch-all first and be advertised with no MED (MED=0), making it look identical to R3's advertisement of the same prefix (also MED=0). R2 has no tiebreaker and uses router-id — which may or may not favor R1.

**Symptoms:**

```
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
Network          Next Hop         Metric  LocPrf  Weight  Path
*> 192.168.3.0   0.0.0.0               0                  32768 i
(MED is 0 — the set metric 50 did not fire)

R1# show route-map TE-TO-ISP-A
route-map TE-TO-ISP-A, permit, sequence 30
  Match clauses:
    ip address prefix-lists: PREFIX-192-168-2
  Set clauses:
    as-path prepend 65001 65001 65001
    metric 100
route-map TE-TO-ISP-A, permit, sequence 40
  Match clauses:
  Set clauses:
    community 65001:100 additive
route-map TE-TO-ISP-A, permit, sequence 50
  Match clauses:
    ip address prefix-lists: PREFIX-192-168-3
  Set clauses:
    metric 50
    community 65001:100 additive
```

The catch-all at sequence 40 has no match clause — it permits all prefixes. Sequence 50 is never reached.

<details>
<summary>Solution</summary>

**Root Cause:**

The route-map TE-TO-ISP-A has a sequence ordering error. The catch-all `permit` statement at sequence 40 has no `match` clause, so it matches every prefix and fires before the PREFIX-192-168-3 match at sequence 50. The `set metric 50` for 192.168.3.0/24 never executes. 192.168.3.0/24 is advertised with MED=0 (unset) instead of MED=50.

The same error likely exists in TE-TO-ISP-B at the corresponding sequences.

**Diagnosis:**

```
R1# show route-map TE-TO-ISP-A
(sequence 40 fires for 192.168.3.0 before sequence 50 can be reached)

R1# show ip bgp neighbors 10.1.12.2 advertised-routes
(192.168.3.0/24 shows metric 0)
```

**Fix:**

Remove the misplaced sequence 40 and sequence 50, recreate them in correct order so the PREFIX-192-168-3 match comes before the catch-all:

```
R1(config)# no route-map TE-TO-ISP-A permit 40
R1(config)# no route-map TE-TO-ISP-A permit 50
R1(config)# route-map TE-TO-ISP-A permit 30
R1(config-route-map)# match ip address prefix-list PREFIX-192-168-3
R1(config-route-map)# set metric 50
R1(config-route-map)# set community 65001:100 additive
R1(config-route-map)# exit
R1(config)# route-map TE-TO-ISP-A permit 40
R1(config-route-map)# set community 65001:100 additive
R1(config-route-map)# exit
R1(config)# end
R1# clear ip bgp 10.1.12.2 soft out
```

Apply the same fix to TE-TO-ISP-B.

**Verify:**

```
R1# show ip bgp neighbors 10.1.12.2 advertised-routes
Network          Next Hop         Metric  LocPrf  Weight  Path
*> 192.168.3.0   0.0.0.0              50                  32768 i
(MED=50 now correctly set)
```

**Key Lesson:** In route-maps, sequence numbers determine evaluation order. A `permit` sequence with no `match` clause is a catch-all that matches every prefix. Always place specific matches at lower sequence numbers and catch-alls at the highest sequence number in the route-map. When debugging, `show route-map` is essential — pay attention to match clause counts to understand which sequences are firing.

</details>

---

### Ticket 3

**Problem:** 192.168.1.0/24 is still being preferred via ISP-B (R3) even after AS-path prepending was configured to steer traffic toward ISP-A. The network operations team confirms that R3's BGP table shows the correct prepended AS-path for 192.168.1.0/24 (`65001 65001 65001 65001`). The R1-R3 session has been soft-reset. However, R3 still shows 192.168.1.0/24 as reachable (which is expected — R3 should still have the route, just with a longer path), and ISP-B customers are still reaching 192.168.1.0/24 via R3.

The engineer suspects the prepend is configured but something prevents the longer AS-path from being the deciding factor for R3's own traffic.

**Symptoms:**

```
R3# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24
  Paths: (2 available, best #1)
  * 65001 65001 65001 65001
      10.1.13.1 from 10.1.13.1 (172.16.1.1)
        Origin IGP, metric 100, localpref 100, valid, external, best
    65002 65001
      10.1.23.1 from 10.1.23.1 (172.16.2.2)
        Origin IGP, metric 0, localpref 100, valid, external
```

R3 is selecting the 4-hop prepended path as best instead of the 2-hop path via R2. This is the opposite of the expected behavior — the shorter AS-path via R2 should be preferred.

**Your Mission:** Diagnose why R3 prefers the longer AS-path and restore the correct behavior where the 2-hop path via R2 is best.

<details>
<summary>Solution</summary>

**Root Cause:**

The TE-TO-ISP-B route-map on R1 has the `set metric 100` applied to 192.168.1.0/24 (which is correct — high MED discourages ISP-B from preferring this path). However, the route arriving via R2 (which traveled 65002 65001) also carries a MED. The issue is a local-preference override: R3 has an inbound route-map from R1 that sets local-preference based on some criteria, and that route-map is inadvertently assigning LP=200 to the path from R1 directly, which overrides the AS-path length comparison. LP is compared before AS-path length in BGP path selection order.

Alternatively, a more common root cause in this topology: R3 has `bgp always-compare-med` configured, and because MED=100 from R1 is higher than MED=0 from R2 (via the R2-R3 link), R3 considers the R2 path "worse" when comparing MEDs. Wait — higher MED = less preferred. So MED=100 from R1 should make R1's path less preferred to R3. The R2 path (MED=0, lower) should be better.

Actual root cause for this ticket: On R3, there is an inbound route-map applied to the neighbor 10.1.13.1 (R1) that sets `local-preference 200` on all routes, regardless of prefix. This LP=200 from R1's direct advertisement to R3 overrides the AS-path length comparison — R3 prefers LP=200 over LP=100 (default from R2). The long prepend is irrelevant because LP is evaluated first.

**Diagnosis:**

```
R3# show ip bgp 192.168.1.0
  (best path via 10.1.13.1 shows localpref 200)
  (path via 10.1.23.1 shows localpref 100)

R3# show route-map
(look for an inbound route-map on neighbor 10.1.13.1 that sets LP)

R3# show ip bgp neighbors 10.1.13.1 | include route-map
  Inbound  route-map is SET-LP-200-FROM-R1
```

A route-map `SET-LP-200-FROM-R1` is assigning LP=200 to all routes received from R1. This was left over from a previous configuration or added in error.

**Fix:**

Remove the inbound route-map on R3 for the neighbor toward R1:

```
R3(config)# router bgp 65003
R3(config-router)# no neighbor 10.1.13.1 route-map SET-LP-200-FROM-R1 in
R3(config-router)# end
R3# clear ip bgp 10.1.13.1 soft in
```

**Verify:**

```
R3# show ip bgp 192.168.1.0
  Paths: (2 available, best #2)
    65001 65001 65001 65001
      10.1.13.1 from 10.1.13.1 (172.16.1.1)
        localpref 100, valid, external
  * 65002 65001
      10.1.23.1 from 10.1.23.1 (172.16.2.2)
        localpref 100, valid, external, best
```

R3 now prefers the 2-hop path via R2 (65002 65001) because both paths have the same LP, and AS-path length is the next tiebreaker.

**Key Lesson:** BGP path selection order matters. Local Preference is evaluated before AS-path length. If an unexpected LP value is on one path, the shorter AS-path will never win the comparison. When AS-path prepending appears to be ignored, always check LP values first — look at `show ip bgp <prefix>` on the receiving router and compare the LocPrf column across all available paths.

</details>

---

## 10. Lab Completion Checklist

Work through this checklist after completing all four tasks. Every item must be verifiable with a show command.

- [ ] `LP-FROM-ISP-A` route-map exists on R1 with three sequences (LP 200, LP 120, LP 150)
- [ ] `LP-FROM-ISP-B` route-map exists on R1 with three sequences (LP 200, LP 120, LP 150)
- [ ] R1 `show ip bgp` shows ISP-A prefixes (198.51.x.x) with LP=200 via 10.1.12.2
- [ ] R1 `show ip bgp` shows ISP-B prefixes (203.0.x.x) with LP=200 via 10.1.13.2
- [ ] R1 `show ip bgp` shows customer routes (10.5.x.x) with LP=120
- [ ] `TE-TO-ISP-A` route-map exists on R1 and is applied outbound to R2 (10.1.12.2)
- [ ] `TE-TO-ISP-B` route-map exists on R1 and is applied outbound to R3 (10.1.13.2)
- [ ] R2 `show ip bgp 192.168.2.0` shows AS-path with four occurrences of 65001 (3x prepend)
- [ ] R3 `show ip bgp 192.168.1.0` shows AS-path with four occurrences of 65001 (3x prepend)
- [ ] R1 `show ip bgp neighbors 10.1.12.2 advertised-routes` shows MED=10 for 192.168.1.0/24
- [ ] `ip route 0.0.0.0 0.0.0.0 Null0` is present in R1's running config
- [ ] `ip prefix-list COND-DEFAULT-CHECK` matches 198.51.100.0/24 (not any other prefix)
- [ ] R4 `show ip route 0.0.0.0` shows a BGP-learned default route via 172.16.1.1
- [ ] After simulating ISP-A failure (shut R2 Fa0/0), R4 loses the default route within 90 seconds
