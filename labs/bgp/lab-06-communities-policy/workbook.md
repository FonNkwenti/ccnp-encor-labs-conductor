# BGP Lab 06 — Communities & Policy Control

**Chapter:** BGP | **Lab Number:** 06 | **Difficulty:** Advanced

---

## 1. Concepts & Skills Covered

This lab introduces BGP Communities — one of the most powerful tools for scalable, flexible routing policy. You will build on the AS-path manipulation and route-map skills from Lab 05 and extend them with community tagging, propagation, and community-based matching.

### Core Topics

| Topic | Description |
|---|---|
| BGP Standard Communities | 32-bit values in `AA:NN` format for route tagging |
| `send-community` | Enabling community propagation to a BGP neighbor |
| `ip community-list` | Matching routes by their community values |
| `set community` | Tagging routes with one or more communities in a route-map |
| Well-Known Community: `no-export` | Preventing re-advertisement beyond an AS boundary |
| Well-Known Community: `no-advertise` | Preventing advertisement to any BGP neighbor |
| Community-based local-preference | Setting inbound preference using community match instead of AS-path |
| eBGP with downstream customers | Peering with AS65004 (R5) and tagging inbound customer routes |
| `additive` keyword | Adding communities without replacing existing ones |

### CCNP ENCOR Exam Relevance

Communities appear directly in the 350-401 blueprint under BGP path selection and policy. Expect questions on:
- What happens when `send-community` is missing
- The meaning of `no-export` and `no-advertise`
- How `ip community-list` and `route-map` combine to match and act on communities
- The `additive` keyword and why it matters

---

## 2. Topology & Scenario

### Scenario

You are the network engineer for an enterprise (AS 65001) with dual-ISP connectivity. The network has been operating since Lab 05 with AS-path manipulation and local-preference policies. Management now requires you to implement a BGP communities strategy to make policy more scalable and to control how routes propagate beyond AS boundaries.

A new downstream customer (R5, AS 65004) has connected to ISP-B (R3). You must ensure that customer routes are treated with the correct priority in the enterprise and that the enterprise's internal prefixes are not advertised by the ISPs to third parties.

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
| R1 | Loopback1 | 192.168.1.1/24 | Enterprise subnet |
| R1 | Loopback2 | 192.168.2.1/24 | Enterprise subnet |
| R1 | Loopback3 | 192.168.3.1/24 | Enterprise subnet |
| R1 | Fa0/0 | 10.1.14.1/30 | Link to R4 |
| R1 | Fa1/0 | 10.1.12.1/30 | Link to R2 (ISP-A) |
| R1 | Fa1/1 | 10.1.13.1/30 | Link to R3 (ISP-B) |
| R2 | Loopback0 | 172.16.2.2/32 | Router-ID |
| R2 | Loopback1-3 | 198.51.100-102.1/24 | ISP-A prefixes |
| R2 | Fa0/0 | 10.1.12.2/30 | Link to R1 |
| R2 | Fa1/0 | 10.1.23.1/30 | Link to R3 |
| R3 | Loopback0 | 172.16.3.3/32 | Router-ID |
| R3 | Loopback1-3 | 203.0.113-115.1/24 | ISP-B prefixes |
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

| Device | Role | Platform | RAM | IOS |
|---|---|---|---|---|
| R1 | Enterprise Edge | c7200 | 256 MB | 12.4T |
| R2 | ISP-A | c7200 | 256 MB | 12.4T |
| R3 | ISP-B | c7200 | 256 MB | 12.4T |
| R4 | Enterprise Internal | c3725 | 128 MB | 12.4 |
| R5 | Downstream Customer | c3725 | 128 MB | 12.4 |

### Console Access Table

| Device | Telnet Port |
|---|---|
| R1 | 5001 |
| R2 | 5002 |
| R3 | 5003 |
| R4 | 5004 |
| R5 | 5005 |

