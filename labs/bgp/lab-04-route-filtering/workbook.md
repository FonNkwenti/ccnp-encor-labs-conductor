# CCNP ENCOR BGP Lab 04: Route Filtering with Prefix-Lists
**Student Workbook**

---

## 1. Concepts & Skills Covered

- Configure `ip prefix-list` entries with sequence numbers, permit/deny, and prefix-length matching
- Apply prefix-lists to BGP neighbors with `neighbor X prefix-list NAME in/out`
- Enable `soft-reconfiguration inbound` to store received BGP updates locally
- Use `clear ip bgp X soft in/out` to apply policy changes without dropping peering sessions
- Apply `distribute-list` (ACL-based) filtering to control BGP advertisement
- Verify filtering results with `show ip bgp neighbors X received-routes` and `advertised-routes`

**CCNP ENCOR Exam Objective:** 3.2.d — Configure and verify BGP route filtering using prefix-lists and distribute-lists

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
│Lo0: 172.16.4.4  │ │Lo0: 172.16.2.2││Lo0: 172.16.3.3│
│    AS 65001     │ │   AS 65002    ││   AS 65003    │
└─────────────────┘ └────────┬──────┘└───────┬───────┘
                       Fa1/0 │               │ Fa0/0
                10.1.23.1/30 │               │ 10.1.23.2/30
                             └───────────────┘
                                10.1.23.0/30
