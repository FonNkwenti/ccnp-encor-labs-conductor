# CCNP ENCOR OSPF Lab 03: Path Selection & Metrics
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Understand OSPF cost calculation (Reference Bandwidth / Interface Bandwidth)
- Identify the default reference bandwidth and its limitations with high-speed links
- Configure `auto-cost reference-bandwidth` for consistent cost scaling
- Manipulate path selection using manual `ip ospf cost` on specific interfaces
- Verify OSPF shortest path selection using the routing table and OSPF database
- Analyze path cost changes and their impact on traffic flow

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
                        │         │ 10.13.0.2/30
                        │    ┌────┴────────┐
                        │    │     R3      │
                        │    │   Branch    │
                        │    │ 10.3.3.3/32 │
                        │    └────┬────────┘
                        │         │ Fa0/0
                        │         │ 10.23.0.2/30
                        │         │
                        │         │ 10.23.0.1/30
                        │         │ Fa0/1
                 ┌──────┴─────────┘
                 │       R2
                 │   Backbone
                 │  10.2.2.2/32
                 └─────────────────┘
```

### Scenario Narrative
With the **Skynet Global** OSPF deployment now stable and network types optimized, management has raised a concern: all FastEthernet links in the topology carry the same OSPF cost of **1**, making it impossible to differentiate between a 100 Mbps link and a future 1 Gbps upgrade. Additionally, the security team requires that all traffic from Headquarters (R1) to the Branch (R3) traverse the Backbone Router (R2) for inline packet inspection, even though a direct link exists.

As the Lead Network Engineer, your mission is to first standardize the OSPF cost model across the entire backbone by adjusting the reference bandwidth, and then implement traffic engineering by manipulating interface costs to enforce the required traffic path.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 03 |
|--------|------|----------|-----------|---------------|
| R1 | Hub / ABR | c7200 | 10.1.1.1/32 | No |
| R2 | Backbone Router | c3725 | 10.2.2.2/32 | No |
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

> **This lab builds on Lab 02.** Ensure that all OSPF adjacencies are stable, network types have been optimized (Point-to-Point on R1-R2 and R1-R3, Broadcast with DR/BDR priorities on R2-R3), and full reachability exists before proceeding.

---

## 5. Lab Challenge: Path Selection & Metrics

### Objective 1: Analyze Default OSPF Cost Calculation
Before making any changes, examine how OSPF calculates interface costs.
- Use `show ip ospf interface` on each router to identify the current **Cost** value for every OSPF-enabled interface.
- Recall the formula: **Cost = Reference Bandwidth / Interface Bandwidth**.
- Determine the default reference bandwidth and calculate why all FastEthernet interfaces share the same cost.
- Identify the current shortest path from R1 to R3's Loopback (10.3.3.3/32) and its total cost.

### Objective 2: Standardize Reference Bandwidth
Skynet Global is planning a phased upgrade to GigabitEthernet links. To ensure OSPF can differentiate between 100 Mbps and 1 Gbps links in the future, you must update the reference bandwidth.
- Configure `auto-cost reference-bandwidth 1000` under the OSPF process on **all three routers**.
- Verify that FastEthernet interface costs have changed from **1** to **10**.
- Confirm that path preferences remain unchanged (all links are still equal speed).

> **Critical:** The reference bandwidth **must** be identical on all OSPF routers in the domain. A mismatch will cause inconsistent cost calculations and potential routing loops.

### Objective 3: Traffic Engineering with Manual Cost
The security team requires that R1-to-R3 traffic flows through R2 for inline inspection.
- Apply a manual cost of **50** to R1's FastEthernet1/1 interface (direct link to R3).
- Verify that R1's routing table now reaches 10.3.3.3/32 via R2 (through Fa1/0) instead of the direct link.
- Confirm the total path cost through R2 versus the direct link cost.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip ospf interface <id>` | Verify the "Cost" field matches the expected value (auto-calculated or manual). |
| `show ip route ospf` | Confirm path selection reflects cost changes. |
| `show ip ospf` | Verify the configured reference bandwidth under the OSPF process. |
| `show ip ospf database router` | Examine link costs advertised in Router LSAs. |

---

## 7. Verification Cheatsheet

