# CCNP ENCOR BGP Lab 05: AS-Path Manipulation & Route-Maps
**Student Workbook**

---

## 1. Concepts & Skills Covered

- Configure `ip as-path access-list` with regular expression patterns
- Build route-maps using `match as-path`, `match ip address prefix-list`, `set local-preference`, and `set as-path prepend`
- Apply route-maps to BGP neighbors inbound and outbound (`neighbor X route-map NAME in/out`)
- Implement AS-path prepending to engineer inbound traffic patterns (make R3 prefer the indirect path via R2)
- Replace weight-based policy with AS-wide Local Preference using route-maps
- Combine filtering and attribute modification in a single route-map

**CCNP ENCOR Exam Objective:** 3.2.e — Configure and verify BGP path manipulation using route-maps and AS-path prepending

---

## 2. Topology & Scenario

### ASCII Diagram
```
              ┌──────────────────────────────┐
              │             R1               │
              │      Enterprise Edge         │
              │     Lo0: 172.16.1.1/32       │
              │         AS 65001             │
              └─┬────────────┬────────────┬──┘
          Fa0/0 │      Fa1/0 │      Fa1/1 │
   10.1.14.1/30 │            │            │
                │      10.1.12.1/30  10.1.13.1/30
                │            │            │
   10.1.14.2/30 │      10.1.12.2/30  10.1.13.2/30
          Fa0/0 │      Fa0/0 │      Fa1/0 │
┌───────────────┴─┐ ┌────────┴──────┐┌────┴──────────┐
│       R4        │ │      R2       ││      R3        │
│  Ent Internal   │ │    ISP-A      ││    ISP-B       │
│ Lo0:172.16.4.4  │ │Lo0:172.16.2.2 ││Lo0:172.16.3.3  │
│    AS 65001     │ │   AS 65002    ││   AS 65003     │
└─────────────────┘ └───────┬───────┘└────────┬───────┘
                      Fa1/0 │                 │ Fa0/0
               10.1.23.1/30 │                 │ 10.1.23.2/30
                             └─────────────────┘
                                 10.1.23.0/30
```

### Traffic Engineering Goal
```
ISP-B (R3) view of 192.168.1.0/24:

  BEFORE prepend:
  *> 10.1.13.1  65001           (1 hop — via R1 direct, preferred)
  *   10.1.23.1  65002 65001    (2 hops — via R2)

  AFTER prepend:
  *   10.1.13.1  65001 65001 65001 65001  (4 hops — via R1 direct, longer)
  *> 10.1.23.1  65002 65001              (2 hops — via R2, now preferred)
```

### Scenario Narrative
**NexaTech Solutions** has a stable BGP environment from Lab 04. The routing policy team now needs to graduate from simple prefix-list filtering to a more powerful tool: **route-maps**. Three new policies must be implemented:

1. **Local Preference Policy** (replace the Weight approach): ISP-A (R2) routes should be preferred enterprise-wide with Local Preference 200. ISP-B (R3) routes should have Local Preference 150. Since Local Preference propagates via iBGP, this means R4 will also prefer ISP-A routes — something Weight cannot achieve.

2. **AS-Path Prepending** (inbound traffic engineering): When R1 advertises enterprise subnets to ISP-B (R3), it should prepend its own AS number three extra times. This makes the R1–R3 direct link appear less attractive to ISP-B than the path through ISP-A (R2). Return traffic from ISP-B networks will now flow via ISP-A, providing traffic engineering and load balancing.

3. **Combined Filter + Attribute** (route-map power): The ISP-B inbound policy should both deny the experimental prefix `203.0.115.0/24` AND set Local Preference 150 on all accepted ISP-B routes — all in a single route-map instead of two separate prefix-list statements.

### Device Role Table
| Device | Role | Platform | AS | Loopback0 |
|--------|------|----------|----|-----------|
| R1 | Enterprise Edge | c7200 | 65001 | 172.16.1.1/32 |
| R2 | ISP-A (Primary) | c7200 | 65002 | 172.16.2.2/32 |
| R3 | ISP-B (Backup) | c7200 | 65003 | 172.16.3.3/32 |
| R4 | Enterprise Internal | c3725 | 65001 | 172.16.4.4/32 |

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R3 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R4 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1 | Fa1/0 | R2 | Fa0/0 | 10.1.12.0/30 |
| R2 | Fa1/0 | R3 | Fa0/0 | 10.1.23.0/30 |
| R1 | Fa1/1 | R3 | Fa1/0 | 10.1.13.0/30 |
| R1 | Fa0/0 | R4 | Fa0/0 | 10.1.14.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |

