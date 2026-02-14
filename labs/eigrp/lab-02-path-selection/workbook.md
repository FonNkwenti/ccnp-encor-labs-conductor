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

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.0.12.0/30 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.0.23.0/30 |
| R1           | Fa1/1           | R3            | Fa0/1            | 10.0.13.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

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

<details>
<summary>Click to view R1 Configuration</summary>

```bash
configure terminal
interface FastEthernet1/1
 delay 5000
end
```
</details>

### Objective 3: Unequal-Cost Load Balancing

<details>
<summary>Click to view R1 Configuration</summary>

```bash
configure terminal
router eigrp 100
 variance 2
end
```
</details>

---

## 10. Lab Completion Checklist

- [ ] Redundant link between R1 and R3 is active and EIGRP adjacent.
- [ ] Successor and Feasible Successor identified in the topology table.
- [ ] Primary path successfully shifted to R2 via delay manipulation.
- [ ] Variance configured and verified in the routing table (two next-hops).
- [ ] Troubleshooting challenge resolved (Feasibility Condition understood).

---

## 11. Troubleshooting Solutions Appendix

### Challenge 1: The Invisible Backup — Solution

**Symptom:** `variance 10` is configured on R1 to enable load balancing to R3 (3.3.3.3/32), but the routing table still shows only one path via R2. The redundant link (Fa1/1) is up and EIGRP adjacent.

**Root Cause:** The Feasibility Condition is not met for the path via R3. The Advertised Distance (AD) from R3 must be less than the Feasible Distance (FD) of the successor route for R3 to be considered a Feasible Successor. Without meeting this condition, variance cannot enable load balancing.

**Solution:**

Check the topology table to understand the metric relationship:

```bash
R1# show ip eigrp topology 3.3.3.3/32
EIGRP-IPv4 Topology Entry for AS 100 for 3.3.3.3/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 2688000
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2688000/2560000), route is Internal
  10.0.13.2 (FastEthernet1/1), from 10.0.13.2, Send flag is 0x0
      Composite metric is (2752000/2560000), route is Internal
```

The path via R3 (2752000) has an AD of 2560000. Compare with the FD via R2 (2688000). Since 2560000 < 2688000, R3 IS a Feasible Successor. Verify variance is set sufficiently high:

```bash
R1# show ip protocols | include variance
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0
EIGRP maximum hopcount 100
EIGRP maximum metric variance 10
```

The variance is 10, so routes with metric ≤ (2688000 × 10) = 26880000 should be included. Since 2752000 is within this range, load balancing should work. If it's not appearing in the routing table, check for an `auto-summary` mismatch or verify both neighbors are reachable:

```bash
R1# show ip route 3.3.3.3
Routing Table: VRF default
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level 1, L2 - IS-IS level 2
       ia - IS-IS inter area, * - candidate default, U - unknown, o - VRF override
       + - replicated route

Routing entry for 3.3.3.3/32
  Known via "eigrp 100", distance 90, metric 2688000, type internal
  Redistributing via eigrp 100
  Last update from 10.0.12.2 on FastEthernet1/0, 00:03:45
  Routing Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, metric 2688000, traffic share count is 1
  10.0.13.2 (FastEthernet1/1), from 10.0.13.2, metric 2752000, traffic share count is 1
```

Both paths should now appear with their respective traffic share counts.

---

### Challenge 2: Accidental Detour — Solution

**Symptom:** Traffic from R1 to R3's loopback (3.3.3.3) is taking a strange path through another remote site with high delay. The primary link is up, but the metric is unexpectedly high.

**Root Cause:** The delay on one of the interfaces has been increased (likely on R1 Fa1/0 or R2), causing EIGRP to prefer a different path even though it should be suboptimal.

**Solution:**

Check the interface delays:

```bash
R1# show interface FastEthernet1/0 | include delay
 Encapsulation ARPA, loopback not set
 Keepalive set (10 sec)
 Half-duplex, 100Mb/s, 100BaseTX/FX
 ARP type: ARPA, ARP Timeout 04:00:00
 Last input never, output 00:00:11, output hang never
 Last clearing of "show interface" counters 00:05:22
 Input queue: 0/75/0/0 (size/max/drops/flips); Total output drops: 0
 Queueing strategy: fifo
 Output queue: 0/40 (size/max)
 5 minute input rate 0 bits/sec, 0 output/sec
 5 minute output rate 0 bits/sec, 0 output/sec
    0 packets input, 0 bytes, 0 no buffer
    0 broadcasts, 0 no buffer drops
    0 runts, 0 bits errors, 0 inserted code errors
    0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 input packet
 100 pps, 100 bits/sec
 Delay: 100 usec
```

The default delay for Fa1/0 is 100 usec. If it's higher, reset it:

```bash
R1# configure terminal
R1(config)# interface FastEthernet1/0
R1(config-if)# no delay
R1(config-if)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show ip eigrp topology 3.3.3.3/32
EIGRP-IPv4 Topology Entry for AS 100 for 3.3.3.3/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 2688000
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2688000/2560000), route is Internal
```

The metric should return to its expected value, and traffic should use the optimal path.

---

### Challenge 3: Metric Madness — Solution

**Symptom:** R1 is no longer learning routes from R3 over the direct link (Fa1/1), although the neighbor relationship is "UP". Pings to R3's interface 10.0.13.2 work, but the 3.3.3.3/32 prefix is only learned via R2.

**Root Cause:** The network statement for the R1-R3 direct link (10.0.13.0/30) is missing or commented out on R3, preventing R3 from advertising the network back to R1.

**Solution:**

Check R3's network statements:

```bash
R3# show running-config | section "router eigrp"
router eigrp 100
 eigrp router-id 3.3.3.3
 network 3.3.3.3 0.0.0.0
 network 10.0.13.0 0.0.0.3
 network 10.0.23.0 0.0.0.3
 passive-interface Loopback0
 no auto-summary
```

If the 10.0.13.0 network statement is missing, add it:

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# network 10.0.13.0 0.0.0.3
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

```bash
R1# show ip eigrp topology 3.3.3.3/32
EIGRP-IPv4 Topology Entry for AS 100 for 3.3.3.3/32
  State is Passive, Query origin flag is 1, 2 Successor(s), FD is 2752000
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2688000/2560000), route is Internal
  10.0.13.2 (FastEthernet1/1), from 10.0.13.2, Send flag is 0x0
      Composite metric is (2752000/2560000), route is Internal
```

Both paths to R3 should now be visible in the topology table.