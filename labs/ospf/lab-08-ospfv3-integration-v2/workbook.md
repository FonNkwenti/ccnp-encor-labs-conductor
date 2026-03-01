# CCNP ENCOR — OSPF Lab 08: OSPFv3 Dual-Stack Integration

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

**Exam Objective:** 3.2.a — Compare routing protocol types (area types, path selection) | 3.2.b — Configure simple OSPFv2/v3 (neighbor adjacency, multiple normal areas, network types)

OSPFv3 is the modern evolution of OSPF designed natively for IPv6. Through its **Address Family** (AF) model, OSPFv3 can simultaneously carry both IPv4 and IPv6 routing information within a single process — a significant architectural advantage over running separate OSPFv2 and OSPFv3 processes. This lab extends the existing OSPFv2 backbone with OSPFv3 AF, adding a new dual-stack border router (R6) and enabling full IPv4 and IPv6 reachability across all four routers.

---

### OSPFv3 vs OSPFv2 — Key Differences

| Feature | OSPFv2 | OSPFv3 |
|---------|--------|--------|
| Native address family | IPv4 only | IPv6 (and IPv4 via AF) |
| Interface activation | `network` statements | Per-interface `ospfv3` commands |
| Router-ID | 32-bit IPv4 address | 32-bit value (still dotted-decimal) |
| Authentication | MD5 / SHA via interface | IPsec (area-level) |
| Link-local addresses | Not used | Used for neighbor discovery |
| Multiple AFs | Not supported | IPv4 unicast + IPv6 unicast |

OSPFv3 uses **link-local addresses** (FE80::/10) for all neighbor relationships and hello packets. Global unicast addresses are used for the routing information itself. This means OSPFv3 adjacencies form using link-local addresses even when global unicast IPv6 is configured.

---

### OSPFv3 Address Families

The OSPFv3 AF model allows a single OSPFv3 process to run independent routing instances for IPv4 and IPv6. Each address family maintains its own LSDB, SPF tree, and routing table.

```
router ospfv3 1
 router-id 10.1.1.1
 !
 address-family ipv4 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
 !
 address-family ipv6 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
```

Key points:
- `router-id` is configured once at the process level — it applies to both AFs.
- `auto-cost reference-bandwidth` must be configured **inside each AF** independently.
- The process-level `router ospfv3` block does not carry routing config itself — everything goes inside the AF blocks or on interfaces.

---

### OSPFv3 Interface Activation

Unlike OSPFv2, OSPFv3 does not use `network` statements. Interfaces are activated per-AF directly on the interface:

```
interface FastEthernet1/0
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
```

Both commands are required to participate in both AFs on the same interface. An interface with only `ospfv3 1 ipv6 area 0` will exchange IPv6 routes only; IPv4 routes will not be carried over that link by OSPFv3.

For loopback interfaces, OSPFv3 treats them as stub networks (cost 1 by default, unless overridden):
```
interface Loopback0
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
```

> **Exam tip:** `ipv6 unicast-routing` must be enabled globally before OSPFv3 can form IPv6 adjacencies. This is the single most common mistake when bringing up OSPFv3 for the first time.

---

### IPv6 Addressing Conventions

This lab uses the `2001:DB8::/32` documentation prefix range (RFC 3849). Subnet conventions:

| Link | IPv6 Subnet | R-near | R-far |
|------|-------------|--------|-------|
| R1–R2 | 2001:DB8:12::/64 | ::1 | ::2 |
| R1–R3 | 2001:DB8:13::/64 | ::1 | ::3 |
| R2–R3 | 2001:DB8:23::/64 | ::2 | ::3 |
| R1–R6 | 2001:DB8:16::/64 | ::1 | ::6 |