### 7.1 Verify Default Interface Cost (Before Changes)
Confirm that all FastEthernet interfaces have the default cost of 1.
```bash
R1# show ip ospf interface FastEthernet 1/0
FastEthernet1/0 is up, line protocol is up
  Internet Address 10.12.0.1/30, Area 0
  Process ID 1, Router ID 10.1.1.1, Network Type POINT_TO_POINT, Cost: 1
  Transmit Delay is 1 sec, State POINT_TO_POINT
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```
*Verify: Cost is 1. With the default reference bandwidth of 100 Mbps, FastEthernet (100 Mbps) = 100/100 = 1.*

### 7.2 Verify Reference Bandwidth Change
After configuring `auto-cost reference-bandwidth 1000`, confirm the new cost.
```bash
R1# show ip ospf interface FastEthernet 1/0
FastEthernet1/0 is up, line protocol is up
  Internet Address 10.12.0.1/30, Area 0
  Process ID 1, Router ID 10.1.1.1, Network Type POINT_TO_POINT, Cost: 10
  Transmit Delay is 1 sec, State POINT_TO_POINT
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```
*Verify: Cost is now 10. With reference bandwidth 1000 Mbps, FastEthernet = 1000/100 = 10.*

### 7.3 Verify OSPF Process Reference Bandwidth
```bash
R1# show ip ospf
 Routing Process "ospf 1" with ID 10.1.1.1
 ...
 Reference bandwidth unit is 1000 mbps
```
*Verify: The reference bandwidth unit confirms the configured value.*

### 7.4 Verify Manual Cost Override
After applying `ip ospf cost 50` on R1's Fa1/1, confirm the override.
```bash
R1# show ip ospf interface FastEthernet 1/1
FastEthernet1/1 is up, line protocol is up
  Internet Address 10.13.0.1/30, Area 0
  Process ID 1, Router ID 10.1.1.1, Network Type POINT_TO_POINT, Cost: 50
  Transmit Delay is 1 sec, State POINT_TO_POINT
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```
*Verify: Cost is 50 (manual override), not 10 (auto-calculated). Manual cost always takes precedence over auto-cost.*

### 7.5 Verify Path Selection After Cost Change
Confirm that R1 now reaches R3's loopback via R2.
```bash
R1# show ip route ospf
      10.0.0.0/8 is variably subnetted, 7 subnets, 2 masks
O        10.2.2.2/32 [110/11] via 10.12.0.1, FastEthernet1/0
O        10.3.3.3/32 [110/21] via 10.12.0.1, FastEthernet1/0
O        10.23.0.0/30 [110/20] via 10.12.0.1, FastEthernet1/0
```
*Verify: 10.3.3.3/32 is reached via Fa1/0 (R2) with cost 21 (R1 Fa1/0=10 + R2 Fa0/1=10 + R3 Lo0=1). The direct path via Fa1/1 would cost 51 (50+1), so R2 is preferred.*

---

## 8. Troubleshooting Scenario

### The Fault
After configuring `auto-cost reference-bandwidth 1000` on R1 and R3, you forgot to apply it to R2. R1 is now reporting an OSPF cost of **21** to reach R3's loopback via R2, but R2 is advertising its links with a cost of **1** instead of **10**.

### The Mission
1. Explain the impact of a reference bandwidth mismatch between OSPF neighbors.
2. Use `show ip ospf interface` on R2 to identify the inconsistency.
3. Correct the configuration and verify that all routers share the same reference bandwidth.

---

## 9. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Objective 2: Reference Bandwidth
```bash
! R1, R2, R3 (must be applied on ALL routers)
router ospf 1
 auto-cost reference-bandwidth 1000
```

### Objective 3: Manual Cost Override
```bash
! R1
interface FastEthernet1/1
 ip ospf cost 50
```

---

## 10. Lab Completion Checklist

- [ ] Default OSPF costs analyzed and understood (Cost = Ref BW / Interface BW).
- [ ] Reference bandwidth set to 1000 Mbps on all three routers.
- [ ] FastEthernet costs verified as 10 after reference bandwidth change.
- [ ] Manual cost of 50 applied to R1's Fa1/1.
- [ ] R1 routes to 10.3.3.3/32 via R2 (cost 21) instead of the direct link (cost 51).
- [ ] Troubleshooting challenge resolved (reference bandwidth mismatch).