```bash
# Connect to any router
telnet 127.0.0.1 5001   # R1
telnet 127.0.0.1 5002   # R2
telnet 127.0.0.1 5003   # R3
telnet 127.0.0.1 5004   # R4
telnet 127.0.0.1 5005   # R5
```

### Platform Notes

- **c7200**: Used for R1, R2, R3. Supports Fa0/0, Fa1/0, Fa1/1, Gi3/0, s2/0-s2/3.
- **c3725**: Used for R4, R5. Supports Fa0/0, Fa0/1, Fa1/0–Fa1/15 (switch), s2/0-s2/3.
- All routers run Cisco IOS 12.4 or 12.4T.
- BGP communities require `send-community` per neighbor — it is NOT enabled by default.

---

## 4. Base Configuration

The initial configuration for this lab is the complete solution from Lab 05 (AS-path manipulation and route-map policies). R5 is added as a new device with only IP addressing — no BGP.

### What is already configured

**All routers (inherited from Lab 05):**
- Interface IP addresses
- OSPF between R1 and R4 (area 0)
- All eBGP and iBGP sessions (R1-R2, R1-R3, R1-R4, R2-R3)
- R1 route-maps: SET-LP-200-ISP-A, POLICY-ISP-B-IN, PREPEND-TO-ISP-B
- R1 AS-path ACLs and prefix-lists
- R4 distribute-list filtering internal prefixes

**R5 (new device):**
- Loopback0: 172.16.5.5/32
- Loopback1: 10.5.1.1/24
- Loopback2: 10.5.2.1/24
- Fa0/0: 10.1.35.2/30 (link to R3)
- NO BGP configured yet

### Load Initial Configs

```bash
# Option 1: Automated setup (recommended)
python3 labs/bgp/lab-06-communities-policy/setup_lab.py

# Option 2: Manual — paste each router's initial-configs/*.cfg via console
```

### Verify Base State

After loading, confirm that the Lab 05 BGP state is intact on R1:

```
R1# show ip bgp summary
R1# show ip bgp
R1# show ip ospf neighbor
```

Confirm R5 is reachable from R3:

```
R3# ping 10.1.35.2
```

---

## 5. Lab Challenge

Complete all five tasks in order. Each task builds on the previous one.

---

### Task 1 — Enable Community Propagation on All BGP Sessions

BGP communities are silently dropped by default. You must explicitly enable `send-community` on every BGP neighbor that should receive or forward communities.

**Requirements:**
- Enable `send-community` on ALL BGP neighbor statements, on ALL routers (R1, R2, R3, R4, R5)
- This includes iBGP sessions (R1-R4) and all eBGP sessions

**Hint:** The command goes under `router bgp` for each neighbor:
```
router bgp <ASN>
 neighbor <IP> send-community
```

**Verification:**
```
R1# show bgp neighbors 10.1.12.2 | include Community
```
You should see: `Community attribute sent to this neighbor`

---

### Task 2 — Tag Enterprise Prefixes with Community 65001:100 on R1

R1 should tag the three enterprise /24 prefixes (192.168.1.0, 192.168.2.0, 192.168.3.0) with standard community `65001:100` when advertising them outbound to both ISP-A (R2) and ISP-B (R3).

**Requirements:**
- Create a prefix-list matching 192.168.0.0/16 ge 24 le 24 (named ENTERPRISE-PREFIXES — already exists)
- Create a route-map named SET-COMMUNITY-OUT:
  - Sequence 10: match ENTERPRISE-PREFIXES, set community 65001:100 additive
  - Sequence 20: permit all (pass-through)
- Apply SET-COMMUNITY-OUT outbound to both R2 (10.1.12.2) and R3 (10.1.13.2)

**Why `additive`?**
The `additive` keyword appends the community to any existing communities on the prefix rather than replacing them. Always use `additive` unless you specifically want to overwrite.

**Verification:**
```
R2# show ip bgp 192.168.1.0
  Community: 65001:100
```

---

### Task 3 — Apply `no-export` to R4's Internal Prefixes