Loopbacks use /128 host routes:
- R1: `2001:DB8:1::1/128`, R2: `2001:DB8:2::2/128`, R3: `2001:DB8:3::3/128`, R6: `2001:DB8:6::6/128`

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| IPv6 interface addressing | Configure global unicast addresses on physical and loopback interfaces |
| OSPFv3 process configuration | Initialize OSPFv3 with router-ID and dual-AF (ipv4 + ipv6 unicast) |
| OSPFv3 interface activation | Enable both AFs on every OSPF-participating interface |
| Dual-stack routing verification | Confirm both IPv4 and IPv6 routes appear via `show ip route` and `show ipv6 route` |
| OSPFv3 neighbor analysis | Use `show ospfv3 neighbor` to verify per-AF adjacency state |

---

## 2. Topology & Scenario

### Scenario

Skynet Global is expanding its backbone to full dual-stack operation. R6, a new Dual-Stack Border router, has been cabled into R1's GigabitEthernet port to serve as the IPv6 gateway for a future partner segment. The network architect has selected OSPFv3 with Address Families as the unified routing protocol — it will carry both IPv4 and IPv6 routing information over the same adjacencies, eliminating the need for two separate routing processes.

Your task is to enable IPv6 on all backbone interfaces, bring up OSPFv3 alongside the existing OSPFv2 deployment, and verify that every router has full dual-stack reachability to every other router's loopback addresses.

### ASCII Topology

```
                ┌───────────────────────────────┐
                │              R1               │
                │          (Hub / ABR)          │
                │  IPv4 Lo0: 10.1.1.1/32        │
                │  IPv6 Lo0: 2001:DB8:1::1/128  │
                └──────┬────────────┬─────┬─────┘
             Fa1/0     │            │     │  Gi3/0
       10.12.0.1/30    │            │     │  10.16.0.1/30
    2001:DB8:12::1     │            │     │  2001:DB8:16::1
           Area 0      │            │     │  Area 0
       10.12.0.2/30    │            │     │  10.16.0.2/30
    2001:DB8:12::2     │            │     │  2001:DB8:16::6
             Fa0/0     │            │     │  Gi3/0
     ┌─────────────────┘            │     └─────────────────────────┐
     │                              │                               │
┌────┴──────────────┐               │               ┌──────────────┴────┐
│       R2          │               │               │       R6          │
│   (Backbone)      │               │               │  (Dual-Stack      │
│ IPv4: 10.2.2.2/32 │               │               │   Border)         │
│ IPv6: 2001:DB8:   │               │               │ IPv4: 10.6.6.6/32 │
│       2::2/128    │               │               │ IPv6: 2001:DB8:   │
└────────┬──────────┘               │               │       6::6/128    │
    Fa1/0│                     Fa1/1│               └───────────────────┘
10.23.0.1/30               10.13.0.1/30
2001:DB8:23::2             2001:DB8:13::1
  Area 1                     Area 0
10.23.0.2/30               10.13.0.2/30
2001:DB8:23::3             2001:DB8:13::3
    Fa0/0│                     Fa1/0│
    ┌────┴─────────────────────────┴────┐
    │                R3                 │
    │            (Branch)               │
    │  IPv4 Lo0: 10.3.3.3/32            │
    │  IPv6 Lo0: 2001:DB8:3::3/128      │
    └───────────────────────────────────┘

  Area 0 (Backbone): R1–R2, R1–R3, R1–R6
  Area 1:            R2–R3
```

---

## 3. Hardware & Environment Specifications

### Device Summary

| Device | Role | Platform | IPv4 Loopback | IPv6 Loopback | Console |
|--------|------|----------|---------------|---------------|---------|
| R1 | Hub / ABR | c7200 | 10.1.1.1/32 | 2001:DB8:1::1/128 | 5001 |
| R2 | Backbone | c7200 | 10.2.2.2/32 | 2001:DB8:2::2/128 | 5002 |
| R3 | Branch | c7200 | 10.3.3.3/32 | 2001:DB8:3::3/128 | 5003 |
| R6 | Dual-Stack Border | c7200 | 10.6.6.6/32 | 2001:DB8:6::6/128 | 5006 |

