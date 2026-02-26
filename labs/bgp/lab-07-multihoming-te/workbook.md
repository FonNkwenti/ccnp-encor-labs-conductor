# BGP Lab 07: Multihoming & Traffic Engineering

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

### CCNP ENCOR Exam Blueprint (350-401)

| Exam Topic | Description |
|------------|-------------|
| **3.2.c** | Configure and verify eBGP between directly connected neighbors — best path selection algorithm and neighbor relationships |
| **3.2.d** | Describe policy-based routing |
| **1.1.b** | High availability techniques such as redundancy, FHRP, and SSO |

### Skills Developed

- **Dual-Homed eBGP Design** — dual ISP attachment for high availability, failover verification
- **Outbound Traffic Engineering** — per-prefix Local Preference to control egress ISP selection
- **Inbound Traffic Engineering** — AS-Path prepending to influence which ISP internet hosts use to reach enterprise prefixes
- **MED (Multi-Exit Discriminator)** — signaling preferred entry points to external ISPs
- **Conditional Default Route Origination** — generating a default route for internal peers only when upstream reachability is confirmed
- **BGP Policy Interaction** — understanding how route-maps, prefix-lists, and attribute manipulation combine to implement traffic engineering

---

## 2. Topology & Scenario

### Business Context

AcmeCorp (AS 65001) runs a dual-homed enterprise WAN connecting to two ISPs:
- **ISP-A (AS 65002)** — primary upstream, preferred for general outbound traffic
- **ISP-B (AS 65003)** — secondary upstream, used for specific destination prefixes and as failover

The network operations team has received the following requirements:

1. **HA Validation** — confirm automatic failover when either ISP link fails
2. **Outbound TE** — route traffic to ISP-A prefixes (198.51.100.x) via ISP-A; route traffic to ISP-B prefixes (203.0.113.x) via ISP-B
3. **Inbound TE** — steer return traffic for 192.168.1.0/24 to enter via ISP-B; steer return traffic for 192.168.2.0/24 to enter via ISP-A
4. **MED Signaling** — advertise a lower MED for 192.168.3.0/24 via ISP-A so ISP-A is the preferred entry for that prefix
5. **Conditional Default** — propagate a default route to R4 (Enterprise Internal) only while ISP connectivity is verified

### ASCII Topology

```
        ┌─────────────────────┐    10.1.23.0/30    ┌─────────────────────┐
        │        R2           │  Fa1/0      Fa0/0  │        R3           │
        │      (ISP-A)        ├────────────────────┤      (ISP-B)        │
        │    AS 65002         │     .1        .2   │    AS 65003         │
        │  Lo0: 172.16.2.2    │                    │  Lo0: 172.16.3.3    │
        └──────────┬──────────┘                    └──────┬──────────────┘
          Fa0/0    │ .2                          .2 │ Fa1/0          │ Fa1/1 .1
     10.1.12.0/30  │                  10.1.13.0/30  │           10.1.35.0/30
          Fa1/0    │ .1                          .1 │ Fa1/1          │ Fa0/0 .2
                   └──────────────┐  ┌──────────────┘               │
                                  │  │                               │
                         ┌────────┴──┴─────────┐          ┌─────────┴──────────┐
                         │          R1          │          │        R5          │
                         │  (Enterprise Edge)   │          │  (Downstream Cust) │
                         │     AS 65001         │          │    AS 65004        │
                         │  Lo0: 172.16.1.1     │          │  Lo0: 172.16.5.5   │
                         └──────────┬───────────┘          └────────────────────┘
                           Fa0/0    │ .1
                       10.1.14.0/30 │
                           Fa0/0    │ .2
                         ┌──────────┴───────────┐
                         │          R4          │
                         │  (Enterprise Int.)   │
                         │     AS 65001         │
                         │  Lo0: 172.16.4.4     │
                         └──────────────────────┘
```

### IP Addressing Summary

| Device | Interface | IP Address | Description |
|--------|-----------|------------|-------------|
| R1 | Fa0/0 | 10.1.14.1/30 | Link to R4 |
| R1 | Fa1/0 | 10.1.12.1/30 | Link to R2 (ISP-A) |
| R1 | Fa1/1 | 10.1.13.1/30 | Link to R3 (ISP-B) |
| R1 | Lo0 | 172.16.1.1/32 | Router ID / iBGP source |
| R1 | Lo1–Lo3 | 192.168.1–3.1/24 | Enterprise prefixes |
| R2 | Fa0/0 | 10.1.12.2/30 | Link to R1 |
| R2 | Fa1/0 | 10.1.23.1/30 | Link to R3 |
| R2 | Lo0 | 172.16.2.2/32 | Router ID |
| R2 | Lo1–Lo3 | 198.51.100–102.1/24 | ISP-A prefixes |
| R3 | Fa0/0 | 10.1.23.2/30 | Link to R2 |
| R3 | Fa1/0 | 10.1.13.2/30 | Link to R1 |
| R3 | Fa1/1 | 10.1.35.1/30 | Link to R5 |
| R3 | Lo0 | 172.16.3.3/32 | Router ID |
| R3 | Lo1–Lo3 | 203.0.113–115.1/24 | ISP-B prefixes |
| R4 | Fa0/0 | 10.1.14.2/30 | Link to R1 |
| R4 | Lo0 | 172.16.4.4/32 | Router ID / iBGP source |
| R5 | Fa0/0 | 10.1.35.2/30 | Link to R3 |
| R5 | Lo0 | 172.16.5.5/32 | Router ID |
| R5 | Lo1–Lo2 | 10.4.10–20.1/24 | Customer prefixes |