R4 advertises 10.4.1.0/24 and 10.4.2.0/24 to R1 via iBGP. These are internal enterprise routes and must NOT be re-advertised by ISPs to the internet. The `no-export` well-known community prevents advertisement beyond the receiving AS boundary.

**Requirements:**
- On R4: create `ip access-list standard ENTERPRISE-INTERNAL` matching 10.4.1.0/24 and 10.4.2.0/24 (already exists)
- Create route-map SET-NO-EXPORT:
  - Sequence 10: match ip address ENTERPRISE-INTERNAL, set community no-export additive
  - Sequence 20: permit all
- Remove the existing `distribute-list ENTERPRISE-INTERNAL out` from the iBGP neighbor
- Apply `neighbor 172.16.1.1 route-map SET-NO-EXPORT out` instead
- Add `neighbor 172.16.1.1 send-community` on R4

**Verification:**
```
R1# show ip bgp 10.4.1.0
  Community: no-export

R2# show ip bgp 10.4.1.0
  (should NOT appear — R1 must not forward no-export routes to eBGP peers)
```

---

### Task 4 — Establish R5 eBGP Session and Tag Customer Routes on R3

R5 (AS 65004) is a downstream customer of ISP-B. R3 must establish eBGP with R5, accept R5's prefixes, and tag them with community `65003:500` so that upstream routers can identify and apply policy to customer routes.

**Requirements on R3:**
- Add eBGP neighbor: `neighbor 10.1.35.2 remote-as 65004`
- Enable `send-community` to R5
- Enable `soft-reconfiguration inbound` for R5
- Create route-map TAG-CUSTOMER-IN:
  - Sequence 10: no match clause (match all), set community 65003:500 additive
- Apply TAG-CUSTOMER-IN inbound from R5

**Requirements on R5:**
- Configure `router bgp 65004`
- Set `bgp router-id 172.16.5.5`
- Add neighbor: `neighbor 10.1.35.1 remote-as 65003`
- Enable `send-community`
- Advertise: 172.16.5.5/32, 10.5.1.0/24, 10.5.2.0/24

**Verification:**
```
R3# show ip bgp summary
  (R5 neighbor should show Active -> Established)

R3# show ip bgp 10.5.1.0
  Community: 65003:500

R3# show ip bgp neighbors 10.1.35.2 received-routes
```

---

### Task 5 — Apply Community-Based Policy on R1 for Customer Routes

R1 currently applies local-preference 150 to all ISP-B routes. Customer routes tagged with `65003:500` should receive a lower local-preference of 120 (making them less preferred than direct ISP-B routes at 150, and far less preferred than ISP-A routes at 200).

**Requirements on R1:**
- Create an `ip community-list standard CUSTOMER-ROUTES permit 65003:500`
- Modify route-map POLICY-ISP-B-IN to add a new entry BEFORE the existing sequence 10:
  - Sequence 8: match community CUSTOMER-ROUTES, set local-preference 120
- The existing deny 5 (203.0.115.0/24) and permit 10 (ISP-B routes at LP 150) must remain

**Final POLICY-ISP-B-IN structure:**
```
route-map POLICY-ISP-B-IN deny 5     <- deny 203.0.115.0/24
route-map POLICY-ISP-B-IN permit 8   <- customer routes: LP 120
route-map POLICY-ISP-B-IN permit 10  <- ISP-B routes: LP 150
route-map POLICY-ISP-B-IN permit 20  <- pass-through
```

**Verification:**
```
R1# show ip bgp 10.5.1.0
  Local preference: 120

R1# show ip bgp 203.0.113.0
  Local preference: 150

R1# show ip bgp 198.51.100.0
  Local preference: 200
```

---

## 6. Verification & Analysis

### Full End-to-End Verification Sequence

#### Step 1: Confirm all BGP sessions are Established

