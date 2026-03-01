# CCNP ENCOR OSPF Lab 06: NSSA & Route Control
**Student Workbook & Instructor Guide**

---

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

**Exam Objective:** 3.2.a — Compare routing concepts of OSPF (area types including NSSA) | 3.2.b — Configure simple OSPFv2 environments including multiple normal areas, summarization, and filtering

The Not-So-Stubby Area (NSSA) solves a specific problem that neither a normal area nor a stub area can solve: how do you allow a peripheral area to import external routes into OSPF while still protecting it from the full weight of external LSAs from the rest of the domain? This lab builds on the multi-area topology from Lab 05 by connecting a new research router (R4) into Area 14. You will configure the area as an NSSA, observe the unique Type 7 LSA lifecycle — from origination on R4, translation at the ABR (R1), and propagation as Type 5 throughout the backbone — then tighten control further with Totally NSSA and inter-area summarization.

### The NSSA Problem Statement

A stub area solves routing-table bloat by blocking external (Type 5) LSAs — but it also prohibits any ASBR from residing inside it. This is a hard constraint: you cannot redistribute external routes from within a stub area at all.

NSSA relaxes this constraint. It allows an ASBR inside the area to originate **Type 7 (NSSA External) LSAs**, which flood only within the NSSA. At the ABR boundary, the ABR translates qualifying Type 7 LSAs into Type 5 LSAs and floods them into the rest of the OSPF domain. The area still blocks incoming Type 5 LSAs from outside, so internal routers are not exposed to the full external routing table from the backbone.

### Type 7 LSA — NSSA External

Type 7 LSAs are structurally similar to Type 5 (AS External) LSAs but have a limited flooding scope — they never leave the NSSA. Key fields:

| Field | Description |
|-------|-------------|
| LSA Type | 7 (NSSA External) |
| Flooding scope | NSSA area only — never crosses into Area 0 or other areas |
| Originated by | ASBR inside the NSSA |
| P-bit | Propagate bit — set to 1 tells the ABR to translate to Type 5 |
| Metric type | E1 (cost-inclusive) or E2 (flat metric, default) |

### Type 7 to Type 5 Translation

When a Type 7 LSA with P-bit=1 enters an ABR that connects the NSSA to Area 0, the ABR:

1. Creates a new Type 5 LSA with the same external prefix and metric.
2. Floods the Type 5 LSA throughout the entire OSPF domain (except other NSSAs and stub areas).
3. Sets itself as the advertising router in the Type 5 LSA — not R4.

If multiple ABRs connect to the same NSSA, only the ABR with the **highest router ID** performs the translation (election to prevent duplicate Type 5 LSAs).

```
R4 (ASBR) → Type 7 LSA (P-bit=1) → [NSSA Area 14] → R1 (ABR) → Type 5 LSA → [Area 0, Area 1, Area 2]
```

### Totally NSSA

Totally NSSA combines NSSA with the totally stubby restriction: the ABR filters all incoming Type 3 Summary LSAs and replaces them with a single default route. Type 7 LSAs can still be originated by internal ASBRs and translated by the ABR.

```
! ABR only — blocks Type 3 LSAs from entering, injects default route
router ospf 1
 area 14 nssa no-summary

! Internal NSSA routers — no change
router ospf 1
 area 14 nssa
```

### ABR Route Summarization

An ABR can aggregate specific prefixes from one area before advertising them into the backbone. For NSSA areas, `area range` controls the Type 5 LSAs that the ABR originates after translating Type 7s. The ABR can suppress individual translated routes and advertise only a summary.

```
router ospf 1
 area 14 range 10.4.0.0 255.255.0.0       ! summarize Area 14 intra-area routes
 area 1 range 10.23.0.0 255.255.255.0     ! summarize Area 1 toward backbone
```

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| NSSA configuration | Enabling Type 7 LSAs in a peripheral area with an ASBR |
| External route redistribution | Injecting connected subnets into OSPF as Type 7 LSAs |
| Type 7 → Type 5 translation | Observing ABR translation and P-bit behavior |
| Totally NSSA | Filtering inter-area Type 3 LSAs while retaining external import capability |
| ABR summarization | Aggregating area prefixes to reduce Type 3 and Type 5 LSA counts |

---

## 2. Topology & Scenario