---

## 3. Hardware & Environment Specifications

### Device Specifications

| Device | Platform | Role | AS | Console Port |
|--------|----------|------|----|--------------|
| R1 | c7200 | Enterprise Edge | 65001 | 5001 |
| R2 | c7200 | ISP-A | 65002 | 5002 |
| R3 | c7200 | ISP-B | 65003 | 5003 |
| R4 | c3725 | Enterprise Internal | 65001 | 5004 |
| R5 | c3725 | Downstream Customer | 65004 | 5005 |

### Console Access Table

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |

### Cabling Summary

| Link ID | Source | Destination | Subnet | Purpose |
|---------|--------|-------------|--------|---------|
| L1 | R1:Fa1/0 | R2:Fa0/0 | 10.1.12.0/30 | Enterprise to ISP-A (eBGP) |
| L2 | R1:Fa1/1 | R3:Fa1/0 | 10.1.13.0/30 | Enterprise to ISP-B (eBGP) |
| L3 | R2:Fa1/0 | R3:Fa0/0 | 10.1.23.0/30 | ISP-A to ISP-B (eBGP) |
| L4 | R1:Fa0/0 | R4:Fa0/0 | 10.1.14.0/30 | Enterprise Edge to Internal (iBGP) |
| L5 | R3:Fa1/1 | R5:Fa0/0 | 10.1.35.0/30 | ISP-B to Downstream Customer (eBGP) |

---

## 4. Base Configuration

### What Is Pre-Configured

The initial configurations carry forward all lab-06 (BGP Communities & Policy Control) solutions:

- IP addressing on all interfaces (loopbacks, point-to-point links)
- OSPF process between R1 and R4 for internal loopback reachability
- eBGP sessions: R1–R2, R1–R3, R2–R3, R3–R5
- iBGP session: R1–R4 (loopback-sourced, next-hop-self)
- BGP network statements advertising all enterprise and ISP prefixes
- Lab-06 community and route-map policies (as starting point to replace)
- Soft-reconfiguration inbound on all policy-relevant sessions

### What Is NOT Pre-Configured

Students must design and implement:

- Per-prefix Local Preference policy for outbound ISP selection
- Per-prefix AS-path prepending for inbound traffic engineering
- MED values on outbound advertisements for preferred entry signaling
- Conditional default route origination to R4

> **Note:** The lab-06 route-maps (community tagging, basic LP, AS-path prepend to ISP-B) must be replaced with the lab-07 traffic engineering policies.

---

## 5. Lab Challenge: Core Implementation

### Task 1: Dual-Homed eBGP Baseline Verification

- Confirm that both ISP sessions (R1–R2 and R1–R3) are established and actively exchanging prefixes.
- Verify that R1's BGP table contains paths for all ISP-A prefixes (198.51.100–102.0/24) and all ISP-B prefixes (203.0.113–115.0/24).
- Confirm that both ISPs have learned the enterprise prefixes (192.168.1–3.0/24).
- Simulate a link failure by administratively shutting R1's ISP-A interface and verify that all 198.51.100.x prefixes are still reachable via ISP-B (through R3's peering with R2). Re-enable the interface when done.

**Verification:** `show ip bgp summary` must show both ISP sessions in Established state. `show ip bgp 198.51.100.0` must show two paths (direct from R2 and via R3) when both links are up. After shutting the ISP-A interface, the prefix must still be reachable with the best path switching to the ISP-B path.

---

### Task 2: Per-Prefix Outbound Traffic Engineering

Design a Local Preference policy on R1 that controls which ISP is used for outbound traffic based on the destination prefix type:

- Routes received from ISP-A that belong to ISP-A's address space (198.51.100–102.0/24) should receive Local Preference 200. All other routes received from ISP-A should receive Local Preference 100.
- Routes received from ISP-B that belong to ISP-B's address space (203.0.113–115.0/24) should receive Local Preference 200. All other routes received from ISP-B should receive Local Preference 100.
- Apply these policies as inbound route-maps on each ISP eBGP session.
- Remove the lab-06 route-maps from both ISP neighbors and replace them with the new per-prefix LP policies.

**Verification:** `show ip bgp 198.51.100.0` must show the path via R2 as best with `localpref 200`. `show ip bgp 203.0.113.0` must show the path via R3 as best with `localpref 200`. Running `show ip bgp` should show ISP-A prefixes (198.x.x.x) with the R2 path marked `>` and ISP-B prefixes (203.x.x.x) with the R3 path marked `>`.