```
R1# show ip bgp summary
BGP router identifier 172.16.1.1, local AS number 65001
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.1.12.2       4 65002      XX      XX        X    0    0  HH:MM:SS       4
10.1.13.2       4 65003      XX      XX        X    0    0  HH:MM:SS       7
172.16.4.4      4 65001      XX      XX        X    0    0  HH:MM:SS       3

R3# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.1.13.1       4 65001      XX      XX        X    0    0  HH:MM:SS       4
10.1.23.1       4 65002      XX      XX        X    0    0  HH:MM:SS       4
10.1.35.2       4 65004      XX      XX        X    0    0  HH:MM:SS       3
```

#### Step 2: Verify send-community is active

```
R1# show bgp neighbors 10.1.12.2 | include Community
Community attribute sent to this neighbor

R1# show bgp neighbors 10.1.13.2 | include Community
Community attribute sent to this neighbor
```

#### Step 3: Verify enterprise community tag (65001:100)

```
R2# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24
  ...
  Community: 65001:100
```

#### Step 4: Verify no-export on R4 internal prefixes

```
R1# show ip bgp 10.4.1.0
  Community: no-export

R2# show ip bgp 10.4.1.0
  (Entry must NOT exist — no-export prevents R1 from forwarding to R2)

R3# show ip bgp 10.4.1.0
  (Entry must NOT exist)
```

#### Step 5: Verify R5 routes tagged with 65003:500

```
R3# show ip bgp 10.5.1.0
  Community: 65003:500

R1# show ip bgp 10.5.1.0
  Local preference: 120
  Community: 65003:500
```

#### Step 6: Verify local-preference hierarchy on R1

```
R1# show ip bgp
   Network          Next Hop     Metric  LocPrf  Weight  Path
*> 198.51.100.0/24  10.1.12.2       0      200      0   65002
*> 203.0.113.0/24   10.1.13.2       0      150      0   65003
*> 10.5.1.0/24      10.1.13.2       0      120      0   65003 65004
*> 10.4.1.0/24      172.16.4.4      0      100      0   i
```

Expected local-preference hierarchy:
- ISP-A routes (via R2): **200** (highest — preferred)
- ISP-B direct routes: **150**
- Customer routes (via R3, from R5): **120** (lower priority)
- iBGP internal routes (R4): **100** (default)

#### Step 7: Confirm no-export enforcement — ISPs must not see R4 prefixes

```
R2# show ip bgp | include 10.4
(no output — R4 prefixes must be invisible to ISP-A)

R3# show ip bgp | include 10.4
(no output — R4 prefixes must be invisible to ISP-B)
```

---

## 7. Verification Cheatsheet

### Quick Reference Commands

| Goal | Command | Where to Run |
|---|---|---|
| BGP session status | `show ip bgp summary` | All routers |
| See community on a prefix | `show ip bgp <prefix>` | Any router |
| Check send-community state | `show bgp neighbors <IP> \| include Community` | R1, R2, R3, R4 |
| Soft-reset inbound policy | `clear ip bgp <IP> soft in` | R1, R3 |
| Check received routes from peer | `show ip bgp neighbors <IP> received-routes` | R1, R3 |
| Check advertised routes to peer | `show ip bgp neighbors <IP> advertised-routes` | R1, R3 |
| Verify community-list | `show ip community-list` | R1 |
| Verify route-map | `show route-map [name]` | R1, R3, R4 |
| BGP table with local-pref | `show ip bgp` | R1 |
| R5 BGP table | `show ip bgp` | R5 |

### Expected Community Values

| Prefix | Community | Applied By | Seen On |
|---|---|---|---|
| 192.168.1-3.0/24 | 65001:100 | R1 SET-COMMUNITY-OUT | R2, R3 |
| 10.4.1-2.0/24 | no-export | R4 SET-NO-EXPORT | R1 only |
| 10.5.1-2.0/24 | 65003:500 | R3 TAG-CUSTOMER-IN | R1, R3 |

### Troubleshooting One-Liners

