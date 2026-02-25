# CCNP ENCOR BGP Lab 03: iBGP Fundamentals & Next-Hop-Self
**Student Workbook**

---

## 1. Concepts & Skills Covered

- Configure iBGP peering between loopback addresses
- Understand the iBGP split-horizon rule (no re-advertisement to other iBGP peers)
- Implement `next-hop-self` on an eBGP-to-iBGP boundary router
- Use an underlying IGP (OSPF) to provide reachability for BGP neighbor statements
- Verify end-to-end reachability through an iBGP transit network

**CCNP ENCOR Exam Objective:** 3.2.c — Configure and verify eBGP between directly connected neighbors (and iBGP principles)

---

## 2. Topology & Scenario

### ASCII Diagram
```
              ┌─────────────────────────┐
              │           R1            │
              │    Enterprise Edge      │
              │   Lo0: 172.16.1.1/32    │
              │       AS 65001          │
              └─┬────────┬───────────┬──┘
          Fa0/0 │        │ Fa1/0     │ Fa1/1
   10.1.14.1/30 │        │           │
                │   10.1.12.1/30  10.1.13.1/30
                │        │           │
   10.1.14.2/30 │   10.1.12.2/30  10.1.13.2/30
          Fa0/0 │        │ Fa0/0     │ Fa1/0
┌───────────────┴─┐ ┌────┴──────────┐┌───────────────┐
│       R4        │ │       R2      ││       R3      │
│  Ent Internal   │ │     ISP-A     ││     ISP-B     │
│Lo0: 172.16.4.4/32 │ Lo0: 172.16.2.2/32 │ Lo0: 172.16.3.3/32 │
│    AS 65001     │ │   AS 65002    ││   AS 65003    │
└─────────────────┘ └────────┬──────┘└───────┬───────┘
                       Fa1/0 │               │ Fa0/0
                10.1.23.1/30 │               │ 10.1.23.2/30
                             └───────────────┘
                                10.1.23.0/30
```

### Scenario Narrative
**NexaTech Solutions** (Enterprise AS 65001) is expanding its internal network. The core router, R4, has been deployed. To avoid redistributing the entire routing table of the internet into the internal OSPF domain, NexaTech has decided to run **iBGP** between the edge router (R1) and the internal router (R4).

Your task is to establish the iBGP session over loopback interfaces for stability (via OSPF), and ensure R4 can learn and reach external ISP routes. You will discover the critical `next-hop-self` requirement during this procress.

### Device Role Table
| Device | Role | Platform | AS | Loopback0 |
|--------|------|----------|----|-----------|
| R1 | Enterprise Edge | c7200 | 65001 | 172.16.1.1/32 |
| R2 | ISP-A (Primary) | c7200 | 65002 | 172.16.2.2/32 |
| R3 | ISP-B (Backup) | c7200 | 65003 | 172.16.3.3/32 |
| **R4** | Enterprise Internal | c3725 | 65001 | 172.16.4.4/32 |

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

The following is **pre-configured** in the initial-configs (chained from Lab 02):

- Hostname, interface IPs, loopback interfaces on all routers
- Full eBGP process established on R1, R2, R3
- BGP path selection using Weight (R1 prefers R2) is active
- **OSPF Area 0** is configured on R1 and R4 covering their link and their `Loopback0` interfaces (needed to reach the iBGP peering IP).

The following is **NOT pre-configured** (you will configure these):

- BGP process on R4
- iBGP neighborship between R1 and R4
- `update-source loopback0` for iBGP stability
- `next-hop-self` behavior on R1

---

## 5. Lab Challenge: Core Implementation

### Task 1: Establish the iBGP Peering Using Loopbacks

- Enter the BGP process on R1. Configure it to form an iBGP peer relationship with R4's loopback IP. Tell BGP to use R1's Loopback0 as the source IP for this session.
- On R4, initialize the BGP process for AS 65001. Form an iBGP relationship with R1's loopback IP. Similarly, tell BGP to use R4's Loopback0 as the source IP for this session.
- On R4, advertise its Loopback0 interface network, as well as the `10.4.1.0/24` and `10.4.2.0/24` networks (configured on Loopback1 and Loopback2) into BGP.

**Verification:** Using `show ip bgp summary` on R4, verify that the neighbor session to R1 is **Established** and R4 is receiving prefixes from R1.

---

### Task 2: Observe the Inaccessible Next-Hop Problem