---

### Task 3: Per-Prefix Inbound Traffic Engineering via AS-Path Prepending

Design outbound route-maps on R1 to influence how internet hosts reach the enterprise prefixes:

- When advertising 192.168.1.0/24 to ISP-A (R2), prepend the AS number three additional times. This makes the AS-path longer via ISP-A, causing internet routers that compare paths from both ISPs to prefer the ISP-B path for inbound traffic to 192.168.1.0/24.
- When advertising 192.168.2.0/24 to ISP-B (R3), prepend the AS number three additional times. This makes internet routers prefer the ISP-A path for inbound traffic to 192.168.2.0/24.
- Advertise 192.168.3.0/24 to both ISPs without any prepending.
- Apply these policies as outbound route-maps on each ISP eBGP session.

**Verification:** On R2, `show ip bgp 192.168.1.0` must show an AS-path of `65001 65001 65001 65001` (original + 3 prepends). On R3, `show ip bgp 192.168.1.0` must show an AS-path of `65001` (no prepend). On R3, `show ip bgp 192.168.2.0` must show an AS-path of `65001 65001 65001 65001`. On R2, `show ip bgp 192.168.2.0` must show an AS-path of `65001`.

---

### Task 4: MED-Based Preferred Entry Signaling

Extend the outbound route-maps from Task 3 to set MED values, signaling ISP-A as the preferred entry point for 192.168.3.0/24:

- When advertising 192.168.3.0/24 to ISP-A, set MED to 10 (low value = preferred entry).
- When advertising 192.168.3.0/24 to ISP-B, set MED to 100 (high value = less preferred entry).
- The MED attribute is compared by BGP when paths to the same prefix arrive from routers in the same neighboring AS. Verify that R2 and R3 each see the expected MED value for this prefix.

**Verification:** On R2, `show ip bgp 192.168.3.0` must show `metric 10` in the path attributes. On R3, `show ip bgp 192.168.3.0` must show `metric 100`. The MED values are set by R1 in its outbound advertisements and are visible in the ISP routers' BGP tables.

---

### Task 5: Conditional Default Route Origination

Configure R1 to advertise a default route to R4 (iBGP) only when ISP connectivity is confirmed:

- Create a prefix-list that matches 198.51.100.0/24, which is a sentinel prefix that appears in R1's BGP table only when ISP-A is reachable.
- Create a route-map that permits only if the sentinel prefix is matched in the BGP table.
- Apply this route-map as a condition on R1's conditional default-originate command toward R4.
- Verify that R4 receives the default route when R1 has ISP-A prefixes. Verify that R4 does not receive a default route if you simulate the condition being absent by testing with a non-matching prefix-list.

**Verification:** On R4, `show ip bgp` must show `0.0.0.0/0` with next-hop 172.16.1.1 and `show ip route 0.0.0.0` must show `B* 0.0.0.0/0 [200/0] via 172.16.1.1`. On R1, `show ip bgp neighbors 172.16.4.4 advertised-routes` must include `0.0.0.0/0`.

---

## 6. Verification & Analysis

### Task 1: Dual-Homed eBGP Baseline

```
R1# show ip bgp summary
BGP router identifier 172.16.1.1, local AS number 65001
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.1.12.2       4 65002      45      42       18    0    0 00:15:22        4  ! ← ISP-A Up, 4 prefixes
10.1.13.2       4 65003      38      35       18    0    0 00:14:55        4  ! ← ISP-B Up, 4 prefixes
172.16.4.4      4 65001      22      20       18    0    0 00:12:10        3  ! ← R4 iBGP Up

R1# show ip bgp 198.51.100.0
BGP routing table entry for 198.51.100.0/24, version 5
Paths: (2 available, best #1, table Default-IP-Routing-Table)
  Advertised to update-groups:
     1
  65002                                                         ! ← AS-path: 1 hop via ISP-A
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, metric 0, localpref 100, valid, external, best  ! ← direct from R2, best
  65002                                                         ! ← same AS, learned via R3
    10.1.13.2 from 10.1.13.2 (172.16.3.3)
      Origin IGP, metric 0, localpref 100, valid, external         ! ← backup path via R3
```

### Task 2: Per-Prefix Outbound TE with Local Preference

