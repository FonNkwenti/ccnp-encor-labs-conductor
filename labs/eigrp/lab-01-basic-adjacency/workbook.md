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

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

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

## 7. Verification Cheatsheet

### Neighbor Adjacency (R2 Example)
Confirm that neighbors are discovered on both physical interfaces.
```bash
R2# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
1   10.0.23.2               Fa0/1                    12 00:04:15   40   240  0  5
0   10.0.12.1               Fa0/0                    13 00:05:22   25   200  0  3
```
*Verify: 'Address' corresponds to neighbors, 'Interface' is correct, and 'Hold' time is counting down from 15.*

### Passive Interface Verification (All Routers)
Ensure Loopback0 is listed as passive and not sending Hellos.
```bash
R1# show ip eigrp interfaces detail Loopback0
EIGRP-IPv4 Interfaces for AS 100
                              Xmit Queue   PeerQ        Mean   Pacing   Multicast    Pending
Interface        Peers        Un/Reliable  Un/Reliable  SRTT   Time     Flow Timer   Routes
Lo0                0             0/0          0/0          0      0/1            0           0
  Hello-interval is 5, Hold-time is 15
  Split-horizon is enabled
  Next xmit serial <none>
  Packetized sent/expedited: 0/0
  Hello's sent/expedited: 0/0
  Un/reliable mcasts: 0/0  Un/reliable ucasts: 0/0
  Mcast exceptions: 0  CR packets: 0  ACKs suppressed: 0
  Retransmissions sent: 0  Out-of-sequence rcvd: 0
  Topology items sent: 0  advertisable: 0
  Passive interface
```
*Verify: The last line confirms 'Passive interface'.*

### Routing Table Reachability (R1 Example)
Verify that all remote Loopbacks and transit subnets are learned.
```bash
R1# show ip route eigrp
      10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks
D        10.0.23.0/30 [90/30720] via 10.0.12.2, 00:06:12, FastEthernet1/0
      2.0.0.0/32 is subnetted, 1 subnets
D        2.2.2.2 [90/130560] via 10.0.12.2, 00:06:12, FastEthernet1/0
      3.0.0.0/32 is subnetted, 1 subnets
D        3.3.3.3 [90/158720] via 10.0.12.2, 00:05:45, FastEthernet1/0
```
*Verify: Routes are marked with 'D' (EIGRP) and next-hops are correct.*

---

## 8. Troubleshooting Scenario

### The Fault
After a recent "optimization" by a junior admin, R2 is no longer forming an adjacency with R1. You notice that R2's configuration now shows `router eigrp 200`.

### The Mission
1. Identify why the adjacency failed using `debug eigrp packets hello`.
2. Restore the configuration to meet the original design requirements (AS 100).
3. Verify that the routing table has repopulated.

---

## 9. Solutions (Spoiler Alert!)

> 💡 **Try to complete the lab without looking at these steps first!**

### Objective 1 & 2: Full Configuration

<details>
<summary>Click to view R1 Configuration</summary>

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
</details>

<details>
<summary>Click to view R2 Configuration</summary>

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
</details>

<details>
<summary>Click to view R3 Configuration</summary>

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
</details>

---

## 10. Lab Completion Checklist

- [ ] All three routers have EIGRP Autonomous System 100 configured.
- [ ] Router-IDs are set to Loopback0 addresses.
- [ ] All physical and loopback networks are advertised with specific wildcard masks.
- [ ] Loopback0 is configured as a Passive Interface on all routers.
- [ ] `show ip eigrp neighbors` shows the expected neighbors.
- [ ] End-to-end ping from R1 to R3's loopback succeeds.
- [ ] Troubleshooting challenge resolved and verified.

---

## 11. Troubleshooting Solutions Appendix

### Challenge 1: The "Ghost" Neighbor — Solution

**Symptom:** R1 and R2 are connected, but `show ip eigrp neighbors` on R1 shows no neighbors. Pings between the physical interfaces are successful.

**Root Cause:** EIGRP is not configured on one of the routers, or the network statement does not include the interconnecting link subnet.

**Solution:**

Verify EIGRP is running and the network statement includes the link:

```bash
R1# show ip protocols
Routing Protocol is "eigrp 100"
Outgoing update filter list for all interfaces is not set
Incoming update filter list for all interfaces is not set
Default networks flagged in outgoing updates
Default networks accepted from incoming updates
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0
EIGRP maximum hopcount 100
EIGRP maximum metric variance 1
Redistributing: eigrp 100

R1# show running-config | include network
 network 1.1.1.1 0.0.0.0
 network 10.0.12.0 0.0.0.3
```

If the network statement is missing on either R1 or R2, add it:

```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# network 10.0.12.0 0.0.0.3
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
```

---

### Challenge 2: The Weight of the World (K-Values) — Solution

**Symptom:** Console messages indicate "K-value mismatch". The adjacency with R3 flaps continuously or never establishes.

**Root Cause:** The K-values (metric weights) are configured differently on R2 than on R3. Default K-values are K1=1, K2=0, K3=1, K4=0, K5=0.

**Solution:**

Verify K-values on both routers:

```bash
R2# show ip eigrp protocols
Routing Protocol is "eigrp 100"
...
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0

R3# show ip eigrp protocols
Routing Protocol is "eigrp 100"
...
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0
```

If K-values differ, correct them on R3 (or the router with incorrect values):

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# metric weights 0 1 0 1 0 0
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

After correcting K-values, the adjacency should stabilize:

```bash
R2# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.23.2               Fa0/0                    14 00:05:30   20   200  0  18
```

---

### Challenge 3: Silent Treatment — Solution

**Symptom:** R2 shows an adjacency with R3, but R3 shows no neighbors on the link to R2. No EIGRP routes from R2 are appearing in R3's routing table.

**Root Cause:** The EIGRP process is not configured on R3, or passive-interface is incorrectly set on the interconnecting interface.

**Solution:**

Verify R3 has EIGRP configured and the interface is not passive:

```bash
R3# show ip eigrp interfaces
EIGRP-IPv4 Interfaces for AS 100
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa0/0              1       0/0       0/0           20       0/0           50           0
Lo0                0       0/0       0/0            -         -             -           0
```

If Fa0/0 shows 0 peers, check if it's passive:

```bash
R3# show ip eigrp interfaces Fa0/0 detail
EIGRP-IPv4 Interfaces for AS 100
Fa0/0              0       0/0       0/0           -         -             -           0
  Passive Interface (configured)
```

If passive, remove it:

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# no passive-interface FastEthernet0/0
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

```bash
R3# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.23.1               Fa0/0                    11 00:01:45   20   200  0  32

R3# show ip route eigrp
D    1.1.1.1 [90/2816000] via 10.0.23.1, 00:01:40, FastEthernet0/0
D    2.2.2.2 [90/2688000] via 10.0.23.1, 00:01:40, FastEthernet0/0
D    10.0.12.0/30 [90/2816000] via 10.0.23.1, 00:01:40, FastEthernet0/0
```

Routes from R2 should now appear in R3's routing table.