### Cabling & IP Addressing

| Local Intf | Local | Remote | Remote Intf | IPv4 Subnet | IPv6 Subnet | Area |
|-----------|-------|--------|------------|-------------|-------------|------|
| Fa1/0 | R1 | R2 | Fa0/0 | 10.12.0.0/30 | 2001:DB8:12::/64 | Area 0 |
| Fa1/1 | R1 | R3 | Fa1/0 | 10.13.0.0/30 | 2001:DB8:13::/64 | Area 0 |
| Gi3/0 | R1 | R6 | Gi3/0 | 10.16.0.0/30 | 2001:DB8:16::/64 | Area 0 |
| Fa1/0 | R2 | R3 | Fa0/0 | 10.23.0.0/30 | 2001:DB8:23::/64 | Area 1 |

### Console Access Table

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R6 | 5006 | `telnet 127.0.0.1 5006` |

---

## 4. Base Configuration

The `initial-configs/` directory pre-loads the following:

**Pre-configured:**
- Hostnames and IPv4 interface addresses on all devices
- Loopback0 IPv4 addresses on all devices
- R1: Gi3/0 connected to R6 with IPv4 address
- OSPFv2 process 1 running on R1, R2, R3 with authentication (SHA-256 on Area 0, MD5 on Area 1)
- R6: IPv4 addressing only, no routing protocol

**NOT pre-configured (you configure these):**
- Global IPv6 unicast routing (`ipv6 unicast-routing`)
- IPv6 addresses on any interface or loopback
- OSPFv3 process on any router
- OSPFv3 interface activation (neither `ipv4` nor `ipv6` AF)
- Any reference bandwidth under OSPFv3 address families

---

## 5. Lab Challenge: Core Implementation

### Task 1: Enable IPv6 and Configure Dual-Stack Addressing

- Enable IPv6 unicast routing globally on all four routers (R1, R2, R3, R6).
- On each router, add an IPv6 global unicast address to `Loopback0` using the `/128` host prefix from the addressing table.
- On each physical link, add an IPv6 global unicast address to the local interface using the `/64` prefix and the last octet that matches the device number (e.g., R1 uses `::1`, R2 uses `::2`).

**Verification:** `show ipv6 interface brief` on each router must show all relevant interfaces as `up/up` with the correct global unicast address. `ping` between adjacent IPv6 addresses must succeed.

---

### Task 2: Configure the OSPFv3 Process

- Initialize OSPFv3 process `1` on all four routers.
- Set the router-ID to match each router's IPv4 loopback address (R1 = `10.1.1.1`, R2 = `10.2.2.2`, R3 = `10.3.3.3`, R6 = `10.6.6.6`).
- Inside the process, enable the `ipv4 unicast` address family and set `auto-cost reference-bandwidth 1000`.
- Enable the `ipv6 unicast` address family and set `auto-cost reference-bandwidth 1000`.

**Verification:** `show ospfv3` on each router must display the process, router-ID, and both address families. `show ospfv3 neighbor` should initially show no neighbors (interfaces not yet activated).

---

### Task 3: Activate OSPFv3 on All Interfaces

- On every OSPF-participating interface (physical and loopback), apply both the IPv4 and IPv6 OSPFv3 activation commands using the correct area assignment:
  - Area 0: R1 Fa1/0, Fa1/1, Gi3/0, Lo0 | R2 Fa0/0, Lo0 | R6 Gi3/0, Lo0
  - Area 1: R2 Fa1/0 | R3 Fa0/0 | R3 Lo0
  - Area 0 on R3: R3 Fa1/0
- Do NOT use `network` statements or the legacy `ipv6 ospf` command.

**Verification:** `show ospfv3 neighbor` on R1 must show three neighbors (R2, R3, R6). `show ospfv3 neighbor` on R2 must show two neighbors (R1, R3). All adjacencies must be in `FULL` state.

---