```

### Scenario Narrative
**NexaTech Solutions** (Enterprise AS 65001) has a fully functional iBGP network (from Lab 03).
The security and routing policy team has issued three new policy requirements:

1. **ISP-A (R2) Inbound:** Only accept the primary transit prefix `198.51.100.0/24` from ISP-A. The secondary prefixes `198.51.101.0/24` and `198.51.102.0/24` are not needed in the enterprise routing table and must be filtered.
2. **ISP-B (R3) Inbound/Outbound:**
   - Inbound: Deny the experimental prefix `203.0.115.0/24` from ISP-B. Accept all other ISP-B prefixes.
   - Outbound: Advertise only the primary enterprise subnet `192.168.1.0/24` to ISP-B. Keep `192.168.2.0/24` and `192.168.3.0/24` private.
3. **Internal (R4) Outbound:** R4 should only advertise its internal application subnets (`10.4.1.0/24`, `10.4.2.0/24`) to R1. Its loopback `172.16.4.4/32` should remain internal and not be propagated via iBGP.

Your task is to implement these policies using prefix-lists and distribute-lists, using soft reconfiguration to apply changes without disrupting live BGP sessions.

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

The following is **pre-configured** in the initial-configs (chained from Lab 03):

- Hostname, interface IPs, loopback interfaces on all routers
- Full eBGP sessions: R1–R2 and R1–R3 (with Weight on R1 preferring R2)
- ISP transit topology: R2–R3 eBGP peering
- iBGP session R1–R4 over loopback addresses with `update-source loopback0` and `next-hop-self`
- OSPF Area 0 on R1 and R4 for iBGP loopback reachability
- All ISP prefixes advertised and reachable end-to-end

The following is **NOT pre-configured** (you will configure these):

- `soft-reconfiguration inbound` on any neighbor
- Any `ip prefix-list` entries
- Any `neighbor X prefix-list` or `neighbor X distribute-list` statements
- ACL `ENTERPRISE-INTERNAL` on R4

---

## 5. Lab Challenge: Core Implementation

### Task 1: Enable Soft Reconfiguration for Inbound Policy

Before applying inbound filters, enable soft reconfiguration on R1 toward both ISP peers. This instructs IOS to store a raw, unfiltered copy of all received BGP updates in memory, enabling the use of `show ip bgp neighbors X received-routes` and allowing `clear ip bgp X soft in` to re-evaluate policy without resetting the TCP session.

- On R1, add `neighbor 10.1.12.2 soft-reconfiguration inbound`
- On R1, add `neighbor 10.1.13.2 soft-reconfiguration inbound`
- Perform a soft inbound reset on both neighbors to begin storing received updates: `clear ip bgp 10.1.12.2 soft in` and `clear ip bgp 10.1.13.2 soft in`

**Verification:** On R1, run `show ip bgp neighbors 10.1.12.2 received-routes`. You should see all three ISP-A prefixes (198.51.100.0/24, 198.51.101.0/24, 198.51.102.0/24) listed. This confirms the raw update store is working.

---

### Task 2: Filter Inbound Routes from ISP-A (R2) with a Prefix-List

NexaTech only wants the primary transit prefix from ISP-A in its routing table.

- On R1, define a prefix-list named `FROM-ISP-A`:
  - Sequence 10: `permit 198.51.100.0/24`
  - Sequence 20: `deny 0.0.0.0/0 le 32` (implicit deny — deny all others)
- Apply this prefix-list inbound to the R2 neighbor: `neighbor 10.1.12.2 prefix-list FROM-ISP-A in`
- Apply the new policy without resetting the BGP session: `clear ip bgp 10.1.12.2 soft in`

**Verification:**
- `show ip bgp neighbors 10.1.12.2 received-routes` — lists all three ISP-A prefixes (unfiltered raw store)
- `show ip bgp neighbors 10.1.12.2 routes` — lists only `198.51.100.0/24` (after filter applied)
- `show ip bgp` on R1 — confirm `198.51.101.0` and `198.51.102.0` are absent from the BGP table

---

### Task 3: Filter Inbound and Outbound Routes for ISP-B (R3)

**Inbound:** NexaTech does not want to accept ISP-B's experimental prefix.

- On R1, define a prefix-list named `FROM-ISP-B`:
  - Sequence 10: `deny 203.0.115.0/24`
  - Sequence 20: `permit 0.0.0.0/0 le 32` (permit all remaining prefixes)
- Apply inbound to the R3 neighbor: `neighbor 10.1.13.2 prefix-list FROM-ISP-B in`

**Outbound:** NexaTech only wants to advertise its primary subnet to ISP-B.

- On R1, define a prefix-list named `TO-ISP-B`:
  - Sequence 10: `permit 192.168.1.0/24`
  - Sequence 20: `deny 0.0.0.0/0 le 32` (deny all others)
- Apply outbound to the R3 neighbor: `neighbor 10.1.13.2 prefix-list TO-ISP-B out`
- Apply both policy changes: `clear ip bgp 10.1.13.2 soft`

**Verification:**
- `show ip bgp neighbors 10.1.13.2 received-routes` — shows all ISP-B prefixes including 203.0.115.0/24
- `show ip bgp neighbors 10.1.13.2 routes` — 203.0.115.0/24 is absent; 203.0.113.0 and 203.0.114.0 present
- `show ip bgp neighbors 10.1.13.2 advertised-routes` — confirms only `192.168.1.0/24` is sent to R3

---

### Task 4: Distribute-List Outbound Filtering on R4

R4 should only advertise its internal application subnets to R1 via iBGP. The loopback0 address (`172.16.4.4/32`) is used only for routing-protocol peering and should not propagate further.

- On R4, create a standard named ACL `ENTERPRISE-INTERNAL`:
  - `permit 10.4.1.0 0.0.0.255`
  - `permit 10.4.2.0 0.0.0.255`
  - (implicit deny all others)
- On R4, apply the distribute-list outbound to R1: `neighbor 172.16.1.1 distribute-list ENTERPRISE-INTERNAL out`
- Apply the change: `clear ip bgp 172.16.1.1 soft out`

**Verification:**
- On R1: `show ip bgp neighbors 172.16.4.4 received-routes` — shows only `10.4.1.0/24` and `10.4.2.0/24`. The `172.16.4.4/32` loopback prefix is absent.
- On R4: `show ip access-lists ENTERPRISE-INTERNAL` — confirms match counts after the soft reset.

---

## 6. Verification & Analysis

### Soft Reconfiguration State
```bash
R1# show ip bgp neighbors 10.1.12.2 received-routes
BGP table version is 8, local router ID is 172.16.1.1
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, m multipath, b backup-path, f RT-Filter
Origin codes: i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*> 172.16.2.2/32    10.1.12.2                0         100 65002 i
*> 198.51.100.0     10.1.12.2                0         100 65002 i
*> 198.51.101.0     10.1.12.2                0         100 65002 i   ! ← present in raw store
*> 198.51.102.0     10.1.12.2                0         100 65002 i   ! ← present in raw store

