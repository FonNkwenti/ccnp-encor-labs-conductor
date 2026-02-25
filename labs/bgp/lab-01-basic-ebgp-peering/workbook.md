# CCNP ENCOR BGP Lab 01: Basic eBGP Peering
**Student Workbook**

---

## 1. Concepts & Skills Covered

- Configure eBGP neighbor relationships between directly connected peers
- Advertise prefixes using the BGP `network` statement
- Verify BGP neighbor states (Idle, Active, OpenSent, OpenConfirm, Established)
- Understand the difference between the BGP table and the IP routing table
- Examine BGP update messages and path attributes

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
**NexaTech Solutions** is an enterprise that has outgrown its single-ISP internet connectivity. The company has acquired its own BGP autonomous system (AS 65001) and is establishing eBGP peering with two internet service providers: **ISP-A** (AS 65002) and **ISP-B** (AS 65003). The two ISPs also peer with each other to provide transit connectivity.

As the Senior Network Engineer, your first task is to establish basic eBGP neighbor relationships across all three links of this triangle topology, advertise each organization's prefixes into BGP, and verify that the BGP table reflects full reachability across all three autonomous systems.

### Device Role Table
| Device | Role | Platform | AS | Loopback0 |
|--------|------|----------|----|-----------|
| R1 | Enterprise Edge | c7200 | 65001 | 172.16.1.1/32 |
| R2 | ISP-A | c7200 | 65002 | 172.16.2.2/32 |
| R3 | ISP-B | c7200 | 65003 | 172.16.3.3/32 |

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

The following is **pre-configured** in the initial-configs:

- Hostname on each router
- Loopback0 interface with IP addressing
- All physical interfaces with IP addressing and descriptions
- Console line settings (logging synchronous, no exec-timeout)

The following is **NOT pre-loaded** (you will configure these):

- BGP routing process
- BGP neighbor statements
- BGP network advertisements
- BGP router-id

---

## 5. Lab Challenge: Core Implementation

### Task 1: Enable BGP and Configure Router-IDs

- Enable the BGP routing process on all three routers, each using its own autonomous system number (R1 = 65001, R2 = 65002, R3 = 65003).
- Set the BGP router-id to match each router's Loopback0 address.

**Verification:** `show ip bgp summary` must show the correct AS number and router-id on each router.

---

### Task 2: Establish eBGP Neighbor Relationships

- On R1, configure eBGP peering with R2 using the directly connected link addresses (10.1.12.0/30 subnet).
- On R1, configure eBGP peering with R3 using the directly connected link addresses (10.1.13.0/30 subnet).
- On R2, configure eBGP peering with R1 and with R3 using the appropriate directly connected link addresses.
- On R3, configure eBGP peering with R1 and with R2 using the appropriate directly connected link addresses.
- All six neighbor statements must reference the remote AS correctly.

**Verification:** `show ip bgp summary` must show all neighbors in **Established** state (State/PfxRcvd column shows a number, not a state name).

---

### Task 3: Advertise Prefixes via the Network Statement

- On R1 (AS 65001), advertise the Enterprise prefixes: 192.168.1.0/24, 192.168.2.0/24, and 192.168.3.0/24. Ensure these prefixes exist in the routing table (create Loopback interfaces as needed).
- On R2 (AS 65002), advertise the ISP-A prefixes: 198.51.100.0/24, 198.51.101.0/24, and 198.51.102.0/24. Create Loopback interfaces to originate these prefixes.
- On R3 (AS 65003), advertise the ISP-B prefixes: 203.0.113.0/24, 203.0.114.0/24, and 203.0.115.0/24. Create Loopback interfaces to originate these prefixes.
- Also advertise each router's primary Loopback0 address (172.16.X.X/32) into BGP.

**Verification:** `show ip bgp` on each router must show all 12 prefixes (4 per AS: 3 advertised + 1 loopback) with valid next-hop addresses.

---

### Task 4: Verify End-to-End BGP Reachability

- From R1, verify that prefixes from AS 65002 and AS 65003 appear in the BGP table with correct AS-path information.
- Confirm that BGP best-path routes are installed in the IP routing table.
- Test reachability by pinging remote loopback addresses from R1 (172.16.2.2 and 172.16.3.3). Source the pings from R1's Loopback0.

**Verification:** `show ip route bgp` must show routes with the `B` code. `ping 172.16.2.2 source 172.16.1.1` and `ping 172.16.3.3 source 172.16.1.1` must succeed.

---

## 6. Verification & Analysis

### Task 1 Verification: BGP Process and Router-ID

```bash
R1# show ip bgp summary
BGP router identifier 172.16.1.1, local AS number 65001   ! ← router-id and AS correct
BGP table version is 13, main routing table version 13
12 network entries using 1680 bytes of memory                ! ← 12 prefixes total
...
```