```bash
# Communities not seen on R2?
R1# show bgp neighbors 10.1.12.2 | include Community
# Must say "Community attribute sent to this neighbor"

# Community-list not matching?
R1# show ip community-list
# Verify exact community value matches what's in the BGP table

# R5 session not coming up?
R5# show ip bgp summary
R3# debug ip bgp 10.1.35.2 events

# no-export not working?
R1# show ip bgp 10.4.1.0 | include Community
# Must show "no-export"
```

---

## 8. Solutions

### Task 1 Solution — Enable send-community on all routers

<details>
<summary>Solution — Task 1: send-community</summary>

**R1:**
```
router bgp 65001
 neighbor 10.1.12.2 send-community
 neighbor 10.1.13.2 send-community
 neighbor 172.16.4.4 send-community
```

**R2:**
```
router bgp 65002
 neighbor 10.1.12.1 send-community
 neighbor 10.1.23.2 send-community
```

**R3:**
```
router bgp 65003
 neighbor 10.1.13.1 send-community
 neighbor 10.1.23.1 send-community
 neighbor 10.1.35.2 send-community
```

**R4:**
```
router bgp 65001
 neighbor 172.16.1.1 send-community
```

**R5:**
```
router bgp 65004
 neighbor 10.1.35.1 send-community
```

**Verify:**
```
R1# show bgp neighbors 10.1.12.2 | include Community
Community attribute sent to this neighbor
```

</details>

---

### Task 2 Solution — Tag Enterprise Prefixes with 65001:100

<details>
<summary>Solution — Task 2: SET-COMMUNITY-OUT on R1</summary>

```
ip prefix-list ENTERPRISE-PREFIXES seq 10 permit 192.168.0.0/16 ge 24 le 24

route-map SET-COMMUNITY-OUT permit 10
 match ip address prefix-list ENTERPRISE-PREFIXES
 set community 65001:100 additive
!
route-map SET-COMMUNITY-OUT permit 20
!
router bgp 65001
 neighbor 10.1.12.2 route-map SET-COMMUNITY-OUT out
 neighbor 10.1.13.2 route-map SET-COMMUNITY-OUT out
```

After applying, soft-reset outbound:
```
R1# clear ip bgp 10.1.12.2 soft out
R1# clear ip bgp 10.1.13.2 soft out
```

**Verify on R2:**
```
R2# show ip bgp 192.168.1.0
  Community: 65001:100
```

Note: R1 still applies PREPEND-TO-ISP-B outbound to R3. You can chain both route-maps using `continue` or apply SET-COMMUNITY-OUT to R2 only and fold the community-setting into PREPEND-TO-ISP-B for R3. The solution config shown uses separate SET-COMMUNITY-OUT applied to both neighbors.

</details>

---

### Task 3 Solution — no-export on R4 Internal Prefixes

<details>
<summary>Solution — Task 3: SET-NO-EXPORT on R4</summary>

```
ip access-list standard ENTERPRISE-INTERNAL
 permit 10.4.1.0 0.0.0.255
 permit 10.4.2.0 0.0.0.255

route-map SET-NO-EXPORT permit 10
 match ip address ENTERPRISE-INTERNAL
 set community no-export additive
!
route-map SET-NO-EXPORT permit 20
!
router bgp 65001
 neighbor 172.16.1.1 send-community
 no neighbor 172.16.1.1 distribute-list ENTERPRISE-INTERNAL out
 neighbor 172.16.1.1 route-map SET-NO-EXPORT out
```

Soft-reset:
```
R4# clear ip bgp 172.16.1.1 soft out
```

**Verify on R1:**
```
R1# show ip bgp 10.4.1.0
  Community: no-export
```

**Verify no-export enforcement — R2 and R3 must NOT have these:**
```
R2# show ip bgp 10.4.1.0
(no entry)
R3# show ip bgp 10.4.1.0
(no entry)
```

</details>

---

### Task 4 Solution — R5 eBGP and Customer Tagging on R3

<details>
<summary>Solution — Task 4: R3 and R5 configuration</summary>

