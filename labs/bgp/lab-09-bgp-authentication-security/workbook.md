# BGP Lab 09: BGP Authentication & Security

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

**Exam Objective:** 3.2.c — Configure and verify eBGP between directly connected neighbors (best path selection algorithm and neighbor relationships); 5.2 — Configure and verify infrastructure security features

BGP is the routing protocol that holds the Internet together — and it is also one of the most historically attacked protocols in networking history. From the Pakistan Telecom route hijack of 2008 to the Cloudflare incident of 2019, BGP misconfigurations and unauthenticated sessions have caused global Internet outages. This lab hardens the fully operational BGP network from Lab 08 by layering four security controls: session authentication, TTL protection, prefix count limits, and bogon route filtering. These controls are standard practice in service provider and enterprise networks, and they appear on the CCNP ENCOR exam as infrastructure security features.

### BGP MD5 Session Authentication

BGP rides on TCP. Without authentication, any device that can establish a TCP connection to a router's BGP port (179) and craft valid BGP OPEN and UPDATE messages could potentially inject routes. RFC 2385 solves this by adding an MD5 hash to every TCP segment. Both BGP peers must share an identical pre-shared key; if the MD5 signature does not match, the TCP segment is silently discarded.

The IOS command is applied per-neighbor:

```
router bgp 65001
 neighbor 10.1.12.2 password BGP_LAB_KEY
```

Critical characteristics of BGP MD5 authentication:

| Attribute | Detail |
|-----------|--------|
| Standard | RFC 2385 — TCP MD5 Signature Option |
| Scope | Per-neighbor (not global) |
| Key rotation | Requires session reset to apply new key |
| Key type | Single static string (not a key-chain) |
| Direction | Bidirectional — both sides must match |
| Failure mode | Session stays in Active state; no NOTIFICATION sent |

When there is a key mismatch, the BGP session will remain in `Active` state — the router attempts TCP connections repeatedly but each TCP SYN-ACK is dropped by the remote peer because the MD5 signature does not match. A common trap: if you configure a password on one side only, the session drops immediately and will not recover until both sides match.

### TTL Security — Generalized TTL Security Mechanism (GTSM)

GTSM (RFC 5082) exploits a simple fact: directly connected BGP peers should receive packets with TTL = 255. A packet from a spoofed source far away on the Internet will have its TTL decremented at every hop. By requiring inbound BGP TCP packets to have TTL >= (255 − N), you ensure that only true direct neighbors (N = 1 hop away) can establish sessions.

```
router bgp 65001
 neighbor 10.1.12.2 ttl-security hops 1
```

For `hops 1` (directly connected eBGP): minimum acceptable TTL = 255 − 1 = 254.

GTSM provides two protections:

1. **Session injection prevention** — A remote attacker cannot spoof BGP packets with TTL 255 because each intervening hop decrements TTL; by the time packets arrive, TTL is far below 254.
2. **CPU exhaustion protection** — Without GTSM, anyone on the Internet can send TCP SYN packets to port 179 and force the router to process them. With GTSM, those packets are dropped in the forwarding plane before reaching the CPU.

Note: GTSM is a complement to MD5 authentication, not a replacement. Use both.

### Maximum-Prefix Limits

A BGP peer that sends an abnormally large number of prefixes — either due to misconfiguration (route leak) or a malicious attack — can fill a router's BGP table, consume memory, and affect forwarding. Maximum-prefix limits are the primary defense:

```
router bgp 65001
 neighbor 10.1.12.2 maximum-prefix 200 80
```

The syntax: `maximum-prefix <count> [warning-threshold%] [warning-only | restart <minutes>]`

| Parameter | Meaning |
|-----------|---------|
| `200` | Maximum prefixes accepted from this peer |
| `80` | Log a warning when 80% of the limit is reached (160 prefixes) |
| `warning-only` | (optional) Log warning but do not tear down session |
| `restart 5` | (optional) Automatically restart session after 5 minutes |

Default behavior without `warning-only`: when the prefix count exceeds the limit, the session is torn down and placed in `Idle (PfxCt)` state. The administrator must manually clear it with `clear ip bgp <peer> soft in`.

Industry sizing guidance: set the maximum-prefix limit to 2× the expected prefix count. For ISP peers advertising ~100 prefixes in a lab, a limit of 200 provides protection without risking false positives.

### Bogon Route Filtering as a Security Control

"Bogons" are IP prefixes that should never appear as BGP routes from external peers: IANA-reserved space, RFC 1918 private addresses, loopback addresses, and link-local space. If a misconfigured or malicious peer advertises these prefixes, and you accept them, your routing table now has private-space routes pointing toward the Internet — which breaks reachability to your own internal networks.

The defense: maintain a prefix-list that explicitly matches bogon space and deny those routes in your inbound route-map before any other policy is applied.

