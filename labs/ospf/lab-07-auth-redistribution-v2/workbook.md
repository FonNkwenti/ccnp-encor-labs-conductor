# CCNP ENCOR — OSPF Lab 07: Authentication & Redistribution

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

**Exam Objective:** 3.2.a — Compare routing protocol types (path selection, metrics, area types) | 3.2.b — Configure simple OSPFv2 (summarization, filtering, neighbor adjacency)

OSPF authentication prevents unauthorized routers from injecting false routing information into the domain. This lab covers two authentication mechanisms — HMAC-SHA-256 (modern key-chain based) and MD5 (legacy area-level) — and demonstrates how OSPF redistributes external routes from EIGRP, classifying them by metric type (E1 or E2) to control how internal routers compute their cost to external destinations.

---

### OSPF Authentication — HMAC-SHA-256

OSPF supports two cryptographic authentication models: the legacy `ip ospf authentication` interface command (MD5), and the newer key-chain model that supports HMAC-SHA-256. Key-chain authentication is applied at the interface level and references a named key-chain defined globally.

```
! Step 1: Define the key-chain globally
key chain OSPF_AUTH
 key 1
  key-string <password>
  cryptographic-algorithm hmac-sha-256

! Step 2: Apply to each OSPF interface
interface FastEthernet1/0
 ip ospf authentication key-chain OSPF_AUTH
```

Key facts:
- The key-chain name is locally significant — it does not need to match on both ends.
- The `key-string` **must** match on both OSPF neighbors.
- The `cryptographic-algorithm` must match on both ends.
- HMAC-SHA-256 produces a stronger digest than MD5 and is preferred for new deployments.
- `show ip ospf interface` confirms the authentication type and key ID in use.

---

### OSPF Authentication — Area-Level MD5

MD5 authentication can be applied at the OSPF area level, which simplifies configuration when all links in an area use the same key. The area is configured to require authentication; each participating interface then provides the key.

```
! Enable MD5 authentication for the area in the OSPF process
router ospf 1
 area 1 authentication message-digest

! Provide the MD5 key on each interface in Area 1
interface FastEthernet1/0
 ip ospf message-digest-key 1 md5 <password>
 ip ospf authentication message-digest
```

| Parameter | Notes |
|-----------|-------|
| Key ID (1–255) | Must match on both ends of the link |
| MD5 password | Must match on both ends; case-sensitive |
| `area N authentication message-digest` | Enables MD5 for all interfaces in that area |
| `ip ospf authentication message-digest` | Interface override — use when mixing auth types within an area |

> **Exam tip:** If an OSPF adjacency drops immediately after adding authentication, check for key-string mismatches first. Use `debug ip ospf adj` to see authentication failure messages.

---

### OSPF Redistribution — External Route Types (E1 vs E2)

When a router redistributes external routes into OSPF, each route is tagged as either **External Type 1 (E1)** or **External Type 2 (E2)**. The difference lies in how the metric changes as the route traverses the OSPF domain:

| Type | Metric Behavior | Default |
|------|----------------|---------|
| E1 | Seed metric + internal OSPF cost accumulated along the path | No |
| E2 | Seed metric only — never changes regardless of path | Yes |

**E2 (default):** The redistributing router (ASBR) assigns a seed metric. All internal routers see the same metric regardless of their distance from the ASBR. If two ASBRs advertise the same E2 prefix, the router uses the ASBR with the lowest cost to reach it.

**E1:** The internal OSPF cost is added to the seed metric at each hop. This makes E1 routes more expensive the farther you are from the ASBR — they behave more like internal routes in that sense.

```
! Redistribute EIGRP 100 into OSPF with default E2 metric type
router ospf 1
 redistribute eigrp 100 subnets

! Redistribute with explicit metric type control via route-map
router ospf 1
 redistribute eigrp 100 subnets route-map EIGRP_TO_OSPF

! Route-map using prefix-lists to tag routes by type
ip prefix-list E1_ROUTES seq 5 permit 172.16.5.0/24
ip prefix-list E2_ROUTES seq 5 permit 172.16.105.0/24

route-map EIGRP_TO_OSPF permit 10
 match ip address prefix-list E1_ROUTES
 set metric-type type-1

route-map EIGRP_TO_OSPF permit 20
 match ip address prefix-list E2_ROUTES
 set metric-type type-2

route-map EIGRP_TO_OSPF permit 30
```

