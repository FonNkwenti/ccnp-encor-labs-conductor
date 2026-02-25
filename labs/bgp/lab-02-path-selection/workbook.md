# CCNP ENCOR BGP Lab 02: BGP Path Selection Algorithm
**Student Workbook**

---

## 1. Concepts & Skills Covered

- Understand the BGP best-path selection decision tree
- Manipulate path selection using Weight (Cisco-proprietary, router-local)
- Configure Local Preference for AS-wide outbound policy
- Observe how AS-Path length influences best-path selection
- Demonstrate MED (Multi-Exit Discriminator) for inter-AS inbound traffic hints

**CCNP ENCOR Exam Objective:** 3.2.c — Configure and verify eBGP between directly connected neighbors (best path selection algorithm and neighbor relationships)

---

## 2. Topology & Scenario

### ASCII Diagram
```
              ┌─────────────────────────┐
              │           R1            │
              │    Enterprise Edge      │
              │   Lo0: 172.16.1.1/32    │
              │       AS 65001          │
              └──────┬───────────┬──────┘
           Fa1/0     │           │     Fa1/1
     10.1.12.1/30    │           │   10.1.13.1/30
                     │           │
     10.1.12.2/30    │           │   10.1.13.2/30
           Fa0/0     │           │     Fa1/0
     ┌───────────────┘           └───────────────┐
     │                                           │
┌────┴──────────────┐           ┌────────────────┴────┐
│       R2          │           │       R3            │
│     ISP-A         │           │     ISP-B           │
│ Lo0: 172.16.2.2/32│           │ Lo0: 172.16.3.3/32  │
│     AS 65002      │           │     AS 65003        │
└─────────┬─────────┘           └─────────┬───────────┘
      Fa1/0│                              │Fa0/0
10.1.23.1/30│                            │10.1.23.2/30
            └────────────────────────────┘
                      10.1.23.0/30
```

### Scenario Narrative
**NexaTech Solutions** has successfully established eBGP peering with both ISPs. The network now has dual-homed internet access, and the BGP tables on all three routers are fully populated.

The CTO wants the network team to understand exactly how BGP chooses paths and to implement a **primary/backup ISP policy**: R2 (ISP-A) should be the preferred outbound path for all Enterprise traffic, with R3 (ISP-B) acting as backup. Additionally, the team must learn to influence **inbound** traffic from the ISPs using MED.

### Device Role Table
| Device | Role | Platform | AS | Loopback0 |
|--------|------|----------|----|-----------|
| R1 | Enterprise Edge | c7200 | 65001 | 172.16.1.1/32 |
| R2 | ISP-A (Primary) | c7200 | 65002 | 172.16.2.2/32 |
| R3 | ISP-B (Backup) | c7200 | 65003 | 172.16.3.3/32 |

### BGP Table State at Lab Start

At the start of this lab, the BGP table on R1 contains 12 prefixes and all neighbors are Established. For example, R1 has two paths to ISP-B prefixes (203.0.113.0/24):

| Path | Next-Hop | AS-Path | Reason |
|------|----------|---------|--------|
| **Best** `*>` | 10.1.13.2 (R3) | `65003` | AS-path length = 1 |
| Alternate | 10.1.12.2 (R2) | `65002 65003` | AS-path length = 2 |

Understanding **why** this selection is made — and how to change it — is the core objective of this lab.

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R3 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1 | Fa1/0 | R2 | Fa0/0 | 10.1.12.0/30 |
| R2 | Fa1/0 | R3 | Fa0/0 | 10.1.23.0/30 |
| R1 | Fa1/1 | R3 | Fa1/0 | 10.1.13.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

The following is **pre-configured** in the initial-configs (chained from Lab 01):

- Hostname, interface IPs, loopback interfaces on all routers
- Full BGP process on R1 (AS 65001), R2 (AS 65002), R3 (AS 65003)
- All eBGP neighbor relationships Established
- 4 prefixes advertised per AS (loopback + 3 route subnets)

The following is **NOT pre-configured** (you will configure these):