Key bogon ranges to filter inbound from ISP peers:

| Prefix | Category |
|--------|----------|
| 0.0.0.0/8 | This network (IANA reserved) |
| 10.0.0.0/8 | RFC 1918 private |
| 127.0.0.0/8 | Loopback |
| 169.254.0.0/16 | Link-local (APIPA) |
| 172.16.0.0/12 | RFC 1918 private |
| 192.0.2.0/24 | Documentation (TEST-NET-1) |
| 192.168.0.0/16 | RFC 1918 private |
| 198.18.0.0/15 | Benchmarking |
| 240.0.0.0/4 | Reserved (Class E) |

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| BGP MD5 Authentication | Configure and verify per-neighbor password authentication on eBGP and iBGP sessions |
| GTSM / TTL Security | Apply TTL-based protection to eBGP sessions against off-path injection attacks |
| Maximum-Prefix Protection | Set inbound prefix limits with warning thresholds to defend against route leaks |
| Bogon Filtering | Build and apply a security-focused prefix-list to block IANA-reserved and private routes |
| Security Troubleshooting | Diagnose BGP session failures and route leaks caused by security misconfigurations |

---

## 2. Topology & Scenario

### Business Context

AcmeCorp (AS 65001) has completed its BGP buildout: dual-homed to ISP-A (AS 65002) and ISP-B (AS 65003), with traffic engineering policies, BGP communities, and a Route Reflector (R1) serving Enterprise Internal (R4) and Enterprise Edge 2 (R6). The downstream customer R5 (AS 65004) peers with ISP-B.

The network operations team has received a security audit report with four critical findings:

1. All BGP sessions are unauthenticated — any device can attempt to join the BGP topology
2. eBGP sessions have no TTL protection — vulnerable to off-path TCP injection
3. No prefix limits are configured — a misconfigured peer could flood the BGP table
4. No bogon filtering is in place — a route leak could inject private space into the Internet routing table

Your task is to address all four findings without disrupting the existing BGP topology.

### ASCII Topology Diagram

```
          ┌────────────────────────────────────────────────────────────────────────────┐
          │                                                                            │
          │                    eBGP Session (10.1.23.0/30)                            │
          │              Fa1/0 10.1.23.1/30 ────── 10.1.23.2/30 Fa0/0                │
          │                                                                            │
          └────────────────────────────────────────────────────────────────────────────┘
                  │                                                        │
          ┌───────┴────────────┐                           ┌──────────────┴──────────┐
          │        R2          │                           │          R3             │
          │      (ISP-A)       │                           │        (ISP-B)          │
          │  Lo0: 172.16.2.2   │                           │   Lo0: 172.16.3.3       │
          │     AS 65002       │                           │       AS 65003          │
          └───────┬────────────┘                           └─────┬────────────┬──────┘
            Fa0/0 │ 10.1.12.2/30               10.1.13.2/30 │ Fa1/0    Fa1/1 │ 10.1.35.1/30
                  │                                          │                │
            Fa1/0 │ 10.1.12.1/30               10.1.13.1/30 │ Fa1/1          │ 10.1.35.2/30 Fa0/0
          ┌───────┴──────────────────────────────────────────┘       ┌────────┴────────┐
          │                        R1                                 │       R5        │
          │            (Enterprise Edge / Route Reflector)            │  (Downstream    │
          │            Lo0: 172.16.1.1/32, AS 65001                  │   Customer)     │
          └───────┬──────────────────────────────┬────────────        │   AS 65004      │
            Fa0/0 │ 10.1.14.1/30        Gi3/0 │ 10.1.16.1/30        │  Lo0:172.16.5.5 │
                  │                            │                      └─────────────────┘
            Fa0/0 │ 10.1.14.2/30        Gi3/0 │ 10.1.16.2/30
          ┌───────┴────────────┐   ┌───────────┴─────────────────────────────────────┐
          │        R4          │   │                     R6                           │
          │  (Enterprise       │   │            (Enterprise Edge 2)                   │
          │   Internal)        │   │             Lo0: 172.16.6.6/32                   │
          │  Lo0:172.16.4.4    │   │                  AS 65001                        │
          │    AS 65001        │   └──────────────────────────────────────────────────┘
          └────────────────────┘

  iBGP (loopback-based via OSPF):  R1 ↔ R4  |  R1 ↔ R6
  eBGP (directly connected):       R1 ↔ R2  |  R1 ↔ R3  |  R2 ↔ R3  |  R3 ↔ R5
```

---

## 3. Hardware & Environment Specifications

### Device Inventory

