# BGP Lab 08: Route Reflectors & iBGP Scaling

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
| **3.2.b** | Describe BGP path selection criteria |

### Skills Developed

- **iBGP Full-Mesh Problem** — understanding why n*(n-1)/2 sessions become unmanageable at scale
- **Route Reflector Design** — selecting the RR, defining the cluster, and understanding the loop-prevention mechanisms
- **cluster-id & originator-id** — how BGP prevents routing loops when reflected routes traverse multiple RRs
- **Route Reflector Client Configuration** — single iBGP session from client to RR eliminates full-mesh requirement
- **next-hop-self on Route Reflectors** — ensuring clients can reach eBGP next-hops that aren't in the IGP
- **IGP Extension for iBGP Loopback Reachability** — running OSPF to cover new iBGP peers
- **Reflected Route Verification** — identifying originator-id and cluster-list attributes in the BGP table

---

## 2. Topology & Scenario

### Business Context

AcmeCorp (AS 65001) is expanding its enterprise BGP infrastructure. The network currently runs a partial iBGP mesh: R1 (Enterprise Edge) peers with R4 (Enterprise Internal). The team is adding R6 — a second enterprise edge router — to terminate additional customer VLANs and provide redundancy.

With three iBGP speakers, a full mesh would require three sessions. As the enterprise grows toward 10+ BGP speakers, the full-mesh model becomes operationally unsustainable. The solution: designate R1 as the **Route Reflector** for the enterprise cluster. R4 and R6 become RR clients, each maintaining a single iBGP session to R1. R1 reflects learned routes between its clients without requiring direct client-to-client peering.

The team has the following requirements:

1. **IGP Reachability** — extend OSPF Area 0 to cover the new R1–R6 link and R6's loopback
2. **Route Reflector** — configure R1 with cluster-id 1; designate R4 and R6 as clients
3. **R6 iBGP** — establish R6's iBGP session to R1 only; advertise R6's enterprise prefix
4. **End-to-End Verification** — confirm R4 receives R6's prefix with originator-id and cluster-list attributes proving RR propagation

### ASCII Topology

```
        ┌──────────────────────┐    10.1.23.0/30    ┌──────────────────────┐
        │          R2          │  Fa1/0      Fa0/0  │          R3          │
        │        (ISP-A)       ├────────────────────┤        (ISP-B)       │
        │      AS 65002        │     .1        .2   │      AS 65003        │
        │   Lo0: 172.16.2.2    │                    │   Lo0: 172.16.3.3    │
        └──────────┬───────────┘                    └───────┬──────────────┘
          Fa0/0   │ .2                           .2 │ Fa1/0          │ Fa1/1 .1
     10.1.12.0/30  │                   10.1.13.0/30  │           10.1.35.0/30
          Fa1/0   │ .1                           .1 │ Fa1/1          │ Fa0/0 .2
                   └──────────────┐  ┌──────────────┘               │
                                  │  │                               │
                         ┌────────┴──┴──────────┐          ┌────────┴──────────┐
                         │           R1          │          │        R5         │
                         │  (Enterprise Edge)    │ Gi3/0    │  (Downstream Cust)│
                         │   ROUTE REFLECTOR     ├──┐       │    AS 65004       │
                         │     AS 65001          │  │ .1    │  Lo0: 172.16.5.5  │
                         │  Lo0: 172.16.1.1      │  │       └───────────────────┘
                         └──────────┬────────────┘  │ 10.1.16.0/30
                           Fa0/0   │ .1             │ .2 Gi3/0
                       10.1.14.0/30│         ┌──────┴────────────┐
                           Fa0/0   │ .2       │        R6         │
                         ┌─────────┴──────┐  │  (Enterprise Edge2│
                         │       R4       │  │    RR CLIENT)     │
                         │(Enterprise Int.)│  │    AS 65001       │
                         │   RR CLIENT    │  │  Lo0: 172.16.6.6   │
                         │   AS 65001     │  │  Lo1: 192.168.6.1  │
                         │ Lo0: 172.16.4.4│  └───────────────────┘
                         └────────────────┘
```

