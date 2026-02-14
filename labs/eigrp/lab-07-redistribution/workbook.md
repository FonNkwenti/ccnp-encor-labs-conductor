# CCNP ENCOR EIGRP Lab 07: Redistribution
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure mutual redistribution between EIGRP and OSPF
- Understand seed metrics for different routing protocols
- Prevent routing loops using route tags and filtering
- Manipulate metrics for redistributed routes to influence path selection
- Verify redistribution using routing tables and topology databases
- Troubleshoot common redistribution issues (metric mismatch, reachability)

---

## 2. Topology & Scenario

### ASCII Diagram
```
                                  ┌─────────────────┐
                                  │       R4        │
                                  │  OSPF Domain    │
                                  │  4.4.4.4/32     │
                                  └────────┬────────┘
                                           │ Fa0/0
                                           │ 10.0.14.2/30
                                           │
                    ┌─────────────────┐    │ Fa1/1
                    │       R1        ├────┘
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
**Skynet Global** has recently acquired a smaller tech firm, **CyberDyne Systems**, which utilizes **OSPF** as its primary internal gateway protocol. As the Lead Network Architect, you must integrate CyberDyne's infrastructure into the Skynet EIGRP domain.

The CyberDyne router (**R4**) is connected to the Skynet Hub (**R1**). Your objective is to perform **mutual redistribution** between the two protocols to ensure full reachability across the merged enterprise. You must be cautious to prevent routing loops and ensure that metrics are correctly translated so that traffic flows through the most efficient paths.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 07 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router / ASBR | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R4 | CyberDyne OSPF Router | c3725 | 4.4.4.4/32 | **Yes** |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R4 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R5 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.0.12.0/30 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.0.23.0/30 |
| R3           | Fa0/1           | R5            | Fa0/0            | 10.0.35.0/30 |
| R1           | Fa1/1           | R4            | Fa0/0            | 10.0.14.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 06.** Ensure that all previous security and filtering configurations are verified before proceeding with redistribution.

### R4 (CyberDyne - Integration)
```bash
enable
configure terminal
hostname R4
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
interface FastEthernet0/0
 ip address 10.0.14.2 255.255.255.252
 no shutdown
router ospf 1
 network 4.4.4.4 0.0.0.0 area 0
 network 10.0.14.0 0.0.0.3 area 0
end
```

### R1 (Link to CyberDyne)
```bash
interface FastEthernet1/1
 description Link to CyberDyne (OSPF Domain)
 ip address 10.0.14.1 255.255.255.252
 no shutdown
router ospf 1
 network 10.0.14.0 0.0.0.3 area 0
end
```

---

## 5. Lab Challenge: Protocol Redistribution & Loop Prevention

### Objective 1: Implement Mutual Redistribution (R1)
Perform mutual redistribution between EIGRP AS 100 and OSPF process 1 on the Hub router.
- Redistribute **EIGRP** into **OSPF**. Use a metric of `100` and ensure the metric-type is **E1**.
- Redistribute **OSPF** into **EIGRP**. Use the standard EIGRP K-values: Bandwidth `10000`, Delay `100`, Reliability `255`, Load `1`, MTU `1500`.

### Objective 2: Loop Prevention using Route Tagging
To prevent potential routing loops during future expansions:
- When redistributing routes into EIGRP on **R1**, tag them with tag `111`.
- When redistributing routes into OSPF on **R1**, tag them with tag `222`.
- Configure a route-map to deny the re-importation of routes already tagged with `111` or `222`.

### Objective 3: Verify Reachability
- Verify that **R4** (CyberDyne) can ping the Skynet Branch loopbacks (**2.2.2.2**, **3.3.3.3**).
- Verify that **R5** (Stub) can reach the CyberDyne loopback (**4.4.4.4**) (assuming previous filters allow it).

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip route ospf` | On R4, confirm Skynet EIGRP routes are present as OSPF E1 routes. |
| `show ip route eigrp` | On R2/R3, confirm CyberDyne OSPF routes are present as EIGRP External routes (EX). |
| `show ip eigrp topology <network>` | Verify that external routes have the correct tag `111`. |
| `show ip ospf database external` | Verify that external LSAs have the correct tag `222`. |

---

## 7. Verification Cheatsheet

### 7.1 Verify OSPF External Routes (R4)
```bash
R4# show ip route ospf
...
O E1  2.2.2.2 [110/120] via 10.0.14.1, 00:05:12, FastEthernet0/0
O E1  3.3.3.3 [110/120] via 10.0.14.1, 00:05:12, FastEthernet0/0
```
*Verify: Routes appear as 'O E1' indicating Type 1 external routes.*

### 7.2 Verify EIGRP External Routes (R2)
```bash
R2# show ip route eigrp
...
D EX  4.4.4.4 [170/2560512] via 10.0.12.1, 00:04:45, FastEthernet0/0
```
*Verify: Routes appear as 'D EX' with an Administrative Distance of 170.*

### 7.3 Verify Tagging (R1)
```bash
R1# show ip eigrp topology 4.4.4.4/32
...
      Originating router is 10.0.14.2
      Route tag is 111
```
*Verify: Tag 111 is present on OSPF-to-EIGRP redistributed routes.*

```bash
R1# show ip ospf database external 2.2.2.2
...
  Routing Bit Set on this LSA
  LS age: 154
  Options: (No TOS-capability, DC)
  LS Type: AS External Link
  Link State ID: 2.2.2.2 (AS Boundary Router address)
  Advertising Router: 1.1.1.1
  LS Seq Number: 80000001
  Checksum: 0x3456
  Length: 36
  Network Mask: /32
	Metric Type: 1 (Comparable directly to link state cost)
	TOS: 0 
	Metric: 100 
	Forward Address: 0.0.0.0
	External Route Tag: 222
```
*Verify: Tag 222 is present on EIGRP-to-OSPF redistributed routes.*