- BGP path selection attributes (Weight, Local Preference, AS-path prepend, MED)
- Route-maps for policy application

---

## 5. Lab Challenge: Core Implementation

### Task 1: Audit the BGP Decision Tree

- On R1, examine the BGP table in detail for a prefix that has two paths: one via R2 (10.1.12.2) and one via R3 (10.1.13.2). Use `show ip bgp 203.0.113.0/24` to see both paths.
- Identify which path is marked with `*>` (best) and state WHY it is selected (which attribute in the decision tree makes the difference).
- Repeat for `show ip bgp 198.51.100.0/24` — identify the best path and the deciding attribute.
- Document the full BGP decision tree order (at minimum: Weight → Local Preference → AS-Path length → Origin → MED → eBGP over iBGP → lowest next-hop IGP metric → oldest path → lowest router-id).

**Verification:** Using `show ip bgp 203.0.113.0/24`, confirm the best path is via 10.1.13.2 with AS-path `65003`. The competing path via 10.1.12.2 shows AS-path `65002 65003`.

---

### Task 2: Weight — Override Default Path Selection

- On R1, configure a neighbor-level weight of 100 for all routes received from R2 (10.1.12.2). Weight default is 0, so R2's routes will now have weight 100 and R3's will have weight 0.
- Perform a soft reset of the BGP session toward R2 to activate the new weight without tearing down the session.
- Verify that R1 now selects R2 as the best path for **all** prefixes — including ISP-B prefixes (e.g., 203.0.113.0/24) that previously used R3 due to shorter AS-path. Weight overrides AS-path length.

**Verification:** `show ip bgp 203.0.113.0/24` must now show `*>` on the path via 10.1.12.2 (weight=100, AS-path `65002 65003`) and `*` on the alternate via 10.1.13.2 (weight=0, AS-path `65003`).

---

### Task 3: Local Preference — AS-Wide Outbound Policy

- Remove the neighbor weight from Task 2 (or configure it to 0), and instead implement Local Preference.
- On R1, create a route-map named `SET_LP_HIGH` that sets local-preference to 200.
- Apply this route-map inbound on the neighbor session with R2 (10.1.12.2). All routes received from R2 will now carry LP=200 in R1's BGP table.
- Perform a soft reset of the R2 session to activate the policy.
- Verify that routes from R2 show LP=200 in R1's BGP table, while routes from R3 retain the default LP=100.
- Confirm R1 selects R2 paths as best for all prefixes (LP 200 > LP 100, and LP is evaluated before AS-path length).

**Verification:** `show ip bgp 203.0.113.0/24` must show `*>` on the R2 path with `localpref 200`, and `*` on the R3 path with `localpref 100`.

---

### Task 4: AS-Path Prepending — Inbound Traffic Engineering

- Remove the Local Preference from Task 3 to restore the default selection (shorter AS-path wins).
- On R2 (ISP-A), create a route-map named `PREPEND_TO_R1` that prepends AS 65002 twice more when advertising routes to R1.
- Apply this route-map outbound on R2's neighbor session to R1 (10.1.12.1).
- Verify that on R1, ISP-A prefixes (198.51.100.0/24) now arrive from R2 with an AS-path of `65002 65002 65002` (length 3), while the same prefix via R3 has AS-path `65003 65002` (length 2) — so R1 now prefers R3 for ISP-A prefixes.

**Verification:** `show ip bgp 198.51.100.0/24` on R1 must show `*>` on the R3 path (AS-path `65003 65002`, length 2) and `*` on the R2 path (AS-path `65002 65002 65002`, length 3).

---

### Task 5: MED — Influencing Adjacent-AS Routing Decisions

- Remove the AS-path prepend from Task 4 on R2.
- On R1, create two route-maps: `SET_MED_LOW` (setting MED=10) and `SET_MED_HIGH` (setting MED=100).
- Apply `SET_MED_LOW` outbound on R1's neighbor session to R2, and `SET_MED_HIGH` outbound on R1's neighbor session to R3.
- This tells ISP-A to prefer the R1-R2 link (MED=10) and tells ISP-B that R1 is less preferred via R3 (MED=100) — simulating a primary/backup inbound traffic policy.
- Verify that R2's BGP entry for 192.168.1.0/24 shows MED=10, and R3's entry shows MED=100.