> **Exam tip:** Route-map clause 30 with no match/set statements is a catch-all permit. Without it, any redistributed routes not matching clauses 10 or 20 would be **denied** (dropped). Always include a final `permit` clause when you want to pass unmatched routes through.

---

### EIGRP Basics for Redistribution

For redistribution to work, EIGRP must establish a neighbor relationship between R2 and R5. EIGRP uses the `network` statement to activate the protocol on interfaces; any subnets advertised by R5 that fall within R5's `network` range will be learned by R2 via EIGRP and then redistributed into OSPF.

```
router eigrp 100
 network 10.25.0.0 0.0.0.3
 network 172.16.5.0 0.0.0.255
 network 172.16.105.0 0.0.0.255
 no auto-summary
```

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| HMAC-SHA-256 key-chain auth | Configure and apply modern OSPF interface authentication |
| MD5 area authentication | Apply legacy MD5 at the OSPF area level |
| EIGRP-to-OSPF redistribution | Inject external routes from a different AS into the OSPF domain |
| Route-map metric control | Use prefix-lists and route-maps to tag redistributed routes as E1 or E2 |
| E1 vs E2 analysis | Verify and explain metric propagation differences from an internal router |

---

## 2. Topology & Scenario

### Scenario

Skynet Global's network backbone connects three core sites (R1, R2, R3). A recent acquisition brought an external partner network operated by R5, which runs EIGRP internally. The security team has mandated that all OSPF router-to-router communication be authenticated immediately. Area 0 backbone links will use the newer HMAC-SHA-256 standard; the inter-area link (Area 1) will use MD5 pending a future migration.

On the integration side, R2 is elected as the ASBR (Autonomous System Boundary Router) to peer with R5 over EIGRP and redistribute the partner's two research subnets (`172.16.5.0/24` and `172.16.105.0/24`) into OSPF. To demonstrate path-selection differences, the operations team wants one subnet tagged as E1 (metric accumulates) and the other as E2 (flat metric). Your job is to implement all of this and verify correct behavior from R3's vantage point.

### ASCII Topology

```
              ┌──────────────────────────────┐
              │             R1               │
              │         (Hub / ABR)          │
              │      Lo0: 10.1.1.1/32        │
              └──────┬────────────┬──────────┘
           Fa1/0     │            │     Fa1/1
     10.12.0.1/30    │            │   10.13.0.1/30
         Area 0      │            │      Area 0
     10.12.0.2/30    │            │   10.13.0.2/30
           Fa0/0     │            │     Fa1/0
     ┌───────────────┘            └────────────────┐
     │                                             │
┌────┴─────────────────┐     ┌──────────────────────┴──┐
│         R2           │     │           R3             │
│  (Backbone / ASBR)   │     │        (Branch)          │
│   Lo0: 10.2.2.2/32   │     │    Lo0: 10.3.3.3/32      │
└──────┬───────┬───────┘     └─────────────┬────────────┘
  Fa1/0│       │Fa1/1               Fa0/0  │
10.23.0.1/30   │10.25.0.1/30    10.23.0.2/30
  Area 1│       └──────────────┐
10.23.0.2/30    EIGRP AS 100   │10.25.0.2/30
  Fa0/0│                  Fa0/0│
     ┌──┴──────────┐   ┌───────┴─────────────────┐
     │  (R3 above) │   │          R5              │
     └─────────────┘   │      (External Partner)  │
                        │    Lo0: 10.5.5.5/32      │
                        │  Lo100: 172.16.5.1/24    │
                        │  Lo200: 172.16.105.1/24  │
                        └─────────────────────────-┘

  Area 0 (Backbone): R1–R2, R1–R3
  Area 1:            R2–R3
  External (EIGRP):  R2–R5
```

---

## 3. Hardware & Environment Specifications

### Device Summary

| Device | Role | Platform | Loopback0 | Console |
|--------|------|----------|-----------|---------|
| R1 | Hub / ABR | c7200 | 10.1.1.1/32 | 5001 |
| R2 | Backbone / ASBR | c7200 | 10.2.2.2/32 | 5002 |
| R3 | Branch | c7200 | 10.3.3.3/32 | 5003 |
| R5 | External Partner | c7200 | 10.5.5.5/32 | 5005 |