### Task 4: Verify Dual-Stack Routing Tables

- On R6, confirm that both IPv4 and IPv6 routes to all other routers' loopbacks appear in the routing table.
- On R3, confirm the same for IPv6 — routes to R1, R2, and R6 loopbacks must be present.
- Ping R6's IPv6 loopback (`2001:DB8:6::6`) from R3 and confirm end-to-end reachability.

**Verification:** `show ip route ospf` and `show ipv6 route ospf` on R3 and R6. Ping `2001:DB8:6::6` sourced from R3's Loopback0. All pings must succeed.

---

## 6. Verification & Analysis

### Task 1 — IPv6 Addressing

```
R1# show ipv6 interface brief
FastEthernet1/0            [up/up]
    FE80::...                                         ! ← link-local (auto-assigned)
    2001:DB8:12::1                                    ! ← global unicast
FastEthernet1/1            [up/up]
    FE80::...
    2001:DB8:13::1                                    ! ← global unicast
GigabitEthernet3/0         [up/up]
    FE80::...
    2001:DB8:16::1                                    ! ← global unicast
Loopback0                  [up/up]
    FE80::...
    2001:DB8:1::1                                     ! ← /128 host route
```

### Task 2 — OSPFv3 Process

```
R1# show ospfv3
OSPFv3 1 address-family ipv4 (router-id 10.1.1.1)
  ...
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa  ! ← area 0 only
  ...
OSPFv3 1 address-family ipv6 (router-id 10.1.1.1)
  ...
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa  ! ← area 0 only on R1
```

### Task 3 — OSPFv3 Neighbors

```
R1# show ospfv3 neighbor
OSPFv3 1 address-family ipv4 (router-id 10.1.1.1)

Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
10.2.2.2          0   FULL/  -        00:00:33    3               FastEthernet1/0  ! ← R2 FULL
10.3.3.3          0   FULL/  -        00:00:31    4               FastEthernet1/1  ! ← R3 FULL
10.6.6.6          0   FULL/  -        00:00:38    3               GigabitEthernet3/0  ! ← R6 FULL

OSPFv3 1 address-family ipv6 (router-id 10.1.1.1)

Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
10.2.2.2          0   FULL/  -        00:00:33    3               FastEthernet1/0  ! ← R2 FULL
10.3.3.3          0   FULL/  -        00:00:31    4               FastEthernet1/1  ! ← R3 FULL
10.6.6.6          0   FULL/  -        00:00:38    3               GigabitEthernet3/0  ! ← R6 FULL
```

### Task 4 — Dual-Stack Routing on R6

```
R6# show ip route ospf
O    10.1.1.1/32 [110/11] via 10.16.0.1, GigabitEthernet3/0     ! ← R1 loopback via OSPFv3 ipv4
O    10.2.2.2/32 [110/21] via 10.16.0.1, GigabitEthernet3/0     ! ← R2 loopback (via R1)
O    10.3.3.3/32 [110/21] via 10.16.0.1, GigabitEthernet3/0     ! ← R3 loopback (via R1)
O    10.12.0.0/30 [110/20] via 10.16.0.1, GigabitEthernet3/0
O    10.13.0.0/30 [110/20] via 10.16.0.1, GigabitEthernet3/0
O    10.23.0.0/30 [110/30] via 10.16.0.1, GigabitEthernet3/0

R6# show ipv6 route ospf
OI  2001:DB8:1::1/128 [110/11]                                   ! ← R1 IPv6 loopback
     via FE80::..., GigabitEthernet3/0
OI  2001:DB8:2::2/128 [110/21]                                   ! ← R2 IPv6 loopback
     via FE80::..., GigabitEthernet3/0
OI  2001:DB8:3::3/128 [110/21]                                   ! ← R3 IPv6 loopback
     via FE80::..., GigabitEthernet3/0

R3# ping 2001:DB8:6::6 source Loopback0
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2001:DB8:6::6, timeout is 2 seconds:
!!!!!                                                            ! ← all 5 succeed
Success rate is 100 percent (5/5)
```