| Device | Platform | Role | AS | Loopback0 |
|--------|----------|------|----|-----------|
| R1 | c7200 | Enterprise Edge / Route Reflector | 65001 | 172.16.1.1/32 |
| R2 | c7200 | ISP-A | 65002 | 172.16.2.2/32 |
| R3 | c7200 | ISP-B | 65003 | 172.16.3.3/32 |
| R4 | c3725 | Enterprise Internal | 65001 | 172.16.4.4/32 |
| R5 | c3725 | Downstream Customer | 65004 | 172.16.5.5/32 |
| R6 | c7200 | Enterprise Edge 2 | 65001 | 172.16.6.6/32 |

### Cabling Table

| Link | Source | Destination | Subnet | Description |
|------|--------|-------------|--------|-------------|
| L1 | R1 Fa1/0 — 10.1.12.1/30 | R2 Fa0/0 — 10.1.12.2/30 | 10.1.12.0/30 | Enterprise to ISP-A (eBGP) |
| L2 | R2 Fa1/0 — 10.1.23.1/30 | R3 Fa0/0 — 10.1.23.2/30 | 10.1.23.0/30 | ISP-A to ISP-B (eBGP) |
| L3 | R1 Fa1/1 — 10.1.13.1/30 | R3 Fa1/0 — 10.1.13.2/30 | 10.1.13.0/30 | Enterprise to ISP-B (eBGP) |
| L4 | R1 Fa0/0 — 10.1.14.1/30 | R4 Fa0/0 — 10.1.14.2/30 | 10.1.14.0/30 | Enterprise Edge to Enterprise Internal |
| L5 | R3 Fa1/1 — 10.1.35.1/30 | R5 Fa0/0 — 10.1.35.2/30 | 10.1.35.0/30 | ISP-B to Downstream Customer (eBGP) |
| L6 | R1 Gi3/0 — 10.1.16.1/30 | R6 Gi3/0 — 10.1.16.2/30 | 10.1.16.0/30 | Enterprise Edge to Enterprise Edge 2 |

### Console Access Table

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |
| R6 | 5006 | `telnet 127.0.0.1 5006` |

---

## 4. Base Configuration

The initial configurations are copied from Lab 08 solutions. The following is already fully configured:

**Pre-configured:**
- IP addressing on all interfaces (loopbacks and physical links)
- OSPF Area 0 on R1, R4, and R6 (for iBGP loopback reachability)
- Complete eBGP sessions: R1↔R2, R1↔R3, R2↔R3, R3↔R5
- iBGP sessions with R1 as Route Reflector: R1↔R4, R1↔R6 (loopback-sourced, next-hop-self)
- Traffic engineering policies from Lab 07: Local Preference, AS-path prepend, MED
- BGP communities and policy from Lab 06 (R3↔R5)
- Route filtering prefix-lists from Lab 04 (ENTERPRISE-INTERNAL, customer prefix filters)
- Conditional default route origination from R1 to R4 (CHECK-ISP-UP route-map)
- Soft reconfiguration inbound on applicable neighbors

**NOT pre-configured (student task):**
- MD5 authentication on any BGP session
- TTL security on any BGP session
- Maximum-prefix limits on any neighbor
- Bogon prefix-list and security-focused route-map entries

---

## 5. Lab Challenge: Core Implementation

### Task 1: MD5 Authentication on All BGP Sessions

- Configure MD5 password authentication on the R1-R2 eBGP neighbor relationship using the key `BGP_LAB_KEY`; configure the matching password on R2's side for its R1 neighbor
- Configure MD5 password authentication on the R1-R3 eBGP session using `BGP_LAB_KEY`; configure the matching password on R3's side for its R1 neighbor
- Configure MD5 password authentication on the R2-R3 ISP peering session using the key `ISP_PEER_KEY`; configure the matching key on both R2 and R3 for this peer
- Configure MD5 password authentication on the R3-R5 customer peering session using the key `CUST_LAB_KEY`; configure the matching key on R5 for its R3 neighbor
- Configure MD5 password authentication on R1's iBGP sessions to R4 and R6 using the key `IBGP_LAB_KEY`; configure matching keys on R4's session to R1 and R6's session to R1
- Verify all six sessions re-establish in Established state after authentication is applied

**Verification:** `show ip bgp summary` must show all peers with state `Established` (numeric uptime/prefix count). `show ip bgp neighbors <peer-ip> | include password` must show `MD5 password configured`.

---

### Task 2: TTL Security (GTSM) for eBGP Peers

- Apply TTL security with a hops value of 1 to R1's directly connected eBGP sessions to R2 and R3 (both R1 and remote side must be configured)
- Apply TTL security with a hops value of 1 to the R2-R3 ISP peering session (both sides)
- Apply TTL security with a hops value of 1 to the R3-R5 customer peering session (both sides)
- Do not apply TTL security to the loopback-based iBGP sessions (R1-R4 and R1-R6); iBGP uses TTL 255 natively and GTSM on loopback-sourced multi-hop sessions requires careful hops calculation

**Verification:** `show ip bgp neighbors <peer-ip> | include TTL` must show `External BGP neighbor may be up to 1 hops away`. Session must remain Established.