### Cabling & IP Addressing

| Local Interface | Local Device | Remote Device | Remote Interface | Subnet | Area |
|-----------------|--------------|---------------|------------------|--------|------|
| Fa1/0 | R1 | R2 | Fa0/0 | 10.12.0.0/30 | Area 0 |
| Fa1/1 | R1 | R3 | Fa1/0 | 10.13.0.0/30 | Area 0 |
| Fa1/0 | R2 | R3 | Fa0/0 | 10.23.0.0/30 | Area 1 |
| Fa1/1 | R2 | R5 | Fa0/0 | 10.25.0.0/30 | External |

### Console Access Table

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |

---

## 4. Base Configuration

The `initial-configs/` directory pre-loads the following on all four devices:

**Pre-configured:**
- Hostnames and interface IP addresses
- Loopback0 on each router
- OSPF process 1 with router-ID and `auto-cost reference-bandwidth 1000`
- Area 0 adjacencies: R1–R2 (Fa1/0 / Fa0/0) and R1–R3 (Fa1/1 / Fa1/0) — point-to-point
- Area 1 adjacency: R2–R3 (Fa1/0 / Fa0/0) — point-to-point
- R5 interface IP addressing and loopbacks for the research subnets

**NOT pre-configured (you configure these):**
- Any OSPF authentication (SHA-256 or MD5)
- EIGRP routing process on R2 or R5
- Redistribution of EIGRP routes into OSPF
- Prefix-lists and route-map for metric-type control

---

## 5. Lab Challenge: Core Implementation

### Task 1: Area 0 Backbone — HMAC-SHA-256 Authentication

- Create a globally-defined key-chain named `OSPF_AUTH` on R1, R2, and R3.
- Inside the key-chain, define key ID `1` with a key-string of your choice.
- Set the cryptographic algorithm to `hmac-sha-256`.
- Apply the key-chain to the Area 0 interfaces on each router:
  - R1: both Fa1/0 (to R2) and Fa1/1 (to R3)
  - R2: Fa0/0 (to R1)
  - R3: Fa1/0 (to R1)
- The key-string must be identical on all three routers.

**Verification:** `show ip ospf interface Fa1/0` on R1 should show `Message digest authentication using HMAC SHA 256` and a key ID. All three OSPF adjacencies must remain `FULL` state in `show ip ospf neighbor`.

---

### Task 2: Area 1 — MD5 Authentication

- Enable MD5 authentication for Area 1 at the OSPF process level on both R2 and R3.
- On each router, configure the Area 1 interface with MD5 key ID `1` and a shared key-string.
  - R2: interface Fa1/0 (to R3)
  - R3: interface Fa0/0 (to R2)
- The MD5 key-string must match on both ends.

**Verification:** `show ip ospf neighbor` on R2 must show R3 as `FULL`. `show ip ospf interface Fa1/0` on R2 should confirm `Message digest authentication enabled`.

---

### Task 3: EIGRP Peering and Redistribution into OSPF

- On R5, enable EIGRP Autonomous System `100`. Advertise the link to R2, the loopback research subnet `172.16.5.0/24`, and the loopback research subnet `172.16.105.0/24`. Disable auto-summary.
- On R2, enable EIGRP AS `100` on the link to R5 only. Disable auto-summary.
- On R2, create two named prefix-lists:
  - One matching exactly `172.16.5.0/24`
  - One matching exactly `172.16.105.0/24`
- Create a route-map named `EIGRP_TO_OSPF` with three clauses:
  - Clause 10: match the first prefix-list; set metric type to `type-1` (E1)
  - Clause 20: match the second prefix-list; set metric type to `type-2` (E2)
  - Clause 30: permit all remaining (catch-all)
- Redistribute EIGRP AS 100 into OSPF using the route-map above. Include subnets.

**Verification:** `show ip eigrp neighbors` on R2 must show R5. `show ip ospf database external` on R1 must list both `172.16.5.0` and `172.16.105.0`. `show ip route ospf` on R3 should show both routes with their respective E1/E2 designations.

---

### Task 4: E1 vs E2 Metric Analysis