> **Analysis:** OSPFv3 uses link-local addresses (FE80::) as the next-hop for IPv6 routes. The `via FE80::...` entries in `show ipv6 route` are normal — the link-local address identifies the outgoing interface's neighbor. The IPv4 routes under OSPFv3 use the global unicast next-hop (e.g., `10.16.0.1`) since IPv4 link-locals don't exist.

---

## 7. Verification Cheatsheet

### IPv6 Global Configuration

```
ipv6 unicast-routing
ipv6 cef

interface <intf>
 ipv6 address <prefix>/<len>
```

| Command | Purpose |
|---------|---------|
| `show ipv6 interface brief` | Confirm IPv6 addresses and interface state |
| `ping ipv6 <address>` | Test IPv6 reachability |
| `show ipv6 neighbors` | View IPv6 neighbor (NDP) cache |

> **Exam tip:** `ipv6 unicast-routing` is disabled by default on all Cisco IOS routers. Without it, the router will not forward IPv6 packets and OSPFv3 IPv6 adjacencies will not form.

---

### OSPFv3 Process Configuration

```
router ospfv3 <process-id>
 router-id <32-bit-id>
 !
 address-family ipv4 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
 !
 address-family ipv6 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
```

| Command | Purpose |
|---------|---------|
| `show ospfv3` | Display process, router-ID, and AF summaries |
| `show ospfv3 database` | View the OSPFv3 LSDB |
| `show ospfv3 database prefix` | View prefix LSAs for the IPv6 AF |

> **Exam tip:** OSPFv3 still requires a 32-bit router-ID in dotted-decimal notation, even in IPv6-only environments. If no IPv4 address exists on the router, configure the router-ID manually with `router-id`.

---

### OSPFv3 Interface Activation

```
interface <intf>
 ospfv3 <process-id> ipv4 area <area>
 ospfv3 <process-id> ipv6 area <area>
```

| Command | Purpose |
|---------|---------|
| `show ospfv3 interface <intf>` | Confirm OSPFv3 is enabled and show area/cost |
| `show ospfv3 neighbor` | List all neighbors per AF with state |
| `show ospfv3 neighbor detail` | Show full neighbor state including link-local |

> **Exam tip:** Each AF is activated independently. An interface with `ospfv3 1 ipv6 area 0` but no `ospfv3 1 ipv4 area 0` will exchange IPv6 routes only — IPv4 routes will not cross that link via OSPFv3.

---

### Dual-Stack Routing Verification

| Command | What to Look For |
|---------|-----------------|
| `show ip route ospf` | IPv4 routes learned via OSPFv3 — code `O` or `OI` |
| `show ipv6 route ospf` | IPv6 routes — `OI` for inter-area, `O` for intra-area |
| `show ospfv3 neighbor` | Both AFs listed, all neighbors `FULL` |
| `show ospfv3 interface brief` | All expected interfaces listed per AF |
| `ping ipv6 <addr> source Loopback0` | End-to-end IPv6 reachability |
| `show ospfv3 database` | Verify LSAs present for both AFs |

---

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard | Common Use |
|-------------|----------|------------|
| /30 | 0.0.0.3 | Point-to-point links |
| /32 | 0.0.0.0 | Host routes / loopbacks |
| /128 | — | IPv6 host routes (no wildcard) |
| /64 | — | IPv6 LAN/link subnets |

---