---

### Task 3: Maximum-Prefix Limits

- Set a maximum-prefix limit of 200 prefixes (80% warning threshold) on R1's inbound sessions to both R2 and R3; the existing ISP advertisements are well below this limit
- Set a maximum-prefix limit of 100 prefixes (80% warning threshold) on R2's inbound session to R1 and on R3's inbound session to R1
- Set a maximum-prefix limit of 50 prefixes (80% warning threshold) on R3's inbound session to R5
- Verify limits are in place and sessions remain established

**Verification:** `show ip bgp neighbors <peer-ip> | include Maximum` must show `Maximum prefixes: <count>` for each configured neighbor.

---

### Task 4: Bogon Route Filtering as a Security Control

- Create a prefix-list named `BOGON-PREFIXES` on R1 that permits (matches) the following IANA-reserved ranges: 0.0.0.0/8, 10.0.0.0/8, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.0.2.0/24, 192.168.0.0/16, 198.18.0.0/15, and 240.0.0.0/4 — use `le 32` on each entry to match all more-specific prefixes within those ranges
- Add a deny sequence at position 5 in both the `ISP-A-IN` and `ISP-B-IN` route-maps that matches this prefix-list; this sequence must be evaluated before the existing permit sequences 10 and 20 to block bogon routes before any local-preference policy is applied
- Verify the bogon filter is active; no RFC 1918 or IANA-reserved prefixes should appear in R1's BGP table sourced from eBGP peers

**Verification:** `show ip prefix-list BOGON-PREFIXES` must list all nine entries. `show ip bgp | begin Network` on R1 must show only publicly routable prefixes from ISP peers.

---

## 6. Verification & Analysis

### Task 1 — MD5 Authentication Verification

```bash
R1# show ip bgp summary
BGP router identifier 172.16.1.1, local AS number 65001
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.1.12.2       4 65002      45      42       18    0    0 00:03:21        4   ! ← Established (numeric), not Active/Idle
10.1.13.2       4 65003      43      41       18    0    0 00:03:19        4   ! ← Established (numeric), not Active/Idle
172.16.4.4      4 65001      38      36       18    0    0 00:03:15        8   ! ← iBGP established
172.16.6.6      4 65001      35      33       18    0    0 00:03:10        8   ! ← iBGP established

R1# show ip bgp neighbors 10.1.12.2 | include password
  MD5 password configured, key-chain not specified   ! ← Confirms MD5 active

R1# show ip bgp neighbors 172.16.4.4 | include password
  MD5 password configured, key-chain not specified   ! ← iBGP MD5 active

R2# show ip bgp neighbors 10.1.12.1 | include password
  MD5 password configured, key-chain not specified   ! ← Both sides confirmed
```

### Task 2 — TTL Security Verification

```bash
R1# show ip bgp neighbors 10.1.12.2 | include TTL
  External BGP neighbor may be up to 1 hops away.   ! ← GTSM hops = 1

R1# show ip bgp neighbors 10.1.13.2 | include TTL
  External BGP neighbor may be up to 1 hops away.   ! ← GTSM active on both ISP sessions

R2# show ip bgp neighbors 10.1.23.2 | include TTL
  External BGP neighbor may be up to 1 hops away.   ! ← ISP-A to ISP-B GTSM active

R3# show ip bgp neighbors 10.1.35.2 | include TTL
  External BGP neighbor may be up to 1 hops away.   ! ← ISP-B to Customer GTSM active
```

### Task 3 — Maximum-Prefix Limits Verification

```bash
R1# show ip bgp neighbors 10.1.12.2 | include Maximum
  Maximum prefixes: 200 80%                          ! ← Limit 200, warn at 160

R1# show ip bgp neighbors 10.1.13.2 | include Maximum
  Maximum prefixes: 200 80%                          ! ← Limit 200, warn at 160

R3# show ip bgp neighbors 10.1.35.2 | include Maximum
  Maximum prefixes: 50 80%                           ! ← Customer limited to 50 prefixes

R2# show ip bgp neighbors 10.1.12.1 | include Maximum
  Maximum prefixes: 100 80%                          ! ← ISP-A limits Enterprise to 100
```

### Task 4 — Bogon Filter Verification

