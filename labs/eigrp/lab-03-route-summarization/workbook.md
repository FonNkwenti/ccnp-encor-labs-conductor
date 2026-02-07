# CCNP ENCOR EIGRP Lab 03: Route Summarization
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure manual route summarization on EIGRP
- Understand how summarization creates query boundaries
- Verify summary routes in the topology table
- Analyze the impact of summarization on routing table size
- Troubleshoot summarization misconfigurations
- Integrate a new router (R7) into an existing EIGRP domain

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa0/0
                        │         │ 10.0.17.1/30
                        │         │
         10.0.12.1/30   │         │ 10.0.17.2/30
                        │         │ Fa0/0
                        │    ┌────┴────────┐
                        │    │     R7      │
                        │    │  (Summary   │
                        │    │  Boundary)  │
                        │    │ Lo0: 7.7.7.7│
                        │    └─────────────┘
                        │
                        │ 10.0.12.2/30
                        │ Fa0/0
                ┌───────┴─────────┐
                │       R2        │
                │ (Branch Router) │
                │  Lo0: 2.2.2.2   │
                └───────┬─────────┘
                        │ Fa0/1
                        │ 10.0.23.1/30
                        │
                        │ 10.0.23.2/30
                        │ Fa0/0
                ┌───────┴─────────┐
                │       R3        │
                │ (Remote Branch) │
                │  Lo0: 3.3.3.3   │
                │  + Summary nets │
                └─────────────────┘
```

### Scenario Narrative
As the Lead Network Architect for **Skynet Global**, you are managing a rapidly expanding enterprise network. The routing tables on the Core (R1) and Branch (R2) routers are growing significantly, and you have observed that EIGRP queries are propagating across the entire domain whenever a remote link flaps, causing unnecessary CPU overhead and potential "Stuck-In-Active" (SIA) issues.

Your mission is to implement **Manual Route Summarization** at key network boundaries. This will optimize the routing table size and, more importantly, create **Query Boundaries** to contain EIGRP convergence events. You have deployed a new router, **R7**, to serve as a summary boundary for the 172.16.0.0/16 regional subnet.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 03 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R7 | Summary Boundary | c3725 | 7.7.7.7/32 | **Yes** |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R7 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 02.** Ensure basic EIGRP connectivity is established before proceeding.

### R7 (New Boundary Router - Complete Config)
Configure R7 with its Loopbacks and establish EIGRP AS 100 connectivity to R1.
```bash
enable
configure terminal
hostname R7
interface Loopback0
 ip address 7.7.7.7 255.255.255.255
interface Loopback1
 ip address 172.16.1.1 255.255.255.0
interface Loopback2
 ip address 172.16.2.1 255.255.255.0
interface Loopback3
 ip address 172.16.3.1 255.255.255.0
interface Loopback4
 ip address 172.16.4.1 255.255.255.0
interface FastEthernet0/0
 description Link to R1 (Hub)
 ip address 10.0.17.2 255.255.255.252
 no shutdown
router eigrp 100
 network 7.7.7.7 0.0.0.0
 network 10.0.17.0 0.0.0.3
 network 172.16.0.0 0.0.255.255
 no auto-summary
 passive-interface default
 no passive-interface FastEthernet0/0
end
```

### R3 (Simulated Branch Networks)
Add the specific subnets that will be summarized at the R3 boundary.
```bash
enable
configure terminal
interface Loopback1
 ip address 192.168.1.1 255.255.255.0
interface Loopback2
 ip address 192.168.2.1 255.255.255.0
interface Loopback3
 ip address 192.168.3.1 255.255.255.0
router eigrp 100
 network 192.168.0.0 0.0.255.255
 passive-interface Loopback1
 passive-interface Loopback2
 passive-interface Loopback3