**R3:**
```
route-map TAG-CUSTOMER-IN permit 10
 set community 65003:500 additive
!
router bgp 65003
 neighbor 10.1.35.2 remote-as 65004
 neighbor 10.1.35.2 send-community
 neighbor 10.1.35.2 soft-reconfiguration inbound
 neighbor 10.1.35.2 route-map TAG-CUSTOMER-IN in
```

**R5:**
```
router bgp 65004
 bgp router-id 172.16.5.5
 neighbor 10.1.35.1 remote-as 65003
 neighbor 10.1.35.1 send-community
 network 172.16.5.5 mask 255.255.255.255
 network 10.5.1.0 mask 255.255.255.0
 network 10.5.2.0 mask 255.255.255.0
```

**Verify session:**
```
R3# show ip bgp summary
10.1.35.2       4 65004 ...  3
```

**Verify community tag:**
```
R3# show ip bgp 10.5.1.0
  Community: 65003:500
```

</details>

---

### Task 5 Solution — Community-Based Local-Preference on R1

<details>
<summary>Solution — Task 5: POLICY-ISP-B-IN with community match</summary>

```
ip community-list standard CUSTOMER-ROUTES permit 65003:500

route-map POLICY-ISP-B-IN deny 5
 match ip address prefix-list DENY-203-115
!
route-map POLICY-ISP-B-IN permit 8
 match community CUSTOMER-ROUTES
 set local-preference 120
!
route-map POLICY-ISP-B-IN permit 10
 match as-path 2
 set local-preference 150
!
route-map POLICY-ISP-B-IN permit 20
```

Soft-reset inbound from R3:
```
R1# clear ip bgp 10.1.13.2 soft in
```

**Verify:**
```
R1# show ip bgp 10.5.1.0
  Local preference: 120

R1# show ip bgp 203.0.113.0
  Local preference: 150

R1# show ip bgp 198.51.100.0
  Local preference: 200
```

**Verify community-list:**
```
R1# show ip community-list
Community standard list CUSTOMER-ROUTES
    permit 65003:500
```

</details>

---

## 9. Troubleshooting Scenarios

### Ticket 1 — Communities Not Propagating to ISP-A

**Problem Statement:**

The network operations team reports that R2 (ISP-A) is not seeing the `65001:100` community on the enterprise prefixes (192.168.1-3.0/24) even though R1 has a route-map applying the community tag. You have been asked to diagnose and fix the issue.

**Your Mission:**

Find out why communities are not reaching R2 and restore correct behavior.

**Symptoms:**
```
R2# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24
  Best path: ...
  (no Community attribute shown)
```

**Success Criteria:**
- `show ip bgp 192.168.1.0` on R2 shows `Community: 65001:100`
- `show bgp neighbors 10.1.12.2 | include Community` on R1 shows "Community attribute sent to this neighbor"

<details>
<summary>Ticket 1 Solution</summary>

**Root Cause:**

The `send-community` statement is missing from R1's neighbor configuration for 10.1.12.2 (R2). BGP does not send community attributes to any neighbor by default — it must be explicitly enabled with `send-community`.

**Diagnosis:**
```
R1# show bgp neighbors 10.1.12.2 | include Community
(no output — or shows "Community attribute not sent")
```

**Fix:**
```
R1(config)# router bgp 65001
R1(config-router)# neighbor 10.1.12.2 send-community
R1(config-router)# end
R1# clear ip bgp 10.1.12.2 soft out
```

**Verify:**
```
R1# show bgp neighbors 10.1.12.2 | include Community
Community attribute sent to this neighbor

R2# show ip bgp 192.168.1.0
  Community: 65001:100
```

**Key Lesson:**

`send-community` is required on EACH neighbor that should receive communities. It is not inherited or global. If you configure it on one neighbor but not another, communities are silently dropped for the neighbor without the configuration.

</details>

---

### Ticket 2 — Community-List Not Matching: Customer Routes Get Wrong Local-Preference

**Problem Statement:**