---

## 4. Base Configuration

The following is **pre-configured** in the initial-configs (chained from Lab 04):

- Hostname, interface IPs, loopbacks on all routers
- eBGP sessions: R1–R2 (primary, weight 100) and R1–R3 (backup)
- ISP transit peering: R2–R3 eBGP
- iBGP: R1–R4 over loopbacks with `update-source loopback0` and `next-hop-self`
- OSPF Area 0 on R1 and R4 for iBGP loopback reachability
- Lab 04 prefix-lists active: `FROM-ISP-A`, `FROM-ISP-B`, `TO-ISP-B`
- R4 distribute-list `ENTERPRISE-INTERNAL` outbound to R1
- `soft-reconfiguration inbound` enabled on R1 for both eBGP peers

The following is **NOT pre-configured** (you will configure these):

- Any `ip as-path access-list` entries
- Any `route-map` definitions
- Any `neighbor X route-map` statements
- The `ENTERPRISE-PREFIXES` and `DENY-203-115` prefix-lists used in route-maps

---

## 5. Lab Challenge: Core Implementation

### Task 1: Configure AS-Path Access-Lists

AS-path access-lists use POSIX-style regular expressions to match the BGP AS-path attribute.

- Configure the following AS-path ACLs on R1:
  - `ip as-path access-list 1 permit ^65002$` — matches routes **originated** in AS 65002 (ISP-A)
  - `ip as-path access-list 2 permit ^65003$` — matches routes **originated** in AS 65003 (ISP-B)
  - `ip as-path access-list 3 permit _65002_` — matches any route **transiting through** AS 65002

Understand the regex anchors:
- `^` anchors to the start of the AS-path (leftmost AS = the originating AS)
- `$` anchors to the end of the AS-path
- `_` is a meta-character matching an AS boundary (space, comma, start, or end of string)

**Verification:** Use BGP table filters to confirm the AS-path ACLs match the right routes:
```
R1# show ip bgp regexp ^65002$
R1# show ip bgp regexp _65002_
```
The first command should show only routes originated in AS 65002. The second should show routes that have 65002 anywhere in the AS-path.

---

### Task 2: Replace Weight with Route-Map Local Preference (Inbound from ISP-A)

Weight is local to the router — it does not propagate via iBGP and therefore cannot influence R4's path selection. Local Preference propagates to all iBGP peers in the same AS, making it the correct tool for AS-wide outbound path preference.

On R1:
1. Define route-map `SET-LP-200-ISP-A`:
   - Sequence 10 (permit): match AS-path ACL 1 → set local-preference 200
   - Sequence 20 (permit): no match clause (pass-through for everything else at default LP=100)
2. Remove the existing `neighbor 10.1.12.2 weight 100` command
3. Remove the existing `neighbor 10.1.12.2 prefix-list FROM-ISP-A in` command
4. Apply the new route-map: `neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in`
5. Perform a soft inbound reset: `clear ip bgp 10.1.12.2 soft in`

> **Note on removing the prefix-list filter:** In this lab, Task 2 replaces the simple prefix-list inbound approach with a more powerful route-map. The route-map `SET-LP-200-ISP-A` does not contain a prefix-list match for ISP-A networks — it uses AS-path matching. This means R1 will again accept all ISP-A prefixes (not just `198.51.100.0/24`). This is intentional for this lab: we're demonstrating AS-path and route-map mechanics. In a production environment, you would add a prefix-list match clause to the route-map to continue filtering.

**Verification:**
- `show ip bgp 198.51.100.0` on R1 — confirm `Local preference: 200`
- `show ip bgp` on R4 — ISP-A routes show `LocPrf 200`, ISP-B routes show `LocPrf 100` (default). This demonstrates Local Preference propagating via iBGP to R4.

---

### Task 3: AS-Path Prepending to Engineer ISP-B Return Traffic