**Verification:** `show ip bgp 192.168.1.0/24` on R2 must show `metric 10`. `show ip bgp 192.168.1.0/24` on R3 must show `metric 100`.

---

## 6. Verification & Analysis

### Task 1 Verification: Two Paths to ISP-B Prefix

```bash
R1# show ip bgp 203.0.113.0/24
BGP routing table entry for 203.0.113.0/24, version 9
Paths: (2 available, best #2, table Default-IP-Routing-Table)
  Advertised to update-groups:
     1
  65002 65003
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, metric 0, localpref 100, valid, external   ! ← AS-path length 2
      Last update: 00:10:05
  65003
    10.1.13.2 from 10.1.13.2 (172.16.3.3)
      Origin IGP, metric 0, localpref 100, valid, external, best   ! ← best: shorter AS-path (1)
      Last update: 00:10:05
```

### Task 2 Verification: Weight Overrides AS-Path

```bash
R1# clear ip bgp 10.1.12.2 soft
R1# show ip bgp 203.0.113.0/24
...
  65002 65003
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, localpref 100, weight 100, valid, external, best   ! ← weight=100 beats weight=0
  65003
    10.1.13.2 from 10.1.13.2 (172.16.3.3)
      Origin IGP, localpref 100, weight 0, valid, external           ! ← weight=0, no longer best

R1# show ip bgp summary | include 10.1.12
10.1.12.2       4 65002      25      25       13    0    0 00:08:12        4   ! ← still Established
```

### Task 3 Verification: Local Preference

```bash
R1# clear ip bgp 10.1.12.2 soft
R1# show ip bgp 203.0.113.0/24
...
  65002 65003
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, localpref 200, valid, external, best   ! ← LP=200, wins over LP=100
  65003
    10.1.13.2 from 10.1.13.2 (172.16.3.3)
      Origin IGP, localpref 100, valid, external         ! ← default LP=100, not best

R1# show ip bgp 203.0.113.0/24 | include localpref
      Origin IGP, localpref 200, valid, external, best   ! ← LP=200 confirmed
```

### Task 4 Verification: AS-Path Prepend

```bash
R2# clear ip bgp 10.1.12.1 soft
R1# show ip bgp 198.51.100.0/24
...
  65002 65002 65002
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, localpref 100, valid, external         ! ← length 3, not best
  65003 65002
    10.1.13.2 from 10.1.13.2 (172.16.3.3)
      Origin IGP, localpref 100, valid, external, best   ! ← length 2, best due to shorter path
```

### Task 5 Verification: MED

```bash
R2# show ip bgp 192.168.1.0/24
BGP routing table entry for 192.168.1.0/24, version 7
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001
    10.1.12.1 from 10.1.12.1 (172.16.1.1)
      Origin IGP, metric 10, localpref 100, valid, external, best   ! ← MED=10 (metric field)

R3# show ip bgp 192.168.1.0/24
BGP routing table entry for 192.168.1.0/24, version 7
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001
    10.1.13.1 from 10.1.13.1 (172.16.1.1)
      Origin IGP, metric 100, localpref 100, valid, external, best   ! ← MED=100 (metric field)
```

---

## 7. Verification Cheatsheet

### BGP Decision Tree Order (Memorize This!)

```
1.  Weight          (Cisco-proprietary, local only)   HIGHEST wins
2.  Local Preference (iBGP, AS-wide)                  HIGHEST wins
3.  Locally Originated (network/aggregate/redist)     LOCAL wins
4.  AS-Path Length                                    SHORTEST wins
5.  Origin Code     (i < e < ?)                       LOWEST wins
6.  MED             (only same neighboring AS)        LOWEST wins
7.  eBGP over iBGP                                    eBGP wins
8.  Lowest IGP metric to next-hop                     LOWEST wins
9.  Oldest eBGP path (for stability)                  OLDEST wins
10. Lowest BGP Router-ID of neighbor                  LOWEST wins
```

