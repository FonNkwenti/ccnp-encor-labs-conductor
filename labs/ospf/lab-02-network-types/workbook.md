# CCNP ENCOR OSPF Lab 02: OSPF Network Types
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Understand and configure different OSPF network types (Broadcast, Point-to-Point)
- Influence DR/BDR elections using interface priorities
- Optimize adjacency establishment by selecting appropriate network types
- Verify the impact of network types on the OSPF topology database
- Analyze the behavior of Hello and Dead timers across different network types

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │    Hub / ABR    │
                    │  Lo0: 10.1.1.1  │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1
                        │         │
           10.12.0.1/30 │         │ 10.13.0.1/30
                        │         │
                        │         │ 10.12.0.2/30
                        │    ┌────┴────────┐
                        │    │     R2      │
                        │    │  Backbone   │
                        │    │ 10.2.2.2/32 │
                        │    └────┬────────┘
                        │         │ Fa0/1
                        │         │ 10.23.0.1/30
                        │         │
                        │         │ 10.23.0.2/30
                        │         │ Fa0/0
                 ┌──────┴─────────┘
                 │       R3        
                 │     Branch      
                 │  10.3.3.3/32    
                 └─────────────────┘
```

### Scenario Narrative
The **Skynet Global** core network expansion is well underway. However, the initial OSPF deployment utilized the default Ethernet settings for all links. As the Lead Network Engineer, you have observed that the point-to-point links between the routers are currently performing unnecessary DR/BDR elections, which slightly increases adjacency settling time and control plane overhead.

Your mission is to optimize the OSPF topology by correctly identifying and configuring the network types for each segment. You will also implement a deterministic DR/BDR election strategy for segments that remain multi-access, ensuring that the Hub router (**R1**) maintains its role as the primary synchronization point for the regional backbone.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 02 |
|--------|------|----------|-----------|---------------|
| R1 | Hub / ABR | c7200 | 10.1.1.1/32 | No |
| R2 | Backbone Router | c3725 | 10.2.2.2/32 | No |
| R3 | Branch Router | c3725 | 10.3.3.3/32 | No |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 01.** Ensure that OSPF adjacencies are established and stable across all links before proceeding with network type optimization.

---

## 5. Lab Challenge: Network Type Optimization

### Objective 1: Optimize Point-to-Point Links
The links between **R1 <-> R2** and **R1 <-> R3** are dedicated physical segments.
- Configure both ends of these links to use the OSPF **Point-to-Point** network type.
- Verify that the DR/BDR election is no longer performed on these segments.
- Confirm that the neighbor state remains **FULL**.

### Objective 2: Deterministic DR/BDR Election
The link between **R2 <-> R3** must remain as a **Broadcast** network type for future multi-access expansion.
- Configure **R2** to be the **Designated Router (DR)** for this segment by increasing its OSPF priority.
- Configure **R3** to be the **Backup Designated Router (BDR)** by ensuring its priority is lower than R2's but higher than the default if necessary.
- Verify the election results using appropriate `show` commands.

### Objective 3: Analyze Timer Behavior
- Examine how the Hello and Dead intervals change (or remain consistent) when switching between Broadcast and Point-to-Point network types.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip ospf interface <id>` | Verify the "Network Type" field matches the objective. |
| `show ip ospf neighbor` | Confirm the "Pri" and "State" fields reflect the new network types and priorities. |
| `show ip ospf database` | Verify that the topology database correctly reflects the segments. |

---

## 7. Verification Cheatsheet

### 7.1 Verify Point-to-Point Network Type
```bash
R1# show ip ospf interface FastEthernet 1/0
FastEthernet1/0 is up, line protocol is up 
  Internet Address 10.12.0.1/30, Area 0 
  Process ID 1, Router ID 10.1.1.1, Network Type POINT_TO_POINT, Cost: 1
```
*Verify: Network Type is now POINT_TO_POINT and DR/BDR fields are missing.*

### 7.2 Verify DR/BDR Priorities
```bash
R2# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.3.3.3         50   FULL/BDR        00:00:32    10.23.0.2       Fa0/1
```
*Verify: R3 appears as BDR with the assigned priority (e.g., 50).*

---

## 8. Troubleshooting Scenario

### The Fault
After changing the network type to Point-to-Point on R1's interface to R2, the adjacency fails to form, even though R2's interface remains at the default Broadcast type.

### The Mission
1. Explain why OSPF adjacencies fail when network types are mismatched between neighbors.
2. Correct the mismatch and restore the neighbor relationship.
3. Verify that the Hello and Dead intervals are identical on both sides.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: Point-to-Point Configuration
```bash
! R1, R2, R3
interface <interface_id>
 ip ospf network point-to-point
```

### Objective 2: Priority Configuration
```bash
! R2
interface FastEthernet 0/1
 ip ospf priority 255

! R3
interface FastEthernet 0/0
 ip ospf priority 100
```

---

## 10. Lab Completion Checklist

- [ ] R1-R2 link optimized as Point-to-Point.
- [ ] R1-R3 link optimized as Point-to-Point.
- [ ] R2 elected as DR on the R2-R3 segment.
- [ ] R3 elected as BDR on the R2-R3 segment.
- [ ] Troubleshooting challenge resolved.