```
R1# show ip bgp 198.51.100.0
...
  65002
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, localpref 200, valid, external, best  ! ← LP=200, ISP-A preferred for ISP-A prefixes
  65002
    10.1.13.2 from 10.1.13.2 (172.16.3.3)
      Origin IGP, localpref 100, valid, external        ! ← LP=100, ISP-B path not preferred

R1# show ip bgp 203.0.113.0
...
  65003
    10.1.13.2 from 10.1.13.2 (172.16.3.3)
      Origin IGP, localpref 200, valid, external, best  ! ← LP=200, ISP-B preferred for ISP-B prefixes
  65003
    10.1.12.2 from 10.1.12.2 (172.16.2.2)
      Origin IGP, localpref 100, valid, external        ! ← LP=100, ISP-A path not preferred

R1# show ip bgp | include Network|>
   Network          Next Hop            Metric LocPrf Weight Path
*> 172.16.1.1/32    0.0.0.0                  0         32768 i
*> 192.168.1.0      0.0.0.0                  0         32768 i
*> 192.168.2.0      0.0.0.0                  0         32768 i
*> 192.168.3.0      0.0.0.0                  0         32768 i
*> 198.51.100.0     10.1.12.2                0    200      0 65002 i  ! ← via R2, LP=200
*  198.51.100.0     10.1.13.2                0    100      0 65002 i  ! ← via R3, LP=100
*> 203.0.113.0      10.1.13.2                0    200      0 65003 i  ! ← via R3, LP=200
*  203.0.113.0      10.1.12.2                0    100      0 65003 i  ! ← via R2, LP=100
```

### Task 3: Per-Prefix Inbound TE with AS-Path Prepending

```
R2# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24, version 3
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001 65001 65001 65001                                    ! ← 4 AS hops (1 original + 3 prepends)
    10.1.12.1 from 10.1.12.1 (172.16.1.1)
      Origin IGP, metric 0, localpref 100, valid, external, best

R3# show ip bgp 192.168.1.0
BGP routing table entry for 192.168.1.0/24, version 3
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001                                                     ! ← 1 AS hop (no prepend to ISP-B)
    10.1.13.1 from 10.1.13.1 (172.16.1.1)
      Origin IGP, metric 0, localpref 100, valid, external, best  ! ← ISP-B is shorter path

R3# show ip bgp 192.168.2.0
BGP routing table entry for 192.168.2.0/24, version 4
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001 65001 65001 65001                                    ! ← 4 AS hops (3 prepends to ISP-B)
    10.1.13.1 from 10.1.13.1 (172.16.1.1)
      Origin IGP, metric 0, localpref 100, valid, external, best

R2# show ip bgp 192.168.2.0
BGP routing table entry for 192.168.2.0/24, version 4
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001                                                     ! ← 1 AS hop (no prepend to ISP-A)
    10.1.12.1 from 10.1.12.1 (172.16.1.1)
      Origin IGP, metric 0, localpref 100, valid, external, best  ! ← ISP-A is shorter path
```

### Task 4: MED Verification

```
R2# show ip bgp 192.168.3.0
BGP routing table entry for 192.168.3.0/24
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001
    10.1.12.1 from 10.1.12.1 (172.16.1.1)
      Origin IGP, metric 10, localpref 100, valid, external, best  ! ← MED=10, prefer ISP-A entry

R3# show ip bgp 192.168.3.0
BGP routing table entry for 192.168.3.0/24
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  65001
    10.1.13.1 from 10.1.13.1 (172.16.1.1)
      Origin IGP, metric 100, localpref 100, valid, external, best  ! ← MED=100, less preferred
```

### Task 5: Conditional Default Route

```
R1# show ip bgp neighbors 172.16.4.4 advertised-routes | include 0.0.0.0
*> 0.0.0.0/0          0.0.0.0                  0         32768 ?  ! ← default being advertised to R4

R4# show ip bgp
BGP table version is 8, local router ID is 172.16.4.4
   Network          Next Hop            Metric LocPrf Weight Path
*> 0.0.0.0          172.16.1.1               0    100      0 ?   ! ← default received from R1

R4# show ip route 0.0.0.0
B*   0.0.0.0/0 [200/0] via 172.16.1.1, 00:08:45  ! ← BGP default route installed, iBGP AD=200
```

---

## 7. Verification Cheatsheet

### Local Preference (Outbound TE)

```
route-map <NAME> permit 10
 match ip address prefix-list <PL-NAME>
 set local-preference <value>
route-map <NAME> permit 20
neighbor <ip> route-map <NAME> in
```

| Command | Purpose |
|---------|---------|
| `show ip bgp <prefix>` | Show all paths and LP value for a prefix |
| `show ip bgp` | Full BGP table — `>` marks best path, `LocPrf` column shows LP |
| `clear ip bgp <neighbor> soft in` | Reapply inbound policy without resetting session |
| `show ip bgp neighbors <ip> received-routes` | Routes received from neighbor (requires soft-reconfig) |

> **Exam tip:** Local Preference is an iBGP attribute — it is NOT carried across AS boundaries. It is the #1 tiebreaker after Weight (which is Cisco-proprietary and local only). Higher LP wins.

### AS-Path Prepending (Inbound TE)

```
route-map <NAME> permit 10
 match ip address prefix-list <PL-NAME>
 set as-path prepend <own-ASN> [<own-ASN> ...]
route-map <NAME> permit 20
neighbor <ip> route-map <NAME> out
```

| Command | Purpose |
|---------|---------|
| `show ip bgp <prefix>` on ISP router | Verify AS-path length received from enterprise |
| `show ip bgp neighbors <ip> advertised-routes` | Confirm what R1 is actually sending |
| `clear ip bgp <neighbor> soft out` | Re-advertise outbound after policy change |