- On R3, examine the routing table entries for `172.16.5.0/24` (E1) and `172.16.105.0/24` (E2).
- Note the metric value for each route.
- Calculate the expected E1 metric: seed metric (default 20) plus the OSPF cost from R3 to R2 (via Area 1, point-to-point, reference bandwidth 1000 Mbps, FastEthernet = 10 cost).
- Confirm the E2 metric equals the seed metric only (20), unchanged regardless of internal path cost.

**Verification:** `show ip route 172.16.5.0` and `show ip route 172.16.105.0` on R3. The E1 route metric must be higher than the E2 metric. Both must be reachable (ping from R3 to `172.16.5.1` and `172.16.105.1`).

---

## 6. Verification & Analysis

### Task 1 — SHA-256 Auth on Area 0

```
R1# show ip ospf neighbor
Neighbor ID   Pri  State    Dead Time  Address     Interface
10.2.2.2       0   FULL/  -  00:00:38   10.12.0.2   FastEthernet1/0   ! ← R2 FULL
10.3.3.3       0   FULL/  -  00:00:35   10.13.0.2   FastEthernet1/1   ! ← R3 FULL

R1# show ip ospf interface FastEthernet1/0
FastEthernet1/0 is up, line protocol is up
  Internet Address 10.12.0.1/30, Area 0, Attached via Network Statement
  Process ID 1, Router ID 10.1.1.1, Network Type POINT_TO_POINT, Cost: 10
  Cryptographic authentication enabled
    Youngest key id is 1                                   ! ← key ID present
    Key chain name: OSPF_AUTH                              ! ← correct key-chain
  SHA-256 HMAC-based Message Digest algorithm            ! ← correct algorithm
```

### Task 2 — MD5 Auth on Area 1

```
R2# show ip ospf interface FastEthernet1/0
FastEthernet1/0 is up, line protocol is up
  Internet Address 10.23.0.1/30, Area 1, Attached via Network Statement
  Process ID 1, Router ID 10.2.2.2, Network Type POINT_TO_POINT, Cost: 10
  Message digest authentication enabled                  ! ← MD5 enabled
    Youngest key id is 1                                  ! ← key ID matches

R2# show ip ospf neighbor
Neighbor ID   Pri  State    Dead Time  Address     Interface
10.1.1.1       0   FULL/  -  00:00:31   10.12.0.1   FastEthernet0/0   ! ← R1 FULL via SHA
10.3.3.3       0   FULL/  -  00:00:33   10.23.0.2   FastEthernet1/0   ! ← R3 FULL via MD5
```

### Task 3 — EIGRP Peering and Redistribution

```
R2# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface      Hold  Uptime    SRTT  RTO   Q   Seq
0   10.25.0.2       Fa1/1           14   00:02:11   20   200   0   4   ! ← R5 neighbor up

R1# show ip ospf database external
            OSPF Router with ID (10.1.1.1) (Process ID 1)

                Type-5 AS External Link States

  LS age: 87
  Options: (No TOS-capability, DC)
  LS Type: AS External Link
  Link State ID: 172.16.5.0 (External Network Number)        ! ← E1 route present
  Advertising Router: 10.2.2.2                               ! ← ASBR is R2
  ...
  External Route Tag: 0
  External Metric: 20 (Type 1)                               ! ← metric type-1

  LS age: 90
  Link State ID: 172.16.105.0 (External Network Number)      ! ← E2 route present
  Advertising Router: 10.2.2.2
  External Metric: 20 (Type 2)                               ! ← metric type-2
```

### Task 4 — E1 vs E2 Metric Comparison on R3

```
R3# show ip route ospf
...
O E1 172.16.5.0/24 [110/30] via 10.23.0.1, FastEthernet0/0     ! ← E1: cost 20+10=30
O E2 172.16.105.0/24 [110/20] via 10.23.0.1, FastEthernet0/0   ! ← E2: cost 20 (seed only)

R3# ping 172.16.5.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 172.16.5.1, timeout is 2 seconds:
!!!!!                                                           ! ← all 5 succeed
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/4 ms

R3# ping 172.16.105.1
!!!!!                                                           ! ← all 5 succeed
```

> **Analysis:** The E1 route (`172.16.5.0/24`) shows metric `30` on R3 because the seed metric (20, assigned at redistribution on R2) is added to R3's internal OSPF cost to reach R2 (cost 10, via the point-to-point Area 1 link). The E2 route (`172.16.105.0/24`) shows metric `20` — exactly the seed value — because E2 metrics are never incremented by internal path cost.

