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

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R5 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.0.12.0/30 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.0.23.0/30 |
| R3           | Fa0/1           | R5            | Fa0/0            | 10.0.35.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |

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

### Objective 1: Stub Configuration

<details>
<summary>Click to view R5 Configuration</summary>

```bash
router eigrp 100
 eigrp stub connected summary
```
</details>

### Objective 2: WAN Tuning

<details>
<summary>Click to view R1 Configuration</summary>

```bash
interface FastEthernet1/0
 bandwidth 1544
 ip hello-interval eigrp 100 60
 ip hold-time eigrp 100 180
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
interface FastEthernet0/0
 bandwidth 1544
 ip hello-interval eigrp 100 60
 ip hold-time eigrp 100 180
```
</details>

---

## 10. Lab Completion Checklist

- [ ] R5 integrated and adjacent with R3.
- [ ] R5 configured as an EIGRP Stub (Connected/Summary).
- [ ] WAN bandwidth (1544) applied to R1 and R2.
- [ ] Hello (60s) and Hold (180s) timers applied to the WAN link.
- [ ] Query boundary verified (R5 not queried during Core flaps).
- [ ] Troubleshooting challenge resolved.

---

## 11. Troubleshooting Solutions Appendix

### Challenge 1: The "Receive-Only" Silence — Solution

**Symptom:** R3 is adjacent with R5 and R5's neighbor status shows it is a "Stub Peer", but R1 and R2 no longer have any routes to the 10.5.x.x networks located behind R5.

**Root Cause:** The stub configuration on R5 is missing the `connected` keyword, so connected routes (10.5.x.x subnets) are not being redistributed and advertised to the core network.

**Solution:**

Check R5's EIGRP configuration:

```bash
R5# show running-config | section "router eigrp"
router eigrp 100
 eigrp router-id 5.5.5.5
 network 5.5.5.5 0.0.0.0
 network 10.0.35.0 0.0.0.3
 eigrp stub summary
```

Add the `connected` keyword to the stub configuration:

```bash
R5# configure terminal
R5(config)# router eigrp 100
R5(config-router)# eigrp stub connected summary
R5(config-router)# exit
R5(config)# end
R5# write memory
```

Also, ensure the 10.5.x.x networks are advertised:

```bash
R5# configure terminal
R5(config)# router eigrp 100
R5(config-router)# network 10.5.0.0 0.0.255.255
R5(config-router)# exit
R5(config)# end
R5# write memory
```

**Verification:**

```bash
R1# show ip route eigrp | include 10.5
D    10.5.0.0/16 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0

R2# show ip route eigrp | include 10.5
D    10.5.0.0/16 [90/2688000] via 10.0.23.2, 00:00:45, FastEthernet0/1
```

Routes from R5 should now appear in R1 and R2 routing tables.

---

### Challenge 2: The WAN Timeout — Solution

**Symptom:** The EIGRP adjacency between R1 and R2 is constantly flapping with logs indicating the neighbor has been "reset" due to "hold timer expired". The physical link is stable.

**Root Cause:** The hello/hold timers are configured asymmetrically between R1 and R2. EIGRP requires matching timers to maintain adjacency. The default is hello=5s, hold=15s. If one side has longer timers (e.g., hello=60s, hold=180s), the other side's hold timer may expire before the hello is received.

**Solution:**

Check the current timers on both routers:

```bash
R1# show ip eigrp interfaces detail FastEthernet1/0
EIGRP-IPv4 Interfaces for AS 100
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa1/0              1       0/0       0/0           15       0/0           50           0
  Hello-interval is 5, Hold-time is 15

R2# show ip eigrp interfaces detail FastEthernet0/0
EIGRP-IPv4 Interfaces for AS 100
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa0/0              1       0/0       0/0           20       0/0           50           0
  Hello-interval is 60, Hold-time is 180
```

The timers are asymmetrical. Configure matching timers on R1:

```bash
R1# configure terminal
R1(config)# interface FastEthernet1/0
R1(config-if)# ip hello-interval eigrp 100 60
R1(config-if)# ip hold-time eigrp 100 180
R1(config-if)# exit
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

The neighbor adjacency should stabilize and no longer flap.

---

### Challenge 3: Forgotten Static Routes — Solution

**Symptom:** R5 has a static route to a legacy server at 192.168.99.1. Despite having `eigrp stub connected summary`, the static route is not appearing in R1's routing table.

**Root Cause:** The `eigrp stub connected summary` configuration only redistributes **connected routes** (routes from configured network statements) and **summaries**. Static routes are not automatically included. To advertise static routes, they must be redistributed into EIGRP.

**Solution:**

Add a network statement to include the static route's subnet, or use redistribution. For this scenario, use a static route to Null0 as a summary and then redistribute static routes:

```bash
R5# configure terminal
R5(config)# ip route 192.168.99.0 255.255.255.0 <next-hop>
R5(config)# router eigrp 100
R5(config-router)# redistribute static
R5(config-router)# exit
R5(config)# end
R5# write memory
```

Alternatively, create a summary route for the static destination and advertise it:

```bash
R5# configure terminal
R5(config)# interface FastEthernet0/0
R5(config-if)# ip summary-address eigrp 100 192.168.99.0 255.255.255.0
R5(config-if)# exit
R5(config)# end
R5# write memory
```

**Verification:**

```bash
R1# show ip route eigrp | include 192.168
D    192.168.99.0/24 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0

R1# ping 192.168.99.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.99.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/25/30 ms
```

The static route to the legacy server should now be reachable across the EIGRP network.