> **Exam tip:** AS-path prepending only influences inbound traffic. Always prepend your OWN AS number. Prepending third-party AS numbers is rejected by many ISPs and considered a misconfiguration.

### MED (Multi-Exit Discriminator)

```
route-map <NAME> permit 10
 match ip address prefix-list <PL-NAME>
 set metric <value>          ! "metric" = MED in BGP context
route-map <NAME> permit 20
neighbor <ip> route-map <NAME> out
```

| Command | Purpose |
|---------|---------|
| `show ip bgp <prefix>` | Shows `metric` field — that is the MED value |
| `show ip bgp neighbors <ip> advertised-routes` | Verify MED is set in outbound advertisement |

> **Exam tip:** MED is only compared when multiple paths arrive from routers in the SAME neighboring AS. Lower MED wins. By default MED is not propagated across AS boundaries (it resets to 0 on eBGP handoff).

### Conditional Default Route Origination

```
ip prefix-list <SENTINEL> seq 10 permit <upstream-prefix>
route-map <CHECK> permit 10
 match ip address prefix-list <SENTINEL>
neighbor <iBGP-peer> default-originate route-map <CHECK>
```

| Command | Purpose |
|---------|---------|
| `show ip bgp neighbors <ip> advertised-routes` | Verify default is being sent (or not sent) |
| `show ip bgp` on R4 | Confirm `0.0.0.0/0` appears in BGP table |
| `show ip route 0.0.0.0` on R4 | Verify default installed in routing table |

> **Exam tip:** `default-originate` without a route-map always sends a default, even if 0.0.0.0/0 is not in the routing table. Adding a `route-map` makes the default conditional on a prefix match in the BGP table.

### BGP Session Management

```
clear ip bgp <neighbor-ip> soft in    ! Reapply inbound policy
clear ip bgp <neighbor-ip> soft out   ! Re-advertise outbound
clear ip bgp * soft                   ! Reset all sessions softly
```

| Command | What to Look For |
|---------|-----------------|
| `show ip bgp summary` | All sessions, state, prefix count |
| `show ip bgp neighbors <ip>` | Detailed session state and applied policy |
| `show ip bgp neighbors <ip> advertised-routes` | Outbound RIB for that neighbor |
| `show ip bgp neighbors <ip> received-routes` | Inbound RIB (requires soft-reconfig inbound) |
| `show ip bgp regexp <ASN>` | Filter BGP table by AS-path regex |
| `show ip bgp community <community>` | Filter by community value |

### Common BGP TE Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| LP policy not taking effect | Forgot `clear ip bgp soft in` after adding route-map |
| AS-path prepend not seen on ISP | Outbound route-map not applied (`neighbor X route-map OUT out`) |
| MED not visible on ISP router | MED is set correctly but ISP router received it via another eBGP hop (resets to 0) |
| Conditional default not sent | Sentinel prefix not in BGP table, or route-map sequence order is wrong |
| R4 not installing default | Next-hop 172.16.1.1 not reachable via OSPF; verify OSPF adjacency |

### Prefix-List Quick Reference

| Syntax | Matches |
|--------|---------|
| `permit 198.51.100.0/24` | Exactly 198.51.100.0/24 |
| `permit 192.168.0.0/16 ge 24 le 24` | Any /24 within 192.168.0.0/16 |
| `permit 0.0.0.0/0 le 32` | Any prefix (wildcard) |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these solutions first!

### Task 1: Dual-Homed eBGP Baseline Verification

<details>
<summary>Click to view Verification Commands</summary>

```bash
! Verify both ISP sessions are up
R1# show ip bgp summary

! Verify dual-path for ISP-A prefix
R1# show ip bgp 198.51.100.0

! Simulate ISP-A failure
R1# configure terminal
R1(config)# interface FastEthernet1/0
R1(config-if)# shutdown

! Verify failover — prefix must still be reachable via ISP-B
R1# show ip bgp 198.51.100.0
! Path should now show only via 10.1.13.2 (ISP-B → R3 → R2 peering)

! Re-enable ISP-A link
R1(config)# interface FastEthernet1/0
R1(config-if)# no shutdown
```

</details>

---

### Task 2: Per-Prefix Outbound Traffic Engineering

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Remove lab-06 route-maps and apply per-prefix LP policy

! Prefix-lists for ISP address space
ip prefix-list ISP-A-PREFIXES seq 10 permit 198.51.100.0/24
ip prefix-list ISP-A-PREFIXES seq 20 permit 198.51.101.0/24
ip prefix-list ISP-A-PREFIXES seq 30 permit 198.51.102.0/24
!
ip prefix-list ISP-B-PREFIXES seq 10 permit 203.0.113.0/24
ip prefix-list ISP-B-PREFIXES seq 20 permit 203.0.114.0/24
ip prefix-list ISP-B-PREFIXES seq 30 permit 203.0.115.0/24
!
! Inbound from ISP-A: prefer ISP-A for ISP-A destinations
route-map ISP-A-IN permit 10
 match ip address prefix-list ISP-A-PREFIXES
 set local-preference 200