Total number of prefixes 4
```

### After Inbound Prefix-List FROM-ISP-A Applied
```bash
R1# show ip bgp neighbors 10.1.12.2 routes
   Network          Next Hop            Metric LocPrf Weight Path
*> 198.51.100.0     10.1.12.2                0         100 65002 i   ! ← only permitted prefix

Total number of prefixes 1                                            ! ← 198.51.101/102 filtered out

R1# show ip bgp | include 198.51
*> 198.51.100.0/24  10.1.12.2                0         100 65002 i
                                                                      ! ← .101 and .102 absent
```

### Outbound Filter to ISP-B (R3)
```bash
R1# show ip bgp neighbors 10.1.13.2 advertised-routes
BGP table version is 8, local router ID is 172.16.1.1

   Network          Next Hop            Metric LocPrf Weight Path
*> 192.168.1.0      0.0.0.0                  0         32768 i   ! ← only this prefix sent

Total number of prefixes 1                                        ! ← .2 and .3 filtered out
```

### R4 Distribute-List Result (on R1)
```bash
R1# show ip bgp neighbors 172.16.4.4 received-routes
   Network          Next Hop            Metric LocPrf Weight Path
*>i10.4.1.0/24      172.16.4.4               0    100      0 i   ! ← internal app subnet
*>i10.4.2.0/24      172.16.4.4               0    100      0 i   ! ← internal app subnet
                                                                   ! ← 172.16.4.4/32 absent
Total number of prefixes 2
```

---

## 7. Verification Cheatsheet

### Prefix-List Configuration
```
ip prefix-list <NAME> seq <10> permit <network/len>
ip prefix-list <NAME> seq <20> deny 0.0.0.0/0 le 32
!
router bgp <ASN>
 neighbor <peer> prefix-list <NAME> in
 neighbor <peer> prefix-list <NAME> out
```

### Distribute-List (ACL-based) Configuration
```
ip access-list standard <NAME>
 permit <network> <wildcard>
!
router bgp <ASN>
 neighbor <peer> distribute-list <NAME> out
```

### Soft Reconfiguration
```
router bgp <ASN>
 neighbor <peer> soft-reconfiguration inbound   ! Enable local update store

! Apply policy changes without TCP session reset:
clear ip bgp <peer> soft in     ! Re-evaluate inbound policy
clear ip bgp <peer> soft out    ! Re-push outbound advertisements
clear ip bgp <peer> soft        ! Both directions
```

### Key Show Commands
| Command | Purpose |
|---------|---------|
| `show ip prefix-list [NAME]` | Display prefix-list entries and match counters |
| `show ip bgp neighbors X received-routes` | All raw updates received from X (requires soft-reconfiguration) |
| `show ip bgp neighbors X routes` | Updates accepted after inbound policy |
| `show ip bgp neighbors X advertised-routes` | What this router is sending to X |
| `show ip access-lists NAME` | Show ACL entries and match counts (for distribute-list) |
| `clear ip bgp X soft in` | Re-apply inbound policy without session reset |
| `clear ip bgp X soft out` | Re-push outbound updates without session reset |

### Common Prefix-List Pitfalls

| Symptom | Likely Cause |
|---------|-------------|
| `show ip bgp neighbors X received-routes` fails with `% Inbound soft reconfiguration not enabled` | Missing `neighbor X soft-reconfiguration inbound` |
| Prefix-list applied but no change in routing table | Missing `clear ip bgp X soft in/out` after applying policy |
| All routes filtered (nothing accepted/advertised) | Missing final `permit 0.0.0.0/0 le 32` entry after deny entries |
| Prefix-list not matching expected prefixes | Incorrect prefix length — use `ge` and `le` modifiers to match ranges |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: Enable Soft Reconfiguration

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
router bgp 65001
 neighbor 10.1.12.2 soft-reconfiguration inbound
 neighbor 10.1.13.2 soft-reconfiguration inbound

! Then trigger update storage:
clear ip bgp 10.1.12.2 soft in
clear ip bgp 10.1.13.2 soft in
```
</details>