When R1 sends enterprise prefixes to ISP-B (R3), it will append its own AS number three extra times. From R3's perspective, the direct link to enterprise (via R1) now has an AS-path of length 4 (`65001 65001 65001 65001`). The path learned via ISP-A (R2) has an AS-path length of 2 (`65002 65001`). BGP will prefer the shorter path — traffic from ISP-B networks destined for enterprise will now flow via ISP-A.

On R1:
1. Create prefix-list `ENTERPRISE-PREFIXES`:
   - `ip prefix-list ENTERPRISE-PREFIXES seq 10 permit 192.168.0.0/16 ge 24 le 24`
2. Define route-map `PREPEND-TO-ISP-B`:
   - Sequence 10 (permit): match prefix-list `ENTERPRISE-PREFIXES` → set as-path prepend `65001 65001 65001`
   - Sequence 20 (permit): no match (pass-through all other routes unchanged)
3. Remove the existing `neighbor 10.1.13.2 prefix-list TO-ISP-B out` command
4. Apply the new outbound route-map: `neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out`
5. Apply: `clear ip bgp 10.1.13.2 soft out`

**Verification on R3:**
```
R3# show ip bgp 192.168.1.0
```
You should see two paths to `192.168.1.0/24`:
- Via `10.1.13.1` (R1 direct): AS-path `65001 65001 65001 65001` — longer, marked `*` (valid but not best)
- Via `10.1.23.1` (R2): AS-path `65002 65001` — shorter, marked `*>` (best)

R3 now prefers the path through R2, meaning ISP-B return traffic to enterprise traverses ISP-A's network.

---

### Task 4: Combined Inbound Policy for ISP-B (Filter + Local Preference)

Replace the existing `FROM-ISP-B` prefix-list with a route-map that combines both prefix denial and Local Preference setting in one structure.

On R1:
1. Create prefix-list `DENY-203-115`:
   - `ip prefix-list DENY-203-115 seq 10 permit 203.0.115.0/24`
2. Define route-map `POLICY-ISP-B-IN`:
   - Sequence 5 (**deny**): match prefix-list `DENY-203-115` — blocks `203.0.115.0/24`
   - Sequence 10 (permit): match AS-path 2 → set local-preference 150
   - Sequence 20 (permit): no match (pass-through remaining routes)
3. Remove the existing `neighbor 10.1.13.2 prefix-list FROM-ISP-B in` command
4. Apply the new inbound route-map: `neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in`
5. Apply: `clear ip bgp 10.1.13.2 soft in`

**Verification:**
- `show ip bgp neighbors 10.1.13.2 routes` on R1 — `203.0.115.0/24` absent; others present with Local Pref 150
- `show ip bgp 203.0.113.0` — confirm `Local preference: 150`
- Compare `show ip bgp` on R4: ISP-A prefixes show `200`, ISP-B prefixes show `150`

---

## 6. Verification & Analysis

### AS-Path ACL Regex Results
```bash
R1# show ip bgp regexp ^65002$
BGP table version is 12, local router ID is 172.16.1.1
   Network          Next Hop            Metric LocPrf Weight Path
*> 172.16.2.2/32    10.1.12.2                0    200      0 65002 i   ! ← only AS 65002 originated routes
*> 198.51.100.0     10.1.12.2                0    200      0 65002 i
*> 198.51.101.0     10.1.12.2                0    200      0 65002 i
*> 198.51.102.0     10.1.12.2                0    200      0 65002 i
```

### Local Preference Propagation to R4
```bash
R4# show ip bgp
BGP table version is 6, local router ID is 172.16.4.4
   Network          Next Hop            Metric LocPrf Weight Path
*>i198.51.100.0     172.16.1.1               0    200      0 65002 i   ! ← LP=200 via ISP-A
*>i203.0.113.0      172.16.1.1               0    150      0 65003 i   ! ← LP=150 via ISP-B
*>i203.0.114.0      172.16.1.1               0    150      0 65003 i
```
R4 can now distinguish path preference — ISP-A is preferred enterprise-wide.

