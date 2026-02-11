# CCNP ENCOR OSPF Lab 01: Basic OSPF Adjacency
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure OSPFv2 router processes and Router-IDs
- Establish OSPF neighbor adjacencies in a single area (Area 0)
- Understand and verify OSPF Hello and Dead intervals
- Examine the OSPF neighbor states (Down, Init, 2-Way, ExStart, Exchange, Loading, Full)
- Verify DR/BDR election process on multi-access segments
- Utilize basic OSPF verification commands

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
As the Lead Network Engineer for **Skynet Global**, you are tasking with modernizing the regional backbone. The current static routing architecture is no longer scalable as the firm expands its global footprint. 

Your mission is to deploy **OSPFv2** as the internal gateway protocol (IGP) for the core infrastructure. You will begin by establishing basic connectivity and neighbor adjacencies between the Headquarters (R1), the Backbone Router (R2), and the regional Branch (R3) within the backbone area (Area 0). Ensuring a stable and robust OSPF neighbor relationship is the foundation for all future advanced routing features.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 01 |
|--------|------|----------|-----------|---------------|
| R1 | Hub / ABR | c7200 | 10.1.1.1/32 | Yes |
| R2 | Backbone Router | c3725 | 10.2.2.2/32 | Yes |
| R3 | Branch Router | c3725 | 10.3.3.3/32 | Yes |

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.12.0.0/30 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.23.0.0/30 |
| R1           | Fa1/1           | R3            | Fa0/1            | 10.13.0.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

Ensure that all routers have their basic IP addresses and hostnames configured as per the `initial-configs/` directory.

---

## 5. Lab Challenge: Core OSPF Adjacency

### Objective 1: Enable OSPFv2 Routing
Initialize the OSPF process on all three routers.
- Use **Process ID 1**.
- Manually assign the **Router-ID** to match the Loopback0 address of each router.

### Objective 2: Establish Area 0 Adjacencies
Enable OSPF on the physical interfaces to form neighbors.
- All links must belong to **Area 0**.
- Use the `network` command or interface-level configuration (`ip ospf 1 area 0`) to enable the protocol.
- Ensure all Loopback0 interfaces are also advertised into OSPF.

### Objective 3: Verify Neighbor States
- Verify that all routers reach the **FULL** neighbor state.
- Identify which routers have been elected as **Designated Router (DR)** and **Backup Designated Router (BDR)** on each segment.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip ospf neighbor` | Confirm all neighbors are in the FULL state. |
| `show ip ospf interface brief` | Verify Area ID, Process ID, and interface status. |
| `show ip route ospf` | Confirm all loopbacks are reachable via OSPF. |
| `show ip protocols` | Verify OSPF Router-ID and active interfaces. |

---

## 7. Verification Cheatsheet

### 7.1 Verify OSPF Neighbors
Confirm that the neighbor relationship has reached the FULL state.
```bash
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.2.2.2          1   FULL/DR         00:00:34    10.12.0.2       Fa1/0
10.3.3.3          1   FULL/BDR        00:00:38    10.13.0.2       Fa1/1
```
*Verify: 'FULL' indicates successful database synchronization. DR/BDR roles depend on boot sequence.*

### 7.2 Verify OSPF Interface Parameters
Check the Hello/Dead timers and network type.
```bash
R1# show ip ospf interface FastEthernet 1/0
FastEthernet1/0 is up, line protocol is up 
  Internet Address 10.12.0.1/30, Area 0 
  Process ID 1, Router ID 10.1.1.1, Network Type BROADCAST, Cost: 1
  Transmit Delay is 1 sec, State BDR, Priority 1 
  Designated Router (ID) 10.2.2.2, Interface address 10.12.0.2
  Backup Designated router (ID) 10.1.1.1, Interface address 10.12.0.1
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```
*Verify: Timer intervals MUST match for adjacency to form.*

### 7.3 Verify Routing Table
```bash
R1# show ip route ospf
      10.0.0.0/8 is variably subnetted, 6 subnets, 2 masks
O        10.2.2.2/32 [110/2] via 10.12.0.2, 00:05:12, FastEthernet1/0
O        10.3.3.3/32 [110/2] via 10.13.0.2, 00:05:12, FastEthernet1/1
```
*Verify: Loopbacks are learned via OSPF (AD 110).*

---

## 8. Troubleshooting Scenario

### The Fault
After configuring OSPF on R3, the adjacency with R1 is stuck in the **EXSTART** state.

### The Mission
1. Investigate potential causes for the EXSTART hang (e.g., MTU mismatch).
2. Use `show ip ospf interface` to check interface parameters.
3. Restore the adjacency to the FULL state and confirm route exchange.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1 & 2: OSPF Configuration
```bash
! R1
router ospf 1
 router-id 10.1.1.1
 network 10.1.1.1 0.0.0.0 area 0
 network 10.12.0.0 0.0.0.3 area 0
 network 10.13.0.0 0.0.0.3 area 0

! R2
router ospf 1
 router-id 10.2.2.2
 network 10.2.2.2 0.0.0.0 area 0
 network 10.12.0.0 0.0.0.3 area 0
 network 10.23.0.0 0.0.0.3 area 0

! R3
router ospf 1
 router-id 10.3.3.3
 network 10.3.3.3 0.0.0.0 area 0
 network 10.13.0.0 0.0.0.3 area 0
 network 10.23.0.0 0.0.0.3 area 0
```

---

## 10. Lab Completion Checklist

- [ ] OSPF Router-IDs correctly assigned.
- [ ] All neighbors in FULL state.
- [ ] Full reachability to all loopbacks via OSPF.
- [ ] DR/BDR roles identified on each segment.
- [ ] Troubleshooting challenge resolved.