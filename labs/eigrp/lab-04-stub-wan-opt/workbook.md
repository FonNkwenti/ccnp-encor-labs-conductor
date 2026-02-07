# CCNP ENCOR EIGRP Lab 04: Stub & WAN Optimization
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure EIGRP stub routers to reduce query traffic
- Understand stub router types (connected, static, summary, redistributed, receive-only)
- Adjust interface bandwidth for accurate metric calculation
- Tune EIGRP hello and hold timers for WAN links
- Verify stub configuration and query boundary effects
- Optimize EIGRP for WAN environments

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1 (WAN Link)
                        │         │ 10.0.12.1/30
                        │         │ BW: 1544 Kbps
           10.0.12.1/30 │         │ Hello: 60, Hold: 180
                        │         │
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
As the Lead Network Architect for **Skynet Global**, you are responsible for optimizing the remote site connectivity and ensuring the stability of the regional WAN infrastructure. 

The network now includes a remote stub site (**R5**) which serves as a leaf node in our topology. Additionally, the link between the Headquarters (R1) and the Branch (R2) is a leased line with specific bandwidth and latency characteristics that must be reflected in our EIGRP metrics and neighbor timers.

Your mission is to secure the remote site as a **Stub Router** to prevent unnecessary query propagation and to tune the WAN interface parameters to match the service provider's SLA.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 04 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | **Yes** |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R5 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 03.** Ensure the remote site R5 is integrated into the topology before starting the optimization challenge.

### R5 (Remote Site - Integration)
```bash
enable
configure terminal
hostname R5
interface Loopback0
 ip address 5.5.5.5 255.255.255.255
interface Loopback1
 ip address 10.5.1.1 255.255.255.0
interface Loopback2
 ip address 10.5.2.1 255.255.255.0
interface Loopback3
 ip address 10.5.3.1 255.255.255.0
interface FastEthernet0/0
 description Link to R3
 ip address 10.0.35.2 255.255.255.252
 no shutdown
router eigrp 100
 network 5.5.5.5 0.0.0.0
 network 10.0.35.0 0.0.0.3
 network 10.5.0.0 0.0.255.255
 no auto-summary
 passive-interface default
 no passive-interface FastEthernet0/0
end
```

### R3 (Branch Extension)
```bash
interface FastEthernet0/1
 description Link to R5 (Remote Site)
 ip address 10.0.35.1 255.255.255.252
 no shutdown
router eigrp 100
 network 10.0.35.0 0.0.0.3
end
```

---

## 5. Lab Challenge: Stub & WAN Optimization

### Objective 1: Implement EIGRP Stub Connectivity
To prevent **R5** from being utilized as a transit router and to stop query propagation to this leaf site:
- Configure **R5** as an EIGRP **Stub Router**.
- Ensure only **Connected** and **Summary** routes are advertised by R5.
- Verify that **R3** recognizes R5 as a stub neighbor.

### Objective 2: Tune WAN Link Parameters
The link between **R1** and **R2** must be optimized for its 1.544 Mbps capacity.
- Set the **Bandwidth** on R1's and R2's interconnecting interfaces to **1544**.
- Configure the EIGRP **Hello Interval** to **60 seconds** and the **Hold Time** to **180 seconds** on the WAN link to accommodate potential latency spikes.

### Objective 3: Validate Query Containment
- Simulate a network failure in the Core (e.g., shutdown a Loopback on R1).
- Use debugging on **R3** and **R5** to verify that **R5** is **NOT** queried for the lost prefix.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip protocols | include stub` | Confirm R5 is operating in stub mode. |
| `show ip eigrp neighbors detail` | Confirm R3 sees the "Stub Peer" flag for R5. |
| `show interface <id> | include BW` | Confirm the 1544 Kbit bandwidth setting on R1/R2. |
| `show ip eigrp interfaces detail <id>` | Verify the 60/180 second EIGRP timers on the WAN link. |

---

## 7. Verification Cheatsheet

### 7.1 Verify Stub Status (R3 Perspective)
Confirm that the hub/distribution router recognizes the remote site as a stub.
```bash
R3# show ip eigrp neighbors detail
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.35.2               Fa0/1                    12 00:05:42   22   200  0  14
   Version 15.3/2.0, Retrans: 0, Retries: 0, Prefixes: 4
   Topology-ids from peer - 0 
   Stub Peer Advertising (CONNECTED SUMMARY) Routes
   Suppressing queries
```
*Verify: The 'Stub Peer' line confirms query suppression is active.*

### 7.2 WAN Link Parameter Verification (R1/R2)
Confirm that bandwidth and EIGRP timers match the WAN specification.
```bash
R1# show ip eigrp interfaces detail FastEthernet1/0
EIGRP-IPv4 Interfaces for AS 100
                              Xmit Queue   PeerQ        Mean   Pacing   Multicast    Pending
Interface        Peers        Un/Reliable  Un/Reliable  SRTT   Time     Flow Timer   Routes
Fa1/0              1             0/0          0/0          20      0/1            0           0
  Hello-interval is 60, Hold-time is 180
  ...
```
*Verify: Hello-interval is 60 and Hold-time is 180.*

```bash
R1# show interface FastEthernet1/0 | include BW
  MTU 1500 bytes, BW 1544 Kbit/sec, DLY 1000 usec, 
```
*Verify: BW is 1544 Kbit.*

### 7.3 Query Scope Verification (R5)
Ensure the stub router does not receive queries for remote network failures.
```bash
R5# debug eigrp packets query
EIGRP Packets debugging is on
    (Query)
!
! <Core link flap simulated on R1>
!
R5#
! (No output should appear on R5)
```
*Verify: No query packets arrive at R5.*

---

## 8. Troubleshooting Scenario

### The Fault
After configuring R5 as a `receive-only` stub for a security test, the Headquarters (R1) loses all routes to the 10.5.x.x networks, even though the neighbor relationship is UP.

### The Mission
1. Explain why R1 lost reachability to R5's local networks.
2. Restore R5 to a standard stub configuration that allows it to advertise its local subnets while remaining a query boundary.
3. Verify reachability from R1 to 10.5.1.1.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: Stub Configuration (R5)
```bash
router eigrp 100
 eigrp stub connected summary
```

### Objective 2: WAN Tuning (R1 & R2)
```bash
interface FastEthernet1/0
 bandwidth 1544
 ip hello-interval eigrp 100 60
 ip hold-time eigrp 100 180
```

---

## 10. Lab Completion Checklist

- [ ] R5 integrated and adjacent with R3.
- [ ] R5 configured as an EIGRP Stub (Connected/Summary).
- [ ] WAN bandwidth (1544) applied to R1 and R2.
- [ ] Hello (60s) and Hold (180s) timers applied to the WAN link.
- [ ] Query boundary verified (R5 not queried during Core flaps).
- [ ] Troubleshooting challenge resolved.