!
route-map ISP-A-IN permit 20
 set local-preference 100
!
! Inbound from ISP-B: prefer ISP-B for ISP-B destinations
route-map ISP-B-IN permit 10
 match ip address prefix-list ISP-B-PREFIXES
 set local-preference 200
!
route-map ISP-B-IN permit 20
 set local-preference 100
!
router bgp 65001
 no neighbor 10.1.12.2 route-map SET-LP-200-ISP-A in
 no neighbor 10.1.12.2 route-map TAG-ISP-A-OUT out
 no neighbor 10.1.12.2 send-community
 neighbor 10.1.12.2 route-map ISP-A-IN in
 !
 no neighbor 10.1.13.2 route-map POLICY-ISP-B-IN in
 no neighbor 10.1.13.2 route-map TAG-AND-PREPEND-ISP-B out
 no neighbor 10.1.13.2 send-community
 neighbor 10.1.13.2 route-map ISP-B-IN in
!
! Apply — soft reset to activate inbound policy
clear ip bgp 10.1.12.2 soft in
clear ip bgp 10.1.13.2 soft in
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
R1# show ip bgp 198.51.100.0
! Expect: localpref 200 on path via 10.1.12.2 (R2), localpref 100 via 10.1.13.2 (R3)

R1# show ip bgp 203.0.113.0
! Expect: localpref 200 on path via 10.1.13.2 (R3), localpref 100 via 10.1.12.2 (R2)
```

</details>

---

### Task 3: Per-Prefix Inbound Traffic Engineering

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Per-prefix prefix-lists for AS-path prepend control
ip prefix-list ENTERPRISE-192-168-1 seq 10 permit 192.168.1.0/24
ip prefix-list ENTERPRISE-192-168-2 seq 10 permit 192.168.2.0/24
!
! Outbound to ISP-A: prepend 3x for 192.168.1.0/24
route-map OUTBOUND-ISP-A permit 10
 match ip address prefix-list ENTERPRISE-192-168-1
 set as-path prepend 65001 65001 65001
!
route-map OUTBOUND-ISP-A permit 20
!
! Outbound to ISP-B: prepend 3x for 192.168.2.0/24
route-map OUTBOUND-ISP-B permit 10
 match ip address prefix-list ENTERPRISE-192-168-2
 set as-path prepend 65001 65001 65001
!
route-map OUTBOUND-ISP-B permit 20
!
router bgp 65001
 neighbor 10.1.12.2 route-map OUTBOUND-ISP-A out
 neighbor 10.1.13.2 route-map OUTBOUND-ISP-B out
!
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R2 — should see 4 AS hops for 192.168.1.0/24
R2# show ip bgp 192.168.1.0
! Expect AS-path: 65001 65001 65001 65001

! On R3 — should see 1 AS hop for 192.168.1.0/24 (no prepend)
R3# show ip bgp 192.168.1.0
! Expect AS-path: 65001

! On R3 — should see 4 AS hops for 192.168.2.0/24
R3# show ip bgp 192.168.2.0
! Expect AS-path: 65001 65001 65001 65001

! On R2 — should see 1 AS hop for 192.168.2.0/24
R2# show ip bgp 192.168.2.0
! Expect AS-path: 65001
```

</details>

---

### Task 4: MED-Based Preferred Entry Signaling

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Add MED to outbound route-maps
ip prefix-list ENTERPRISE-192-168-3 seq 10 permit 192.168.3.0/24
!
! Extend OUTBOUND-ISP-A: set MED 10 for 192.168.3.0/24
! (Add before the existing permit 20 catch-all)
no route-map OUTBOUND-ISP-A permit 20
!
route-map OUTBOUND-ISP-A permit 20
 match ip address prefix-list ENTERPRISE-192-168-3
 set metric 10
!
route-map OUTBOUND-ISP-A permit 30
!
! Extend OUTBOUND-ISP-B: set MED 100 for 192.168.3.0/24
no route-map OUTBOUND-ISP-B permit 20
!
route-map OUTBOUND-ISP-B permit 20
 match ip address prefix-list ENTERPRISE-192-168-3
 set metric 100
!
route-map OUTBOUND-ISP-B permit 30
!
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R2 — verify MED=10 for 192.168.3.0/24
R2# show ip bgp 192.168.3.0
! Expect: metric 10

! On R3 — verify MED=100 for 192.168.3.0/24
R3# show ip bgp 192.168.3.0
! Expect: metric 100
```

</details>

---

### Task 5: Conditional Default Route Origination

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Conditional default route to R4
ip prefix-list ISP-A-REACHABILITY seq 10 permit 198.51.100.0/24
!
route-map CHECK-ISP-UP permit 10
 match ip address prefix-list ISP-A-REACHABILITY
!
router bgp 65001
 neighbor 172.16.4.4 default-originate route-map CHECK-ISP-UP
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R1 — verify default being sent to R4
R1# show ip bgp neighbors 172.16.4.4 advertised-routes
! Expect: 0.0.0.0/0 in the output

! On R4 — verify default received and installed
R4# show ip bgp
! Expect: *> 0.0.0.0   172.16.1.1   ...

R4# show ip route 0.0.0.0
! Expect: B* 0.0.0.0/0 [200/0] via 172.16.1.1
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good (solution state)
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore to solution state
```