- On R4, look at the BGP table. You should see all the external prefixes from ISP-A and ISP-B (e.g., `198.51.100.0/24`, `203.0.113.0/24`). However, you will notice they do NOT have the `*>` (best path) marker next to them. Instead, they just have `*`. why?
- R1 forwarded these eBGP routes to R4 via iBGP. By default, eBGP-learned next-hops are NOT changed when advertised to iBGP peers. Therefore R4 sees the next-hop for `198.51.100.0/24` as `10.1.12.2` (R2's interface IP).
- Check R4's routing table (`show ip route 10.1.12.2`). R4 does not have a route to that subnet, because it's an external transit link not in OSPF. Since the BGP next-hop is inaccessible, the BGP route is invalid and cannot be installed in the routing table.

**Verification:** `show ip bgp` on R4 shows external prefixes with `*` but no `>` marker. `show ip route bgp` shows no routes installed.

---

### Task 3: Resolve the Next-Hop Problem with Next-Hop-Self

- The traditional solution is for the edge router (R1) to change the next-hop to itself before advertising external routes into the iBGP domain.
- On R1, configure its BGP peering toward R4 so that it acts as the "next-hop-self".
- Perform a soft (or hard, if soft doesn't trigger immediately) BGP reset of the R4 session on R1 to force an update.
- Verify R4's BGP table again. The next-hop for all external prefixes should now be `172.16.1.1` (R1's loopback, which R4 can reach via OSPF). The `*>` marker should now appear, meaning the routes are valid and best.
- Verify end-to-end reachability by pinging ISP-A's prefix (`198.51.100.1`) from R4, sourcing from its loopback0.

**Verification:** `show ip bgp` on R4 shows `*>` for external prefixes, with next-hop `172.16.1.1`. `ping 198.51.100.1 source 172.16.4.4` succeeds.

---

## 6. Verification & Analysis

### Task 1 & 2 Verification: BGP Table with Inaccessible Next-Hops

```bash
R4# show ip bgp summary
BGP router identifier 172.16.4.4, local AS number 65001
BGP table version is 3, main routing table version 3
Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
172.16.1.1      4        65001      9      5        3    0    0 00:03:00       12   ! ← Established

R4# show ip bgp
BGP table version is 3, local router ID is 172.16.4.4
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal, 
              r RIB-failure, S Stale, m multipath, b backup-path, f RT-Filter, 
              x best-external, a additional-path, c RIB-compressed, 
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 * i 172.16.2.2/32    10.1.12.2                0    100      0 65002 i   ! ← No '>' because next-hop is unreachable
 * i 192.168.1.0      172.16.1.1               0    100      0 i         ! ← '>' because next-hop is reachable
 * i 198.51.100.0/24  10.1.12.2                0    100      0 65002 i   ! ← Inaccessible next-hop

R4# show ip route 10.1.12.2
% Network not in table      ! ← Confirms IGP has no path to the next-hop
```

### Task 3 Verification: Next-Hop-Self Resolves Issue

```bash
R4# show ip bgp
...
     Network          Next Hop            Metric LocPrf Weight Path
 *>i 172.16.2.2/32    172.16.1.1               0    100      0 65002 i   ! ← Now valid & best (>)
 *>i 192.168.1.0      172.16.1.1               0    100      0 i
 *>i 198.51.100.0/24  172.16.1.1               0    100      0 65002 i   ! ← Next hop is now R1 (reachable)

R4# ping 198.51.100.1 source 172.16.4.4
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 198.51.100.1, timeout is 2 seconds:
Packet sent with a source address of 172.16.4.4 
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 24/36/53 ms   ! ← End-to-end reachability
```

---

## 7. Verification Cheatsheet

### iBGP Peering over Loopbacks

```
router bgp <ASN>
 neighbor <peer-loopback-ip> remote-as <ASN>
 neighbor <peer-loopback-ip> update-source loopback0
```

| Command | Purpose |
|---------|---------|
| `neighbor <ip> update-source <interface>` | Force BGP to source TCP packets from a specific interface (crucial when using loopbacks for peering). |

> **Exam tip:** When configuring iBGP via loopbacks, the `update-source` command is required. Otherwise, the router will use the physical exit interface's IP as the source, and the peer will reject the TCP connection (due to an IP mismatch in its `neighbor` statement).

### iBGP Next-Hop-Self

```
router bgp <ASN>
 neighbor <ibgp-peer-ip> next-hop-self
```

| Command | Purpose |
|---------|---------|
| `neighbor <ip> next-hop-self` | Force the router to change the NEXT_HOP BGP attribute to its own IP address when advertising a route to this neighbor. |

> **Exam tip:** By default, BGP does NOT change the NEXT_HOP attribute when forwarding routes learned from an eBGP peer to an iBGP peer. `next-hop-self` is standard practice on edge/border routers interacting with internal iBGP peers.

### Common iBGP Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| iBGP session stays in `Active` or `Connect` state | Missing `update-source loopback0` command; or underlying IGP (OSPF) is not providing reachability to the loopback IP. |
| Routes show in BGP table but no `*>` symbol | The BGP next-hop is inaccessible via the routing table. |
| Routes not updating after config changes | A BGP session reset (`clear ip bgp * soft`) is likely needed. |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: iBGP Peering Using Loopbacks

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
router bgp 65001
 neighbor 172.16.4.4 remote-as 65001
 neighbor 172.16.4.4 update-source Loopback0
```
</details>

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4
router bgp 65001
 bgp router-id 172.16.4.4
 neighbor 172.16.1.1 remote-as 65001
 neighbor 172.16.1.1 update-source Loopback0
 network 172.16.4.4 mask 255.255.255.255
 network 10.4.1.0 mask 255.255.255.0
 network 10.4.2.0 mask 255.255.255.0
```
</details>

### Task 3: Resolve the Next-Hop Problem

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 (Setting next-hop-self towards R4)
router bgp 65001
 neighbor 172.16.4.4 next-hop-self

! Important: trigger an update to push the change
clear ip bgp 172.16.4.4 soft out
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

### Ticket 1 — R4 BGP Session Stuck in Active State

The operations team was installing R4, but the BGP session simply will not establish with R1. Connectivity between the routers exists, but BGP refuses to transition to Established.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip bgp summary` on R4 shows the neighbor state as *Established* (a number under State/PfxRcd), not *Active*.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R4, check the status: `show ip bgp summary`. The state for 172.16.1.1 is *Active* (BGP is trying to initiate TCP connections but failing).
2. Check connectivity: `ping 172.16.1.1 source loopback0`. The ping succeeds. Basic connectivity via OSPF is fine.
3. On R1, check its BGP summary: `show ip bgp summary`. You'll notice R1 is listening for 172.16.4.4, but the session is idle/active.
4. On R1, view the configuration: `show running-config | section bgp`. R1 has a neighbor statement for `172.16.4.4`, but it is **missing the `update-source loopback0` command**.
5. Root cause: Because R1 didn't specify `update-source loopback0`, when it attempts to initiate a TCP connection to R4, it uses its physical interface IP (`10.1.14.1`). R4 expects connections from `172.16.1.1` and therefore rejects R1's TCP SYN packet.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
router bgp 65001
 neighbor 172.16.4.4 update-source loopback0
```
</details>

---

### Ticket 2 — External Routes Missing from R4 Routing Table

A junior engineer made a "cleanup" change to the BGP configuration on R1. Immediately after, employees connecting via R4 reported total loss of internet access. R4's BGP table still has the routes, but they are not active in the actual routing table.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip bgp` on R4 shows `*>` next to external prefixes. R4 can ping external prefixes.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R4, check the BGP table: `show ip bgp`. Verify that external prefixes exist (e.g., `198.51.100.0/24`) but only have the `*` (valid) marker, not the `>` (best) marker.
2. Note the "Next Hop" value for those routes (e.g., `10.1.12.2` or `10.1.13.2`).
3. Check the routing table for that next hop: `show ip route 10.1.12.2`. It will state `% Network not in table`.
4. Without a reachable next-hop, BGP refuses to install the prefix.
5. On R1, review the neighbor statement toward R4: `show running-config | section bgp`. You will notice that `neighbor 172.16.4.4 next-hop-self` is missing.
6. Root cause: R1 is advertising external prefixes to R4 without changing the next-hop attribute. R4 cannot reach ISP IP addresses because they are not part of the internal OSPF network.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
router bgp 65001
 neighbor 172.16.4.4 next-hop-self
!
clear ip bgp 172.16.4.4 soft out
```
</details>

---

### Ticket 3 — Sudden Loss of BGP Peering

Due to an unintended OSPF configuration change on R4, the iBGP session to R1 dropped and will not come back up.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** R1 and R4 reestablish their BGP neighborship. `show ip ospf neighbor` shows adjacencies.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R4, verify BGP status: `show ip bgp summary`. The state is *Active*.
2. Ping R1's loopback from R4's loopback: `ping 172.16.1.1 source loopback0`. The ping fails.
3. Check OSPF routing table on R4: `show ip route ospf`. There are no OSPF routes!
4. Check OSPF configuration on R4: `show running-config | section ospf`. The network statement for the `Loopback0` interface (`network 172.16.4.4 0.0.0.0 area 0`) is present, but the physical link `network 10.1.14.0 0.0.0.3 area 0` is missing.
5. Root cause: Without the physical interface participating in OSPF, R4 cannot form OSPF adjacencies and cannot share its loopback address or learn R1's loopback address. Without UDP/TCP reachability over the loopbacks, BGP cannot establish.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4
router ospf 1
 network 10.1.14.0 0.0.0.3 area 0
```
</details>

---

## 10. Lab Completion Checklist

### Core Implementation
- [ ] R1 and R4 peered via iBGP over Loopback0 interfaces
- [ ] `update-source loopback0` correctly specified on both peers
- [ ] Inaccessible next-hop problem observed on R4's BGP table
- [ ] `next-hop-self` applied on R1 toward R4
- [ ] R4 successful pings to external ISP prefixes sourced from its loopback

### Troubleshooting
- [ ] Ticket 1: Missing `update-source loopback0` diagnosed and fixed
- [ ] Ticket 2: Missing `next-hop-self` diagnosed and fixed
- [ ] Ticket 3: Missing OSPF network statement diagnosed and fixed