**iBGP Sessions (via Loopback0, over OSPF):**
- R1 → R4: `172.16.1.1` ↔ `172.16.4.4` (RR to Client)
- R1 → R6: `172.16.1.1` ↔ `172.16.6.6` (RR to Client) — **NEW**
- R4 and R6 do NOT peer with each other (RR eliminates full-mesh)

---

## 3. Hardware & Environment Specifications

### Device Inventory

| Device | Platform | Role | AS | Loopback0 |
|--------|----------|------|----|-----------|
| R1 | c7200 | Enterprise Edge / Route Reflector | 65001 | 172.16.1.1/32 |
| R2 | c7200 | ISP-A | 65002 | 172.16.2.2/32 |
| R3 | c7200 | ISP-B | 65003 | 172.16.3.3/32 |
| R4 | c3725 | Enterprise Internal / RR Client | 65001 | 172.16.4.4/32 |
| R5 | c3725 | Downstream Customer | 65004 | 172.16.5.5/32 |
| R6 | c7200 | Enterprise Edge 2 / RR Client | 65001 | 172.16.6.6/32 |

### Cabling Table

| Link ID | Source | Source IP | Target | Target IP | Subnet | Purpose |
|---------|--------|-----------|--------|-----------|--------|---------|
| L1 | R1 Fa1/0 | 10.1.12.1 | R2 Fa0/0 | 10.1.12.2 | 10.1.12.0/30 | Enterprise eBGP to ISP-A |
| L2 | R2 Fa1/0 | 10.1.23.1 | R3 Fa0/0 | 10.1.23.2 | 10.1.23.0/30 | ISP-A to ISP-B (eBGP) |
| L3 | R1 Fa1/1 | 10.1.13.1 | R3 Fa1/0 | 10.1.13.2 | 10.1.13.0/30 | Enterprise eBGP to ISP-B |
| L4 | R1 Fa0/0 | 10.1.14.1 | R4 Fa0/0 | 10.1.14.2 | 10.1.14.0/30 | Enterprise IGP + iBGP underlay |
| L5 | R3 Fa1/1 | 10.1.35.1 | R5 Fa0/0 | 10.1.35.2 | 10.1.35.0/30 | ISP-B to Downstream Customer |
| L6 | R1 Gi3/0 | 10.1.16.1 | R6 Gi3/0 | 10.1.16.2 | 10.1.16.0/30 | Enterprise IGP + iBGP underlay (NEW) |

### Console Access Table

| Device | Console Port | Connection Command |
|--------|--------------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |
| R6 | 5006 | `telnet 127.0.0.1 5006` |

---

## 4. Base Configuration

### Pre-Loaded (initial-configs/)

All configurations from Lab 07 are carried forward:

- **IP addressing** — all interfaces and loopbacks on R1–R5
- **OSPF Area 0** — running on R1 (covering 10.1.14.0/30 and 172.16.1.1/32) and R4 (covering 10.1.14.0/30 and 172.16.4.4/32)
- **eBGP sessions** — R1 ↔ R2 (ISP-A) and R1 ↔ R3 (ISP-B), both with full inbound/outbound route-maps from Lab 07
- **iBGP session** — R1 ↔ R4 (peering via loopbacks, next-hop-self, conditional default-originate)
- **Lab 07 traffic engineering policy** — Local Preference, AS-Path prepending, MED, and conditional default route
- **R6** — IP addressing pre-configured on Loopback0, Loopback1, and Gi3/0 only; no routing protocol config

### NOT Pre-Configured (student must implement)

- OSPF extension to cover the R1–R6 link and R6's loopback
- Route Reflector designation on R1 (cluster-id and client assignments)
- R6 added as iBGP neighbor on R1 with route-reflector-client
- R4 re-designated as route-reflector-client on R1
- R6 iBGP session (peer to R1, update-source Loopback0)
- R6 prefix advertisement into BGP

---

## 5. Lab Challenge: Core Implementation

### Task 1: Extend OSPF to R6