### Task 2: Inbound Filter from ISP-A (R2)

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
ip prefix-list FROM-ISP-A seq 10 permit 198.51.100.0/24
ip prefix-list FROM-ISP-A seq 20 deny 0.0.0.0/0 le 32

router bgp 65001
 neighbor 10.1.12.2 prefix-list FROM-ISP-A in

! Apply policy:
clear ip bgp 10.1.12.2 soft in
```
</details>

### Task 3: Inbound and Outbound Filters for ISP-B (R3)

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
ip prefix-list FROM-ISP-B seq 10 deny 203.0.115.0/24
ip prefix-list FROM-ISP-B seq 20 permit 0.0.0.0/0 le 32

ip prefix-list TO-ISP-B seq 10 permit 192.168.1.0/24
ip prefix-list TO-ISP-B seq 20 deny 0.0.0.0/0 le 32

router bgp 65001
 neighbor 10.1.13.2 prefix-list FROM-ISP-B in
 neighbor 10.1.13.2 prefix-list TO-ISP-B out

! Apply both directions:
clear ip bgp 10.1.13.2 soft
```
</details>

### Task 4: Distribute-List on R4

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4
ip access-list standard ENTERPRISE-INTERNAL
 permit 10.4.1.0 0.0.0.255
 permit 10.4.2.0 0.0.0.255

router bgp 65001
 neighbor 172.16.1.1 distribute-list ENTERPRISE-INTERNAL out

! Apply policy:
clear ip bgp 172.16.1.1 soft out
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

### Ticket 1 — Prefix-List Blocking All Routes from ISP-A

After a change window, the NOC reports that R1 is no longer receiving any routes from ISP-A. The BGP session is established, but `show ip bgp` shows no ISP-A prefixes. The engineer claims they "just updated the prefix-list."

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip bgp` on R1 shows `198.51.100.0/24` from ISP-A (next hop `10.1.12.2`). The `198.51.101.0` and `198.51.102.0` prefixes remain absent.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, check the BGP table: `show ip bgp`. Notice that no ISP-A (65002) prefixes appear.
2. The BGP session is up: `show ip bgp summary` shows R2 neighbor as Established with a prefix count.
3. Check the received-routes store: `show ip bgp neighbors 10.1.12.2 received-routes`. You can see all three ISP-A prefixes are being received.
4. Check the accepted routes: `show ip bgp neighbors 10.1.12.2 routes`. Zero prefixes shown — the filter is blocking everything.
5. View the prefix-list: `show ip prefix-list FROM-ISP-A`. You will find the list has a `deny 198.51.100.0/24` at sequence 10 (a deny instead of a permit), followed by `deny 0.0.0.0/0 le 32`. Result: every ISP-A prefix is denied.
6. Root cause: The prefix-list has a `deny` statement for the one prefix that should be allowed. The permit and deny are swapped.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — Remove the broken entry and replace with correct permit
no ip prefix-list FROM-ISP-A seq 10
ip prefix-list FROM-ISP-A seq 10 permit 198.51.100.0/24

! Re-apply inbound policy
clear ip bgp 10.1.12.2 soft in
```
</details>

---

### Ticket 2 — Cannot View Received Routes from ISP-B