---

## 8. Troubleshooting Scenario

### The Fault
After configuring redistribution, R4 can see Skynet routes, but R2 cannot see the 4.4.4.4 loopback from CyberDyne.

### The Mission
1. Check if redistribution is active on R1 under the `router eigrp 100` process.
2. Verify if a seed metric was provided for OSPF-to-EIGRP redistribution. (Remember: EIGRP has an infinite default metric for external routes!)
3. Restore reachability and confirm the routes appear as `D EX` on R2.

---

## 9. Solutions (Spoiler Alert!)

### Objectives 1 & 2: Mutual Redistribution & Tagging

<details>
<summary>Click to view R1 Configuration</summary>

```bash
route-map EIGRP_TO_OSPF permit 10
 set tag 222
 set metric 100
 set metric-type type-1
!
route-map OSPF_TO_EIGRP permit 10
 set tag 111
!
router eigrp 100
 redistribute ospf 1 metric 10000 100 255 1 1500 route-map OSPF_TO_EIGRP
!
router ospf 1
 redistribute eigrp 100 route-map EIGRP_TO_OSPF subnets
```
</details>

---

## 10. Lab Completion Checklist

- [ ] Mutual redistribution functional on R1.
- [ ] OSPF routes visible as `D EX` in Skynet domain.
- [ ] EIGRP routes visible as `O E1` in CyberDyne domain.
- [ ] Route tags applied and verified for both protocols.
- [ ] Full reachability between R4 and R5.

---

## 11. Troubleshooting Solutions Appendix

### Challenge 1: The Infinite Distance (Seed Metrics) — Solution

**Symptom:** R1 is successfully learning CyberDyne (OSPF) routes, but R2 and R3 have no external (D EX) routes in their routing tables. R1's `router eigrp 100` configuration shows redistribution is active.

**Root Cause:** The redistribute command on R1 is missing the `metric` parameter, so OSPF routes are being redistributed with an infinite metric (unreachable) and are not propagated to other EIGRP routers.

**Solution:**

Check the redistribute configuration on R1:

```bash
R1# show running-config | section "router eigrp"
router eigrp 100
 redistribute ospf 1
```

Add the metric parameters (K-values: bandwidth, delay, reliability, load, MTU):

```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# redistribute ospf 1 metric 10000 100 255 1 1500
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R2# show ip route eigrp | include EX
D EX 4.4.4.4/32 [170/2956800] via 10.0.12.1, 00:01:15, FastEthernet0/0

R3# show ip route eigrp | include EX
D EX 4.4.4.4/32 [170/2834800] via 10.0.23.1, 00:01:30, FastEthernet0/0
```

OSPF routes should now appear as external EIGRP routes (D EX) in R2 and R3.

---

### Challenge 2: Tagged Out (Redistribution Loop Prevention) — Solution

**Symptom:** A complex route-map is implemented to prevent loops, but R4 (OSPF) is not receiving any Skynet routes. Tag `222` is in the configuration, but no external LSAs on R4.

**Root Cause:** The route-map used in the `redistribute eigrp` statement on R1 is incorrectly filtering all EIGRP routes, or the route-map match condition is too restrictive.

**Solution:**

Check the route-map on R1:

```bash
R1# show route-map EIGRP_TO_OSPF
route-map EIGRP_TO_OSPF, permit, sequence 10
  Match clauses:
    tag 222
  Set clauses:
    tag 333
  Policy routing matches: 0 packets, 0 bytes
route-map EIGRP_TO_OSPF, deny, sequence 20
  Match clauses:
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```

The route-map is matching only routes with tag 222 (which don't exist yet because they haven't been created). Change the match condition to permit all EIGRP routes:

```bash
R1# configure terminal
R1(config)# route-map EIGRP_TO_OSPF permit 10
R1(config-route-map)# no match tag 222
R1(config-route-map)# exit
R1(config)# route-map EIGRP_TO_OSPF permit 20
R1(config-route-map)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R4# show ip route ospf | include E1
O E1 1.1.1.1/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 2.2.2.2/32 [110/2728] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 3.3.3.3/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
```

EIGRP routes should now appear as external OSPF routes (O E1) on R4.

---

### Challenge 3: Subnet Scarcity — Solution

**Symptom:** R4 can reach R1's directly connected interfaces, but it cannot see the EIGRP loopbacks (2.2.2.2, 3.3.3.3) or the stub networks.

**Root Cause:** The redistribute command is missing the `subnets` keyword in the OSPF redistribution, so only summarized routes (not individual subnets) are being advertised.

**Solution:**

Check the OSPF configuration on R1:

```bash
R1# show running-config | section "router ospf"
router ospf 1
 redistribute eigrp 100 route-map EIGRP_TO_OSPF
```

Add the `subnets` keyword to permit redistribution of host routes and subnets:

```bash
R1# configure terminal
R1(config)# router ospf 1
R1(config-router)# redistribute eigrp 100 route-map EIGRP_TO_OSPF subnets
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R4# show ip route ospf
O E1 1.1.1.1/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 2.2.2.2/32 [110/2728] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 3.3.3.3/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 5.5.5.5/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 10.0.23.0/30 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 10.0.35.0/30 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
```

All EIGRP routes including loopbacks and subnets should now be visible on R4.