**Enterprise Context:** Acme Corp's OSPF backbone (Area 0), distribution layer (Area 1), and branch stub (Area 2) are all operational from Lab 05. A new R&D router (R4) has been deployed in a dedicated research segment — Area 14. The research team runs simulated lab subnets on R4 that must be reachable from all parts of the enterprise, but R4 should not receive the full external routing table from the backbone. Your task is to bring R4 online in an NSSA, redistribute its research subnet into OSPF, verify the Type 7 → Type 5 translation at R1, then tighten the design with Totally NSSA and inter-area summarization.

### ASCII Diagram

```
                         ┌───────────────────────┐
                         │          R1           │
                         │      Hub / ABR        │
                         │   Lo0: 10.1.1.1/32    │
              Fa0/0      └───────┬───────┬───────┘      Fa0/0
        10.14.0.1/30             │       │             10.14.0.2/30
                                 │Area 0 │
        10.14.0.2/30    Fa1/0    │       │ Fa1/1    10.14.0.1/30
               ┌─────────────────┘       └─────────────────┐
               │                                           │
  ┌────────────┴────────┐                 ┌───────────────┴──────────┐
  │         R2          │                 │           R3             │
  │   Backbone Router   │                 │  Branch Router / ABR     │
  │   Lo0:10.2.2.2/32   │                 │   Lo0: 10.3.3.3/32       │
  └──────────┬──────────┘                 └────────────┬─────────────┘
         Fa0/1│                                    Fa1/1│
   10.23.0.1/30│ ◄── Area 1 ──────────────────►  │10.37.0.1/30
               │                                       │  Area 2 (Totally Stubby)
   10.23.0.2/30│                           10.37.0.2/30│
         Fa0/0 │                                 Fa0/0 │
             ┌─┘                                    ┌──┘
             │ (R2 Fa0/1 ↔ R3 Fa0/0 via 10.23.0.0/30)
             └──────────────────────────────────────┘

  ┌──────────────────────┐
  │         R4           │
  │     NSSA Router      │
  │  Lo0: 10.4.4.4/32    │     Loopback100: 172.16.4.1/24
  │  Lo100: 172.16.4.0/24│     (simulated research subnet)
  └──────────────────────┘

             R7 (Stub Router, Lo0: 10.7.7.7/32)
             connected to R3 Fa1/1 via 10.37.0.0/30
             — Area 2 (Totally Stubby) — configured from Lab 05
```

**Simplified layout:**

```
              ┌─────────────────────────┐
              │           R1            │
              │       Hub / ABR         │
              │    Lo0: 10.1.1.1/32     │
              └──┬──────────────────┬───┘
           Fa1/0 │    Fa1/1   Fa0/0 │
   10.12.0.0/30  │  10.13.0.0/30   │  10.14.0.0/30
     Area 0      │      Area 0     │  Area 14 (NSSA)
   10.12.0.2/30  │  10.13.0.2/30   │  10.14.0.2/30
           Fa0/0 │    Fa0/1   Fa0/0 │
    ┌────────────┘         ┌────────┘
    │                      │
┌───┴─────┐          ┌─────┴────┐       ┌───────────────────┐
│   R2    │          │   R3     │       │        R4         │
│Backbone │          │Branch/ABR│       │   NSSA / ASBR     │
│10.2.2.2 │          │10.3.3.3  │       │   10.4.4.4/32     │
└────┬────┘          └────┬─────┘       │  Lo100:172.16.4.0 │
Fa0/1│             Fa1/1  │             └───────────────────┘
     │◄─Area 1─►          │ Area 2
     │10.23.0.0/30        │10.37.0.0/30
     │              ┌─────┴─────┐
     └──────────────┤    R7     │
                    │Stub Router│
                    │10.7.7.7   │
                    └───────────┘
```

**Area Summary:**

| Area    | Routers          | Links                         | Type           |
|---------|------------------|-------------------------------|----------------|
| Area 0  | R1, R2, R3       | R1-R2 (10.12.0.0/30), R1-R3 (10.13.0.0/30) | Backbone |
| Area 1  | R2, R3           | R2-R3 (10.23.0.0/30)         | Normal         |
| Area 2  | R3 (ABR), R7     | R3-R7 (10.37.0.0/30)         | Totally Stubby |
| Area 14 | R1 (ABR), R4     | R1-R4 (10.14.0.0/30)         | NSSA           |

---