---

## 7. Verification Cheatsheet

### OSPF Authentication — Key-Chain (HMAC-SHA-256)

```
key chain <name>
 key <id>
  key-string <password>
  cryptographic-algorithm hmac-sha-256

interface <intf>
 ip ospf authentication key-chain <name>
```

| Command | Purpose |
|---------|---------|
| `show ip ospf interface <intf>` | Confirm auth type, key ID, and key-chain name |
| `show key chain` | List all configured key-chains and keys |
| `debug ip ospf adj` | View authentication negotiation in real time |

> **Exam tip:** Key-chain names are locally significant. Only the key-string and algorithm must match on both ends of the link.

---

### OSPF Authentication — Area MD5

```
router ospf 1
 area <N> authentication message-digest

interface <intf>
 ip ospf message-digest-key <id> md5 <password>
 ip ospf authentication message-digest
```

| Command | Purpose |
|---------|---------|
| `show ip ospf interface` | Shows `Message digest authentication enabled` if MD5 is active |
| `show ip ospf` | Lists areas with authentication mode |

> **Exam tip:** `area N authentication` enables plain-text auth for the area. `area N authentication message-digest` enables MD5. The interface command `ip ospf authentication message-digest` overrides the area setting per-interface if needed.

---

### EIGRP Configuration

```
router eigrp <AS>
 network <subnet> <wildcard>
 no auto-summary
```

| Command | Purpose |
|---------|---------|
| `show ip eigrp neighbors` | Verify neighbor adjacency is up |
| `show ip eigrp topology` | View EIGRP topology table |
| `show ip route eigrp` | See EIGRP-learned routes in the routing table |

---

### OSPF Redistribution with Metric-Type Control

```
ip prefix-list <name> seq 5 permit <prefix/len>

route-map <name> permit 10
 match ip address prefix-list <list>
 set metric-type type-1

route-map <name> permit 20
 match ip address prefix-list <list>
 set metric-type type-2

route-map <name> permit 30

router ospf 1
 redistribute eigrp <AS> subnets route-map <name>
```

| Command | Purpose |
|---------|---------|
| `show ip ospf database external` | Verify external LSAs (Type 5) and their metric types |
| `show ip route ospf` | Confirm E1/E2 routes appear in the routing table |
| `show route-map <name>` | Confirm route-map match/set logic and hit counts |
| `show ip prefix-list` | Verify prefix-list entries |

> **Exam tip:** E1 routes are marked `O E1` in the routing table; E2 routes are `O E2`. Without `subnets` in the `redistribute` command, only classful networks are redistributed — individual subnets like `172.16.5.0/24` will be dropped.

---

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip ospf neighbor` | All expected neighbors in `FULL` state |
| `show ip ospf interface <intf>` | Authentication type (SHA / MD5), key ID, FULL state |
| `show ip ospf database external` | Type-5 LSAs with correct metric types |
| `show ip route ospf` | `O E1` and `O E2` entries present |
| `show ip eigrp neighbors` | R5 neighbor shows on R2 |
| `show route-map EIGRP_TO_OSPF` | Match counts > 0 for clauses 10 and 20 |
| `ping 172.16.5.1 source Lo0` | End-to-end reachability from R1 or R3 |

---

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard Mask | Common Use |
|-------------|---------------|------------|
| /30 | 0.0.0.3 | Point-to-point links |
| /24 | 0.0.0.255 | Standard subnets |
| /32 | 0.0.0.0 | Host routes, loopbacks |

---

### Common Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Adjacency drops after adding auth | Key-string mismatch or algorithm mismatch |
| `show ip ospf interface` shows no auth | Key-chain not applied to interface |
| External routes missing from R1/R3 | `redistribute` command missing or lacks `subnets` |
| Both external routes show E2 | Route-map not attached to `redistribute`, or wrong clause order |
| E1 metric unexpectedly low | Reference bandwidth mismatch — check `auto-cost reference-bandwidth` |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Objective 1 & 2: OSPF Authentication (SHA-256 + MD5)

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
key chain OSPF_AUTH
 key 1
  key-string Cisco$ecure123
  cryptographic-algorithm hmac-sha-256
!
interface FastEthernet1/0
 ip ospf authentication key-chain OSPF_AUTH
!
interface FastEthernet1/1
 ip ospf authentication key-chain OSPF_AUTH
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2
key chain OSPF_AUTH
 key 1
  key-string Cisco$ecure123
  cryptographic-algorithm hmac-sha-256
!
interface FastEthernet0/0
 ip ospf authentication key-chain OSPF_AUTH
!
interface FastEthernet1/0
 ip ospf message-digest-key 1 md5 OspfMd5Key1
 ip ospf authentication message-digest
!
router ospf 1
 area 1 authentication message-digest
```
</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3
key chain OSPF_AUTH
 key 1
  key-string Cisco$ecure123
  cryptographic-algorithm hmac-sha-256