### AS-Path Prepend Effect on R3
```bash
R3# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24, version 5
Paths: (2 available, best #2, table Default-IP-Routing-Table)
  Advertised to update-groups:
     1
  65001 65001 65001 65001                               ! ← 4 hops via R1 direct
    10.1.13.1 from 10.1.13.1 (172.16.1.1)
      Origin IGP, metric 0, localpref 100, valid, external
  65002 65001                                           ! ← 2 hops via R2, BEST
    10.1.23.1 from 10.1.23.1 (172.16.2.2)
      Origin IGP, metric 0, localpref 100, valid, external, best
```

### Route-Map Counters
```bash
R1# show route-map SET-LP-200-ISP-A
route-map SET-LP-200-ISP-A, permit, sequence 10
  Match clauses:
    as-path (as-path filter): 1
  Set clauses:
    local-preference 200
  Policy routing matches: 4 packets, 4 routes    ! ← ISP-A routes matched
route-map SET-LP-200-ISP-A, permit, sequence 20
  Match clauses:
  Set clauses:
  Policy routing matches: 2 packets, 2 routes    ! ← other routes passed through
```

---

## 7. Verification Cheatsheet

### AS-Path Access-List Syntax
```
ip as-path access-list <1-500> {permit|deny} <regex>

Common regex patterns:
  ^65002$      — originated ONLY in AS 65002 (no transit)
  _65002_      — 65002 anywhere in AS-path (transit or origin)
  ^$           — locally originated routes (empty AS-path)
  ^65002_      — AS-path starts with 65002
  _65002$      — AS-path ends with 65002 (originated in 65002)
```

### Route-Map Skeleton
```
route-map NAME {permit|deny} <sequence>
 match as-path <acl-number>
 match ip address prefix-list <name>
 set local-preference <0-4294967295>
 set as-path prepend <ASN> [ASN ...]
!
! Always add a final permit with no match clause (pass-through):
route-map NAME permit <high-seq>
```

### Apply to BGP Neighbor
```
router bgp <ASN>
 neighbor <peer> route-map NAME in    ! inbound (affects received routes)
 neighbor <peer> route-map NAME out   ! outbound (affects advertised routes)
```

### Key Show Commands
| Command | Purpose |
|---------|---------|
| `show ip as-path-access-list` | Display all AS-path ACL entries |
| `show ip bgp regexp <regex>` | Filter BGP table by AS-path pattern |
| `show route-map [NAME]` | Display route-map definition and match counts |
| `show ip bgp <prefix>` | Full BGP path details for a specific prefix |
| `show ip bgp neighbors X routes` | Accepted inbound routes from neighbor X |
| `show ip bgp neighbors X advertised-routes` | What is being sent to neighbor X |

### Route-Map Logic Refresher

| Condition | Route-Map Action | Result |
|-----------|-----------------|--------|
| match + permit clause | Route accepted, set clauses applied | Process this route with modifications |
| match + deny clause | Route dropped | Route not accepted/advertised |
| no match in any clause | Implicit deny at end of route-map | Route dropped (common mistake!) |
| permit clause with no match | Matches ALL routes — use as pass-through | All unmatched routes pass through |

> **Critical:** Always add a final `permit <high-seq>` with no match clause, or all unmatched routes will be implicitly denied.

### Common Route-Map Pitfalls

| Symptom | Likely Cause |
|---------|-------------|
| All routes from a neighbor blocked | Missing final `permit` pass-through sequence in route-map |
| AS-path prepend has no effect | Route-map applied `in` instead of `out` |
| Local preference not visible on R4 | Using `set weight` instead of `set local-preference` (weight is local only) |
| AS-path ACL matches too many routes | Regex too broad — e.g., `.*65002.*` matches more than `^65002$` |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: AS-Path Access-Lists

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
ip as-path access-list 1 permit ^65002$
ip as-path access-list 2 permit ^65003$
ip as-path access-list 3 permit _65002_
```
</details>

### Task 2: Route-Map with Local Preference (ISP-A)

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
route-map SET-LP-200-ISP-A permit 10
 match as-path 1
 set local-preference 200
!
route-map SET-LP-200-ISP-A permit 20
!
router bgp 65001
 no neighbor 10.1.12.2 weight 100
 no neighbor 10.1.12.2 prefix-list FROM-ISP-A in
 neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in
!
clear ip bgp 10.1.12.2 soft in
```
</details>