- On R1, include the R1–R6 link subnet (10.1.16.0/30) in the OSPF process so the GigabitEthernet link participates in Area 0
- On R6, enable OSPF process 1 with router-id 172.16.6.6 and include both the R1–R6 link subnet (10.1.16.0/30) and R6's Loopback0 (172.16.6.6/32) in Area 0
- After OSPF converges, R1 must have a route to 172.16.6.6/32 and R6 must have a route to 172.16.1.1/32 — this loopback reachability is the IGP underlay that iBGP sessions will use

**Verification:** `show ip ospf neighbor` on R1 must show R6 (172.16.6.6) as FULL. `show ip route 172.16.6.6` on R1 and `show ip route 172.16.1.1` on R6 must return OSPF routes.

---

### Task 2: Configure R1 as Route Reflector

- Assign cluster-id 1 to R1's BGP process — this identifies R1 as a route reflector in cluster 1 and is stamped on all reflected routes to prevent loops
- Designate R4 as a route-reflector-client on R1's existing iBGP neighbor statement for 172.16.4.4
- Add R6 (172.16.6.6) as a new iBGP neighbor in AS 65001: source sessions from Loopback0, apply next-hop-self, and designate it as a route-reflector-client
- Keep all existing eBGP neighbors (R2 and R3) and the conditional default-originate for R4 unchanged

**Verification:** `show bgp neighbors 172.16.6.6` on R1 must show the session as `Established` and report `Route Reflector Client`. `show bgp neighbors 172.16.4.4` must also show `Route Reflector Client`.

---

### Task 3: Configure R6 as RR Client

- On R6, enable BGP in AS 65001 with router-id 172.16.6.6
- Add a single iBGP neighbor: R1's loopback (172.16.1.1) in AS 65001, sourced from R6's Loopback0
- Note: R6 does NOT need to peer with R4 — the route reflector handles distribution between clients
- Advertise R6's Loopback0 (172.16.6.6/32) and Loopback1 (192.168.6.0/24) into BGP using network statements

**Verification:** `show bgp summary` on R6 must show one neighbor (172.16.1.1) in state `Established`. `show bgp` must list 172.16.6.6/32 and 192.168.6.0/24 as locally originated.

---

### Task 4: Verify Route Reflector Propagation

- On R4, confirm it receives R6's prefixes (192.168.6.0/24 and 172.16.6.6/32) — these arrived via the route reflector, not directly from R6
- Examine the BGP table entry for 192.168.6.0/24 on R4: it must show an `Originator ID` of 172.16.6.6 and a non-empty `Cluster-list` containing cluster-id 1
- On R6, confirm it receives R4's prefixes (10.4.1.0/24 and 10.4.2.0/24) with `Originator ID` of 172.16.4.4
- Confirm that neither R4 nor R6 has a direct iBGP session to the other — all reflected routes travel through R1

**Verification:** `show bgp 192.168.6.0` on R4 must display `Originator: 172.16.6.6` and `Cluster list: 0.0.0.1`. `show bgp 10.4.1.0` on R6 must display `Originator: 172.16.4.4` and `Cluster list: 0.0.0.1`.

---

## 6. Verification & Analysis

### Task 1: OSPF Extended to R6

```
R1# show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
172.16.4.4        1   FULL/DR         00:00:33    10.1.14.2       FastEthernet0/0
172.16.6.6        1   FULL/DR         00:00:38    10.1.16.2       GigabitEthernet3/0  ! ← R6 FULL

R6# show ip route 172.16.1.1
O     172.16.1.1/32 [110/2] via 10.1.16.1, 00:01:12, GigabitEthernet3/0  ! ← OSPF route to RR loopback

R1# show ip route 172.16.6.6
O     172.16.6.6/32 [110/2] via 10.1.16.2, 00:01:05, GigabitEthernet3/0  ! ← OSPF route to R6 loopback
```

### Task 2: R1 Route Reflector Status