> **Exam tip:** Weight is evaluated FIRST and is LOCAL to the router — it is never advertised. Local Preference is evaluated SECOND and IS sent to iBGP peers within the AS.

### Weight Configuration

```
router bgp <ASN>
 neighbor <ip> weight <0-65535>
```

| Command | Purpose |
|---------|---------|
| `neighbor <ip> weight <value>` | Set weight for ALL routes from a neighbor |
| `set weight <value>` (in route-map) | Set weight for SPECIFIC routes via route-map |
| `clear ip bgp <ip> soft` | Soft-reset to apply new weight without resetting TCP session |

> **Exam tip:** `neighbor weight` applies to all routes from that neighbor. Use a route-map with `set weight` to apply weight per-prefix. Weight is local — it is never advertised to any peer.

### Local Preference Configuration

```
route-map SET_LP permit 10
 set local-preference <0-4294967295>
!
router bgp <ASN>
 neighbor <ip> route-map SET_LP in
```

| Command | Purpose |
|---------|---------|
| `set local-preference <value>` | Set LP in a route-map |
| `bgp default local-preference <value>` | Change the AS-wide LP default (normally 100) |
| `clear ip bgp <ip> soft in` | Re-process inbound updates with new policy |

> **Exam tip:** Local Preference is advertised to all iBGP peers but **not** to eBGP peers. It is only meaningful inside a single AS. In a single-router AS, LP only matters when there are multiple exit points.

### AS-Path Prepending

```
route-map PREPEND permit 10
 set as-path prepend <own-ASN> <own-ASN>
!
router bgp <ASN>
 neighbor <ip> route-map PREPEND out
```

| Command | Purpose |
|---------|---------|
| `set as-path prepend <ASN> ...` | Prepend one or more AS numbers to outbound updates |
| `show ip bgp <prefix>` | Verify AS-path length on the receiving router |

> **Exam tip:** Only prepend your own AS number. Prepending a foreign ASN is invalid and may be rejected. Each repetition of your ASN adds 1 to the path length.

### MED Configuration

```
route-map SET_MED permit 10
 set metric <0-4294967295>
!
router bgp <ASN>
 neighbor <ip> route-map SET_MED out
```

| Command | Purpose |
|---------|---------|
| `set metric <value>` | Set MED in a route-map (outbound to neighbors) |
| `bgp always-compare-med` | Compare MEDs even from different neighboring ASes |

> **Exam tip:** MED is non-transitive — it is NOT passed beyond the adjacent AS by default. It is only compared between paths from the SAME neighboring AS. Lower MED is preferred.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip bgp <prefix>` | Best path marker (`>`), all paths, attributes (weight, localpref, metric) |
| `show ip bgp <prefix> detail` | Full attribute detail for each path |
| `show ip bgp regexp _65002_` | All paths transiting AS 65002 |
| `show ip bgp neighbors <ip> advertised-routes` | Confirm prepended paths are being sent |
| `show ip bgp neighbors <ip> routes` | Routes received before policy application |

### Common BGP Path Selection Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Weight not taking effect | `clear ip bgp soft` not performed; or route-map not applied |
| LP set but path unchanged | LP is evaluated after Weight; check Weight first |
| AS-path prepend visible on sender but not receiver | `soft out` clear needed on the sending router |
| MED shows 0 on neighbor | Route-map applied `in` instead of `out` on the originating router |
| `bgp always-compare-med` needed | Comparing MEDs from different neighboring ASes (non-default) |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 2: Weight

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — neighbor-level weight (simplest method)
router bgp 65001
 neighbor 10.1.12.2 weight 100

! OR via route-map for per-prefix control:
route-map PREFER_R2 permit 10
 set weight 100
!
router bgp 65001
 neighbor 10.1.12.2 route-map PREFER_R2 in

! Apply changes:
clear ip bgp 10.1.12.2 soft
```
</details>