### Task 3: AS-Path Prepending (Outbound to ISP-B)

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
ip prefix-list ENTERPRISE-PREFIXES seq 10 permit 192.168.0.0/16 ge 24 le 24
!
route-map PREPEND-TO-ISP-B permit 10
 match ip address prefix-list ENTERPRISE-PREFIXES
 set as-path prepend 65001 65001 65001
!
route-map PREPEND-TO-ISP-B permit 20
!
router bgp 65001
 no neighbor 10.1.13.2 prefix-list TO-ISP-B out
 neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out
!
clear ip bgp 10.1.13.2 soft out
```
</details>

### Task 4: Combined ISP-B Inbound Policy

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
ip prefix-list DENY-203-115 seq 10 permit 203.0.115.0/24
!
route-map POLICY-ISP-B-IN deny 5
 match ip address prefix-list DENY-203-115
!
route-map POLICY-ISP-B-IN permit 10
 match as-path 2
 set local-preference 150
!
route-map POLICY-ISP-B-IN permit 20
!
router bgp 65001
 no neighbor 10.1.13.2 prefix-list FROM-ISP-B in
 neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in
!
clear ip bgp 10.1.13.2 soft in
```
</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then
diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket N
python3 scripts/fault-injection/apply_solution.py      # restore
```

---

### Ticket 1 — Route-Map Blocking All Routes from ISP-A

After applying the new route-map policy on R1, the NOC reports that NexaTech is no longer receiving any prefixes from ISP-A. The BGP session with R2 is established, but `show ip bgp summary` shows 0 prefixes received from R2.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** R1's BGP table contains ISP-A prefixes (198.51.100.0, 198.51.101.0, 198.51.102.0). `show route-map SET-LP-200-ISP-A` shows match counts > 0.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, check the BGP summary: `show ip bgp summary`. The R2 neighbor shows `0` under State/PfxRcd — zero prefixes accepted.
2. Check received routes: `show ip bgp neighbors 10.1.12.2 received-routes`. You can see all ISP-A prefixes in the raw store.
3. Check accepted routes: `show ip bgp neighbors 10.1.12.2 routes`. Zero routes shown — the route-map is blocking everything.
4. Examine the route-map: `show route-map SET-LP-200-ISP-A`. Notice that only two sequences exist: seq 10 with a match on as-path 1 and `set local-preference 200`. There is no seq 20 pass-through.
5. Check what happens to routes that don't match seq 10: in a route-map, the implicit action at the end (after all sequences are exhausted without a match) is **deny**. Since seq 10 only matches routes originated in AS 65002 (`^65002$`), routes like `172.16.2.2/32` (R2's loopback, which R2 originates) or any routes from AS 65003 that R2 learns and re-advertises would match, but non-ISP-A routes (if any) would be denied. However, the real issue: the ISP-A routes DO match seq 10 and are permitted — so why 0 prefixes?
6. Re-inspect seq 10 carefully: `show route-map SET-LP-200-ISP-A`. Seq 10 is **deny** (not permit). The engineer created the sequence with `route-map SET-LP-200-ISP-A deny 10` instead of `permit 10`.
7. Root cause: A `deny` sequence in a route-map denies matching routes. All ISP-A routes match AS-path 1 and are thus denied. No pass-through sequence exists for non-matching routes.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — replace the deny sequence with permit
no route-map SET-LP-200-ISP-A 10
route-map SET-LP-200-ISP-A permit 10
 match as-path 1
 set local-preference 200
!
! Ensure pass-through exists
route-map SET-LP-200-ISP-A permit 20
!
clear ip bgp 10.1.12.2 soft in
```
</details>

---

### Ticket 2 — AS-Path Prepending Not Affecting ISP-B Path Selection