```
R1# show bgp neighbors 172.16.6.6 | include BGP|State|Route Reflector
BGP neighbor is 172.16.6.6,  remote AS 65001, internal link
  BGP state = Established, up for 00:03:44          ! ← session must be Established
    Route Reflector Client                           ! ← R6 is an RR client

R1# show bgp neighbors 172.16.4.4 | include BGP|State|Route Reflector
BGP neighbor is 172.16.4.4,  remote AS 65001, internal link
  BGP state = Established, up for 00:45:18          ! ← pre-existing session, still Established
    Route Reflector Client                           ! ← R4 now explicitly an RR client

R1# show bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.1.12.2       4 65002      88      82       45    0    0 01:05:22       3  ! ← ISP-A eBGP
10.1.13.2       4 65003      87      81       45    0    0 01:05:15       3  ! ← ISP-B eBGP
172.16.4.4      4 65001      66      74       45    0    0 00:45:18       3  ! ← R4 RR client
172.16.6.6      4 65001      28      32       45    0    0 00:03:44       3  ! ← R6 RR client (new)
```

### Task 3: R6 BGP Table

```
R6# show bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
172.16.1.1      4 65001      32      28       12    0    0 00:03:44       9  ! ← single iBGP peer (RR)

R6# show bgp | begin Network
   Network          Next Hop            Metric LocPrf Weight Path
*> 172.16.6.6/32    0.0.0.0                  0         32768 i   ! ← locally originated
*> 192.168.1.0      0.0.0.0                  0         32768 i   ! ← locally originated (Lo1)
*>i198.51.100.0     10.1.12.2                0    200      0 65002 i  ! ← from RR via R2, next-hop = eBGP addr
*>i198.51.101.0     10.1.12.2                0    200      0 65002 i
*>i203.0.113.0      10.1.13.2                0    200      0 65003 i  ! ← from RR via R3
```

### Task 4: Route Reflector Propagation Attributes

```
R4# show bgp 192.168.6.0
BGP routing table entry for 192.168.6.0/24, version 18
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  Not advertised to any peer
  65001
    172.16.1.1 (metric 2) from 172.16.1.1 (172.16.6.6)   ! ← via R1, originated by R6
      Origin IGP, metric 0, localpref 100, valid, internal, best
      Originator: 172.16.6.6                              ! ← original source is R6
      Cluster list: 0.0.0.1                               ! ← reflected through cluster-id 1 (R1)

R6# show bgp 10.4.1.0
BGP routing table entry for 10.4.1.0/24, version 6
Paths: (1 available, best #1, table Default-IP-Routing-Table)
  Not advertised to any peer
  65001
    172.16.1.1 (metric 2) from 172.16.1.1 (172.16.4.4)   ! ← via R1, originated by R4
      Origin IGP, metric 0, localpref 100, valid, internal, best
      Originator: 172.16.4.4                              ! ← original source is R4
      Cluster list: 0.0.0.1                               ! ← reflected through cluster-id 1 (R1)
```

---

## 7. Verification Cheatsheet

### OSPF Extension

```
router ospf 1
 network 10.1.16.0 0.0.0.3 area 0
 network 172.16.6.6 0.0.0.0 area 0
```

| Command | Purpose |
|---------|---------|
| `show ip ospf neighbor` | Confirm R6 in FULL state on R1 |
| `show ip route 172.16.X.X` | Verify loopback reachability via OSPF |
| `show ip ospf interface brief` | Check which interfaces are running OSPF |

> **Exam tip:** iBGP sessions source from loopbacks to survive interface failures. OSPF must advertise those loopbacks for the session to form.

### Route Reflector Configuration

```
router bgp 65001
 bgp cluster-id 1
 neighbor <client-ip> route-reflector-client
 neighbor <client-ip> next-hop-self
```

| Command | Purpose |
|---------|---------|
| `bgp cluster-id <id>` | Designate this router as RR and assign cluster identity |
| `neighbor X route-reflector-client` | Mark a neighbor as an RR client |
| `neighbor X next-hop-self` | Rewrite eBGP next-hops so clients can forward traffic |

> **Exam tip:** The RR does NOT need `route-reflector-client` on eBGP neighbors — only on iBGP clients. The RR reflects routes between clients; non-client iBGP peers (if any) still require a full mesh among themselves.

### Route Reflector Client Configuration

```
router bgp 65001
 neighbor <rr-ip> remote-as 65001
 neighbor <rr-ip> update-source Loopback0
```