R1 should set local-preference 120 for routes tagged with community `65003:500` (R5 customer routes). Instead, these routes are getting local-preference 150 (the ISP-B default). Policy is leaking customer routes into the higher-priority ISP-B bucket.

**Your Mission:**

Identify why the community-list match is failing and fix it so customer routes correctly receive local-preference 120.

**Symptoms:**
```
R1# show ip bgp 10.5.1.0
  Local preference: 150
  Community: 65003:500
```

The community IS on the route, but the community-list match is not working.

**Success Criteria:**
- `show ip bgp 10.5.1.0` on R1 shows `Local preference: 120`
- `show ip bgp 203.0.113.0` on R1 still shows `Local preference: 150`
- `show ip community-list` on R1 shows the correct community value

<details>
<summary>Ticket 2 Solution</summary>

**Root Cause:**

The community-list is configured with the wrong community number, so it never matches the routes tagged `65003:500`. The misconfiguration looks like:

```
ip community-list standard CUSTOMER-ROUTES permit 65003:999
```

This will never match routes tagged with `65003:500`.

**Diagnosis:**
```
R1# show ip community-list
Community standard list CUSTOMER-ROUTES
    permit 65003:999

R1# show ip bgp 10.5.1.0
  Community: 65003:500
  Local preference: 150
```

The community value in the list (65003:999) does not match the value on the route (65003:500), so sequence 8 of POLICY-ISP-B-IN never fires. The route falls through to sequence 10 and gets LP 150.

**Fix:**
```
R1(config)# no ip community-list standard CUSTOMER-ROUTES
R1(config)# ip community-list standard CUSTOMER-ROUTES permit 65003:500
R1(config)# end
R1# clear ip bgp 10.1.13.2 soft in
```

**Verify:**
```
R1# show ip community-list
Community standard list CUSTOMER-ROUTES
    permit 65003:500

R1# show ip bgp 10.5.1.0
  Local preference: 120
```

**Key Lesson:**

Community values must match exactly — both the AS portion and the value portion. When debugging, always compare `show ip community-list` against `show ip bgp <prefix>` to confirm the values align character-for-character.

</details>

---

### Ticket 3 — R5 BGP Session Up But No Routes Advertised

**Problem Statement:**

The BGP session between R3 and R5 is showing as Established (`show ip bgp summary` on R3 shows R5 in Up/Down state with a timestamp). However, R3 is receiving 0 prefixes from R5, and the customer subnets (10.5.1.0/24, 10.5.2.0/24) are completely absent from R3's BGP table.

**Your Mission:**

Determine why R5 is not advertising any prefixes and fix the configuration so that all three R5 prefixes appear in R3's BGP table with community 65003:500.

**Symptoms:**
```
R3# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.1.35.2       4 65004      12      10        5    0    0  00:01:43        0

R5# show ip bgp
(empty or no entries)
```

**Success Criteria:**
- `show ip bgp summary` on R3 shows R5 with PfxRcd = 3
- `show ip bgp 10.5.1.0` on R3 shows `Community: 65003:500`
- `show ip bgp 10.5.2.0` on R3 shows `Community: 65003:500`

<details>
<summary>Ticket 3 Solution</summary>

**Root Cause:**

R5's BGP configuration is missing the `network` statements. The BGP session comes up (TCP + BGP OPEN succeed) but R5 has nothing to advertise because no prefixes have been injected into the BGP table via `network` commands.

**Diagnosis:**
```
R5# show ip bgp
(no entries)

R5# show running-config | section router bgp
router bgp 65004
 bgp router-id 172.16.5.5
 neighbor 10.1.35.1 remote-as 65003
 neighbor 10.1.35.1 send-community
 (no network statements)
```

**Fix:**
```
R5(config)# router bgp 65004
R5(config-router)# network 172.16.5.5 mask 255.255.255.255
R5(config-router)# network 10.5.1.0 mask 255.255.255.0
R5(config-router)# network 10.5.2.0 mask 255.255.255.0
R5(config-router)# end
```