## 3. Hardware & Environment Specifications

### Device Summary

| Device | Platform | Role                  | Loopback0       | Console Port |
|--------|----------|-----------------------|-----------------|--------------|
| R1     | c7200    | Hub / ABR             | 10.1.1.1/32     | 5001         |
| R2     | c7200    | Backbone Router       | 10.2.2.2/32     | 5002         |
| R3     | c7200    | Branch Router / ABR   | 10.3.3.3/32     | 5003         |
| R4     | c7200    | NSSA Router / ASBR    | 10.4.4.4/32     | 5004         |
| R7     | c3725    | Stub Router (Area 2)  | 10.7.7.7/32     | 5007         |

### Cabling

| Link | Source     | Destination | Subnet          | Area            |
|------|------------|-------------|-----------------|-----------------|
| L1   | R1 Fa1/0   | R2 Fa0/0    | 10.12.0.0/30    | Area 0          |
| L2   | R2 Fa0/1   | R3 Fa0/0    | 10.23.0.0/30    | Area 1          |
| L3   | R1 Fa1/1   | R3 Fa0/1    | 10.13.0.0/30    | Area 0          |
| L4   | R1 Fa0/0   | R4 Fa0/0    | 10.14.0.0/30    | Area 14 (NSSA)  |
| L6   | R3 Fa1/1   | R7 Fa0/0    | 10.37.0.0/30    | Area 2 (Stub)   |

### Console Access Table

| Device | Port | Connection Command          |
|--------|------|-----------------------------|
| R1     | 5001 | `telnet 127.0.0.1 5001`     |
| R2     | 5002 | `telnet 127.0.0.1 5002`     |
| R3     | 5003 | `telnet 127.0.0.1 5003`     |
| R4     | 5004 | `telnet 127.0.0.1 5004`     |
| R7     | 5007 | `telnet 127.0.0.1 5007`     |

---

## 4. Base Configuration

The `initial-configs/` directory pre-loads the following:

**Pre-configured (carried forward from Lab 05):**
- Full OSPF multi-area topology: Area 0 (R1-R2, R1-R3), Area 1 (R2-R3), Area 2 Totally Stubby (R3-R7)
- R1 Fa0/0 interface with IP addressing for the R1-R4 link (not yet in OSPF)
- R4 hostname, Loopback0 (10.4.4.4/32), Loopback100 (172.16.4.1/24), and Fa0/0 IP addressing
- R7 fully configured as a Totally Stubby area router in Area 2

**NOT pre-configured — student must build:**
- OSPF routing process on R4
- Area 14 participation for R1 and R4
- NSSA configuration on Area 14
- External route redistribution on R4 (Loopback100)
- Totally NSSA configuration on R1
- ABR inter-area summarization

---

## 5. Lab Challenge: Core Implementation

### Task 1: Add R4 to the OSPF Domain in Area 14

- Enable an OSPF routing process on R4 with process ID 1. Set its router ID to its Loopback0 address.
- Advertise R4's Loopback0 and the R1-R4 link subnet into Area 14 as a **normal** (non-NSSA) area first — this gives you a baseline to compare.
- On R1, advertise the R1-R4 link subnet into Area 14 (normal area).
- Verify adjacency and confirm R4 receives inter-area routes from Area 0 and Area 1.

**Verification:** `show ip ospf neighbor` on R1 must show R4 in FULL state. `show ip route ospf` on R4 must display `O IA` routes for Area 0 and Area 1 subnets.

---

### Task 2: Configure Area 14 as NSSA and Redistribute External Routes

- Configure Area 14 as an NSSA on **both** R1 (ABR) and R4 (internal router). The adjacency will briefly drop and re-establish.
- On R4, configure a second loopback interface (Loopback100) with the address `172.16.4.1/24` to simulate a research subnet.
- On R4, redistribute connected interfaces into OSPF so the research subnet is injected as a Type 7 LSA into Area 14.
- Verify that R1's OSPF database contains a Type 7 LSA for `172.16.4.0/24`.
- Verify that R1 translates the Type 7 LSA into a Type 5 LSA and floods it into Area 0.
- Confirm the external route is visible in R2 and R3's routing tables.

**Verification:** `show ip ospf database nssa-external` on R4 must list `172.16.4.0`. `show ip ospf database external` on R2 must list `172.16.4.0` as a Type 5 LSA. `show ip route ospf` on R2 must show `O E2 172.16.4.0/24`.