| Command | Purpose |
|---------|---------|
| `update-source Loopback0` | Source iBGP TCP session from loopback (required for stability) |
| `network X.X.X.X mask Y.Y.Y.Y` | Advertise a prefix — exact match required in routing table |

> **Exam tip:** RR clients need NO special configuration — just a standard iBGP session to the RR. The `route-reflector-client` command is configured only on the RR, not on the client.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show bgp summary` | All neighbors in `Established`; non-zero PfxRcd |
| `show bgp neighbors X route-reflector-client` | Confirms the neighbor is designated an RR client |
| `show bgp X.X.X.X` | Shows Originator ID and Cluster-list on reflected routes |
| `show bgp` | Full BGP table — verify all expected prefixes present |
| `show ip ospf neighbor` | All enterprise routers in FULL state |
| `show ip route X.X.X.X` | Confirms route installed in RIB |

### Route Reflector Loop Prevention

| Attribute | Set By | Checked By | Purpose |
|-----------|--------|-----------|---------|
| `Originator ID` | First RR to reflect the route | All BGP speakers | Router ignores route if originator-id = own router-id |
| `Cluster list` | Every RR that reflects the route | All RRs | RR discards route if its own cluster-id is in the list |

### Common BGP Route Reflector Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Client has no routes from other clients | `route-reflector-client` missing on one or both client neighbors |
| Client has routes but can't forward | `next-hop-self` missing on RR; eBGP next-hops not reachable |
| iBGP session flapping or not forming | OSPF not advertising loopback; `update-source Loopback0` missing |
| Reflected routes rejected by client | `cluster-id` on RR matches a value in cluster-list (loop detected) |
| Client receives its own routes back | Normal — BGP drops these via originator-id check; not a fault |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: Extend OSPF to R6

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — add the R1-R6 link to OSPF Area 0
router ospf 1
 network 10.1.16.0 0.0.0.3 area 0
```
</details>

<details>
<summary>Click to view R6 Configuration</summary>

```bash
! R6 — enable OSPF, include the link subnet and loopback
router ospf 1
 router-id 172.16.6.6
 network 10.1.16.0 0.0.0.3 area 0
 network 172.16.6.6 0.0.0.0 area 0
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip ospf neighbor
show ip route 172.16.6.6
show ip route 172.16.1.1
```
</details>

---