<details>
<summary>Click to view Verification</summary>

```bash
R1# show ip bgp 203.0.113.0/24
! Best path (*>) should be via 10.1.12.2 with weight 100
show ip bgp summary
! R2 neighbor PfxRcvd should still show 4
```
</details>

### Task 3: Local Preference

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! Step 1: Remove weight from Task 2
router bgp 65001
 neighbor 10.1.12.2 weight 0

! Step 2: Configure Local Preference via route-map
route-map SET_LP_HIGH permit 10
 set local-preference 200
!
router bgp 65001
 neighbor 10.1.12.2 route-map SET_LP_HIGH in

! Apply:
clear ip bgp 10.1.12.2 soft in
```
</details>

<details>
<summary>Click to view Verification</summary>

```bash
R1# show ip bgp 203.0.113.0/24
! Best path (*>) must be via 10.1.12.2 with localpref 200
R1# show ip bgp | include 65003
! All ISP-B routes should show 10.1.12.2 as next-hop
```
</details>

### Task 4: AS-Path Prepending

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! Step 1: Remove LP from R1 Task 3
! On R1:
router bgp 65001
 no neighbor 10.1.12.2 route-map SET_LP_HIGH in
clear ip bgp 10.1.12.2 soft in

! Step 2: Prepend on R2 for routes sent to R1
route-map PREPEND_TO_R1 permit 10
 set as-path prepend 65002 65002
!
router bgp 65002
 neighbor 10.1.12.1 route-map PREPEND_TO_R1 out

! Apply:
clear ip bgp 10.1.12.1 soft out
```
</details>

<details>
<summary>Click to view Verification</summary>

```bash
R1# show ip bgp 198.51.100.0/24
! AS-path from R2 now shows "65002 65002 65002" (length 3)
! Best path must be via R3 with "65003 65002" (length 2)

R2# show ip bgp neighbors 10.1.12.1 advertised-routes
! Routes should show prepended AS-path "65002 65002 65002"
```
</details>

### Task 5: MED

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! Step 1: Remove prepend from R2 Task 4
! On R2:
router bgp 65002
 no neighbor 10.1.12.1 route-map PREPEND_TO_R1 out
clear ip bgp 10.1.12.1 soft out

! Step 2: Set MED on R1 outbound to R2 and R3
route-map SET_MED_LOW permit 10
 set metric 10
!
route-map SET_MED_HIGH permit 10
 set metric 100
!
router bgp 65001
 neighbor 10.1.12.2 route-map SET_MED_LOW out
 neighbor 10.1.13.2 route-map SET_MED_HIGH out

! Apply:
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out
```
</details>

<details>
<summary>Click to view Verification</summary>

```bash
R2# show ip bgp 192.168.1.0/24
! Must show: metric 10

R3# show ip bgp 192.168.1.0/24
! Must show: metric 100

R1# show ip bgp neighbors 10.1.12.2 advertised-routes | include 192.168
! Confirm MED=10 is being sent to R2
```
</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then
diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore
```

---

### Ticket 1 — R1 is Not Preferring R2 for ISP-A Prefixes Despite Shorter AS-Path

The operations team reports that traffic from the Enterprise to ISP-A (198.51.100.0/24) is going out via R3 (10.1.13.2) instead of directly via R2 (10.1.12.2), even though the direct R2 path has a shorter AS-path. No maintenance windows are active.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip bgp 198.51.100.0/24` on R1 shows `*>` on the path via 10.1.12.2 (R2) with AS-path `65002` (length 1). R3 path with `65003 65002` (length 2) is the alternate.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, run `show ip bgp 198.51.100.0/24` — best path is via 10.1.13.2 (R3) even though AS-path is longer.
2. Note the attributes: the R3 path shows `weight 200`, the R2 path shows `weight 0`.
3. Weight is evaluated BEFORE AS-path length. A higher weight on the R3 neighbor is overriding the shorter AS-path.
4. On R1, run `show ip bgp neighbors 10.1.13.2 | include weight` or check `show running-config | section router bgp` — `neighbor 10.1.13.2 weight 200` is configured.
5. Root cause: Weight 200 was applied to neighbor R3, making all R3 routes win over R2 routes.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
router bgp 65001
 no neighbor 10.1.13.2 weight 200
!
clear ip bgp 10.1.13.2 soft
```
</details>