Note: The loopback and LAN subnets must exist in R5's routing table for the `network` command to inject them into BGP. Since they are configured as Loopback interfaces, they are always in the routing table.

**Verify:**
```
R5# show ip bgp
   Network          Next Hop     Metric  LocPrf  Weight Path
*> 10.5.1.0/24      0.0.0.0           0         32768 i
*> 10.5.2.0/24      0.0.0.0           0         32768 i
*> 172.16.5.5/32    0.0.0.0           0         32768 i

R3# show ip bgp summary
10.1.35.2       4 65004 ...  3

R3# show ip bgp 10.5.1.0
  Community: 65003:500
```

**Key Lesson:**

A BGP session being Established (PfxRcvd = 0, but neighbor is Up) does NOT mean routes are being advertised. The session is a TCP connection — routes are a separate concern. Always check `show ip bgp` on the advertising router and verify that `network` statements are present AND the prefixes exist in the routing table.

</details>

---

## 10. Lab Completion Checklist

Use this checklist to confirm all lab objectives have been met before considering the lab complete.

### BGP Sessions

- [ ] R1 — R2 (AS65001 — AS65002) session is Established
- [ ] R1 — R3 (AS65001 — AS65003) session is Established
- [ ] R1 — R4 (iBGP, AS65001) session is Established
- [ ] R2 — R3 (AS65002 — AS65003) session is Established
- [ ] R3 — R5 (AS65003 — AS65004) session is Established

### send-community

- [ ] R1 has `send-community` on all 3 neighbors (10.1.12.2, 10.1.13.2, 172.16.4.4)
- [ ] R2 has `send-community` on both neighbors
- [ ] R3 has `send-community` on all 3 neighbors (including R5)
- [ ] R4 has `send-community` on R1 iBGP neighbor
- [ ] R5 has `send-community` on R3 neighbor

### Task 2 — Enterprise Community Tag

- [ ] R1 route-map SET-COMMUNITY-OUT exists
- [ ] 192.168.1.0/24 carries community 65001:100 at R2
- [ ] 192.168.2.0/24 carries community 65001:100 at R2
- [ ] 192.168.3.0/24 carries community 65001:100 at R2

### Task 3 — no-export on R4 Prefixes

- [ ] R4 route-map SET-NO-EXPORT exists
- [ ] R4 uses route-map (not distribute-list) outbound to R1
- [ ] R1 sees 10.4.1.0/24 with community no-export
- [ ] R2 does NOT have 10.4.1.0/24 in its BGP table
- [ ] R3 does NOT have 10.4.1.0/24 in its BGP table

### Task 4 — R5 Customer Routes

- [ ] R3 — R5 eBGP session is Established with PfxRcd = 3
- [ ] R3 route-map TAG-CUSTOMER-IN exists and is applied inbound from R5
- [ ] 10.5.1.0/24 carries community 65003:500 on R3
- [ ] 10.5.2.0/24 carries community 65003:500 on R3

### Task 5 — Community-Based Local-Preference on R1

- [ ] `ip community-list standard CUSTOMER-ROUTES permit 65003:500` exists on R1
- [ ] POLICY-ISP-B-IN has sequence 8 matching CUSTOMER-ROUTES
- [ ] R1 shows local-preference 120 for 10.5.1.0/24
- [ ] R1 shows local-preference 150 for 203.0.113.0/24 (ISP-B direct)
- [ ] R1 shows local-preference 200 for 198.51.100.0/24 (ISP-A)

### Policy Hierarchy Verification

Run on R1 and confirm the three-tier local-preference is intact:

```
R1# show ip bgp
```

Expected:
| Prefix Source | Local Pref | Policy |
|---|---|---|
| ISP-A (R2 routes) | 200 | SET-LP-200-ISP-A |
| ISP-B direct routes | 150 | POLICY-ISP-B-IN seq 10 |
| Customer routes (R5 via R3) | 120 | POLICY-ISP-B-IN seq 8 |
| iBGP internal (R4) | 100 | default |