### Common OSPFv3 Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| No IPv6 OSPFv3 neighbors at all | `ipv6 unicast-routing` missing |
| IPv4 AF neighbors but no IPv6 AF | `ospfv3 1 ipv6 area N` missing on interface |
| Neighbors form but IPv6 routes missing | Loopback not activated in OSPFv3 IPv6 AF |
| Inter-area routes missing | Wrong area assigned on interface |
| Reference bandwidth inconsistency | `auto-cost reference-bandwidth` differs between routers or AFs |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Objective 1 & 2: IPv6 Addressing and OSPFv3 Process

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
ipv6 unicast-routing
ipv6 cef
!
interface Loopback0
 ipv6 address 2001:DB8:1::1/128
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
interface FastEthernet1/0
 ipv6 address 2001:DB8:12::1/64
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
interface FastEthernet1/1
 ipv6 address 2001:DB8:13::1/64
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
interface GigabitEthernet3/0
 ipv6 address 2001:DB8:16::1/64
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
router ospfv3 1
 router-id 10.1.1.1
 !
 address-family ipv4 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
 !
 address-family ipv6 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2
ipv6 unicast-routing
ipv6 cef
!
interface Loopback0
 ipv6 address 2001:DB8:2::2/128
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
interface FastEthernet0/0
 ipv6 address 2001:DB8:12::2/64
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
interface FastEthernet1/0
 ipv6 address 2001:DB8:23::2/64
 ospfv3 1 ipv4 area 1
 ospfv3 1 ipv6 area 1
!
router ospfv3 1
 router-id 10.2.2.2
 !
 address-family ipv4 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
 !
 address-family ipv6 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
```
</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3
ipv6 unicast-routing
ipv6 cef
!
interface Loopback0
 ipv6 address 2001:DB8:3::3/128
 ospfv3 1 ipv4 area 1
 ospfv3 1 ipv6 area 1
!
interface FastEthernet0/0
 ipv6 address 2001:DB8:23::3/64
 ospfv3 1 ipv4 area 1
 ospfv3 1 ipv6 area 1
!
interface FastEthernet1/0
 ipv6 address 2001:DB8:13::3/64
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
router ospfv3 1
 router-id 10.3.3.3
 !
 address-family ipv4 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
 !
 address-family ipv6 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
```
</details>

<details>
<summary>Click to view R6 Configuration</summary>

```bash
! R6
ipv6 unicast-routing
ipv6 cef
!
interface Loopback0
 ipv6 address 2001:DB8:6::6/128
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
interface GigabitEthernet3/0
 ipv6 address 2001:DB8:16::6/64
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
router ospfv3 1
 router-id 10.6.6.6
 !
 address-family ipv4 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
 !
 address-family ipv6 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ospfv3
show ospfv3 neighbor
show ipv6 interface brief
show ip route ospf
show ipv6 route ospf
ping ipv6 2001:DB8:6::6 source Loopback0
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

### Ticket 1 — R6 Has No OSPFv3 Neighbors

A technician reports that R6 was added to the GNS3 topology but shows zero OSPFv3 neighbors. R1 also shows R6 as missing from its neighbor table. All physical interfaces are up.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ospfv3 neighbor` on R1 shows R6 in `FULL` state for both AFs.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R6, run `show ospfv3 neighbor` — confirm no neighbors.
2. On R6, run `show ipv6 interface GigabitEthernet3/0` — check if IPv6 is enabled.
3. On R6, run `show running-config | include unicast-routing` — if empty, IPv6 forwarding is disabled.
4. On R6, run `show running-config | section ospfv3` — confirm process exists.
5. The fault is `no ipv6 unicast-routing` on R6. Without IPv6 forwarding enabled, OSPFv3 cannot form IPv6 adjacencies — even the IPv6 AF of OSPFv3 fails to bring up neighbors.
</details>

<details>
<summary>Click to view Fix</summary>

On R6, enable IPv6 unicast routing:

```bash
ipv6 unicast-routing
```

The OSPFv3 process will automatically detect the change and begin forming adjacencies. Verify with `show ospfv3 neighbor` on R1 — R6 should appear in `FULL` state within 40 seconds.
</details>

---

### Ticket 2 — R3 IPv6 Loopback Unreachable from R1 and R6