### Task 2 Verification: Neighbor States

```bash
R1# show ip bgp summary
...
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcvd
10.1.12.2       4 65002      15      14       13    0    0 00:05:32        4   ! ← R2 Established, 4 prefixes
10.1.13.2       4 65003      15      14       13    0    0 00:05:28        4   ! ← R3 Established, 4 prefixes
```

```bash
R2# show ip bgp summary
...
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcvd
10.1.12.1       4 65001      14      15       13    0    0 00:05:32        4   ! ← R1 Established
10.1.23.2       4 65003      14      15       13    0    0 00:05:28        4   ! ← R3 Established
```

### Task 3 Verification: BGP Table with All Prefixes

```bash
R1# show ip bgp
BGP table version is 13, local router ID is 172.16.1.1
...
   Network          Next Hop            Metric LocPrf Weight Path
*> 172.16.1.1/32    0.0.0.0                  0         32768 i       ! ← local origin
*> 172.16.2.2/32    10.1.12.2                0             0 65002 i ! ← from R2
*> 172.16.3.3/32    10.1.13.2                0             0 65003 i ! ← from R3
*> 192.168.1.0/24   0.0.0.0                  0         32768 i       ! ← local
*> 192.168.2.0/24   0.0.0.0                  0         32768 i       ! ← local
*> 192.168.3.0/24   0.0.0.0                  0         32768 i       ! ← local
*  198.51.100.0/24  10.1.13.2                              0 65003 65002 i
*>                  10.1.12.2                0             0 65002 i ! ← best via R2 (shorter AS-path)
*  198.51.101.0/24  10.1.13.2                              0 65003 65002 i
*>                  10.1.12.2                0             0 65002 i ! ← best via R2
*  198.51.102.0/24  10.1.13.2                              0 65003 65002 i
*>                  10.1.12.2                0             0 65002 i ! ← best via R2
*  203.0.113.0/24   10.1.12.2                              0 65002 65003 i
*>                  10.1.13.2                0             0 65003 i ! ← best via R3 (shorter AS-path)
*  203.0.114.0/24   10.1.12.2                              0 65002 65003 i
*>                  10.1.13.2                0             0 65003 i ! ← best via R3
*  203.0.115.0/24   10.1.12.2                              0 65002 65003 i
*>                  10.1.13.2                0             0 65003 i ! ← best via R3
```

### Task 4 Verification: Routing Table and Reachability

```bash
R1# show ip route bgp
...
B    172.16.2.2/32 [20/0] via 10.1.12.2, 00:05:32         ! ← AD=20 (eBGP)
B    172.16.3.3/32 [20/0] via 10.1.13.2, 00:05:28         ! ← AD=20 (eBGP)
B    198.51.100.0/24 [20/0] via 10.1.12.2, 00:05:32       ! ← via R2 directly
B    198.51.101.0/24 [20/0] via 10.1.12.2, 00:05:32       ! ← via R2 directly
B    198.51.102.0/24 [20/0] via 10.1.12.2, 00:05:32       ! ← via R2 directly
B    203.0.113.0/24 [20/0] via 10.1.13.2, 00:05:28        ! ← via R3 directly
B    203.0.114.0/24 [20/0] via 10.1.13.2, 00:05:28        ! ← via R3 directly
B    203.0.115.0/24 [20/0] via 10.1.13.2, 00:05:28        ! ← via R3 directly

R1# ping 172.16.2.2 source 172.16.1.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 172.16.2.2, timeout is 2 seconds:
Packet sent with a source address of 172.16.1.1
!!!!!                                                       ! ← 100% success
Success rate is 100 percent (5/5), round-trip min/avg/max = 4/8/12 ms

R1# ping 172.16.3.3 source 172.16.1.1
!!!!!                                                       ! ← 100% success
```

---

## 7. Verification Cheatsheet

### BGP Process Configuration

```
router bgp <ASN>
 bgp router-id <router-id>
 neighbor <ip> remote-as <remote-ASN>
 network <prefix> mask <mask>
```

| Command | Purpose |
|---------|---------|
| `router bgp 65001` | Enable BGP with local AS number |
| `bgp router-id 172.16.1.1` | Set explicit router-id |
| `neighbor 10.1.12.2 remote-as 65002` | Define eBGP peer with remote AS |
| `network 192.168.1.0 mask 255.255.255.0` | Advertise a prefix into BGP |

> **Exam tip:** The `network` command in BGP does not enable BGP on an interface (unlike OSPF/EIGRP). It advertises a prefix that must already exist in the routing table with an exact mask match.

### BGP Neighbor Management

```
neighbor <ip> remote-as <ASN>
neighbor <ip> update-source <interface>
neighbor <ip> ebgp-multihop <ttl>
```

