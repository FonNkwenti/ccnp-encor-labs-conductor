# CCNP ENCOR EIGRP Lab 05: Authentication & Advanced
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure EIGRP MD5 authentication using key chains
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
                        │(Tag 111)│
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
Following a recent security audit by the **Skynet Global** Cyber-Defense unit, several vulnerabilities were identified in the regional routing domain. Specifically, the EIGRP adjacency between the Headquarters (R1) and the Branch (R2) is currently unauthenticated, making it susceptible to route injection attacks. 

As the Senior Security Engineer, your task is to implement a robust authentication framework across the Core and Branch routers. You must deploy **MD5 authentication** between the Hub (R1) and the Branch (R2) to secure the control plane.

Furthermore, you will use **Route Tagging** on the Hub (R1) to identify and track headquarters routes as they propagate across the domain, and apply **Offset Lists** to manipulate the metric of routes from the Stub Network (R5), demonstrating advanced EIGRP traffic engineering techniques.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 05 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |

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

> ⚠️ **This lab builds on Lab 04.** Ensure that the basic EIGRP adjacency and Stub configuration from the previous lab is functional before applying security hardening.

---

## 5. Lab Challenge: Security Hardening & Advanced Control

### Objective 1: Implement MD5 Authentication (R1 <-> R2)
Secure the control plane communication between the Hub and the Branch.
- Create a key-chain named `SKYNET_MD5` on **R1** and **R2**.
- Configure `key 1` with the password `SkynetSecret`.
- Enable EIGRP MD5 authentication on the interfaces connecting R1 and R2.

### Objective 2: Route Tagging for Hub Identification (R1)
Tag the Hub router's loopback route for identification and auditing as it propagates across the domain.
- On **R1**, create an access-list matching `1.1.1.1/32` (the Hub loopback).
- Create a route-map named `TAG_HQ` that matches the access-list and sets tag `111`.
- Include a second permit clause (sequence 20) with no match to allow all other routes through untagged.
- Apply this route-map to the EIGRP process using `distribute-list route-map TAG_HQ out FastEthernet1/0`.
- Verify on **R5** that the tag `111` is visible using `show ip eigrp topology 1.1.1.1/32`.

### Objective 3: Traffic Engineering with Offset Lists (R1)
Manipulate the metric of routes from the Stub Network (R5) to influence path selection.
- On **R1**, create an access-list matching R5's networks (`5.5.5.5/32` and `10.5.0.0/16`).
- Use an **Offset List** to add `500000` to the composite metric of these routes as they are received on `FastEthernet1/0`.
- Verify that the feasible distance (FD) for R5's routes increases in the topology table.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip eigrp neighbors detail` | Verify that neighbors are authenticated and show the correct auth type. |
| `show key chain` | Confirm key-chain configuration on R1/R2. |
| `show ip eigrp topology 1.1.1.1/32` (on R5) | Confirm that R5 sees tag `111` for the Hub loopback (`Internal tag is 111`). |
| `show ip eigrp topology 5.5.5.5/32` (on R1) | Verify the increased FD for R5's routes due to the offset list. |

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

### 7.2 Verify Route Tagging (R5 Perspective)
```bash
R5# show ip eigrp topology 1.1.1.1/32
IP-EIGRP (AS 100): Topology entry for 1.1.1.1/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 1862656
  Routing Descriptor Blocks:
  10.0.35.1 (FastEthernet0/0), from 10.0.35.1, Send flag is 0x0
      Composite metric is (1862656/1837056), Route is Internal
      Vector metric:
        Minimum bandwidth is 1544 Kbit
        Total delay is 8000 microseconds
        Reliability is 255/255
        Load is 1/255
        Minimum MTU is 1500
        Hop count is 3
        Internal tag is 111
```

### 7.3 Verify Offset List (R1 Perspective)
The FD for R5's routes should increase by 500000 after applying the offset list.
```bash
R1# show ip eigrp topology 5.5.5.5/32
EIGRP-IPv4 Topology Entry for AS(100)/ID(1.1.1.1) for 5.5.5.5/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 2339616
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2339616/435200), route is Internal
      ...
```
Note: The FD increases from `1839616` (base) to `2339616` (base + 500000 offset).

---

## 8. Troubleshooting Scenario

### The Fault
After configuring route tagging on R1, downstream routers (R5) report receiving the Hub loopback route (1.1.1.1/32) but without tag `111`. Separately, the offset list on R1 is not increasing the metric for R5's routes as expected.

### The Mission
1. Verify that the route-map `TAG_HQ` is correctly applied on R1.
2. Check whether the `distribute-list route-map` is active in the correct direction.
3. Verify the offset list ACL matches the correct networks.
4. Restore proper tagging and confirm that R5 sees tag `111`, and the offset list increases R5's route metrics on R1.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: MD5 Authentication

<details>
<summary>Click to view R1 Configuration</summary>

```bash
key chain SKYNET_MD5
 key 1
  key-string SkynetSecret
!
interface FastEthernet1/0
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 SKYNET_MD5
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
key chain SKYNET_MD5
 key 1
  key-string SkynetSecret
!
interface FastEthernet0/0
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 SKYNET_MD5
```
</details>

### Objective 2: Route Tagging

<details>
<summary>Click to view R1 Configuration</summary>

```bash
access-list 11 permit 1.1.1.1
!
route-map TAG_HQ permit 10
 match ip address 11
 set tag 111
route-map TAG_HQ permit 20
!
router eigrp 100
 distribute-list route-map TAG_HQ out FastEthernet1/0
```
</details>

### Objective 3: Offset List

<details>
<summary>Click to view R1 Configuration</summary>

```bash
access-list 55 permit 5.5.5.5
access-list 55 permit 10.5.0.0 0.0.255.255
!
router eigrp 100
 offset-list 55 in 500000 FastEthernet1/0
```
</details>

---

## 10. Lab Completion Checklist

- [ ] MD5 Authentication active between R1 and R2.
- [ ] Hub loopback (1.1.1.1/32) tagged with `111` and visible on R5.
- [ ] Offset list correctly increases metric for R5 routes (5.5.5.5/32) on R1.
- [ ] Troubleshooting challenge resolved.
