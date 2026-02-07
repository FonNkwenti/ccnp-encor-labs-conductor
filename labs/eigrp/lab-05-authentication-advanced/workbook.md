# CCNP ENCOR EIGRP Lab 05: Authentication & Advanced
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure EIGRP MD5 authentication using key chains
- Implement HMAC-SHA-256 authentication for EIGRP
- Apply route tagging to identify source networks
- Utilize offset lists for EIGRP metric manipulation
- Verify secure adjacency establishment and route propagation
- Understand advanced EIGRP traffic engineering techniques

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
                        │ (MD5)   │ 10.0.12.1/30
                        │         │
           10.0.12.1/30 │         │
                        │         │ 10.0.12.2/30
                        │    ┌────┴────────┐
                        │    │     R2      │
                        │    │   Branch    │
                        │    │ 2.2.2.2/32  │
                        │    └────┬────────┘
                        │         │ Fa0/1 (SHA-256)
                        │         │ 10.0.23.1/30
                        │         │
                        │         │ 10.0.23.2/30
                        │         │ Fa0/0
                 ┌──────┴─────────┘
                 │       R3        
                 │  Remote Branch  
                 │  3.3.3.3/32     
                 └───┬─────────┐
                     │ Fa0/1   │ (Tag 555)
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
Following a recent security audit by the **Skynet Global** Cyber-Defense unit, several vulnerabilities were identified in the regional routing domain. Specifically, the EIGRP adjacency between the Headquarters (R1) and the Branch (R2) is currently unauthenticated, making it susceptible to route injection attacks. 

As the Senior Security Engineer, your task is to implement a robust authentication framework across the Core and Branch routers. You must deploy **MD5 authentication** between the Hub (R1) and the Branch (R2), and upgrade the Remote Branch (R3) to utilize the advanced **SHA-256 HMAC authentication** to meet the enterprise's "Encryption-in-Transit" mandate.

Furthermore, you will use **Route Tagging** to identify and track routes originating from the non-trusted Stub Network (R5) and apply **Offset Lists** to manipulate traffic flow, ensuring that high-priority security traffic is appropriately prioritized.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 05 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |

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

> ⚠️ **This lab builds on Lab 04.** Ensure that the basic EIGRP adjacency and Stub configuration from the previous lab is functional before applying security hardening.

---

## 5. Lab Challenge: Security Hardening & Advanced Control

### Objective 1: Implement MD5 Authentication (R1 <-> R2)
Secure the control plane communication between the Hub and the Branch.
- Create a key-chain named `SKYNET_MD5` on **R1** and **R2**.
- Configure `key 1` with the password `SkynetSecret`.
- Enable EIGRP MD5 authentication on the interfaces connecting R1 and R2.

### Objective 2: Implement SHA-256 Authentication (R2 <-> R3)
Deploy advanced HMAC-SHA-256 authentication for the Remote Branch link.
- On **R2** and **R3**, enable EIGRP SHA-256 authentication on the interconnecting FastEthernet interfaces.
- Use the password `AdvancedSecurity256`.
- *Note: SHA-256 for EIGRP does not use key-chains in IOS 15.x; it is configured directly on the interface.*

### Objective 3: Route Tagging for Untrusted Networks (R5)
Identify routes coming from the R5 stub network for auditing purposes.
- On **R3**, create a route-map to tag all routes received from **R5** with the tag `555`.
- Apply this route-map to the EIGRP process or interface as appropriate to ensure R1 receives the tagged routes.

### Objective 4: Traffic Engineering with Offset Lists (R1)
Manipulate the metric of tagged routes to influence path selection.
- On **R1**, identify routes with tag `555`.
- Use an **Offset List** to add `500000` to the composite metric of these routes as they are received.
- Verify that the feasible distance (FD) for these routes increases in the topology table.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip eigrp neighbors detail` | Verify that neighbors are authenticated and show the correct auth type. |
| `show key chain` | Confirm key-chain configuration on R1/R2. |
| `show ip eigrp topology <network> | include tag` | Confirm that R1 sees the tag `555` for R5's networks. |
| `show ip eigrp topology` | Verify the increased metric for tagged routes on R1. |

---

## 7. Verification Cheatsheet

### 7.1 Verify MD5 Authentication (R1 Perspective)
```bash
R1# show ip eigrp neighbors detail
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
   Version 15.3/2.0, Retrans: 0, Retries: 0, Prefixes: 8
   Topology-ids from peer - 0 
   Authentication MD5, key-chain "SKYNET_MD5"
```

### 7.2 Verify SHA-256 Authentication (R3 Perspective)
```bash
R3# show ip eigrp neighbors detail
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.23.1               Fa0/0                    11 00:01:45   20   200  0  32
   Version 12.4/2.0, Retrans: 0, Retries: 0, Prefixes: 6
   Topology-ids from peer - 0 
   Authentication SHA-256
```

### 7.3 Verify Route Tagging & Offset Lists (R1 Perspective)
```bash
R1# show ip eigrp topology 5.5.5.5/32
EIGRP-IPv4 Topology Entry for AS 100 for 5.5.5.5/32
  State is Reply Pending, Query Origin Flag is 1, 1 Successor(s), FD is 1282560
  Descriptor Cards:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (1282560/1024000), Route is Internal
      Vector metric:
        Minimum bandwidth is 1544 Kbit
        Total delay is 40000 microseconds
        Reliability is 255/255
        Load is 1/255
        Minimum MTU is 1500
        Hop count is 3
        Originating router is 5.5.5.5
      Route tag is 555
```

---

## 8. Troubleshooting Scenario

### The Fault
After enabling SHA-256 authentication between R2 and R3, the neighbor relationship fails to form. `debug eigrp packets` shows "authentication off or bad key".

### The Mission
1. Verify if the SHA-256 password matches on both sides.
2. Check if the interface is correctly configured for `ip authentication mode eigrp 100 hmac-sha-256`.
3. Restore the adjacency and confirm secure route exchange.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: MD5 Authentication (R1/R2)
```bash
key chain SKYNET_MD5
 key 1
  key-string SkynetSecret
interface FastEthernet1/0
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 SKYNET_MD5
```

### Objective 2: SHA-256 Authentication (R2/R3)
```bash
interface FastEthernet0/1
 ip authentication mode eigrp 100 hmac-sha-256 SkynetSHA
! Note: R3 uses Fa0/0
```

### Objective 3: Route Tagging (R3)
```bash
access-list 55 permit 5.5.5.5
access-list 55 permit 10.5.0.0 0.0.255.255
!
route-map TAG_R5 permit 10
 match ip address 55
 set tag 555
route-map TAG_R5 permit 20
!
router eigrp 100
 redistribute connected route-map TAG_R5
! OR apply to neighbor if supported
```

### Objective 4: Offset List (R1)
```bash
route-map MATCH_TAG permit 10
 match tag 555
!
router eigrp 100
 offset-list 0 in 500000 FastEthernet1/0 route-map MATCH_TAG
```

---

## 10. Lab Completion Checklist

- [ ] MD5 Authentication active between R1 and R2.
- [ ] SHA-256 Authentication active between R2 and R3.
- [ ] R5 networks tagged with `555` on R1.
- [ ] Offset list correctly increases metric for tagged routes on R1.
- [ ] Troubleshooting challenge resolved.
