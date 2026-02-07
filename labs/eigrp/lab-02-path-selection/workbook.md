# CCNP ENCOR EIGRP Lab 02: Path Selection & Metrics
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Understand EIGRP composite metric calculation (Bandwidth + Delay)
- Analyze the DUAL algorithm and Feasibility Condition
- Identify Successor and Feasible Successor routes
- Manipulate path selection using interface delay
- Configure variance for unequal-cost load balancing
- Interpret EIGRP topology table entries

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1 (NEW)
                        │         │
          10.0.12.1/30  │         │ 10.0.13.1/30
                        │         │
                        │         │ 10.0.13.2/30
                ┌───────┴─────┐   │ Fa0/1
                │      R2     │   │
                │   Branch    │   │
                │  2.2.2.2    │   │
                └───────┬─────┴───┘
                        │ Fa0/1
                        │ 10.0.23.1/30
                        │
                        │ 10.0.23.2/30
                        │ Fa0/0
                ┌───────┴─────────┐
                │       R3        │
                │ (Remote Branch) │
                │  Lo0: 3.3.3.3   │
                └─────────────────┘
```

### Scenario Narrative
As the Lead Network Architect for **Skynet Global**, you have implemented redundancy between the Headquarters (R1) and the Remote Branch (R3). A new direct point-to-point link has been established, supplementing the existing path through the regional Branch Office (R2).

Management has noticed that all traffic is currently favoring the direct link. Your objective is to validate the current EIGRP path selection, manipulate the metrics to prefer the indirect path for specific traffic engineering requirements, and finally enable unequal-cost load balancing to utilize all available bandwidth effectively.

### Device Role Table
| Device | Role | Platform | Loopback0 | EIGRP AS |
|--------|------|----------|-----------|----------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | 100 |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | 100 |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | 100 |

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

> ⚠️ **This lab builds on Lab 01.** Apply these updates to establish the redundant link before starting the challenge.

### R1 (New Link Configuration)
```bash
enable
configure terminal
!
interface FastEthernet1/1
 description Redundant Link to R3
 ip address 10.0.13.1 255.255.255.252
 no shutdown
!
router eigrp 100
 network 10.0.13.0 0.0.0.3
!
end
```

### R3 (New Link Configuration)
```bash
enable
configure terminal
!
interface FastEthernet0/1
 description Redundant Link to R1
 ip address 10.0.13.2 255.255.255.252
 no shutdown
!
router eigrp 100
 network 10.0.13.0 0.0.0.3
!
end
```

---

## 5. Lab Challenge: Path Selection & Optimization

### Objective 1: Analyze Default Metric Calculation
Validate that EIGRP correctly identifies the direct link (Fa1/1) as the Successor for the 3.3.3.3/32 prefix. 
- Examine the EIGRP topology table to identify the **Feasible Distance (FD)** and **Reported Distance (RD)** for both paths.
- Confirm which path is currently installed in the routing table.

### Objective 2: Metric Manipulation
Skynet Global requirements specify that the link through R2 should be the primary path for data traffic to R3.
- Modify the **Delay** on R1's Fa1/1 interface to ensure the path through R2 becomes the **Successor**.
- Verify the routing table update.

### Objective 3: Unequal-Cost Load Balancing
To maximize resource utilization, you must enable load balancing across both the primary and backup paths.
- Configure EIGRP **Variance** on R1 to allow both paths to be installed in the routing table simultaneously.
- Verify that both next-hops are visible in the routing table for 3.3.3.3/32.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip eigrp topology 3.3.3.3/32` | View FD, RD, and Successor/Feasible Successor status. |
| `show ip route 3.3.3.3` | Confirm the active path(s) in the RIB. |
| `show ip protocols` | Verify the configured Variance multiplier. |

---

## 7. Verification Cheatsheet

### 7.1 Topology Table Analysis (R1)
Verify the Successor, Feasible Successor, and distance metrics.
```bash
R1# show ip eigrp topology 3.3.3.3/32
EIGRP-IPv4 Topology Entry for AS 100 for 3.3.3.3/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 156160
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (156160/128256), Route is Internal
      Vector metric:
        Minimum bandwidth is 100000 Kbit
        Total delay is 5100 microseconds
        Reliability is 255/255
        Load is 1/255
        Minimum MTU is 1500
        Hop count is 2
        Originating router is 3.3.3.3
  10.0.13.2 (FastEthernet1/1), from 10.0.13.2, Send flag is 0x0
      Composite metric is (258560/2560), Route is Internal
      Vector metric:
        Minimum bandwidth is 100000 Kbit
        Total delay is 9100 microseconds
        Reliability is 255/255
        Load is 1/255
        Minimum MTU is 1500
        Hop count is 1
        Originating router is 3.3.3.3
```
*Note: The first entry is the Successor (lowest metric). The second entry is the Feasible Successor (RD 2560 < FD 156160).*

### 7.2 Routing Table with Variance (R1)
Confirm that both paths are installed in the RIB.
```bash
R1# show ip route 3.3.3.3
Routing entry for 3.3.3.3/32
  Known via "eigrp 100", distance 90, metric 156160, type internal
  Redistributing via eigrp 100
  Last update from 10.0.12.2 on FastEthernet1/0, 00:04:12 ago
  Routing Descriptor Blocks:
  * 10.0.12.2, from 10.0.12.2, 00:04:12 ago, via FastEthernet1/0
      Route metric is 156160, traffic share count is 120
      Total delay is 5100 microseconds, minimum bandwidth is 100000 Kbit
      Reliability 255/255, minimum MTU 1500 bytes
      Loading 1/255, Hops 2
    10.0.13.2, from 10.0.13.2, 00:04:12 ago, via FastEthernet1/1
      Route metric is 258560, traffic share count is 72
      Total delay is 9100 microseconds, minimum bandwidth is 100000 Kbit
      Reliability 255/255, minimum MTU 1500 bytes
      Loading 1/255, Hops 1
```
*Note: Two descriptor blocks exist with different traffic share counts.*

---

## 8. Troubleshooting Scenario

### The Fault
After configuring a Variance of 10, R1 still only uses a single path to reach R3's Loopback, even though the secondary path is visible in the topology table.

### The Mission
1. Analyze the topology table to determine if the secondary path meets the **Feasibility Condition**.
2. Identify the relationship between the Successor's FD and the neighbor's RD.
3. Propose and implement a change to allow unequal-cost load balancing to function correctly.

---

## 9. Solutions (Spoiler Alert!)

> 💡 **Try to complete the lab challenge without looking at these steps first!**

### Objective 2: Metric Manipulation
**R1:**
```bash
configure terminal
interface FastEthernet1/1
 delay 5000
end
```

### Objective 3: Unequal-Cost Load Balancing
**R1:**
```bash
configure terminal
router eigrp 100
 variance 2
end
```

---

## 10. Lab Completion Checklist

- [ ] Redundant link between R1 and R3 is active and EIGRP adjacent.
- [ ] Successor and Feasible Successor identified in the topology table.
- [ ] Primary path successfully shifted to R2 via delay manipulation.
- [ ] Variance configured and verified in the routing table (two next-hops).
- [ ] Troubleshooting challenge resolved (Feasibility Condition understood).