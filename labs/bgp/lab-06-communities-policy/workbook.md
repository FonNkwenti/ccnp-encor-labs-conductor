# BGP Lab 06 — BGP Communities & Policy Control

## Table of Contents

1. [Concepts & Skills Covered](#1-concepts--skills-covered)
2. [Topology & Scenario](#2-topology--scenario)
3. [Hardware & Environment Specifications](#3-hardware--environment-specifications)
4. [Base Configuration](#4-base-configuration)
5. [Lab Challenge: Core Implementation](#5-lab-challenge-core-implementation)
6. [Verification & Analysis](#6-verification--analysis)
7. [Verification Cheatsheet](#7-verification-cheatsheet)
8. [Solutions (Spoiler Alert!)](#8-solutions-spoiler-alert)
9. [Troubleshooting Scenarios](#9-troubleshooting-scenarios)
10. [Lab Completion Checklist](#10-lab-completion-checklist)

---

## 1. Concepts & Skills Covered

This lab addresses the following CCNP ENCOR 350-401 exam blueprint bullets:

- **3.2.c** — Configure and verify eBGP between directly connected neighbors (best path selection algorithm and neighbor relationships)
- **3.2.d** — Describe policy-based routing

**BGP Community topics explored:**

- Standard BGP community format (`AA:NN`) and how communities are carried as a path attribute
- Well-known communities: `no-export`, `no-advertise`, and `local-AS` — and how each restricts re-advertisement
- Community propagation with `send-community` (the attribute is stripped by default without this command)
- Community lists (`ip community-list`) for matching communities in route-maps
- Building multi-stage route-maps that both set communities and manipulate other attributes (local-preference, AS-path)
- Using communities to implement provider-customer policy at AS boundaries

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp (AS 65001) is dual-homed to two ISPs: ISP-A (AS 65002) and ISP-B (AS 65003). A new downstream customer — DataStream Ltd (AS 65004, R5) — has contracted ISP-B for connectivity.

The network team must implement a community-based policy framework:

1. Tag outbound enterprise prefixes so ISPs can apply their own policy based on Acme's intent
2. Prevent ISP-B's internal experimental prefix from leaking beyond DataStream
3. Allow DataStream to signal its preferred routes to ISP-B using community tags
4. Prevent ISP-A's internal prefix from leaving the enterprise AS boundary

### ASCII Topology

```
         ┌──────────────────────────────────────┐
         │                 R1                   │
         │          (Enterprise Edge)           │
         │         Lo0: 172.16.1.1/32           │
         │              AS: 65001               │
         └───────┬──────────────┬──────────┬───┘
           Fa0/0 │        Fa1/0 │    Fa1/1 │
     10.1.14.1/30│  10.1.12.1/30│          │10.1.13.1/30
                 │              │          │
     10.1.14.2/30│  10.1.12.2/30│          │10.1.13.2/30
           Fa0/0 │        Fa0/0 │    Fa1/0 │
    ┌────────────┴──┐    ┌──────┴──────────┴───────────────────┐
    │      R4       │    │      R2          │      R3           │
    │  (Enterprise  │    │   (ISP-A)        │   (ISP-B)        │
    │   Internal)   │    │  AS: 65002       │  AS: 65003        │
    │   AS: 65001   │    │Lo0:172.16.2.2/32 │Lo0:172.16.3.3/32 │
    │Lo0:172.16.4.4 │    └──────┬───────────┴───────────┬──────┘
    └───────────────┘      Fa1/0│10.1.23.1  10.1.23.2   │Fa0/0
                                └───── 10.1.23.0/30 ─────┘
                                                          │Fa1/1
                                               10.1.35.1/30│
                                                           │
                                               10.1.35.2/30│
                                                     Fa0/0 │
                                          ┌────────────────┴───────┐
                                          │           R5            │
                                          │  (Downstream Customer)  │
                                          │       AS: 65004         │
                                          │  Lo0: 172.16.5.5/32     │
                                          └─────────────────────────┘
```

**BGP Session Summary:**

| Session | Type | Peers |
|---------|------|-------|
| R1 — R2 | eBGP | 10.1.12.1 ↔ 10.1.12.2 |
| R1 — R3 | eBGP | 10.1.13.1 ↔ 10.1.13.2 |
| R1 — R4 | iBGP | Lo0 ↔ Lo0 (65001) |
| R2 — R3 | eBGP | 10.1.23.1 ↔ 10.1.23.2 |
| R3 — R5 | eBGP | 10.1.35.1 ↔ 10.1.35.2 |

---

## 3. Hardware & Environment Specifications

### Device Inventory

| Device | Platform | Role | AS | Loopback0 |
|--------|----------|------|----|-----------|
| R1 | c7200 | Enterprise Edge | 65001 | 172.16.1.1/32 |
| R2 | c7200 | ISP-A | 65002 | 172.16.2.2/32 |
| R3 | c7200 | ISP-B | 65003 | 172.16.3.3/32 |
| R4 | c3725 | Enterprise Internal | 65001 | 172.16.4.4/32 |
| R5 | c3725 | Downstream Customer | 65004 | 172.16.5.5/32 |

### Cabling Table

| Link | Source | Target | Subnet | Purpose |
|------|--------|--------|--------|---------|
| L1 | R1:Fa1/0 | R2:Fa0/0 | 10.1.12.0/30 | Enterprise to ISP-A (eBGP) |
| L2 | R2:Fa1/0 | R3:Fa0/0 | 10.1.23.0/30 | ISP-A to ISP-B (eBGP) |
| L3 | R1:Fa1/1 | R3:Fa1/0 | 10.1.13.0/30 | Enterprise to ISP-B (eBGP) |
| L4 | R1:Fa0/0 | R4:Fa0/0 | 10.1.14.0/30 | Enterprise Edge to Internal (iBGP) |
| L5 | R3:Fa1/1 | R5:Fa0/0 | 10.1.35.0/30 | ISP-B to Downstream Customer (eBGP) |

### Console Access Table

| Device | Console Port | Connection Command |
|--------|-------------|-------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |

---

## 4. Base Configuration

Run `python3 setup_lab.py` to push the initial configurations to all five routers.

### What IS pre-loaded

- Hostnames and interface IP addresses on all devices
- OSPF process on R1 and R4 (loopback and link between them — required for iBGP next-hop reachability)
- BGP process and neighbor statements on R1, R2, R3, and R4 (from Lab 05 solutions)
- AS-path access-lists and prefix-lists on R1 (from Lab 05)
- Existing route-maps from Lab 05: `SET-LP-200-ISP-A`, `POLICY-ISP-B-IN`, `PREPEND-TO-ISP-B`

### What is NOT pre-loaded (student must configure)

- Community tagging route-maps on R1 (outbound to ISP-A and ISP-B)
- `send-community` activation on R1's eBGP sessions
- Well-known `local-AS` community tagging on R1 for the ISP-A internal prefix
- BGP process and neighbor relationship on R5 (R5 is new — no BGP pre-configured)
- Community tagging route-map on R5 (outbound to R3)
- `send-community` on R5's eBGP session
- Community-list and community-based route-maps on R3 (inbound from R5, outbound to R5)
- `no-export` community tagging on R3 for the ISP-B experimental prefix

---

## 5. Lab Challenge: Core Implementation

### Task 1: Tag Enterprise Prefixes with Standard Communities

On R1, implement outbound community tagging so downstream ISPs can apply their own policy based on Acme's intent:

- Create a new outbound route-map for the R2 (ISP-A) neighbor. For enterprise prefixes matching the `ENTERPRISE-PREFIXES` prefix-list, set a standard community value of `65001:100`. All other prefixes pass through without a community tag.
- Modify the existing outbound route-map applied to the R3 (ISP-B) neighbor. For enterprise prefixes, set community `65001:200` in addition to the existing AS-path prepend. All other prefixes pass through unchanged.
- Enable community propagation on both eBGP sessions (R2 and R3). Without this, the community attribute is stripped before the UPDATE message leaves R1.

**Verification:** `show ip bgp 192.168.1.0` on R2 should show `Community: 65001:100` in the prefix detail. On R3, the same prefix should show `Community: 65001:200`.

---

### Task 2: Apply the no-export Well-Known Community on R3

ISP-B's 203.0.115.0/24 prefix is an internal experimental range not intended for re-advertisement. Configure R3 to enforce this:

- Create an outbound route-map on R3 applied to the R5 neighbor. For the 203.0.115.0/24 prefix, set the well-known `no-export` community before advertising it to R5.
- All other prefixes must still be advertised to R5 without modification.
- Enable community propagation so R5 receives the community attribute.

**Verification:** `show ip bgp 203.0.115.0` on R5 should show `Community: no-export`. Confirm that R5 cannot re-advertise this prefix externally (it will not appear in any eBGP UPDATE sent by R5).

---

### Task 3: Community-Based Inbound Policy on R3 from R5

DataStream (R5, AS 65004) signals preferred routes using community tags. Configure both ends of the R3–R5 session:

- On R5, configure a BGP process with AS 65004 and establish an eBGP session to R3 (10.1.35.1). Advertise R5's loopback and customer prefixes (10.4.1.0/24 and 10.4.2.0/24).
- On R5, create an outbound route-map that sets community `65004:100` on the customer prefixes (10.4.1.0/24 and 10.4.2.0/24). Enable community propagation to R3.
- On R3, create a community-list named `R5-PREFERRED` that matches community value `65004:100`.
- On R3, create an inbound route-map for the R5 neighbor. Routes matching `R5-PREFERRED` receive a local-preference of 180. All other routes pass through.
- Enable soft-reconfiguration inbound on R3's R5 session so policy changes can be applied without hard resets.

**Verification:** `show ip bgp 10.4.1.0` on R3 should show `Local preference: 180` and `Community: 65004:100`. The BGP table on R3 should show R5's routes as best (highest local-pref relative to any other path).

---

### Task 4: Tag ISP-A Internal Prefix with local-AS Community

ISP-A advertises 198.51.102.0/24 — an internal range that should not leave AS 65001. Configure R1 to enforce this at the eBGP boundary:

- Modify the existing inbound route-map on R1 for the R2 (ISP-A) neighbor. Add a new sequence that matches 198.51.102.0/24 (using a new prefix-list named `ISP-A-INTERNAL`) and sets the well-known `local-AS` community, in addition to setting local-preference 200.
- The existing sequence that sets local-preference 200 for all other ISP-A routes must continue to function — add it as a subsequent sequence in the same route-map.
- Perform a soft inbound reset for the R2 session so the updated policy takes effect immediately without dropping the session.

**Verification:** `show ip bgp 198.51.102.0` on R1 should show `Community: local-AS` and `Local preference: 200`. Confirm the prefix does not appear in R3's or R5's BGP table (the local-AS community prevents eBGP re-advertisement).

---

## 6. Verification & Analysis

### Task 1 Verification — Community Tags Leaving R1

```
R2# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24, version 8
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  Advertised to update-groups:
     1
  65001
    10.1.12.1 from 10.1.12.1 (172.16.1.1)
      Origin IGP, metric 0, localpref 100, valid, external, best
      Community: 65001:100                       ! ← community tag must be present
      Last update: 00:01:22 ago
```

```
R3# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24, version 6
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001
    10.1.13.1 from 10.1.13.1 (172.16.1.1)
      Origin IGP, metric 0, localpref 100, valid, external, best
      Community: 65001:200                       ! ← ISP-B receives the 200 tag
      AS-Path: 65001 65001 65001 65001           ! ← three prepends still present
      Last update: 00:01:18 ago
```

### Task 2 Verification — no-export on R5

```
R5# show ip bgp 203.0.115.0
BGP routing table entry for 203.0.115.0/24, version 4
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65003
    10.1.35.1 from 10.1.35.1 (172.16.3.3)
      Origin IGP, metric 0, localpref 100, valid, external, best
      Community: no-export                       ! ← well-known community present
      Last update: 00:00:55 ago
```

```
R5# show ip bgp neighbors 10.1.35.1 advertised-routes | include 203.0.115
                                                           ! ← must return empty
```

### Task 3 Verification — R5 Community Received and Matched on R3

```
R5# show ip bgp neighbors 10.1.35.1 advertised-routes
   Network          Next Hop            Metric LocPrf Weight Path
*> 10.4.1.0/24      0.0.0.0                  0         32768 i
*> 10.4.2.0/24      0.0.0.0                  0         32768 i   ! ← both prefixes advertised
*> 172.16.5.5/32    0.0.0.0                  0         32768 i

R3# show ip bgp 10.4.1.0
BGP routing table entry for 10.4.1.0/24, version 9
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65004
    10.1.35.2 from 10.1.35.2 (172.16.5.5)
      Origin IGP, metric 0, localpref 180, valid, external, best   ! ← LP 180 applied
      Community: 65004:100                                          ! ← community received and matched
      Last update: 00:01:05 ago
```

### Task 4 Verification — local-AS Community Blocking Re-Advertisement

```
R1# show ip bgp 198.51.102.0
BGP routing table entry for 198.51.102.0/24, version 11
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65002
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, metric 0, localpref 200, valid, external, best
      Community: local-AS                        ! ← well-known community present
      Last update: 00:00:42 ago

R3# show ip bgp 198.51.102.0
% Network not in table                           ! ← local-AS prevents eBGP re-advertisement
```

---

## 7. Verification Cheatsheet

### BGP Community Configuration

```
ip community-list standard <name> permit <AA:NN | well-known>

route-map <name> permit <seq>
 match community <community-list-name>
 set community <AA:NN | no-export | no-advertise | local-AS>

router bgp <ASN>
 neighbor <ip> send-community
```

| Command | Purpose |
|---------|---------|
| `ip community-list standard NAME permit AA:NN` | Define a named community match list |
| `set community AA:NN` | Tag routes with a standard community value |
| `set community no-export` | Prevent re-advertisement beyond the receiving AS |
| `set community no-advertise` | Prevent re-advertisement to any BGP peer |
| `set community local-AS` | Prevent re-advertisement to eBGP peers outside sub-AS |
| `neighbor X send-community` | Required to carry the COMMUNITY attribute in UPDATEs |
| `set community AA:NN additive` | Add community to existing tags (does not overwrite) |

> **Exam tip:** `send-community` is per-neighbor and opt-in. Without it, IOS strips the COMMUNITY attribute from every outgoing UPDATE regardless of route-map `set community` statements.

### Community Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip bgp <prefix>` | `Community:` line in prefix detail — value and format |
| `show ip bgp community <AA:NN>` | All prefixes carrying a specific community value |
| `show ip bgp community no-export` | All prefixes tagged with the no-export well-known community |
| `show ip bgp neighbors <ip> advertised-routes` | Prefixes actually sent to the neighbor after outbound policy |
| `show ip bgp neighbors <ip> received-routes` | Raw prefixes received before inbound policy (requires soft-reconfig) |
| `show ip community-list` | Active community-list definitions and sequence numbers |
| `show route-map` | Route-map sequences, match/set operations, and hit counters |

### Well-Known Community Quick Reference

| Community | Scope | Effect |
|-----------|-------|--------|
| `no-export` | AS boundary | Not advertised to any eBGP peer (stays within the AS or confederation) |
| `no-advertise` | All peers | Not advertised to any BGP peer (iBGP or eBGP) |
| `local-AS` | Sub-AS / confederation | Not advertised outside the local sub-AS (eBGP blocked) |
| `internet` | All peers | Default — no restriction, advertised freely (rarely configured explicitly) |

### Community Format Reference

| Format | Example | Notes |
|--------|---------|-------|
| Standard `AA:NN` | `65001:100` | AA = your ASN, NN = value (0–65535 each) |
| Decimal | `4259905636` | `65001 × 65536 + 100` — legacy display format |
| `ip bgp-community new-format` | (global command) | Switches display from decimal to `AA:NN` format |

> **Exam tip:** Always configure `ip bgp-community new-format` globally before working with communities — otherwise IOS displays the community as a large decimal number, which is difficult to read and verify.

### Common BGP Community Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Community not visible on receiving router | `send-community` missing on the sending router's neighbor statement |
| Community visible but route-map not matching | Community-list name mismatch in the `match community` statement |
| `no-export` prefix still seen at eBGP peer | Route-map not applied outbound, or `send-community` missing |
| `local-AS` prefix re-advertised to eBGP | Community set inbound but route-map sequence order wrong (permit before set) |
| Community set but disappears after iBGP | iBGP peer missing `send-community` — attribute stripped at each hop |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: Tag Enterprise Prefixes with Standard Communities

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! Outbound to ISP-A — set community 65001:100 on enterprise prefixes
route-map TAG-ISP-A-OUT permit 10
 match ip address prefix-list ENTERPRISE-PREFIXES
 set community 65001:100
!
route-map TAG-ISP-A-OUT permit 20
!
! Outbound to ISP-B — set community 65001:200 and prepend (replaces PREPEND-TO-ISP-B)
route-map TAG-AND-PREPEND-ISP-B permit 10
 match ip address prefix-list ENTERPRISE-PREFIXES
 set community 65001:200
 set as-path prepend 65001 65001 65001
!
route-map TAG-AND-PREPEND-ISP-B permit 20
!
router bgp 65001
 neighbor 10.1.12.2 send-community
 neighbor 10.1.12.2 route-map TAG-ISP-A-OUT out
 neighbor 10.1.13.2 send-community
 no neighbor 10.1.13.2 route-map PREPEND-TO-ISP-B out
 neighbor 10.1.13.2 route-map TAG-AND-PREPEND-ISP-B out
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
R2# show ip bgp 192.168.1.0
R3# show ip bgp 192.168.1.0
R1# show route-map TAG-ISP-A-OUT
R1# show route-map TAG-AND-PREPEND-ISP-B
```
</details>

---

### Task 2: Apply no-export on R3 for ISP-B Internal Prefix

<details>
<summary>Click to view R3 Configuration</summary>

```bash
ip prefix-list ISP-B-INTERNAL seq 10 permit 203.0.115.0/24
!
route-map POLICY-TO-R5 permit 10
 match ip address prefix-list ISP-B-INTERNAL
 set community no-export
!
route-map POLICY-TO-R5 permit 20
!
router bgp 65003
 neighbor 10.1.35.2 remote-as 65004
 neighbor 10.1.35.2 send-community
 neighbor 10.1.35.2 route-map POLICY-TO-R5 out
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
R5# show ip bgp 203.0.115.0
R5# show ip bgp neighbors 10.1.35.1 advertised-routes
R3# show route-map POLICY-TO-R5
```
</details>

---

### Task 3: Community-Based Inbound Policy on R3 from R5

<details>
<summary>Click to view R5 Configuration</summary>

```bash
ip prefix-list R5-CUSTOMER-ROUTES seq 10 permit 10.4.1.0/24
ip prefix-list R5-CUSTOMER-ROUTES seq 20 permit 10.4.2.0/24
!
route-map SET-COMM-OUT permit 10
 match ip address prefix-list R5-CUSTOMER-ROUTES
 set community 65004:100
!
route-map SET-COMM-OUT permit 20
!
router bgp 65004
 bgp router-id 172.16.5.5
 neighbor 10.1.35.1 remote-as 65003
 neighbor 10.1.35.1 soft-reconfiguration inbound
 neighbor 10.1.35.1 send-community
 neighbor 10.1.35.1 route-map SET-COMM-OUT out
 !
 network 172.16.5.5 mask 255.255.255.255
 network 10.4.1.0 mask 255.255.255.0
 network 10.4.2.0 mask 255.255.255.0
```
</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
ip community-list standard R5-PREFERRED permit 65004:100
!
route-map POLICY-FROM-R5 permit 10
 match community R5-PREFERRED
 set local-preference 180
!
route-map POLICY-FROM-R5 permit 20
!
router bgp 65003
 neighbor 10.1.35.2 soft-reconfiguration inbound
 neighbor 10.1.35.2 route-map POLICY-FROM-R5 in
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
R5# show ip bgp neighbors 10.1.35.1 advertised-routes
R3# show ip bgp 10.4.1.0
R3# show ip bgp 10.4.2.0
R3# show ip community-list
```
</details>

---

### Task 4: Tag ISP-A Internal Prefix with local-AS Community

<details>
<summary>Click to view R1 Configuration</summary>

```bash
ip prefix-list ISP-A-INTERNAL seq 10 permit 198.51.102.0/24
!
! Rebuild SET-LP-200-ISP-A with new sequence at top
no route-map SET-LP-200-ISP-A
route-map SET-LP-200-ISP-A permit 10
 match ip address prefix-list ISP-A-INTERNAL
 set local-preference 200
 set community local-AS
!
route-map SET-LP-200-ISP-A permit 15
 match as-path 1
 set local-preference 200
!
route-map SET-LP-200-ISP-A permit 20
!
! Soft reset to apply without dropping session
clear ip bgp 10.1.12.2 soft in
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
R1# show ip bgp 198.51.102.0
R3# show ip bgp 198.51.102.0
R4# show ip bgp 198.51.102.0
R1# show route-map SET-LP-200-ISP-A
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
python3 scripts/fault-injection/inject_scenario_02.py  # Ticket 2
python3 scripts/fault-injection/inject_scenario_03.py  # Ticket 3
python3 scripts/fault-injection/apply_solution.py      # restore
```

---

### Ticket 1 — R5's Routes Arrive at R3 but Local Preference is 100, Not 180

The operations team expects R3 to prefer R5's customer routes with a local-preference of 180 based on the community signal agreed upon with DataStream. After a recent config change, R3 is showing LocPrf 100 for those routes instead.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip bgp 10.4.1.0` on R3 shows `localpref 180` and `Community: 65004:100`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Check R3's BGP table for R5's routes: `R3# show ip bgp 10.4.1.0`
   - Confirm the Community attribute is present: `Community: 65004:100`
   - Note the local-preference value — it should be 180 but is 100

2. Check whether the inbound route-map is applied to the R5 neighbor:
   `R3# show bgp neighbors 10.1.35.2 | include route-map`
   - If no inbound route-map is listed, the policy is missing or detached

3. Check whether the community-list still exists:
   `R3# show ip community-list`
   - If the list is absent or has a different name, the `match community` in the route-map will not match any routes

4. Verify the route-map definition:
   `R3# show route-map POLICY-FROM-R5`
   - Check that sequence 10 matches `R5-PREFERRED` and sets `local-preference 180`

5. Root cause: The community-list `R5-PREFERRED` has been removed or renamed, causing the `match community` clause to match nothing — routes fall through to sequence 20 (permit without action), so local-pref remains at the BGP default of 100.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
R3(config)# ip community-list standard R5-PREFERRED permit 65004:100
R3# clear ip bgp 10.1.35.2 soft in
```

Verify: `R3# show ip bgp 10.4.1.0` — local-pref must return to 180.
</details>

---

### Ticket 2 — R2 Is Receiving Enterprise Prefixes Without a Community Tag

The ISP-A operations team reports that Acme's prefixes (192.168.x.x) are arriving at R2 without the expected `65001:100` community tag. Their policy automation engine relies on this tag to apply QoS and route-preference logic.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip bgp 192.168.1.0` on R2 shows `Community: 65001:100`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R2, examine the community attribute on received prefixes:
   `R2# show ip bgp 192.168.1.0`
   - If the `Community:` line is absent or shows no value, the tag is not arriving

2. On R1, check whether the outbound route-map is applied to R2's neighbor:
   `R1# show bgp neighbors 10.1.12.2 | include route-map`
   - The outbound route-map `TAG-ISP-A-OUT` should appear — if missing, the map was removed

3. Verify the route-map still exists:
   `R1# show route-map TAG-ISP-A-OUT`

4. Check send-community status on the R2 neighbor:
   `R1# show bgp neighbors 10.1.12.2 | include community`
   - `Community attribute sent to this neighbor` must appear — if absent, `send-community` is missing

5. Root cause: The outbound route-map `TAG-ISP-A-OUT` has been detached from the R2 neighbor statement on R1.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
R1(config)# router bgp 65001
R1(config-router)# neighbor 10.1.12.2 route-map TAG-ISP-A-OUT out
R1# clear ip bgp 10.1.12.2 soft out
```

Verify: `R2# show ip bgp 192.168.1.0` — `Community: 65001:100` must appear.
</details>

---

### Ticket 3 — DataStream Reports Receiving an ISP-B Internal Prefix Marked Confidential

DataStream (R5) is receiving the 203.0.115.0/24 prefix from ISP-B without any community tag. The service contract requires ISP-B to tag this prefix with `no-export` so DataStream cannot re-advertise it beyond AS 65004. DataStream is now leaking the prefix to an upstream peer.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip bgp 203.0.115.0` on R5 shows `Community: no-export`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R5, check the community attribute on the 203.0.115.0/24 prefix:
   `R5# show ip bgp 203.0.115.0`
   - The `Community:` line should show `no-export` — if absent, the tag is not arriving

2. On R3, verify the outbound route-map to R5 is applied:
   `R3# show bgp neighbors 10.1.35.2 | include route-map`
   - `POLICY-TO-R5` should appear in the outbound direction

3. Verify the route-map definition:
   `R3# show route-map POLICY-TO-R5`
   - Sequence 10 should match `ISP-B-INTERNAL` and set `community no-export`

4. Check send-community on R3's R5 neighbor:
   `R3# show bgp neighbors 10.1.35.2 | include community`
   - If `send-community` is absent, the community attribute is stripped before the UPDATE leaves R3

5. Root cause: The outbound route-map `POLICY-TO-R5` has been detached from R3's R5 neighbor statement, so 203.0.115.0/24 is advertised without the `no-export` tag.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
R3(config)# router bgp 65003
R3(config-router)# neighbor 10.1.35.2 route-map POLICY-TO-R5 out
R3# clear ip bgp 10.1.35.2 soft out
```

Verify: `R5# show ip bgp 203.0.115.0` — `Community: no-export` must appear.
</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] R2 receives 192.168.x.x prefixes from R1 with community `65001:100`
- [ ] R3 receives 192.168.x.x prefixes from R1 with community `65001:200` and AS-path prepend
- [ ] R3 advertises 203.0.115.0/24 to R5 with `no-export` community
- [ ] R5 has a BGP session with R3 in Established state
- [ ] R5 advertises 10.4.1.0/24 and 10.4.2.0/24 with community `65004:100`
- [ ] R3 shows local-preference 180 for R5's customer prefixes
- [ ] R1 shows 198.51.102.0/24 with `local-AS` community and local-preference 200
- [ ] 198.51.102.0/24 does not appear in R3's or R5's BGP table

### Troubleshooting

- [ ] Ticket 1 resolved: R3 correctly applies local-preference 180 to R5's tagged routes
- [ ] Ticket 2 resolved: R2 receives enterprise prefixes with `65001:100` community
- [ ] Ticket 3 resolved: R5 receives 203.0.115.0/24 with `no-export` community
