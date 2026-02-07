# CCNP ENCOR EIGRP Lab 06: Filtering & Control
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Implement route filtering using EIGRP `distribute-list`
- Configure prefix-lists for granular route matching
- Utilize route-maps for advanced traffic engineering and attribute manipulation
- Manage EIGRP adjacency with passive-interfaces
- Verify route propagation and filtering effects
- Understand the order of operations for EIGRP filtering mechanisms

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1 (WAN Link)
                        │         │ 10.0.12.1/30
                        │         │
           10.0.12.1/30 │         │
                        │         │ 10.0.12.2/30
                        │    ┌────┴────────┐
                        │    │     R2      │
                        │    │   Branch    │
                        │    │ 2.2.2.2/32  │
                        │    └────┬────────┘
                        │         │ Fa0/1
                        │         │ 10.0.23.1/30
                        │         │
                        │         │ 10.0.23.2/30
                        │         │ Fa0/0
                 ┌──────┴─────────┘
                 │       R3        
                 │  Remote Branch  
                 │  3.3.3.3/32     
                 └───┬─────────┐
                     │ Fa0/1   │
                     │         │ 10.0.35.1/30
                     │         │
                     │         │ 10.0.35.2/30
                     │         │ Fa0/0
              ┌──────┴─────────┘
              │       R5        
              │   Stub Network  
              │  5.5.5.5/32     
              └─────────────────┘
```

### Scenario Narrative
With the security framework established in the previous phase, the **Skynet Global** CTO has now mandated a more granular control over the enterprise's reachability information. Currently, too much internal infrastructure information is being leaked to the Branch and Remote Branch sites, creating unnecessary routing table overhead and potential security risks.

As the Network Engineer, your mission is to implement **Traffic Engineering** and **Route Filtering** to ensure that only authorized prefixes are propagated throughout the EIGRP domain. You will use **Prefix-Lists** and **Distribute-Lists** to prevent the Hub (R1) from receiving non-essential routes and employ **Route-Maps** to selectively allow traffic based on Skynet Global's connectivity policies.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 06 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R5 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 05.** Ensure authentication (MD5/SHA) is functional between all routers before starting the filtering challenge.

---

## 5. Lab Challenge: Route Filtering & Traffic Control

### Objective 1: Implement Granular Filtering with Prefix-Lists (R1)
The Headquarters (R1) should only receive specific networks from the Branch.
- Create an **IP Prefix-List** named `AUTHORIZED_NETS` on **R1**.
- The list must permit:
    - The Branch Loopback (2.2.2.2/32)
    - The Remote Branch Loopback (3.3.3.3/32)
    - The Stub site major network (10.5.0.0/16)
- Apply this prefix-list using a **Distribute-List** in the EIGRP process on R1 to filter incoming updates on `FastEthernet1/0`.

### Objective 2: Advanced Control using Route-Maps (R2)
The Branch (R2) needs to selectively filter routes advertised to the Remote Branch (R3).
- Create a **Route-Map** named `RM_FILTER_R3` on **R2**.
- Use a prefix-list to match and **deny** the propagation of R1's Loopback (1.1.1.1/32) to R3.
- Allow all other routes.
- Apply the route-map using a **Distribute-List** in the EIGRP process on R2 for outbound updates to R3.

### Objective 3: Standard Access-List Filtering (R3)
- On **R3**, use a **Standard Access-List** to prevent the Stub Network (R5) from receiving any 10.0.x.x infrastructure routes.
- R5 should only know about its local subnets and the default route (if provided) or specific enterprise loopbacks.
- Apply this filter using a **Distribute-List** on R3 for outbound updates to R5.

### Objective 4: Verification of Filtering Order
- Use `show ip route` on R1, R3, and R5 to verify that the filtering is working as intended.
- Confirm that filtered routes are removed from the routing table but may still exist in the topology table (depending on where the filter is applied).

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip prefix-list` | Verify prefix-list entries and hit counts. |
| `show ip route eigrp` | Confirm that R1 only sees permitted routes in its routing table. |
| `show ip eigrp topology` | Check if filtered routes are still present in the topology table (useful for understanding `distribute-list in` behavior). |
| `show ip eigrp neighbors detail` | Confirm authentication is still UP. |

---

## 7. Verification Cheatsheet

### 7.1 Verify Prefix-List Hits (R1)
```bash
R1# show ip prefix-list AUTHORIZED_NETS
ip prefix-list AUTHORIZED_NETS: 3 entries
   seq 5 permit 2.2.2.2/32 (hit count 2)
   seq 10 permit 3.3.3.3/32 (hit count 2)
   seq 15 permit 10.5.0.0/16 ge 24 le 32 (hit count 8)
```

### 7.2 Routing Table Validation (R5)
Ensure R5 has limited visibility into the core infrastructure.
```bash
R5# show ip route eigrp
! (Should NOT see 10.0.12.0/30, 10.0.23.0/30 etc. based on R3's filter)
```

### 7.3 Topology Table Analysis (R2)
```bash
R2# show ip eigrp topology
! (Check for routes that are filtered outbound to R3 but still visible on R2)
```

---

## 8. Troubleshooting Scenario

### The Fault
After applying the `AUTHORIZED_NETS` prefix-list on R1, the neighbor adjacency with R2 remains UP, but R1 can no longer ping R3's loopback (3.3.3.3), even though it is explicitly permitted in the prefix-list.

### The Mission
1. Check the `show ip route` on R1.
2. Investigate if the next-hop prefix (10.0.12.0/30) was accidentally filtered by the prefix-list. (Hint: EIGRP needs to know the route to the next-hop to install the prefix!)
3. Update the prefix-list to include the necessary infrastructure subnets for recursive lookup.
4. Verify end-to-end reachability.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: Prefix-List Filtering (R1)
```bash
ip prefix-list AUTHORIZED_NETS seq 5 permit 2.2.2.2/32
ip prefix-list AUTHORIZED_NETS seq 10 permit 3.3.3.3/32
ip prefix-list AUTHORIZED_NETS seq 15 permit 10.5.0.0/16 ge 24 le 32
ip prefix-list AUTHORIZED_NETS seq 20 permit 10.0.12.0/30 ! Fix for next-hop
!
router eigrp 100
 distribute-list prefix AUTHORIZED_NETS in FastEthernet1/0
```

### Objective 2: Route-Map Control (R2)
```bash
ip prefix-list R1_LOOP permit 1.1.1.1/32
!
route-map RM_FILTER_R3 deny 10
 match ip address prefix-list R1_LOOP
route-map RM_FILTER_R3 permit 20
!
router eigrp 100
 distribute-list route-map RM_FILTER_R3 out FastEthernet0/1
```

### Objective 3: Access-List Filtering (R3)
```bash
access-list 66 deny 10.0.0.0 0.255.255.255
access-list 66 permit any
!
router eigrp 100
 distribute-list 66 out FastEthernet0/1
```

---

## 10. Lab Completion Checklist

- [ ] R1 prefix-list applied and verified (correct routes in routing table).
- [ ] R2 route-map filtering R1's loopback from R3.
- [ ] R3 access-list filtering infrastructure routes from R5.
- [ ] Troubleshooting challenge resolved (recursive lookup understanding).
- [ ] All adjacencies remain stable with authentication.
