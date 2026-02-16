# CCNP ENCOR OSPF Lab 04: Multi-Area OSPF
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Understand OSPF Multi-Area hierarchy and the role of Area 0 (Backbone Area)
- Identify and configure Area Border Router (ABR) functionality
- Analyze OSPF LSA Types (Type 1: Router, Type 2: Network, Type 3: Summary)
- Verify inter-area routing and database consistency
- Understand the requirement for all non-backbone areas to connect to Area 0

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
           10.12.0.1/30 │ Area 0  │ 10.13.0.1/30
                        │         │
                        │         │ 10.13.0.2/30
                        │    ┌────┴────────┐
                        │    │     R3      │
                        │    │   Branch    │
                        │    │ 10.3.3.3/32 │
                        │    └────┬────────┘
                        │         │ Fa0/0
                        │         │ 10.23.0.2/30
                        │         │ Area 1
                        │         │ 10.23.0.1/30
                        │         │ Fa0/1
                 ┌──────┴─────────┘
                 │       R2
                 │ Backbone/ABR
                 │  10.2.2.2/32
                 └─────────────────┘
```

### Scenario Narrative
The **Skynet Global** network is growing rapidly. To prevent the OSPF Link-State Database (LSDB) from becoming too large and to contain the impact of SPF calculations during topology changes, the architectural team has decided to transition from a single-area design to a Multi-Area hierarchy.

Your task is to move the branch office link between **R2** and **R3** into a new **Area 1**. This will transform **R2** into an Area Border Router (ABR). You will then verify that inter-area communication remains functional and examine how OSPF uses Summary LSAs (Type 3) to advertise routes between areas.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 04 |
|--------|------|----------|-----------|---------------|
| R1 | Hub / ABR | c7200 | 10.1.1.1/32 | No |
| R2 | Backbone Router / ABR | c3725 | 10.2.2.2/32 | No |
| R3 | Branch Router | c3725 | 10.3.3.3/32 | No |

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet | Area |
|--------------|-----------------|---------------|------------------|--------|------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.12.0.0/30 | 0 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.23.0.0/30 | 1 |
| R1           | Fa1/1           | R3            | Fa0/1            | 10.13.0.0/30 | 0 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

> **This lab builds on Lab 03.** Ensure that all OSPF adjacencies are stable, reference bandwidth is set to 1000 Mbps, and manual cost manipulations from Lab 03 have been removed or accounted for.

---

## 5. Lab Challenge: Multi-Area OSPF

### Objective 1: Migrate Link to Area 1
Isolate the branch link from the backbone area updates.
- On **R2**, change the OSPF area for interface `FastEthernet0/1` from **Area 0** to **Area 1**.
- On **R3**, change the OSPF area for interface `FastEthernet0/0` from **Area 0** to **Area 1**.
- Also on **R3**, move `Loopback0` into **Area 1**.
- Verify that the neighbor adjacency between R2 and R3 re-establishes successfully.

### Objective 2: Verify ABR Role and Inter-Area Reachability
With Area 1 active, confirm that R2 is correctly performing its role as an ABR.
- Use `show ip ospf` on **R2** to confirm it identifies itself as an Area Border Router.
- Verify that **R1** (in Area 0) can still ping **R3's** loopback (10.3.3.3) in Area 1.
- Examine the routing table on **R1**. Identify the code for routes learned from Area 1.

### Objective 3: Analyze OSPF LSA Types
Examine the OSPF database to understand how multi-area routing is achieved.
- On **R1**, use `show ip ospf database` to view the LSDB.
- Identify the **Summary Net Link States (Area 0)** section. What LSA type are these?
- On **R2**, examine the database for both Area 0 and Area 1. Note the difference in Router LSAs (Type 1) between the two areas.
- Locate the LSA for R3's loopback (10.3.3.3) in R1's database. Identify the advertising router.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip ospf` | Confirm "It is an area border router" on R2. |
| `show ip route ospf` | Confirm Area 1 routes are marked with `IA` (Inter-Area). |
| `show ip ospf database` | Verify existence of Type 1, 2, and 3 LSAs. |
| `show ip ospf database summary` | Examine detailed information for Type 3 Summary LSAs. |

---

## 7. Verification Cheatsheet

### 7.1 Verify ABR Status on R2
```bash
R2# show ip ospf | include border
 Routing Process "ospf 1" with ID 10.2.2.2
 It is an area border router
```

### 7.2 Verify Inter-Area Routes on R1
Confirm that R3's loopback and the branch link are now IA routes.
```bash
R1# show ip route ospf
      10.0.0.0/8 is variably subnetted, 7 subnets, 2 masks
O IA     10.3.3.3/32 [110/21] via 10.12.0.2, FastEthernet1/0
O IA     10.23.0.0/30 [110/20] via 10.12.0.2, FastEthernet1/0
```
*Note: The IA code indicates an OSPF Inter-Area route.*

### 7.3 Analyze Summary LSAs (Type 3)
```bash
R1# show ip ospf database summary 10.3.3.3

            OSPF Router with ID (10.1.1.1) (Process ID 1)

                Summary Net Link States (Area 0)

  LS age: 154
  Options: (No TOS-capability, DC, Upward)
  LS Type: Summary Links(Network)
  Link State ID: 10.3.3.3 (summary Network Number)
  Advertising Router: 10.2.2.2
  LS Seq Number: 80000001
  Checksum: 0x4A3D
  Length: 28
  Network Mask: /32
        MTID: 0         Metric: 11
```
*Verify: The Advertising Router is the ABR (R2), and the LS Type is Summary Links.*

---

## 8. Troubleshooting Scenario

### The Fault
You moved R3's `FastEthernet0/1` (the link to R1) into **Area 1** as well. Now, R1 reports that it has lost reachability to R3's loopback, even though the physical link is up and pings between physical interfaces work.

### The Mission
1. Explain why moving the R1-R3 link into Area 1 broke backbone connectivity for R3.
2. Recall the rule regarding Area 0 continuity and non-backbone area connectivity.
3. Correct the interface area configuration to restore full reachability.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: Migrate Link to Area 1
```bash
! R2
router ospf 1
 no network 10.23.0.0 0.0.0.3 area 0
 network 10.23.0.0 0.0.0.3 area 1

! R3
router ospf 1
 no network 10.23.0.0 0.0.0.3 area 0
 no network 3.3.3.3 0.0.0.0 area 0
 network 10.23.0.0 0.0.0.3 area 1
 network 3.3.3.3 0.0.0.0 area 1
```

---

## 10. Lab Completion Checklist

- [ ] R2-R3 link migrated to Area 1.
- [ ] R3 Loopback0 migrated to Area 1.
- [ ] R2 verified as an ABR.
- [ ] R1 reaches R3 via Inter-Area (IA) routes.
- [ ] LSA Type 3 (Summary) analyzed in the LSDB.
- [ ] Troubleshooting challenge resolved (Backbone continuity).
