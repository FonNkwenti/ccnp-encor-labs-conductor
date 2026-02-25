# Lab 06: OSPF NSSA & Route Control
## Skynet Global: Area 4 R&D Expansion

### Scenario
As Skynet Global continues to consolidate its AI research divisions, a new high-security R&D node (**R4**) has been established in **Area 4**. To maintain a lean routing table and prevent the research network from being flooded with external routes from the backbone, you have been tasked with configuring Area 4 as a **Not-So-Stubby Area (NSSA)**.

Furthermore, R4 will be performing external route injection (simulated research subnets) which must be translated and advertised back into the backbone. Finally, to ensure routing efficiency, you must implement inter-area summarization on the ABR (**R1**).

### Objectives
1. **Scenario Readiness**: Ensure R1, R2, R3, and R4 are running OSPFv2 with correct area memberships.
2. **NSSA Migration**: Transition Area 4 (R1-R4) from a standard area to an **NSSA**.
3. **External Injection**: Inject the `172.16.4.0/24` subnet on R4 into OSPF as an external route.
4. **Totally NSSA**: Optimize Area 4 further by making it a **Totally NSSA**, replacing Type 3 LSAs with a default route.
5. **Route Control**: Implement inter-area summarization on R1 for the backbone and branch segments advertised into Area 4.

---

### Hardware Specifications
| Device | Role | Platform | Image |
|--------|------|----------|-------|
| R1 | Hub/ABR | c7200 | IOS 15.x |
| R2 | Backbone | c7200 | IOS 15.x |
| R3 | Branch | c7200 | IOS 15.x |
| R4 | NSSA Router | c7200 | IOS 15.x |

#### Cabling & Connectivity
| Local Interface | Local Device | Remote Device | Remote Interface | Subnet |
|-----------------|--------------|---------------|------------------|--------|
| Fa0/0 | R1 | R4 | Fa0/0 | 10.14.0.0/30 |
| Fa1/0 | R1 | R2 | Fa0/0 | 10.12.0.0/30 |
| Fa1/1 | R1 | R3 | Fa1/0 | 10.13.0.0/30 |
| Fa1/0 | R2 | R3 | Fa0/0 | 10.23.0.0/30 |

---

### Challenge Tasks

#### Task 1: Area 4 NSSA Configuration
- Configure the link between R1 and R4 as OSPF **Area 4**.
- On both R1 and R4, transition Area 4 to **NSSA**.
- **Verification**: Ensure the OSPF adjacency between R1 and R4 re-establishes and is recognized as an NSSA neighbor.

#### Task 2: Type 7 LSA Injection
- On **R4**, redistribute the `Loopback100` (172.16.4.0/24) into OSPF.
- **Verification**: Check the OSPF database on R4 for a **Type 7 LSA**. Check the routing table on R2/R3 to see how this route is received.

#### Task 3: Translation and Optimization
- Verify that **R1** (the ABR) is performing the **Type 7 to Type 5 translation**.
- Configure Area 4 as **Totally NSSA** on R1 to block Type 3 LSAs.
- **Verification**: Ensure R4 only sees a default route for inter-area and external traffic (except its own NSSA externals).

#### Task 4: Inter-Area Summarization
- On **R1**, summarize the Area 1 network (`10.23.0.0/24`) before it is advertised into Area 0.
- **Verification**: Check R2's routing table for the summary route.

---

### Verification Cheatsheet
| Check | Command |
|-------|---------|
| OSPF Neighbors | `show ip ospf neighbor` |
| NSSA Status | `show ip ospf | include Area 4` |
| Type 7 LSAs | `show ip ospf database nssa-external` |
| OSPF Database | `show ip ospf database` |
| Routing Table | `show ip route ospf` |

---

### Solutions
<details>
<summary>Click to view R1 Configuration</summary>

```bash
router ospf 1
 area 14 nssa no-summary
 area 1 range 10.23.0.0 255.255.255.0
 network 10.14.0.0 0.0.0.3 area 14
```
</details>

<details>
<summary>Click to view R4 Configuration</summary>

```bash
router ospf 1
 area 14 nssa
 redistribute connected subnets
```
</details>