| Command | Purpose |
|---------|---------|
| `neighbor <ip> remote-as <ASN>` | Establish peering (eBGP if ASN differs) |
| `neighbor <ip> shutdown` | Administratively disable a peer |
| `clear ip bgp *` | Reset all BGP sessions |
| `clear ip bgp <ip> soft` | Soft reset (no session teardown) |

> **Exam tip:** eBGP peers must be directly connected by default (TTL=1). Use `ebgp-multihop` only when peering via loopbacks or across intermediate hops.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip bgp summary` | Neighbor state, AS number, prefix count, uptime |
| `show ip bgp` | Full BGP table with paths, next-hops, AS-path |
| `show ip bgp neighbors <ip>` | Detailed peer info: state, capabilities, timers |
| `show ip bgp neighbors <ip> routes` | Routes received from a specific peer |
| `show ip bgp neighbors <ip> advertised-routes` | Routes sent to a specific peer |
| `show ip route bgp` | BGP routes installed in the routing table |
| `show ip protocols` | BGP process summary, neighbors, networks |
| `debug ip bgp updates` | Real-time BGP update messages (use with caution) |

### BGP State Machine Quick Reference

| State | Description |
|-------|-------------|
| Idle | No BGP activity; waiting to start |
| Connect | TCP connection attempt in progress |
| Active | TCP connection failed; retrying (common misconfiguration indicator) |
| OpenSent | TCP connected; OPEN message sent; waiting for reply |
| OpenConfirm | OPEN received; parameters being validated |
| Established | Peering up; exchanging UPDATE messages |

> **Exam tip:** If a neighbor is stuck in **Active** state, check: (1) IP reachability to the peer, (2) correct remote-as, (3) no ACL blocking TCP port 179.

### Common BGP Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Neighbor stuck in Active | No IP reachability, wrong neighbor IP, ACL blocking TCP 179 |
| Neighbor stuck in Idle (Admin) | `neighbor shutdown` is configured |
| Prefixes not in BGP table | Missing `network` statement or prefix not in routing table |
| Route not installed in routing table | Next-hop unreachable or better route from another protocol |
| AS-path shows unexpected path | Transit AS advertising routes through unintended path |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1 & 2: BGP Process and eBGP Neighbors

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Enterprise Edge (AS 65001)
router bgp 65001
 bgp router-id 172.16.1.1
 neighbor 10.1.12.2 remote-as 65002
 neighbor 10.1.13.2 remote-as 65003
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — ISP-A (AS 65002)
router bgp 65002
 bgp router-id 172.16.2.2
 neighbor 10.1.12.1 remote-as 65001
 neighbor 10.1.23.2 remote-as 65003
```
</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — ISP-B (AS 65003)
router bgp 65003
 bgp router-id 172.16.3.3
 neighbor 10.1.13.1 remote-as 65001
 neighbor 10.1.23.1 remote-as 65002
```
</details>

### Task 3: Network Advertisements

<details>
<summary>Click to view R1 Prefix Configuration</summary>

```bash
! R1 — Advertised Loopbacks
interface Loopback1
 ip address 192.168.1.1 255.255.255.0
interface Loopback2
 ip address 192.168.2.1 255.255.255.0
interface Loopback3
 ip address 192.168.3.1 255.255.255.0
!
router bgp 65001
 network 172.16.1.1 mask 255.255.255.255
 network 192.168.1.0 mask 255.255.255.0
 network 192.168.2.0 mask 255.255.255.0
 network 192.168.3.0 mask 255.255.255.0
```
</details>

<details>
<summary>Click to view R2 Prefix Configuration</summary>

```bash
! R2 — Advertised Loopbacks
interface Loopback1
 ip address 198.51.100.1 255.255.255.0
interface Loopback2
 ip address 198.51.101.1 255.255.255.0
interface Loopback3
 ip address 198.51.102.1 255.255.255.0
!
router bgp 65002
 network 172.16.2.2 mask 255.255.255.255
 network 198.51.100.0 mask 255.255.255.0
 network 198.51.101.0 mask 255.255.255.0
 network 198.51.102.0 mask 255.255.255.0
```
</details>

<details>
<summary>Click to view R3 Prefix Configuration</summary>

```bash
! R3 — Advertised Loopbacks
interface Loopback1
 ip address 203.0.113.1 255.255.255.0
interface Loopback2
 ip address 203.0.114.1 255.255.255.0
interface Loopback3
 ip address 203.0.115.1 255.255.255.0
!
router bgp 65003
 network 172.16.3.3 mask 255.255.255.255
 network 203.0.113.0 mask 255.255.255.0
 network 203.0.114.0 mask 255.255.255.0
 network 203.0.115.0 mask 255.255.255.0