---

### Task 3: Upgrade Area 14 to Totally NSSA

- Modify R1's NSSA configuration with the IOS keyword that suppresses all inter-area Type 3 Summary LSAs from entering Area 14 — only the default route should remain.
- R4's configuration requires **no change** for this step.
- Verify that R4's routing table loses all inter-area `O IA` routes and retains only the default route from OSPF.
- Confirm that the external route (`172.16.4.0/24`) is still being translated to Type 5 and visible in the backbone — Totally NSSA does not block Type 7 origination.

**Verification:** `show ip route ospf` on R4 must show only `O*IA 0.0.0.0/0` as an OSPF route. `show ip route ospf` on R2 must still show `O E2 172.16.4.0/24` — the external route must remain reachable from the backbone.

---

### Task 4: Configure ABR Summarization

- On R1, summarize the Area 14 intra-area prefixes (R4's loopback 10.4.4.4/32 and the link 10.14.0.0/30) toward the backbone using a single aggregate.
- Additionally, configure R1 to summarize the Area 1 prefix (10.23.0.0/30) toward the backbone.
- Verify that individual component prefixes are suppressed and only the summary routes appear in R2's routing table.

**Verification:** `show ip route ospf` on R2 must show the Area 14 summary and Area 1 summary as `O IA` entries. The individual component routes (10.4.4.4/32, 10.14.0.0/30, 10.23.0.0/30) must NOT appear as separate entries.

---

## 6. Verification & Analysis

### Task 1 Verification — R4 in Normal Area 14

```
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.2.2.2          1   FULL/  -        00:00:39    10.12.0.2       FastEthernet1/0
10.3.3.3          1   FULL/  -        00:00:36    10.13.0.2       FastEthernet1/1
10.4.4.4          1   FULL/DR         00:00:31    10.14.0.2       FastEthernet0/0  ! ← R4 must be FULL

R4# show ip route ospf
O IA  10.1.1.1 [110/2] via 10.14.0.1, 00:00:22, FastEthernet0/0  ! ← inter-area routes visible
O IA  10.2.2.2 [110/3] via 10.14.0.1, 00:00:22, FastEthernet0/0
O IA  10.3.3.3 [110/3] via 10.14.0.1, 00:00:22, FastEthernet0/0
O IA  10.12.0.0 [110/3] via 10.14.0.1, 00:00:22, FastEthernet0/0
O IA  10.13.0.0 [110/3] via 10.14.0.1, 00:00:22, FastEthernet0/0
O IA  10.23.0.0 [110/3] via 10.14.0.1, 00:00:22, FastEthernet0/0
```

### Task 2 Verification — NSSA with External Redistribution

```
R4# show ip ospf database nssa-external
            OSPF Router with ID (10.4.4.4) (Process ID 1)

                Type-7 AS External Link States (Area 14)
Link ID         ADV Router      Age  Seq#       Checksum Tag
172.16.4.0      10.4.4.4        45   0x80000001 0x00XXXX 0  ! ← Type 7 originated by R4

R1# show ip ospf database external
            OSPF Router with ID (10.1.1.1) (Process ID 1)

                Type-5 AS External Link States
Link ID         ADV Router      Age  Seq#       Checksum Tag
172.16.4.0      10.1.1.1        42   0x80000001 0x00XXXX 0  ! ← Type 5 translated by R1 (ADV Router = R1, not R4)

R2# show ip route ospf
O E2  172.16.4.0/24 [110/20] via 10.12.0.2, 00:00:30, FastEthernet0/0  ! ← external route reachable from backbone
O IA  10.4.4.4 [110/3] via 10.12.0.2, 00:00:30, FastEthernet0/0
O IA  10.14.0.0 [110/3] via 10.12.0.2, 00:00:30, FastEthernet0/0
```

### Task 3 Verification — Totally NSSA

```
R4# show ip ospf database
            OSPF Router with ID (10.4.4.4) (Process ID 1)

                Router Link States (Area 14)
Link ID         ADV Router      Age  Seq#       Checksum Link count
10.1.1.1        10.1.1.1          8  0x80000003 0x00XXXX 1
10.4.4.4        10.4.4.4          6  0x80000003 0x00XXXX 3

                Summary Net Link States (Area 14)
Link ID         ADV Router      Age  Seq#       Checksum
0.0.0.0         10.1.1.1          8  0x80000002 0x00XXXX  ! ← ONLY this Type 3 (default) remains

                Type-7 AS External Link States (Area 14)
Link ID         ADV Router      Age  Seq#       Checksum Tag
172.16.4.0      10.4.4.4          6  0x80000001 0x00XXXX 0  ! ← Type 7 still present (NSSA allows it)

R4# show ip route ospf
O*IA  0.0.0.0/0 [110/2] via 10.14.0.1, FastEthernet0/0  ! ← only OSPF route (default)
! No O IA inter-area routes — all suppressed by Totally NSSA

R2# show ip route ospf
O E2  172.16.4.0/24 [110/20] via ...  ! ← still reachable from backbone — Type 7 → Type 5 still occurs
```

### Task 4 Verification — ABR Summarization

```
R1# show ip ospf database summary
                Summary Net Link States (Area 0)
Link ID         ADV Router      Age  Seq#       Checksum
10.4.0.0        10.1.1.1         20  0x80000001 0x00XXXX  ! ← Area 14 summary originated by R1
10.23.0.0       10.1.1.1         20  0x80000001 0x00XXXX  ! ← Area 1 summary originated by R1

R2# show ip route ospf
O IA  10.4.0.0/14 [110/2] via 10.12.0.2, FastEthernet0/0   ! ← Area 14 summary (covers 10.4.4.4 + 10.14.0.0)
O IA  10.23.0.0/24 [110/2] via 10.12.0.2, FastEthernet0/0  ! ← Area 1 summary
O E2  172.16.4.0/24 [110/20] via 10.12.0.2, FastEthernet0/0
! Individual routes 10.4.4.4/32 and 10.14.0.0/30 must NOT appear
```

---

## 7. Verification Cheatsheet

### NSSA Configuration

```
router ospf 1
 area 14 nssa              ! Applied to ALL routers in NSSA (ABR and internal)
 area 14 nssa no-summary   ! Totally NSSA — ABR only (suppresses Type 3 LSAs)
```

| Command                          | Purpose                                                           |
|----------------------------------|-------------------------------------------------------------------|
| `area X nssa`                    | Configure NSSA — allows Type 7 LSAs, blocks incoming Type 5       |
| `area X nssa no-summary`         | Totally NSSA — also blocks inter-area Type 3 LSAs (ABR only)      |
| `area X nssa default-information-originate` | Force-originate default route into NSSA (normally automatic with no-summary) |
| `redistribute connected subnets` | Inject connected interfaces as Type 7 LSAs (on ASBR)             |

> **Exam tip:** In a Totally NSSA, `no-summary` is configured only on the ABR. Unlike Totally Stubby, the internal router still uses `area X nssa` (not `area X nssa no-summary`). The default route is automatically injected when `no-summary` is configured.

### Redistribution into NSSA

```
router ospf 1
 redistribute connected subnets
 redistribute static subnets
 redistribute eigrp 100 subnets metric 20 metric-type 2
```

| Command                              | What to Look For                                              |
|--------------------------------------|---------------------------------------------------------------|
| `redistribute connected subnets`     | Injects all connected interfaces as Type 7 NSSA LSAs          |
| `default-metric <value>`             | Sets the default metric for redistributed routes              |

### Database Verification

```
show ip ospf database
show ip ospf database nssa-external
show ip ospf database external
show ip ospf database summary
```

| Command                                | What to Look For                                                     |
|----------------------------------------|----------------------------------------------------------------------|
| `show ip ospf database nssa-external`  | Type 7 LSAs in the NSSA — originated by local ASBR                  |
| `show ip ospf database external`       | Type 5 LSAs in backbone — translated from Type 7 by ABR             |
| `show ip ospf database summary`        | Type 3 LSAs — default (0.0.0.0) only in Totally NSSA                |
| `show ip ospf`                         | Area type confirmation: "Area 14 is a NSSA" or "…stub, no summary"  |

### Routing Table Verification

| Command                  | What to Look For                                                            |
|--------------------------|-----------------------------------------------------------------------------|
| `show ip route ospf`     | `O E2` for external routes; `O*IA 0.0.0.0/0` in Totally NSSA on R4        |
| `show ip route`          | Gateway of last resort set to R1 address on R4 (Totally NSSA)              |
| `show ip ospf neighbor`  | R4 FULL state on R1; drops if area type mismatch (nssa vs normal)           |

### Wildcard Mask Quick Reference

| Subnet Mask         | Wildcard Mask   | Common Use                 |
|---------------------|-----------------|----------------------------|
| 255.255.255.255     | 0.0.0.0         | Host route / loopback      |
| 255.255.255.252     | 0.0.0.3         | /30 point-to-point link    |
| 255.255.255.0       | 0.0.0.255       | /24 redistributed subnet   |
| 255.255.0.0         | 0.0.255.255     | /16 summary range          |

### Common NSSA Failure Causes

| Symptom                                      | Likely Cause                                                           |
|----------------------------------------------|------------------------------------------------------------------------|
| R4 shows no OSPF neighbors                   | Area type mismatch (one side nssa, other side normal or stub)          |
| Type 7 LSA present on R4 but no Type 5 on R2 | P-bit cleared, or R1 is not the highest-RID ABR, or redistribution missing |
| R4 still receives full inter-area table       | `no-summary` not configured on R1 (ABR)                               |
| External route missing after Totally NSSA     | Redistribution was removed — Type 7 must still be originated by R4    |
| Summary route missing from backbone           | `area range` not configured or range too narrow to cover component prefixes |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: Add R4 to OSPF (Normal Area 14)

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — add Area 14 network statement (no NSSA yet)
router ospf 1
 network 10.14.0.0 0.0.0.3 area 14
```
</details>

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4
router ospf 1
 router-id 10.4.4.4
 network 10.4.4.4 0.0.0.0 area 14
 network 10.14.0.0 0.0.0.3 area 14
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip ospf neighbor
show ip route ospf
show ip ospf database
```
</details>

---

### Task 2: Configure NSSA and Redistribute External Routes

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — configure NSSA on the ABR
router ospf 1
 area 14 nssa
```
</details>

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4 — configure NSSA on internal router and add Loopback100
interface Loopback100
 description Simulated Research Subnet
 ip address 172.16.4.1 255.255.255.0
!
router ospf 1
 area 14 nssa
 redistribute connected subnets
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R4 — confirm Type 7 LSA originated
show ip ospf database nssa-external

! On R1 — confirm Type 5 translation
show ip ospf database external

! On R2 — confirm external route in routing table
show ip route ospf
```
</details>

---

### Task 3: Upgrade to Totally NSSA

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — add no-summary to suppress inter-area Type 3 LSAs
router ospf 1
 area 14 nssa no-summary
! R4 requires NO configuration change
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R4 — confirm only default route remains
show ip route ospf
show ip ospf database

! On R2 — confirm external route still present
show ip route ospf
```
</details>

---

### Task 4: ABR Summarization

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — summarize Area 14 prefixes and Area 1 prefix
router ospf 1
 area 14 range 10.4.0.0 255.252.0.0
 area 1 range 10.23.0.0 255.255.255.0
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R2 — confirm summary present, components absent
show ip route ospf

! On R1 — confirm null route and summary LSA
show ip route
show ip ospf database summary
```
</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only show commands and targeted configuration changes.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good state
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore after each ticket
```

---

### Ticket 1 — R4 Has No OSPF Neighbors After Area Migration

The NOC reports that R4 lost all OSPF adjacencies following a planned Area 14 migration. R4 was previously in a normal area; the migration was supposed to convert it to NSSA.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip ospf neighbor` on R1 shows R4 in FULL state. R4's routing table contains `O*IA 0.0.0.0/0`.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Check R4 neighbors
R4# show ip ospf neighbor
! Expected: empty — no neighbors

! Step 2: Verify area type on both sides
R1# show ip ospf
! Look for Area 14 type: "NSSA" or "Normal"
R4# show ip ospf
! Look for Area 14 type — must match R1

! Step 3: Check Hello packets
R4# debug ip ospf hello
! Look for: "Mismatched hello parameters" — N-bit (NSSA capability) mismatch

! Root cause: R1 has area 14 nssa configured; R4 does not (or vice versa).
! OSPF N-bit in Hello packets indicates NSSA capability — mismatch prevents adjacency.
```
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4 — add NSSA configuration to match R1
R4(config)# router ospf 1
R4(config-router)# area 14 nssa
! Adjacency re-establishes within one dead interval
```
</details>

---

### Ticket 2 — Research Subnet Not Reachable From Headquarters

R4's research subnet (172.16.4.0/24) should be reachable from all parts of the enterprise. The NOC reports that pings from R2 to 172.16.4.1 fail. R4 shows OSPF neighbors as FULL.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip route ospf` on R2 shows `O E2 172.16.4.0/24`. Pings from R2 to 172.16.4.1 succeed.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Check if Type 7 LSA exists on R4
R4# show ip ospf database nssa-external
! Expected (fault active): empty — no Type 7 LSA for 172.16.4.0

! Step 2: Check R4 routing table
R4# show ip route
! Confirm 172.16.4.0/24 is connected (Loopback100 up)

! Step 3: Check redistribution in OSPF config
R4# show running-config | section ospf
! Look for: "redistribute connected subnets" — if absent, Type 7 is not generated

! Step 4: Check if Type 5 exists on R2
R2# show ip ospf database external
! Expected (fault active): 172.16.4.0 absent — confirms redistribution is the issue

! Root cause: "redistribute connected subnets" removed from R4's OSPF process.
! Without redistribution, Loopback100 is not injected as a Type 7 LSA.
```
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4 — restore redistribution
R4(config)# router ospf 1
R4(config-router)# redistribute connected subnets
! Type 7 LSA generated immediately; R1 translates to Type 5 within SPF convergence
```
</details>

---

### Ticket 3 — R4 Routing Table Has Dozens of Inter-Area Routes

A junior engineer was asked to "simplify" Area 14's configuration and made changes to R1. Now R4's routing table shows all enterprise subnets instead of just a default route.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** R4's routing table shows only `O*IA 0.0.0.0/0` as an OSPF route. `show ip ospf database` on R4 shows only Type 1 Router LSAs, one Type 3 default, and one Type 7 for 172.16.4.0.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Check R4 routing table
R4# show ip route ospf
! Expected (fault active): many O IA routes — Area 14 receiving all inter-area Type 3 LSAs

! Step 2: Check R4's OSPF database
R4# show ip ospf database
! Look for: many "Summary Net Link States" entries — Type 3 LSAs flooding in

! Step 3: Verify Area 14 type on R1
R1# show ip ospf
! Look for Area 14 description: "is a NSSA" or "is a NSSA, no summary"
! If it says "is a NSSA" (without "no summary"), totally NSSA is not active

! Step 4: Check R1 running config
R1# show running-config | section ospf
! Look for: "area 14 nssa no-summary" — if only "area 14 nssa" present, no-summary was removed

! Root cause: "area 14 nssa no-summary" changed to "area 14 nssa" on R1.
! Area 14 reverted to regular NSSA — all inter-area Type 3 LSAs now flood in.
```
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — restore totally NSSA
R1(config)# router ospf 1
R1(config-router)# area 14 nssa no-summary
! R1 immediately withdraws inter-area Type 3 LSAs from Area 14 (except default route)
```
</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] R4 establishes OSPF adjacency with R1 in normal Area 14
- [ ] R4 routing table shows inter-area routes from Area 0 and Area 1 before NSSA config
- [ ] Area 14 configured as NSSA on both R1 and R4 — adjacency re-establishes
- [ ] Loopback100 (172.16.4.0/24) added on R4 and redistributed into OSPF
- [ ] `show ip ospf database nssa-external` on R4 shows Type 7 LSA for 172.16.4.0
- [ ] `show ip ospf database external` on R1/R2 shows Type 5 LSA for 172.16.4.0 — ADV Router is R1
- [ ] `O E2 172.16.4.0/24` visible in R2 and R3 routing tables
- [ ] Area 14 upgraded to Totally NSSA via `no-summary` on R1 only
- [ ] R4 routing table contains only `O*IA 0.0.0.0/0` — no other OSPF routes
- [ ] External route `172.16.4.0/24` still reachable from backbone after Totally NSSA
- [ ] ABR summarization configured on R1 for Area 14 and Area 1 prefixes
- [ ] Summary routes visible on R2 — component routes suppressed

### Troubleshooting

- [ ] Ticket 1 resolved: NSSA area type mismatch identified and corrected on R4
- [ ] Ticket 2 resolved: missing redistribution on R4 identified and restored
- [ ] Ticket 3 resolved: `no-summary` restored on R1; R4 routing table reduced to default only
