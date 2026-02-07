# CCNP ENCOR EIGRP Lab 01: Basic EIGRP Adjacency
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure EIGRP Autonomous System and Router-ID
- Understand the EIGRP neighbor discovery process (Hello packets, multicast 224.0.0.10)
- Verify neighbor relationships using `show ip eigrp neighbors`
- Implement passive interfaces to prevent unnecessary Hello traffic
- Troubleshoot common adjacency failures (AS mismatch, K-value mismatch)
- Interpret EIGRP topology and routing tables

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───────┬─────────┘
                            │ Fa1/0
                            │ 10.0.12.1/30
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
                    └─────────────────┘
```

### Scenario Narrative
As the Lead Network Architect for **Skynet Global**, you have been tasked with establishing a new routing domain between the Headquarters (R1), the regional Branch Office (R2), and a newly acquired Remote Site (R3). 

The company has standardized on **EIGRP Autonomous System 100**. Your mission is to ensure stable neighbor adjacencies across the point-to-point FastEthernet links while adhering to security best practices by suppressing routing updates on non-essential interfaces. The business depends on full reachability between all Loopback interfaces for management and monitoring.

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

### Interface Slot Configuration
| Device | Slot 0 | Slot 1 | Slot 3 |
|--------|--------|--------|--------|
| R1 (c7200) | Fa0/0 | Fa1/0, Fa1/1 | Gi3/0 |
| R2 (c3725) | Fa0/0, Fa0/1 | - | - |
| R3 (c3725) | Fa0/0, Fa0/1 | - | - |

---

## 4. Base Configuration

> ⚠️ **Apply these configurations BEFORE starting the EIGRP challenge.**

### R1 (Hub Router)
```bash
enable
configure terminal
!
hostname R1
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
 no shutdown
!
interface FastEthernet1/0
 description Link to R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R2 (Branch Router)
```bash
enable
configure terminal
!
hostname R2
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
 no shutdown
!
interface FastEthernet0/0
 description Link to R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface FastEthernet0/1
 description Link to R3
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R3 (Remote Branch)
```bash
enable
configure terminal
!
hostname R3
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
 no shutdown
!
interface FastEthernet0/0
 description Link to R2
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

---

## 5. Lab Challenge: Core Implementation

### Objective 1: Establish EIGRP Adjacencies
Configure EIGRP on all three routers using **Autonomous System 100**. 
- Ensure the **Router-ID** on each device matches its respective Loopback0 address.
- Advertise all connected networks (including Loopbacks) into the EIGRP process.
- Use the most specific wildcard masks possible for network advertisements.
- Disable automatic route summarization.

### Objective 2: Traffic Optimization & Security
Security policy dictates that EIGRP control plane traffic (Hellos) should not be leaked onto non-transit networks.
- Configure all **Loopback** interfaces as **Passive Interfaces**.

---

## 6. Verification & Analysis

Use the following commands to verify your implementation. Successful completion of the challenge should result in the outcomes listed below.

### Verification Checklist
- [ ] **Neighbor Adjacency:** Run `show ip eigrp neighbors`. Does R2 see both R1 and R3?
- [ ] **Passive Interfaces:** Run `show ip eigrp interfaces`. Are the Loopback interfaces suppressed while physical links remain active?
- [ ] **Routing Table:** Run `show ip route eigrp`. Does R1 have routes to R2 and R3's loopbacks?
- [ ] **End-to-End Connectivity:** Ping from R1's Loopback0 to R3's Loopback0 (`ping 3.3.3.3 source 1.1.1.1`).

### Verification Table
| Command | Expected Outcome |
|---------|------------------|
| `show ip eigrp neighbors` | Adjacencies established on all transit links. |
| `show ip protocols` | Confirming AS 100 and correct Passive Interfaces. |
| `show ip route eigrp` | Full reachability to all remote prefixes. |

---

## 7. Troubleshooting Scenario

### The Fault
After a recent "optimization" by a junior admin, R2 is no longer forming an adjacency with R1. You notice that R2's configuration now shows `router eigrp 200`.

### The Mission
1. Identify why the adjacency failed using `debug eigrp packets hello`.
2. Restore the configuration to meet the original design requirements (AS 100).
3. Verify that the routing table has repopulated.

---

## 8. Solutions (Spoiler Alert!)

> 💡 **Try to complete the lab without looking at these steps first!**

### Objective 1 & 2: Full Configuration

**R1 (Hub):**
```bash
configure terminal
router eigrp 100
 eigrp router-id 1.1.1.1
 network 1.1.1.1 0.0.0.0
 network 10.0.12.0 0.0.0.3
 passive-interface Loopback0
 no auto-summary
end
```

**R2 (Branch):**
```bash
configure terminal
router eigrp 100
 eigrp router-id 2.2.2.2
 network 2.2.2.2 0.0.0.0
 network 10.0.12.0 0.0.0.3
 network 10.0.23.0 0.0.0.3
 passive-interface Loopback0
 no auto-summary
end
```

**R3 (Remote):**
```bash
configure terminal
router eigrp 100
 eigrp router-id 3.3.3.3
 network 3.3.3.3 0.0.0.0
 network 10.0.23.0 0.0.0.3
 passive-interface Loopback0
 no auto-summary
end
```

---

## 9. Lab Completion Checklist

- [ ] All three routers have EIGRP Autonomous System 100 configured.
- [ ] Router-IDs are set to Loopback0 addresses.
- [ ] All physical and loopback networks are advertised with specific wildcard masks.
- [ ] Loopback0 is configured as a Passive Interface on all routers.
- [ ] `show ip eigrp neighbors` shows the expected neighbors.
- [ ] End-to-end ping from R1 to R3's loopback succeeds.
- [ ] Troubleshooting challenge resolved and verified.