```bash
R1# show ip prefix-list BOGON-PREFIXES
ip prefix-list BOGON-PREFIXES: 9 entries
   seq 10 permit 0.0.0.0/8 le 32       ! ← This network
   seq 20 permit 10.0.0.0/8 le 32      ! ← RFC 1918
   seq 30 permit 127.0.0.0/8 le 32     ! ← Loopback
   seq 40 permit 169.254.0.0/16 le 32  ! ← Link-local
   seq 50 permit 172.16.0.0/12 le 32   ! ← RFC 1918
   seq 60 permit 192.0.2.0/24 le 32    ! ← TEST-NET-1
   seq 70 permit 192.168.0.0/16 le 32  ! ← RFC 1918
   seq 80 permit 198.18.0.0/15 le 32   ! ← Benchmarking
   seq 90 permit 240.0.0.0/4 le 32     ! ← Reserved (Class E)

R1# show route-map ISP-A-IN
route-map ISP-A-IN, deny, sequence 5
  Match clauses:
    ip address prefix-lists: BOGON-PREFIXES   ! ← Bogon deny before any permit
  Set clauses:
route-map ISP-A-IN, permit, sequence 10
  Match clauses:
    ip address prefix-lists: ISP-A-PREFIXES
  Set clauses:
    local-preference 200
route-map ISP-A-IN, permit, sequence 20
  Set clauses:
    local-preference 100

R1# show ip bgp | begin Network
   Network          Next Hop            Metric LocPrf Weight Path
*> 172.16.1.1/32    0.0.0.0                  0         32768 i
*> 172.16.2.2/32    10.1.12.2                0          100 0 65002 i
*> 172.16.3.3/32    10.1.13.2                0          100 0 65003 i
*> 192.168.1.0      0.0.0.0                  0         32768 i
*> 192.168.2.0      0.0.0.0                  0         32768 i
*> 192.168.3.0      0.0.0.0                  0         32768 i
*> 198.51.100.0     10.1.12.2                0        200 0 65002 i  ! ← ISP-A LP=200
*> 198.51.101.0     10.1.12.2                0        200 0 65002 i
*> 198.51.102.0     10.1.12.2                0        200 0 65002 i
*> 203.0.113.0      10.1.13.2                0        200 0 65003 i  ! ← ISP-B LP=200
! ← No 10.x.x.x, 172.16.x.x (except loopbacks), 192.168.x.x from ISP peers
```

---

## 7. Verification Cheatsheet

### BGP MD5 Authentication

```
router bgp <asn>
 neighbor <ip> password <key-string>
```

| Command | Purpose |
|---------|---------|
| `neighbor <ip> password <key>` | Configure MD5 authentication for a BGP peer |
| `show ip bgp neighbors <ip> \| include password` | Verify MD5 is configured |
| `show ip bgp summary` | Check session state (must reach Established) |
| `clear ip bgp <ip>` | Hard reset — use only when troubleshooting auth failures |
| `clear ip bgp <ip> soft` | Soft reset without tearing the session |

> **Exam tip:** BGP MD5 uses RFC 2385. If password mismatches, the session stays in `Active` state — the TCP connection never completes. Unlike OSPF/EIGRP which use key-chains, BGP uses a single static string per neighbor.

### TTL Security (GTSM)

```
router bgp <asn>
 neighbor <ip> ttl-security hops <1-254>
```

| Command | Purpose |
|---------|---------|
| `neighbor <ip> ttl-security hops 1` | Enable GTSM for directly connected eBGP peer |
| `show ip bgp neighbors <ip> \| include TTL` | Verify GTSM is active |
| `show ip bgp neighbors <ip> \| include hops` | Show configured hop count |

> **Exam tip:** `ttl-security hops 1` means packets must arrive with TTL >= 254 (255-1). This prevents off-path attackers from injecting BGP TCP segments. Both peers must be configured. GTSM is most useful for eBGP; loopback-based iBGP uses TTL 255 natively.

### Maximum-Prefix Limits

```
router bgp <asn>
 neighbor <ip> maximum-prefix <count> [threshold%] [warning-only | restart <minutes>]
```

| Command | Purpose |
|---------|---------|
| `neighbor <ip> maximum-prefix 200 80` | Limit to 200 prefixes; warn at 160 |
| `neighbor <ip> maximum-prefix 200 80 warning-only` | Log warning only — do not tear session |
| `neighbor <ip> maximum-prefix 200 80 restart 5` | Tear down and auto-restart after 5 min |
| `show ip bgp neighbors <ip> \| include Maximum` | Verify limit and threshold |
| `show ip bgp neighbors <ip> \| include prefixes` | Show current prefix count vs limit |
| `clear ip bgp <ip>` | Manually recover after `Idle (PfxCt)` state |

> **Exam tip:** When the prefix count exceeds the limit, the session enters `Idle (PfxCt)` — it will NOT automatically recover (unless `restart` is configured). You must manually clear it. Set limits to ~2× expected prefix count to avoid false positives.

### Bogon Filtering

```
ip prefix-list BOGON-PREFIXES permit <bogon-range> le 32
!
route-map <ISP-INBOUND> deny 5
 match ip address prefix-list BOGON-PREFIXES
route-map <ISP-INBOUND> permit 10
 ...existing policy...
```