The network team applied AS-path prepending to ISP-B and ran a soft reset. However, checking R3's BGP table reveals that R3 still prefers the direct path to enterprise via R1 (not the path via R2 as intended). The prepend does not appear to be working.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip bgp 192.168.1.0` on R3 shows the path via `10.1.23.1` (R2) as best (`*>`), not the path via `10.1.13.1` (R1).

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R3, examine paths: `show ip bgp 192.168.1.0`. The direct path via R1 (`10.1.13.1`) shows AS-path `65001` (1 hop) and is marked `*>` (best). The path via R2 shows `65002 65001` (2 hops). Prepending is NOT active.
2. On R1, check the route-map: `show route-map PREPEND-TO-ISP-B`. The route-map has seq 10 with `match ip address prefix-list ENTERPRISE-PREFIXES` and `set as-path prepend 65001 65001 65001`. The match count shows 0 — the route-map is never hitting.
3. Check the neighbor configuration on R1: `show running-config | section bgp`. Look at the neighbor 10.1.13.2 statements. You'll find: `neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B in` — the route-map is applied **inbound** from R3, not **outbound** to R3.
4. Root cause: `in` applies the route-map to routes received FROM R3. In the inbound direction, the `match ip address prefix-list ENTERPRISE-PREFIXES` check runs against ISP-B prefixes (e.g., 203.0.113.0/24), which do NOT match the enterprise prefix-list. So the route-map has no effect on outgoing enterprise advertisements.
5. Prepending must be applied **outbound** (`out`) to modify the AS-path on routes R1 **sends** to R3.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — change direction from 'in' to 'out'
router bgp 65001
 no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B in
 neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out
!
clear ip bgp 10.1.13.2 soft out
```
</details>

---

### Ticket 3 — R4 Cannot Distinguish ISP Preference (Local Preference Not Propagating)

The routing policy team confirmed that R1 correctly prefers ISP-A routes locally. However, R4 shows all ISP routes with the same preference — it cannot determine which ISP to prefer when sending traffic, causing suboptimal routing from the internal network.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip bgp` on R4 displays ISP-A routes (65002) with `LocPrf 200` and ISP-B routes (65003) with `LocPrf 150`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R4, check the BGP table: `show ip bgp`. ISP-A and ISP-B routes both show `LocPrf 100` (the default) — no differentiation.
2. On R1, check the local BGP table: `show ip bgp`. R1 itself also shows `LocPrf 100` for ISP-A routes instead of 200.
3. Check the route-map definition on R1: `show route-map SET-LP-200-ISP-A`. Under seq 10, the `Set clauses:` line reads `weight 200` instead of `local-preference 200`.
4. Verify: `show ip bgp 198.51.100.0`. The route shows `weight: 200` but `Local preference: 100`. Weight is a Cisco proprietary attribute that is LOCAL to the router and is NOT propagated in BGP updates. R4 receives the iBGP update without any weight value.
5. Root cause: `set weight 200` was used in place of `set local-preference 200`. Weight only influences path selection on the local router (R1), not across the AS. Local Preference is the correct BGP attribute to use for AS-wide outbound policy.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — replace set weight with set local-preference in the route-map
no route-map SET-LP-200-ISP-A 10
route-map SET-LP-200-ISP-A permit 10
 match as-path 1
 set local-preference 200
!
clear ip bgp 10.1.12.2 soft in
```
</details>

---

## 10. Lab Completion Checklist

### Core Implementation
- [ ] AS-path ACL 1 (`^65002$`) and ACL 2 (`^65003$`) defined and tested
- [ ] Route-map `SET-LP-200-ISP-A` applied inbound from R2; ISP-A routes show LP=200 on R1 and R4
- [ ] Old `neighbor 10.1.12.2 weight 100` removed
- [ ] Prefix-list `ENTERPRISE-PREFIXES` created matching 192.168.x.x/24 range
- [ ] Route-map `PREPEND-TO-ISP-B` applied **outbound** to R3
- [ ] R3 `show ip bgp 192.168.1.0` shows 4-hop path via R1 (not best) and 2-hop via R2 (best)
- [ ] Route-map `POLICY-ISP-B-IN` applied inbound from R3; 203.0.115.0/24 blocked; LP=150 set on ISP-B routes
- [ ] R4 BGP table shows LP=200 for ISP-A and LP=150 for ISP-B routes

### Troubleshooting
- [ ] Ticket 1: `deny` vs `permit` in route-map sequence diagnosed and fixed
- [ ] Ticket 2: Route-map applied `in` instead of `out` diagnosed and fixed
- [ ] Ticket 3: `set weight` vs `set local-preference` difference explained and fixed