!
interface FastEthernet0/0
 ip ospf message-digest-key 1 md5 OspfMd5Key1
 ip ospf authentication message-digest
!
interface FastEthernet1/0
 ip ospf authentication key-chain OSPF_AUTH
!
router ospf 1
 area 1 authentication message-digest
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip ospf neighbor
show ip ospf interface FastEthernet1/0
show ip ospf interface FastEthernet1/1
show key chain
```
</details>

---

### Objective 3: EIGRP Peering and Redistribution

<details>
<summary>Click to view R5 Configuration</summary>

```bash
! R5
router eigrp 100
 network 10.25.0.0 0.0.0.3
 network 172.16.5.0 0.0.0.255
 network 172.16.105.0 0.0.0.255
 no auto-summary
```
</details>

<details>
<summary>Click to view R2 Redistribution Configuration</summary>

```bash
! R2
ip prefix-list E1_ROUTES seq 5 permit 172.16.5.0/24
ip prefix-list E2_ROUTES seq 5 permit 172.16.105.0/24
!
route-map EIGRP_TO_OSPF permit 10
 match ip address prefix-list E1_ROUTES
 set metric-type type-1
!
route-map EIGRP_TO_OSPF permit 20
 match ip address prefix-list E2_ROUTES
 set metric-type type-2
!
route-map EIGRP_TO_OSPF permit 30
!
router eigrp 100
 network 10.25.0.0 0.0.0.3
 no auto-summary
!
router ospf 1
 redistribute eigrp 100 subnets route-map EIGRP_TO_OSPF
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip eigrp neighbors
show ip ospf database external
show ip route ospf
show route-map EIGRP_TO_OSPF
```
</details>

---

### Objective 4: E1 vs E2 Metric Analysis

<details>
<summary>Click to view Expected Output on R3</summary>

```bash
R3# show ip route ospf
O E1 172.16.5.0/24 [110/30] via 10.23.0.1, FastEthernet0/0
!  E1 metric = seed (20) + OSPF cost R3→R2 via Area 1 (10) = 30

O E2 172.16.105.0/24 [110/20] via 10.23.0.1, FastEthernet0/0
!  E2 metric = seed (20) only — internal cost not added

R3# show ip route 172.16.5.0
Routing entry for 172.16.5.0/24
  Known via "ospf 1", distance 110, metric 30, type extern 1
  ...

R3# show ip route 172.16.105.0
Routing entry for 172.16.105.0/24
  Known via "ospf 1", distance 110, metric 20, type extern 2
  ...
```
</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                    # reset to known-good
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore
```

---

### Ticket 1 — R1 Loses Both Area 0 Adjacencies

The operations team reports that R1 suddenly shows no OSPF neighbors on the backbone links. The router was working correctly until a junior engineer "updated the security keys" on R2 and R3 earlier today.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip ospf neighbor` on R1 shows both R2 and R3 in `FULL` state.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Run `show ip ospf neighbor` on R1 — expect to see no neighbors or neighbors stuck in ATTEMPT/INIT.
2. Run `show ip ospf interface FastEthernet1/0` on R1 — check the key ID and auth type displayed.
3. Run `show key chain` on R1 — note the key-string (it is not shown in plaintext, but the key ID is visible).
4. Run `show ip ospf interface FastEthernet0/0` on R2 — compare the key ID.
5. Run `debug ip ospf adj` briefly — look for `Authentication error` messages.
6. The fault is an OSPF key-string mismatch on R2 and R3 — the `OSPF_AUTH` key-chain `key 1` has a different `key-string` than R1.
</details>

<details>
<summary>Click to view Fix</summary>

On R2 and R3, correct the key-chain key-string to match R1:

```bash
! On R2
key chain OSPF_AUTH
 key 1
  key-string Cisco$ecure123