```
</details>

### Task 4: Reachability Verification

<details>
<summary>Click to view Verification Commands</summary>

```bash
! From R1
show ip bgp summary
show ip bgp
show ip route bgp
ping 172.16.2.2 source 172.16.1.1
ping 172.16.3.3 source 172.16.1.1

! From R2
show ip bgp summary
ping 172.16.1.1 source 172.16.2.2
ping 172.16.3.3 source 172.16.2.2

! From R3
show ip bgp summary
ping 172.16.1.1 source 172.16.3.3
ping 172.16.2.2 source 172.16.3.3
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

### Ticket 1 — R1 Cannot Establish Peering with ISP-A

A junior engineer reports that R1's BGP session with ISP-A (R2) is stuck and will not come up. The session with ISP-B (R3) is working fine. R1 can ping R2's interface address successfully.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** R1-R2 eBGP session reaches Established state and prefixes are exchanged.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, run `show ip bgp summary` — the neighbor 10.1.12.2 shows **Active** state instead of Established.
2. On R2, run `show ip bgp summary` — check if R1 (10.1.12.1) appears as a neighbor at all.
3. On R2, run `show running-config | section router bgp` — the `remote-as` for neighbor 10.1.12.1 is set to **65003** instead of 65001.
4. The wrong remote-as causes the OPEN message AS number validation to fail.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R2
router bgp 65002
 no neighbor 10.1.12.1 remote-as 65003
 neighbor 10.1.12.1 remote-as 65001
```
</details>

---

### Ticket 2 — ISP-B Prefixes Missing from R1's BGP Table

The NOC reports that R1 cannot reach any of ISP-B's (R3) advertised prefixes (203.0.113.0/24, etc.), although the eBGP session between R1 and R3 shows as Established.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** All four ISP-B prefixes (172.16.3.3/32, 203.0.113.0/24, 203.0.114.0/24, 203.0.115.0/24) appear in R1's BGP table via 10.1.13.2.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, run `show ip bgp summary` — R3 neighbor (10.1.13.2) shows Established but PfxRcvd is **0**.
2. On R3, run `show ip bgp` — the BGP table is empty or shows no locally originated routes.
3. On R3, run `show running-config | section router bgp` — the `network` statements are missing.
4. The BGP process is running and the neighbor is configured, but no prefixes are being advertised.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3
router bgp 65003
 network 172.16.3.3 mask 255.255.255.255
 network 203.0.113.0 mask 255.255.255.0
 network 203.0.114.0 mask 255.255.255.0
 network 203.0.115.0 mask 255.255.255.0
```
</details>

---

### Ticket 3 — R2 Has No Route to Enterprise Prefixes Despite Active Session

R2's monitoring system shows that it has an Established BGP session with R1, but R2 cannot reach any of the Enterprise prefixes (192.168.X.0/24). Pings from R2 to R1's Loopback0 succeed.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** R2's BGP table shows all four Enterprise prefixes (172.16.1.1/32, 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24) from R1 via 10.1.12.1.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R2, run `show ip bgp summary` — R1 (10.1.12.1) shows Established but PfxRcvd is **0** or only shows the loopback.
2. On R1, run `show ip bgp` — the Enterprise prefixes (192.168.X.0/24) may not appear locally.
3. On R1, run `show ip route connected` — check if the loopback interfaces for 192.168.X.0/24 exist.
4. On R1, run `show running-config | include interface Loopback` — Loopback1, 2, 3 are **shut down**, so the connected routes are not in the routing table, and the `network` statements cannot find a matching prefix.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
interface Loopback1
 no shutdown
interface Loopback2
 no shutdown
interface Loopback3
 no shutdown
```
</details>

---

## 10. Lab Completion Checklist

### Core Implementation
- [ ] BGP process enabled on R1 (AS 65001), R2 (AS 65002), R3 (AS 65003)
- [ ] Router-IDs set to Loopback0 addresses on all routers
- [ ] All six eBGP neighbor relationships in Established state
- [ ] Enterprise prefixes (192.168.1-3.0/24 + 172.16.1.1/32) advertised from R1
- [ ] ISP-A prefixes (198.51.100-102.0/24 + 172.16.2.2/32) advertised from R2
- [ ] ISP-B prefixes (203.0.113-115.0/24 + 172.16.3.3/32) advertised from R3
- [ ] All 12 prefixes visible in BGP table on each router
- [ ] BGP routes installed in the IP routing table (AD 20)
- [ ] End-to-end loopback reachability confirmed via ping

### Troubleshooting
- [ ] Ticket 1: Wrong remote-as diagnosed and fixed
- [ ] Ticket 2: Missing network statements diagnosed and fixed
- [ ] Ticket 3: Shutdown loopbacks diagnosed and fixed