### Task 2: Configure R1 as Route Reflector

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Route Reflector: cluster-id, existing client R4, new client R6
router bgp 65001
 bgp cluster-id 1
 ! R4 — existing iBGP peer, now explicitly an RR client
 neighbor 172.16.4.4 route-reflector-client
 ! R6 — new iBGP peer, RR client
 neighbor 172.16.6.6 remote-as 65001
 neighbor 172.16.6.6 update-source Loopback0
 neighbor 172.16.6.6 next-hop-self
 neighbor 172.16.6.6 route-reflector-client
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show bgp neighbors 172.16.6.6
show bgp neighbors 172.16.4.4
show bgp summary
```
</details>

---

### Task 3: Configure R6 as RR Client

<details>
<summary>Click to view R6 Configuration</summary>

```bash
! R6 — standard iBGP client; single peer to RR (R1)
router bgp 65001
 bgp router-id 172.16.6.6
 neighbor 172.16.1.1 remote-as 65001
 neighbor 172.16.1.1 update-source Loopback0
 !
 network 172.16.6.6 mask 255.255.255.255
 network 192.168.6.0 mask 255.255.255.0
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show bgp summary
show bgp | begin Network
```
</details>

---

### Task 4: Verify Route Reflector Propagation

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R4 — check R6's prefix shows RR attributes
show bgp 192.168.6.0
! Expect: Originator: 172.16.6.6 / Cluster list: 0.0.0.1

! On R6 — check R4's prefix shows RR attributes
show bgp 10.4.1.0
! Expect: Originator: 172.16.4.4 / Cluster list: 0.0.0.1

! Confirm no direct R4-R6 session exists
show bgp summary
! On R4: only 172.16.1.1 as iBGP neighbor
! On R6: only 172.16.1.1 as iBGP neighbor
```
</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then
diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good (initial-configs)
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/inject_scenario_02.py  # Ticket 2
python3 scripts/fault-injection/inject_scenario_03.py  # Ticket 3
python3 scripts/fault-injection/apply_solution.py      # restore to solution state
```

---

### Ticket 1 — R6 Can See ISP Routes But Cannot Forward Traffic to the Internet

The network team reports that R6's BGP table is fully populated with ISP prefixes from R2 and R3, but pings from R6 to 198.51.100.1 and 203.0.113.1 time out. Traceroute shows R6 has no valid next-hop.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** R6 can ping ISP prefixes (198.51.100.1, 203.0.113.1). `show ip route` on R6 shows ISP routes with a reachable next-hop.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R6, run `show bgp 198.51.100.0` — examine the Next Hop field
   - Expected (faulty): Next Hop = `10.1.12.2` (eBGP address of R2, not in R6's routing table)
   - A good RR configuration should show Next Hop = `172.16.1.1` (R1's loopback, reachable via OSPF)

2. On R6, run `show ip route 10.1.12.2` — confirm this address is unreachable from R6
   - R6 only has OSPF routes to enterprise loopbacks; it has no path to the 10.1.12.x eBGP subnets

3. On R1, run `show bgp neighbors 172.16.6.6` — look for `next-hop-self` in the neighbor details
   - If `next-hop-self` is missing, R1 is advertising ISP prefixes to R6 with the original eBGP next-hop unchanged

4. On R1, run `show bgp neighbors 172.16.6.6 advertised-routes` — confirm next-hop values in advertisements
   - Without `next-hop-self`: next-hop = eBGP peer address (not reachable by R6)
   - With `next-hop-self`: next-hop = R1's loopback (172.16.1.1, reachable via OSPF)
</details>

<details>
<summary>Click to view Fix</summary>

**Root cause:** `next-hop-self` was removed from R1's neighbor statement for R6. R1 is reflecting ISP routes to R6 with the original eBGP next-hop addresses (10.1.12.2 and 10.1.13.2), which R6 cannot reach.

**Fix on R1:**
```bash
router bgp 65001
 neighbor 172.16.6.6 next-hop-self
clear ip bgp 172.16.6.6 soft out
```

**Verify:** `show bgp 198.51.100.0` on R6 — Next Hop must change to `172.16.1.1`.
</details>

---

### Ticket 2 — R4 and R6 Are Not Receiving Each Other's Prefixes

The enterprise team reports that internal routing is broken. R6 cannot reach 10.4.1.0/24 (R4's enterprise prefix), and R4 cannot reach 192.168.6.0/24 (R6's enterprise prefix). Both R4 and R6 report their BGP sessions to R1 as Established with the correct prefix counts.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show bgp 192.168.6.0` on R4 shows a valid route. `show bgp 10.4.1.0` on R6 shows a valid route. Both have Originator ID and Cluster-list attributes.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R4, run `show bgp summary` — confirm R4's only iBGP neighbor (172.16.1.1) is Established
   - The session is up, so the issue is not connectivity

2. On R4, run `show bgp 192.168.6.0` — check if the route exists
   - If absent: R1 is not reflecting R6's routes to R4

3. On R1, run `show bgp neighbors 172.16.4.4 | include Reflector`
   - If no `Route Reflector Client` line appears, R4 is NOT an RR client
   - R1 will not reflect routes to a non-client iBGP neighbor; they must learn routes via full mesh

4. On R1, run `show bgp neighbors 172.16.6.6 | include Reflector`
   - Check if R6 is still correctly designated as an RR client

5. On R1, run `show bgp` — confirm R1 has routes from both R4 and R6 in its table
   - R1 receives the routes but refuses to reflect them because the target is not flagged as a client
</details>

<details>
<summary>Click to view Fix</summary>

**Root cause:** The `route-reflector-client` command was removed from R1's neighbor statement for R4. R4 is now a non-client iBGP peer. Under iBGP split-horizon rules, R1 cannot reflect R6's routes to R4 (and vice versa) because a route learned from an iBGP peer is never re-advertised to another iBGP peer unless the receiver is an RR client.