| Command | Purpose |
|---------|---------|
| `show ip prefix-list BOGON-PREFIXES` | Verify all bogon entries are present |
| `show route-map <name>` | Confirm deny sequence 5 is first in the route-map |
| `show ip bgp \| begin Network` | Verify no bogon prefixes appear in BGP table |
| `show ip bgp regexp _65002_` | Show routes received from a specific AS |

> **Exam tip:** In a route-map used for BGP filtering, prefix-list `permit` means "this prefix MATCHES the clause." The route-map `deny 5` clause then drops matching (bogon) routes. Non-bogon routes fall through to permit 10 and 20. Sequence numbers matter — lower numbers are evaluated first.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip bgp summary` | All peers show numeric value in State/PfxRcd column (not Active/Idle) |
| `show ip bgp neighbors <ip> \| include password` | `MD5 password configured` |
| `show ip bgp neighbors <ip> \| include TTL` | `External BGP neighbor may be up to 1 hops away` |
| `show ip bgp neighbors <ip> \| include Maximum` | `Maximum prefixes: <N> <threshold>%` |
| `show ip prefix-list BOGON-PREFIXES` | Nine permit entries covering all bogon ranges |
| `show route-map ISP-A-IN` | Sequence 5 deny appears before sequences 10 and 20 |

### Common BGP Security Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Session stuck in `Active` state | MD5 password mismatch or configured on only one side |
| Session flaps, then `Active` after auth change | Applied password on one side but not the other |
| Session `Idle (PfxCt)` | Maximum-prefix limit exceeded; must `clear ip bgp <ip>` |
| Bogon prefix appears in BGP table | Bogon filter missing or route-map sequence order incorrect |
| TTL security causes session drop | GTSM `hops` value not matching actual path (e.g., set hops 2 but only 1 hop away) |
| BGP session drops after `clear ip bgp <ip> soft in` | Prefix count re-evaluated; limit immediately exceeded again |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: MD5 Authentication on All BGP Sessions

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Add MD5 passwords to all BGP neighbors
router bgp 65001
 neighbor 10.1.12.2 password BGP_LAB_KEY
 neighbor 10.1.13.2 password BGP_LAB_KEY
 neighbor 172.16.4.4 password IBGP_LAB_KEY
 neighbor 172.16.6.6 password IBGP_LAB_KEY
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — Match passwords for both eBGP sessions
router bgp 65002
 neighbor 10.1.12.1 password BGP_LAB_KEY
 neighbor 10.1.23.2 password ISP_PEER_KEY
```
</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — Match passwords for all three eBGP sessions
router bgp 65003
 neighbor 10.1.13.1 password BGP_LAB_KEY
 neighbor 10.1.23.1 password ISP_PEER_KEY
 neighbor 10.1.35.2 password CUST_LAB_KEY
```
</details>

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4 — Match iBGP password for R1 neighbor
router bgp 65001
 neighbor 172.16.1.1 password IBGP_LAB_KEY
```
</details>

<details>
<summary>Click to view R5 Configuration</summary>

```bash
! R5 — Match customer peering password
router bgp 65004
 neighbor 10.1.35.1 password CUST_LAB_KEY
```
</details>

<details>
<summary>Click to view R6 Configuration</summary>

```bash
! R6 — Match iBGP password for R1 neighbor
router bgp 65001
 neighbor 172.16.1.1 password IBGP_LAB_KEY
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip bgp summary
show ip bgp neighbors 10.1.12.2 | include password
show ip bgp neighbors 10.1.13.2 | include password
show ip bgp neighbors 172.16.4.4 | include password
show ip bgp neighbors 172.16.6.6 | include password
```
</details>

---

### Task 2: TTL Security (GTSM) for eBGP Peers

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Apply TTL security to directly connected eBGP peers
router bgp 65001
 neighbor 10.1.12.2 ttl-security hops 1
 neighbor 10.1.13.2 ttl-security hops 1
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — Apply TTL security to R1 and R3 eBGP sessions
router bgp 65002
 neighbor 10.1.12.1 ttl-security hops 1
 neighbor 10.1.23.2 ttl-security hops 1
```
</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — Apply TTL security to all three eBGP sessions
router bgp 65003
 neighbor 10.1.13.1 ttl-security hops 1
 neighbor 10.1.23.1 ttl-security hops 1
 neighbor 10.1.35.2 ttl-security hops 1
```
</details>

<details>
<summary>Click to view R5 Configuration</summary>

```bash
! R5 — Apply TTL security to R3 eBGP session
router bgp 65004
 neighbor 10.1.35.1 ttl-security hops 1
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip bgp neighbors 10.1.12.2 | include TTL
show ip bgp neighbors 10.1.13.2 | include TTL
show ip bgp summary
```
</details>

---