---

### Ticket 1 — R4 Has No Default Route Despite Active ISP Sessions

You receive a ticket from the network operations center: "R4 cannot reach internet prefixes. Both ISP sessions show as Established on R1, but R4 has no route to the internet."

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** R4's routing table contains `B* 0.0.0.0/0 [200/0] via 172.16.1.1` and can reach ISP prefixes via the default.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Confirm ISP sessions are up on R1
R1# show ip bgp summary
! Both 10.1.12.2 and 10.1.13.2 should be Established

! Step 2: Check if R1 is generating a default to R4
R1# show ip bgp neighbors 172.16.4.4 advertised-routes
! Is 0.0.0.0/0 in the output? If not, the condition is not met.

! Step 3: Check the conditional route-map on R1
R1# show route-map CHECK-ISP-UP
! Look at the match clause — which prefix-list is it matching?

! Step 4: Verify what prefix-list SENTINEL-PREFIX contains
R1# show ip prefix-list
! The sentinel prefix-list should match 198.51.100.0/24 (an ISP-A prefix in the BGP table)
! If it matches a non-existent prefix, the condition will never be true

! Step 5: Verify the sentinel prefix IS in the BGP table
R1# show ip bgp 198.51.100.0
! If this shows a valid path, the prefix exists — but the sentinel prefix-list is wrong
```

**Root cause:** The `CHECK-ISP-UP` route-map references a prefix-list that matches a non-existent prefix (e.g., 198.51.110.0/24 instead of 198.51.100.0/24). The condition never evaluates to true so R1 never sends the default to R4.

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — Fix the sentinel prefix-list to match the correct ISP-A prefix
R1# configure terminal
R1(config)# no ip prefix-list ISP-A-REACHABILITY
R1(config)# ip prefix-list ISP-A-REACHABILITY seq 10 permit 198.51.100.0/24
R1(config)# end

! Trigger BGP to re-evaluate the conditional
R1# clear ip bgp 172.16.4.4 soft out

! Verify on R4
R4# show ip bgp
! Expect: *> 0.0.0.0   172.16.1.1
R4# show ip route 0.0.0.0
! Expect: B* 0.0.0.0/0 [200/0] via 172.16.1.1
```

</details>

---

### Ticket 2 — Inbound Traffic for 192.168.2.0/24 Arrives via ISP-B Instead of ISP-A

A monitoring tool reports that traffic from internet hosts to 192.168.2.0/24 is arriving via the ISP-B (R3) link instead of the expected ISP-A (R2) link. The TE policy should be directing this prefix's inbound traffic through ISP-A.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip bgp 192.168.2.0` on R2 shows AS-path `65001` (1 hop, no prepend) and on R3 shows AS-path `65001 65001 65001 65001` (4 hops, prepended). Internet routers prefer the shorter R2/ISP-A path for 192.168.2.0/24.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Check what R2 sees for 192.168.2.0/24
R2# show ip bgp 192.168.2.0
! If AS-path is 65001 65001 65001 65001 (4 hops), the prepend is being applied toward ISP-A
! It should have AS-path 65001 (1 hop) — prepend is on the WRONG outbound route-map

! Step 2: Check what R3 sees for 192.168.2.0/24
R3# show ip bgp 192.168.2.0
! If AS-path is 65001 (1 hop), ISP-B has the shorter path — wrong direction

! Step 3: On R1, verify what is being advertised to each ISP
R1# show ip bgp neighbors 10.1.12.2 advertised-routes | include 192.168.2.0
! Shows what R1 is sending to R2 (ISP-A)

R1# show ip bgp neighbors 10.1.13.2 advertised-routes | include 192.168.2.0
! Shows what R1 is sending to R3 (ISP-B)