A senior engineer wants to audit what ISP-B is actually sending before applying a new inbound policy. When they run `show ip bgp neighbors 10.1.13.2 received-routes` on R1, they get an error message instead of a route list.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip bgp neighbors 10.1.13.2 received-routes` on R1 returns the list of ISP-B prefixes without any error.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Run the failing command: `show ip bgp neighbors 10.1.13.2 received-routes`. The error reads `% Inbound soft reconfiguration not enabled`.
2. Check the running BGP config: `show running-config | section bgp`. Look at the neighbor statements for `10.1.13.2`. The `soft-reconfiguration inbound` command is absent for this neighbor.
3. Without `soft-reconfiguration inbound`, IOS does not maintain a pre-policy copy of received updates, so the `received-routes` command cannot function.
4. Note: `show ip bgp neighbors 10.1.13.2 routes` (accepted routes after policy) still works even without soft reconfiguration, but does not show what was received before the filter.
5. Root cause: The `neighbor 10.1.13.2 soft-reconfiguration inbound` command was removed (or never added).
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
router bgp 65001
 neighbor 10.1.13.2 soft-reconfiguration inbound

! Trigger a soft reset to start storing updates immediately
clear ip bgp 10.1.13.2 soft in
```
</details>

---

### Ticket 3 — Outbound Prefix Filter Not Taking Effect

An engineer applied the `TO-ISP-B` outbound prefix-list to block `192.168.2.0/24` and `192.168.3.0/24` from being advertised to ISP-B. However, when the ISP-B team checks their routing table, they report still receiving all three enterprise prefixes. R3's `show ip bgp` confirms all three are present.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip bgp neighbors 10.1.13.2 advertised-routes` on R1 shows only `192.168.1.0/24`. R3's BGP table does not contain `192.168.2.0` or `192.168.3.0`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1, check what is being advertised: `show ip bgp neighbors 10.1.13.2 advertised-routes`. All three enterprise prefixes (192.168.1/2/3) appear — the filter is not working.
2. Check the prefix-list itself: `show ip prefix-list TO-ISP-B`. The prefix-list is defined correctly.
3. Check the neighbor config: `show running-config | section bgp`. Look at the neighbor statement for `10.1.13.2`. The line `neighbor 10.1.13.2 prefix-list TO-ISP-B out` is present.
4. Check the match counters: `show ip prefix-list TO-ISP-B`. The match count shows zero matches — the filter has never been evaluated.
5. Root cause: The prefix-list was applied but a `clear ip bgp 10.1.13.2 soft out` was never performed. IOS does not automatically re-send updates when a new outbound policy is applied. The soft outbound reset triggers R1 to re-advertise its routes to R3, this time subject to the new prefix-list.
</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — trigger outbound soft reset to re-advertise with the new filter active
clear ip bgp 10.1.13.2 soft out
```
</details>

---

## 10. Lab Completion Checklist

### Core Implementation
- [ ] `soft-reconfiguration inbound` enabled on R1 toward R2 (10.1.12.2)
- [ ] `soft-reconfiguration inbound` enabled on R1 toward R3 (10.1.13.2)
- [ ] Prefix-list `FROM-ISP-A` permits only `198.51.100.0/24` from R2
- [ ] `198.51.101.0/24` and `198.51.102.0/24` absent from R1 BGP table
- [ ] Prefix-list `FROM-ISP-B` denies `203.0.115.0/24`; permits other ISP-B routes
- [ ] Prefix-list `TO-ISP-B` restricts R1 to advertising only `192.168.1.0/24` to R3
- [ ] `show ip bgp neighbors 10.1.13.2 advertised-routes` confirms single prefix sent
- [ ] ACL `ENTERPRISE-INTERNAL` on R4 permits only `10.4.1.0/24` and `10.4.2.0/24`
- [ ] R4 distribute-list outbound applied and verified (`172.16.4.4/32` absent from R1's received-routes from R4)

### Troubleshooting
- [ ] Ticket 1: Inverted deny/permit in prefix-list diagnosed and fixed
- [ ] Ticket 2: Missing `soft-reconfiguration inbound` diagnosed and fixed
- [ ] Ticket 3: Missing `clear ip bgp soft out` diagnosed and fix applied