### Task 3: Maximum-Prefix Limits

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Set maximum-prefix limits for ISP sessions
router bgp 65001
 neighbor 10.1.12.2 maximum-prefix 200 80
 neighbor 10.1.13.2 maximum-prefix 200 80
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — Limit prefixes accepted from Enterprise and from ISP-B
router bgp 65002
 neighbor 10.1.12.1 maximum-prefix 100 80
 neighbor 10.1.23.2 maximum-prefix 500 80
```
</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — Limit prefixes from Enterprise, from ISP-A, and from Customer
router bgp 65003
 neighbor 10.1.13.1 maximum-prefix 100 80
 neighbor 10.1.23.1 maximum-prefix 500 80
 neighbor 10.1.35.2 maximum-prefix 50 80
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip bgp neighbors 10.1.12.2 | include Maximum
show ip bgp neighbors 10.1.13.2 | include Maximum
show ip bgp neighbors 172.16.4.4 | include Maximum
```
</details>

---

### Task 4: Bogon Route Filtering as a Security Control

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Create bogon prefix-list and update inbound route-maps
ip prefix-list BOGON-PREFIXES seq 10 permit 0.0.0.0/8 le 32
ip prefix-list BOGON-PREFIXES seq 20 permit 10.0.0.0/8 le 32
ip prefix-list BOGON-PREFIXES seq 30 permit 127.0.0.0/8 le 32
ip prefix-list BOGON-PREFIXES seq 40 permit 169.254.0.0/16 le 32
ip prefix-list BOGON-PREFIXES seq 50 permit 172.16.0.0/12 le 32
ip prefix-list BOGON-PREFIXES seq 60 permit 192.0.2.0/24 le 32
ip prefix-list BOGON-PREFIXES seq 70 permit 192.168.0.0/16 le 32
ip prefix-list BOGON-PREFIXES seq 80 permit 198.18.0.0/15 le 32
ip prefix-list BOGON-PREFIXES seq 90 permit 240.0.0.0/4 le 32
!
route-map ISP-A-IN deny 5
 match ip address prefix-list BOGON-PREFIXES
!
route-map ISP-B-IN deny 5
 match ip address prefix-list BOGON-PREFIXES
!
! After adding route-map entries, soft-clear inbound to re-apply policy:
! R1# clear ip bgp 10.1.12.2 soft in
! R1# clear ip bgp 10.1.13.2 soft in
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip prefix-list BOGON-PREFIXES
show route-map ISP-A-IN
show route-map ISP-B-IN
show ip bgp | begin Network
clear ip bgp 10.1.12.2 soft in
clear ip bgp 10.1.13.2 soft in
```
</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore
```

---

### Ticket 1 — R1 Cannot Form eBGP Session with ISP-A

A junior engineer was rotating BGP passwords as part of a quarterly security review. Shortly after the change, the NOC reports that all ISP-A routes have disappeared from the enterprise routing table. R1 shows its ISP-A neighbor is no longer established.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip bgp summary` on R1 shows R2 (10.1.12.2) with a numeric prefix count and non-zero uptime.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Check R1 BGP summary — identify R2 state
R1# show ip bgp summary
! Look for 10.1.12.2 — if it shows "Active" instead of a prefix count, authentication is failing

! Step 2: Confirm MD5 is configured
R1# show ip bgp neighbors 10.1.12.2 | include password
!   MD5 password configured — confirms R1 has a key

! Step 3: Check session state detail
R1# show ip bgp neighbors 10.1.12.2 | include state|BGP state
!   BGP state = Active — TCP connection never completing
!   Root cause: password mismatch between R1 and R2

! Step 4: Verify from R2's perspective
R2# show ip bgp neighbors 10.1.12.1 | include password|state
! R2 has a different password — the keys don't match
```
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! The fault: R2's password for the R1 neighbor was changed to a wrong value.
! Fix: restore the correct password on R2

R2(config)# router bgp 65002
R2(config-router)# neighbor 10.1.12.1 password BGP_LAB_KEY

! Verify recovery — session should re-establish within ~30 seconds
R1# show ip bgp summary
! 10.1.12.2 must show numeric PfxRcd, not "Active"
```
</details>

---

### Ticket 2 — ISP-A Neighbor Repeatedly Enters Idle State

Immediately after a BGP policy review, R1's session to ISP-A keeps flapping. The neighbor enters `Idle` state within seconds of being cleared, and the syslog on R1 shows a maximum prefix warning message.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** R1's session to R2 remains Established and `show ip bgp neighbors 10.1.12.2 | include Maximum` shows a limit appropriate for the ISP-A peering.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Check BGP summary
R1# show ip bgp summary
! Look for 10.1.12.2 — if state shows "Idle" this is suspicious

! Step 2: Check the neighbor detail for prefix information
R1# show ip bgp neighbors 10.1.12.2 | include Maximum|prefix|Prefix
! You will see: Maximum prefixes: 1
! And: Prefix received 4 (maximum: 1) — session torn down

! Step 3: Look at syslog for confirmation
! %BGP-3-MAXPFX: No. of prefix received from 10.1.12.2 (afi 0) reaches 1, max 1
! This confirms the maximum-prefix limit is set to 1 — far too low for ISP peering

! Step 4: Identify the incorrect value
R1# show run | section bgp
! neighbor 10.1.12.2 maximum-prefix 1    <-- the fault
```
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! The fault: maximum-prefix on the R2 neighbor was set to 1
! Fix: restore appropriate limit (200) and clear the session