! Step 4: Inspect the outbound route-maps on R1
R1# show route-map OUTBOUND-ISP-A
R1# show route-map OUTBOUND-ISP-B
! The 192.168.2.0/24 prefix-list match and as-path prepend should be in OUTBOUND-ISP-B
! If it is in OUTBOUND-ISP-A instead, that is the fault
```

**Root cause:** The AS-path prepend for 192.168.2.0/24 is configured in `OUTBOUND-ISP-A` (applied toward ISP-A) instead of `OUTBOUND-ISP-B` (toward ISP-B). This makes ISP-A see the longer path, causing inbound traffic for 192.168.2.0/24 to enter via ISP-B — the opposite of the intended policy.

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — Remove prepend from OUTBOUND-ISP-A and add to OUTBOUND-ISP-B
R1# configure terminal
!
! Remove 192.168.2.0/24 prepend from OUTBOUND-ISP-A (it does not belong here)
R1(config)# no route-map OUTBOUND-ISP-A permit 10
R1(config)# route-map OUTBOUND-ISP-A permit 10
R1(config-route-map)# match ip address prefix-list ENTERPRISE-192-168-1
R1(config-route-map)# set as-path prepend 65001 65001 65001
R1(config-route-map)# exit
!
! Ensure OUTBOUND-ISP-B has 192.168.2.0/24 prepend
R1(config)# route-map OUTBOUND-ISP-B permit 10
R1(config-route-map)# match ip address prefix-list ENTERPRISE-192-168-2
R1(config-route-map)# set as-path prepend 65001 65001 65001
R1(config-route-map)# exit
R1(config)# end
!
clear ip bgp 10.1.12.2 soft out
clear ip bgp 10.1.13.2 soft out

! Verify on R2 — should show AS-path 65001 (1 hop)
R2# show ip bgp 192.168.2.0
! Verify on R3 — should show AS-path 65001 65001 65001 65001 (4 hops)
R3# show ip bgp 192.168.2.0
```

</details>

---

### Ticket 3 — All Outbound Traffic Is Taking the ISP-B Path Regardless of Destination

Operations reports that traffic from R4 to both ISP-A prefixes (198.51.100.x) and ISP-B prefixes (203.0.113.x) is exiting via ISP-B. The outbound TE policy should prefer ISP-A for ISP-A prefixes.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip bgp 198.51.100.0` on R1 shows `localpref 200` on the path via R2 (10.1.12.2) and `localpref 100` on the path via R3 (10.1.13.2). The `>` best-path marker is on the R2 path.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Check LP values on R1 for an ISP-A prefix
R1# show ip bgp 198.51.100.0
! If localpref is 50 (or lower than 100) on the R2 path, the inbound policy is inverted

! Step 2: Check LP values for an ISP-B prefix
R1# show ip bgp 203.0.113.0
! ISP-B path should show localpref 200 (correct if ISP-B-IN is OK)
! If ISP-A path is lower than ISP-B path for ALL prefixes, ISP-A-IN is misconfigured

! Step 3: Inspect the ISP-A-IN route-map
R1# show route-map ISP-A-IN
! Look at the set local-preference values
! Seq 10 (matching ISP-A-PREFIXES) should set LP 200
! If it is setting LP 50 (or anything lower than 100), that is the fault

! Step 4: Check received routes from ISP-A with LP
R1# show ip bgp neighbors 10.1.12.2 received-routes | include 198.51
! Verify the routes are arriving and being policy-matched
```

**Root cause:** The `ISP-A-IN` route-map has Local Preference set to 50 for ISP-A prefixes. This makes the ISP-A path LESS preferred than the default LP (100) that ISP-B paths receive, causing all ISP-A-origin traffic to route through ISP-B instead.

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — Correct the LP value in ISP-A-IN
R1# configure terminal
R1(config)# route-map ISP-A-IN permit 10
R1(config-route-map)# set local-preference 200
R1(config-route-map)# end
!
! Reapply inbound policy
R1# clear ip bgp 10.1.12.2 soft in

! Verify
R1# show ip bgp 198.51.100.0
! Expect: localpref 200 on path via 10.1.12.2, localpref 100 via 10.1.13.2
! The > symbol must be on the 10.1.12.2 path
```

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] Both ISP eBGP sessions show as Established in `show ip bgp summary`
- [ ] iBGP session R1–R4 is Established
- [ ] Failover test: ISP-A link shutdown → 198.51.100.0/24 still reachable via ISP-B path
- [ ] `show ip bgp 198.51.100.0` on R1 shows LP=200 on R2 path, LP=100 on R3 path
- [ ] `show ip bgp 203.0.113.0` on R1 shows LP=200 on R3 path, LP=100 on R2 path
- [ ] `show ip bgp 192.168.1.0` on R2 shows AS-path `65001 65001 65001 65001` (4 hops)
- [ ] `show ip bgp 192.168.1.0` on R3 shows AS-path `65001` (1 hop)
- [ ] `show ip bgp 192.168.2.0` on R3 shows AS-path `65001 65001 65001 65001` (4 hops)
- [ ] `show ip bgp 192.168.2.0` on R2 shows AS-path `65001` (1 hop)
- [ ] `show ip bgp 192.168.3.0` on R2 shows `metric 10`
- [ ] `show ip bgp 192.168.3.0` on R3 shows `metric 100`
- [ ] `show ip bgp` on R4 shows `0.0.0.0/0` with next-hop 172.16.1.1
- [ ] `show ip route 0.0.0.0` on R4 shows `B* 0.0.0.0/0 [200/0] via 172.16.1.1`

### Troubleshooting

- [ ] Ticket 1: Identified sentinel prefix-list mismatch as root cause; restored default route to R4
- [ ] Ticket 2: Identified reversed AS-path prepend direction; corrected OUTBOUND-ISP-A and OUTBOUND-ISP-B
- [ ] Ticket 3: Identified inverted LP value (50 instead of 200) in ISP-A-IN; corrected and verified