**Fix on R1:**
```bash
router bgp 65001
 neighbor 172.16.4.4 route-reflector-client
clear ip bgp 172.16.4.4 soft out
```

**Verify:** `show bgp 192.168.6.0` on R4 must now show Originator ID = 172.16.6.6 and Cluster list = 0.0.0.1.
</details>

---

### Ticket 3 — R6's BGP Session to R1 Will Not Establish

A new deployment has just been pushed for R6. The engineer reports that R6's BGP process started and shows the neighbor configured, but the session to R1 (172.16.1.1) is stuck in `Active` state. R1 does not show R6 as a connected neighbor in `show bgp summary`.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show bgp summary` on R6 shows 172.16.1.1 in `Established` state. `show bgp summary` on R1 shows 172.16.6.6 in `Established` state with non-zero PfxRcd.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R6, run `show bgp summary` — confirm neighbor 172.16.1.1 is in `Active` (not `Established`)
   - `Active` means R6 is sending TCP SYN packets but not receiving a response

2. On R6, run `show ip route 172.16.1.1` — verify OSPF route to R1's loopback is present
   - If missing: OSPF is not running or is not advertising R1's loopback — fix OSPF first

3. On R6, run `show bgp neighbors 172.16.1.1 | include source`
   - Check what source address R6 is using for the BGP TCP session
   - If no `update-source Loopback0` is configured, R6 uses the outbound interface IP (10.1.16.2)

4. On R1, run `show bgp neighbors 172.16.6.6 | include source`
   - R1 expects TCP connections from 172.16.6.6 (R6's loopback) but is receiving them from 10.1.16.2
   - BGP neighbors are identified by the remote IP; R1 has no neighbor statement for 10.1.16.2 → drops the TCP connection

5. Confirm the mismatch: R6 sources from 10.1.16.2, R1 expects 172.16.6.6 → session cannot form
</details>

<details>
<summary>Click to view Fix</summary>

**Root cause:** `update-source Loopback0` is missing from R6's BGP neighbor configuration. R6 is sourcing the iBGP TCP session from its GigabitEthernet3/0 interface (10.1.16.2) instead of Loopback0 (172.16.6.6). R1 is configured to accept a connection from 172.16.6.6 and rejects the mismatched source.

**Fix on R6:**
```bash
router bgp 65001
 neighbor 172.16.1.1 update-source Loopback0
clear ip bgp 172.16.1.1
```

**Verify:** `show bgp summary` on R6 — 172.16.1.1 must reach `Established`. `show bgp summary` on R1 — 172.16.6.6 must appear with non-zero PfxRcd.
</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] OSPF adjacency between R1 and R6 is FULL (`show ip ospf neighbor`)
- [ ] R1 has an OSPF route to 172.16.6.6/32; R6 has an OSPF route to 172.16.1.1/32
- [ ] R1 `show bgp summary` shows four neighbors: 10.1.12.2, 10.1.13.2, 172.16.4.4, 172.16.6.6 — all Established
- [ ] R1 `show bgp neighbors 172.16.4.4` reports `Route Reflector Client`
- [ ] R1 `show bgp neighbors 172.16.6.6` reports `Route Reflector Client`
- [ ] R6 `show bgp summary` shows exactly one neighbor (172.16.1.1) — Established
- [ ] R4 `show bgp 192.168.6.0` shows Originator: 172.16.6.6 and Cluster list: 0.0.0.1
- [ ] R6 `show bgp 10.4.1.0` shows Originator: 172.16.4.4 and Cluster list: 0.0.0.1
- [ ] R6 `show bgp 198.51.100.0` shows Next Hop = 172.16.1.1 (not the raw eBGP address)
- [ ] R4 and R6 have NO direct iBGP session with each other

### Troubleshooting

- [ ] Ticket 1 diagnosed and fixed: next-hop-self restored on R1 for R6; R6 can reach ISP prefixes
- [ ] Ticket 2 diagnosed and fixed: route-reflector-client restored for R4; inter-client reflection working
- [ ] Ticket 3 diagnosed and fixed: update-source Loopback0 restored on R6; session Established