R1(config)# router bgp 65001
R1(config-router)# no neighbor 10.1.12.2 maximum-prefix 1
R1(config-router)# neighbor 10.1.12.2 maximum-prefix 200 80

! Session is in Idle (PfxCt) — must manually clear
R1# clear ip bgp 10.1.12.2

! Verify recovery
R1# show ip bgp summary
! 10.1.12.2 must show numeric PfxRcd (not Idle)
R1# show ip bgp neighbors 10.1.12.2 | include Maximum
! Maximum prefixes: 200  80%
```
</details>

---

### Ticket 3 — Enterprise BGP Table Contains an Unexpected Private-Space Route

A security scan of R1's BGP routing table flagged a private IP prefix (10.99.0.0/24) appearing in the BGP table with a next-hop pointing to ISP-A. This prefix should not be visible — ISPs should not be advertising private space. The bogon filter appears to be missing or broken.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip bgp` on R1 shows no 10.x.x.x prefixes sourced from AS 65002 or AS 65003. `show route-map ISP-A-IN` confirms sequence 5 deny is present.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Confirm the bogon prefix is in the BGP table
R1# show ip bgp 10.99.0.0/24
! You see: BGP routing table entry for 10.99.0.0/24
! Next hop: 10.1.12.2 (R2/ISP-A) — private space sourced from ISP

! Step 2: Check if the bogon filter still exists
R1# show ip prefix-list BOGON-PREFIXES
! May show: prefix-list not found — or missing the 10.0.0.0/8 entry

! Step 3: Check the ISP-A-IN route-map for the deny sequence
R1# show route-map ISP-A-IN
! The deny sequence 5 is missing — only permit 10 and 20 remain
! Root cause: the bogon filter entry was removed from the route-map

! Step 4: Verify R2 is advertising the bogon prefix
R2# show ip bgp neighbors 10.1.12.1 advertised-routes | include 10.99
! Confirms R2 is sending 10.99.0.0/24 — it was injected for this scenario
```
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! The fault: the bogon deny sequence was removed from ISP-A-IN;
!            R2 has a loopback with 10.99.0.0/24 being advertised via BGP.
! Fix (two parts): restore the bogon deny clause and re-apply inbound policy

! Part 1: Restore bogon deny in route-map on R1
R1(config)# route-map ISP-A-IN deny 5
R1(config-route-map)# match ip address prefix-list BOGON-PREFIXES
R1(config-route-map)# exit

! Part 2: Soft-clear inbound to re-apply the updated route-map
R1# clear ip bgp 10.1.12.2 soft in

! Verify the bogon prefix is gone
R1# show ip bgp 10.99.0.0/24
! Output: Network not in table

R1# show route-map ISP-A-IN
! route-map ISP-A-IN, deny, sequence 5 must appear first
```
</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] **Task 1** — MD5 authentication configured and confirmed on all six BGP sessions (R1-R2, R1-R3, R2-R3, R3-R5, R1-R4, R1-R6)
- [ ] **Task 1** — All sessions reach Established state after authentication is applied
- [ ] **Task 2** — TTL security (hops 1) active on all four directly connected eBGP sessions
- [ ] **Task 2** — eBGP sessions remain Established with GTSM enabled
- [ ] **Task 3** — Maximum-prefix limits set on R1 (200/80% for ISP peers), R2 and R3 (100/80% for Enterprise), and R3 (50/80% for customer)
- [ ] **Task 3** — All sessions remain Established; no false positives triggered
- [ ] **Task 4** — BOGON-PREFIXES prefix-list present with nine entries on R1
- [ ] **Task 4** — ISP-A-IN and ISP-B-IN route-maps have a deny sequence 5 matching BOGON-PREFIXES before any permit sequences
- [ ] **Task 4** — No private or IANA-reserved prefixes appear in R1's BGP table from eBGP peers

### Troubleshooting

- [ ] **Ticket 1** — Identified and corrected MD5 password mismatch on R2; R1-R2 session re-established
- [ ] **Ticket 2** — Identified maximum-prefix limit set to 1; restored to 200; session recovered from `Idle (PfxCt)`
- [ ] **Ticket 3** — Identified missing bogon deny clause in ISP-A-IN; restored sequence 5; soft-cleared inbound; 10.99.0.0/24 no longer appears in BGP table