The IPv4 loopback of R3 (`10.3.3.3`) is reachable from all routers, but attempts to ping R3's IPv6 loopback (`2001:DB8:3::3`) from R1 and R6 fail with no route to host.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ipv6 route ospf` on R1 includes `2001:DB8:3::3/128`. Ping from R6 to `2001:DB8:3::3` succeeds.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, run `show ipv6 route ospf` — confirm `2001:DB8:3::3/128` is absent.
2. On R3, run `show ospfv3 interface` — check whether `Loopback0` appears in the list for the IPv6 AF.
3. On R3, run `show running-config interface Loopback0` — check for `ospfv3 1 ipv6 area 1`.
4. If the loopback is missing the `ospfv3 1 ipv6 area 1` command, the IPv6 host route is not being advertised into OSPFv3.
5. Note that the IPv4 loopback works because `ospfv3 1 ipv4 area 1` may still be present — only the IPv6 AF was removed.
</details>

<details>
<summary>Click to view Fix</summary>

On R3, reactivate the IPv6 AF on Loopback0:

```bash
interface Loopback0
 ospfv3 1 ipv6 area 1
```

Verify with `show ipv6 route ospf` on R1 — `2001:DB8:3::3/128` should appear as an `OI` (inter-area) route within seconds.
</details>

---

### Ticket 3 — R6 Has No IPv4 Routes in Its Routing Table

R6 can ping IPv6 addresses across the network but its `show ip route` shows no OSPF entries — the IPv4 routing table is empty except for connected routes.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip route ospf` on R6 lists loopbacks and subnets for R1, R2, and R3.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R6, run `show ip route ospf` — confirm no OSPF IPv4 entries.
2. On R6, run `show ipv6 route ospf` — confirm IPv6 routes are present (IPv6 AF is working).
3. On R6, run `show ospfv3 interface GigabitEthernet3/0` — check which AFs are enabled on the interface.
4. On R6, run `show running-config interface GigabitEthernet3/0` — look for `ospfv3 1 ipv4 area 0`.
5. The fault is that `ospfv3 1 ipv4 area 0` was removed from R6's Gi3/0. Without it, R6 does not participate in the IPv4 unicast AF — it has IPv6 adjacency only.
</details>

<details>
<summary>Click to view Fix</summary>

On R6, re-enable the IPv4 AF on GigabitEthernet3/0:

```bash
interface GigabitEthernet3/0
 ospfv3 1 ipv4 area 0
```

Verify with `show ip route ospf` on R6 — IPv4 OSPF routes for R1, R2, and R3 loopbacks should appear immediately.
</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] `ipv6 unicast-routing` enabled on R1, R2, R3, R6
- [ ] IPv6 global unicast addresses configured on all physical interfaces and loopbacks
- [ ] OSPFv3 process 1 initialized on all four routers with correct router-IDs
- [ ] `auto-cost reference-bandwidth 1000` set in both ipv4 and ipv6 AFs on every router
- [ ] `ospfv3 1 ipv4 area N` and `ospfv3 1 ipv6 area N` applied to all OSPF interfaces
- [ ] R1 shows three OSPFv3 neighbors (R2, R3, R6) — FULL for both AFs
- [ ] R2 shows two OSPFv3 neighbors (R1, R3) — FULL for both AFs
- [ ] `show ip route ospf` on R6 includes loopbacks for R1, R2, R3
- [ ] `show ipv6 route ospf` on R6 includes IPv6 loopbacks for R1, R2, R3
- [ ] Ping from R3 (`source Loopback0`) to `2001:DB8:6::6` succeeds
- [ ] Ping from R6 (`source Loopback0`) to `2001:DB8:3::3` succeeds

### Troubleshooting

- [ ] Ticket 1 completed: `ipv6 unicast-routing` missing on R6 identified and restored
- [ ] Ticket 2 completed: R3 Loopback0 missing `ospfv3 1 ipv6 area 1` identified and restored
- [ ] Ticket 3 completed: R6 Gi3/0 missing `ospfv3 1 ipv4 area 0` identified and restored