! On R3
key chain OSPF_AUTH
 key 1
  key-string Cisco$ecure123
```

Verify with `show ip ospf neighbor` — both adjacencies should reform within 10–40 seconds.
</details>

---

### Ticket 2 — External Partner Routes Absent from R1 and R3

The network team confirms R2 and R5 have an active EIGRP neighbor relationship, but neither R1 nor R3 can see the partner research subnets (`172.16.5.0/24` and `172.16.105.0/24`) in their routing tables.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip route ospf` on R1 and R3 shows both `O E1` and `O E2` entries for the research subnets.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R2, run `show ip eigrp neighbors` — confirm R5 is up.
2. On R2, run `show ip route eigrp` — confirm R2 has the partner subnets in its table.
3. On R2, run `show ip ospf database external` — if empty, the routes are not being redistributed.
4. On R2, run `show running-config | section ospf` — check whether a `redistribute eigrp 100 subnets` statement exists.
5. The fault is a missing `redistribute` statement under the OSPF process on R2.
</details>

<details>
<summary>Click to view Fix</summary>

On R2, add the redistribute statement:

```bash
router ospf 1
 redistribute eigrp 100 subnets route-map EIGRP_TO_OSPF
```

Verify with `show ip ospf database external` on R1 — both Type-5 LSAs should appear within seconds.
</details>

---

### Ticket 3 — External Routes Have Reversed Metric Types

The security audit confirms R1 can see both external subnets. However, the network architect reports the metric types are backwards: `172.16.5.0/24` is showing as `O E2` and `172.16.105.0/24` is showing as `O E1` — the opposite of what was specified in the design document.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip route ospf` on R3 shows `172.16.5.0/24` as `O E1` and `172.16.105.0/24` as `O E2`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R3, run `show ip route ospf` — confirm the metric type mismatch.
2. On R2, run `show route-map EIGRP_TO_OSPF` — examine which prefix-list each clause matches and what metric-type it sets.
3. On R2, run `show ip prefix-list` — examine what each prefix-list permits.
4. The fault is that the route-map `set metric-type` values in clauses 10 and 20 are swapped — clause 10 sets `type-2` and clause 20 sets `type-1`.
</details>

<details>
<summary>Click to view Fix</summary>

On R2, correct the route-map metric-type assignments:

```bash
route-map EIGRP_TO_OSPF permit 10
 match ip address prefix-list E1_ROUTES
 set metric-type type-1

route-map EIGRP_TO_OSPF permit 20
 match ip address prefix-list E2_ROUTES
 set metric-type type-2
```

Verify with `show ip route ospf` on R3 — `172.16.5.0/24` must show `O E1` and `172.16.105.0/24` must show `O E2`.
</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] Key-chain `OSPF_AUTH` configured with HMAC-SHA-256 on R1, R2, and R3
- [ ] SHA-256 authentication applied to all Area 0 interfaces (R1:Fa1/0, R1:Fa1/1, R2:Fa0/0, R3:Fa1/0)
- [ ] MD5 authentication enabled for Area 1 on R2 and R3 (process-level + interface key)
- [ ] All four OSPF adjacencies in `FULL` state (R1–R2, R1–R3, R2–R3)
- [ ] `show ip ospf interface` confirms correct auth type on each interface
- [ ] EIGRP AS 100 peering active between R2 and R5
- [ ] Both research subnets visible in R2's EIGRP topology table
- [ ] Redistribution configured with `subnets` and route-map `EIGRP_TO_OSPF`
- [ ] `172.16.5.0/24` appears as `O E1` on R1 and R3
- [ ] `172.16.105.0/24` appears as `O E2` on R1 and R3
- [ ] E1 metric on R3 equals seed (20) + internal cost (10) = 30
- [ ] E2 metric on R3 equals seed (20) only
- [ ] Ping from R3 to both `172.16.5.1` and `172.16.105.1` succeeds

### Troubleshooting

- [ ] Ticket 1 completed: key-string mismatch diagnosed and fixed
- [ ] Ticket 2 completed: missing redistribute statement identified and restored
- [ ] Ticket 3 completed: reversed E1/E2 metric-type assignments corrected