end
```

---

## 5. Lab Challenge: Route Summarization

### Objective 1: Implement Regional Summarization at R7
Configure manual route summarization on R7's outbound interface to R1.
- Summarize all `172.16.x.x` networks into a single `/16` advertisement.
- Verify that R1 receives only the summary route and no longer sees the individual `/24` subnets.
- Confirm the presence of the **Discard Route** (Null0) in R7's routing table.

### Objective 2: Implement Remote Site Summarization at R3
Configure manual route summarization on R3's outbound interface to R2.
- Summarize the `192.168.1.0/24`, `192.168.2.0/24`, and `192.168.3.0/24` networks into a single `/16` advertisement.
- Verify that R2 and R1 only see the summary route.

### Objective 3: Validate Query Boundary Containment
Confirm that summarization effectively limits the scope of EIGRP queries.
- Enable EIGRP packet debugging on R1.
- Simulate a failure of a specific subnet at R3 (e.g., shutdown `Loopback1`).
- Observe that R1 does **not** receive a query for the failed subnet, as the summary route at R3 remains valid.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip route eigrp` | Only `/16` summaries for `172.16.0.0` and `192.168.0.0` are present. |
| `show ip route | include Null0` | A discard route for each summary exists on the summarizing router. |
| `show ip eigrp topology` | The summary route is present in the topology table with a distance matching the best component. |
| `debug eigrp packets query` | No queries received on R1 when a summarized subnet flaps. |

---

## 7. Verification Cheatsheet

### 7.1 Verify Inbound Summary Routes (R1)
Confirm that R1 is receiving summarized advertisements for the regional (172.16.0.0/16) and remote (192.168.0.0/16) sites.
```bash
R1# show ip route eigrp | include 0.0/16
D        172.16.0.0/16 [90/156160] via 10.0.17.2, 00:05:12, FastEthernet0/0
D        192.168.0.0/16 [90/158720] via 10.0.12.2, 00:04:45, FastEthernet1/0
```
*Verify: Routes are summarized (mask /16) and individual /24 subnets are absent.*

### 7.2 Verify Local Discard Routes (R7/R3)
On the summarizing routers, ensure a discard route to `Null0` exists to prevent routing loops.
```bash
R7# show ip route 172.16.0.0 255.255.0.0
Routing entry for 172.16.0.0/16
  Known via "eigrp 100", distance 5, metric 128256, type internal
  Redistributing via eigrp 100
  Routing Descriptor Blocks:
  * directly connected, via Null0
      Route metric is 128256, traffic share count is 1
      Total delay is 5000 microseconds, minimum bandwidth is 100000 Kbit
      Reliability 255/255, minimum MTU 1500 bytes
      Loading 1/255, Hops 0
```
*Verify: The 'directly connected, via Null0' entry is present with an Administrative Distance of 5.*

### 7.3 Query Containment Test (R1)
Verify that R1 remains "blind" to component route flapping at the remote site.
```bash
R1# debug eigrp packets query
EIGRP Packets debugging is on
    (Query)
!
! <Wait for subnet flap at R3>
!
R1#
! (No output should appear)
```
*Verify: R1 does not receive queries because the summary route at R3 remains UP.*

---

## 8. Troubleshooting Scenario

### The Fault
After implementing the summary at R7, R3 can no longer reach any of the `172.16.x.x` subnets. Analysis on R1 reveals that the route to `172.16.0.0/16` is pointing to `Null0` instead of being learned from R7.

### The Mission
1. Identify the configuration error on R1 that is causing it to discard traffic for the `172.16.0.0/16` range.
2. Correct the configuration to restore end-to-end reachability.
3. Verify that R1 now learns the summary correctly from R7.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: Regional Summarization (R7)
```bash
interface FastEthernet0/0
 ip summary-address eigrp 100 172.16.0.0 255.255.0.0
```

### Objective 2: Remote Site Summarization (R3)
```bash
interface FastEthernet0/0
 ip summary-address eigrp 100 192.168.0.0 255.255.0.0
```

---

## 10. Lab Completion Checklist

- [ ] R7 integrated and EIGRP adjacency established with R1.
- [ ] Manual summarization configured on R7 (172.16.0.0/16).
- [ ] Manual summarization configured on R3 (192.168.0.0/16).
- [ ] Null0 discard routes verified on R7 and R3.
- [ ] R1 and R2 routing tables optimized (summaries only).
- [ ] Query boundary containment verified via debug.
- [ ] Troubleshooting challenge resolved.