---

### Ticket 2 — All Best Paths on R1 Are Via R3 Despite Policy Requiring R2 as Primary

A change control was processed last night to make R2 (ISP-A) the preferred outbound path. After the change, monitoring shows that ALL prefixes on R1 have their best path via R3 (10.1.13.2) — the opposite of the intended policy.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** R1 selects R2 paths as best for prefixes where R2 has a direct advertisement. `show ip bgp 198.51.100.0/24` shows `*>` via 10.1.12.2.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, run `show ip bgp` — all `*>` (best) entries show 10.1.13.2 as next-hop.
2. Run `show ip bgp 198.51.100.0/24` — the path via R2 shows `localpref 50`, the path via R3 shows `localpref 100` (default).
3. Local Preference is evaluated second in the decision tree. LP=50 on R2's routes is LOWER than the default LP=100 on R3's routes, so R3 always wins.
4. On R1, run `show running-config | section route-map` — a route-map is setting LP=50 on routes from R2.
5. Root cause: The route-map was configured with `set local-preference 50` instead of `set local-preference 200`.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
route-map BROKEN_LP permit 10
 set local-preference 200
!
clear ip bgp 10.1.12.2 soft in
```
</details>

---

### Ticket 3 — ISP-A Reports They Are Not Seeing MED Values for Enterprise Prefixes

R2's NOC contacts NexaTech to report that Enterprise prefixes (192.168.1.0/24) appear in R2's BGP table with no MED (metric=0), even though R1 was recently configured to send MED=10 toward R2.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip bgp 192.168.1.0/24` on R2 shows `metric 10`. `show ip bgp 192.168.1.0/24` on R3 shows `metric 100`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R2, run `show ip bgp 192.168.1.0/24` — the path shows `metric 0`, no MED.
2. On R3, run `show ip bgp 192.168.1.0/24` — also shows `metric 0`.
3. On R1, run `show ip bgp neighbors 10.1.12.2 advertised-routes` — the prefix shows `metric 0` when advertised.
4. On R1, run `show running-config | section router bgp` — the MED route-maps are applied with the `in` keyword instead of `out`: `neighbor 10.1.12.2 route-map SET_MED_LOW in`.
5. Root cause: The route-map setting MED is applied inbound (modifying routes R1 receives from R2), not outbound (modifying routes R1 sends to R2). MED must be set on outbound advertisements.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
router bgp 65001
 no neighbor 10.1.12.2 route-map SET_MED_LOW in
 no neighbor 10.1.13.2 route-map SET_MED_HIGH in
 neighbor 10.1.12.2 route-map SET_MED_LOW out
 neighbor 10.1.13.2 route-map SET_MED_HIGH out
!
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out
```
</details>

---

## 10. Lab Completion Checklist

### Core Implementation
- [ ] BGP decision tree documented (10 steps in order)
- [ ] Weight=100 set on R1 for R2 neighbor; ISP-B prefixes shift to R2 path
- [ ] Local Preference=200 set on R1 for routes from R2; all prefixes prefer R2
- [ ] AS-path prepend (2x AS 65002) configured on R2 toward R1; ISP-A prefixes shift to R3
- [ ] MED=10 advertised by R1 to R2; MED=100 advertised to R3 for Enterprise prefixes
- [ ] Verified MED values on R2 (`metric 10`) and R3 (`metric 100`)

### Troubleshooting
- [ ] Ticket 1: Wrong weight on R3 neighbor diagnosed and fixed
- [ ] Ticket 2: Low Local Preference (50) on R2 routes diagnosed and fixed
- [ ] Ticket 3: Route-map applied inbound instead of outbound for MED diagnosed and fixed
