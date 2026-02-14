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

As the Senior Security Engineer, your task is to implement a robust authentication framework across the Core and Branch routers. You must deploy **MD5 authentication** between the Hub (R1) and the Branch (R2) to secure the control plane.

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

### Objective 2: Route Tagging for Untrusted Networks (R5)
Identify routes coming from the R5 stub network for auditing purposes.
- On **R3**, create a route-map to tag all routes received from **R5** with the tag `555`.
- Apply this route-map to the EIGRP process or interface as appropriate to ensure R1 receives the tagged routes.

### Objective 3: Traffic Engineering with Offset Lists (R1)
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

### 7.2 Verify Route Tagging & Offset Lists (R1 Perspective)
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
After configuring route tagging on R3 for R5's networks, R1 reports receiving the routes but without tag `555`. The offset list on R1 is therefore having no effect on the metric.

### The Mission
1. Verify that the route-map `TAG_R5` is correctly applied on R3.
2. Check whether the `distribute-list route-map` is active in the correct direction.
3. Restore proper tagging and confirm that R1 sees tag `555` and the offset list applies.

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
<summary>Click to view R3 Configuration</summary>

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
 distribute-list route-map TAG_R5 out FastEthernet0/0
```
</details>

### Objective 3: Offset List

<details>
<summary>Click to view R1 Configuration</summary>

```bash
route-map MATCH_TAG permit 10
 match tag 555
!
router eigrp 100
 offset-list 0 in 500000 FastEthernet1/0 route-map MATCH_TAG
```
</details>

---

## 10. Lab Completion Checklist

- [ ] MD5 Authentication active between R1 and R2.
- [ ] R5 networks tagged with `555` on R1.
- [ ] Offset list correctly increases metric for tagged routes on R1.
- [ ] Troubleshooting challenge resolved.

---

## 11. Troubleshooting Solutions Appendix

### Challenge 1: The "Secret" Mismatch (MD5) — Solution

**Symptom:** R1 and R2 are physically connected, but the EIGRP adjacency has dropped. `show ip eigrp neighbors` is empty on both sides. Console logs on R1 show "authentication bad key".

**Root Cause:** The MD5 key-chain password was changed from `SkynetSecret` to `WRONG_PASSWORD` on R2, causing authentication failure.

**Solution:**

On **R2**, correct the key-chain password to match R1:

```bash
R2# configure terminal
R2(config)# key chain SKYNET_MD5
R2(config-keychain)# key 1
R2(config-keychain-key)# key-string SkynetSecret
R2(config-keychain-key)# exit
R2(config-keychain)# exit
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R1# show ip eigrp neighbors detail
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
   Version 15.3/2.0, Retrans: 0, Retries: 0, Prefixes: 8
   Authentication MD5, key-chain "SKYNET_MD5"
```

The neighbor adjacency should re-establish and show MD5 authentication active.

---

### Challenge 2: Tagging & Offsets Gone Wrong — Solution

**Symptom:** R1 is successfully receiving routes from R5, but they are not being tagged with `555`, and consequently, the Offset List is not applying the expected metric penalty.

**Root Cause:** The `distribute-list route-map TAG_R5 out` was removed from the EIGRP router configuration on R3, preventing the route-map from being applied to routes sent to R1.

**Solution:**

On **R3**, re-apply the distribute-list route-map configuration:

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# distribute-list route-map TAG_R5 out FastEthernet0/0
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

Verify on **R1** that the routes from R5 are now tagged with `555`:

```bash
R1# show ip eigrp topology 5.5.5.5/32
EIGRP-IPv4 Topology Entry for AS 100 for 5.5.5.5/32
  State is Reply Pending, Query origin flag is 1, 1 Successor(s), FD is 1282560
  Descriptor Cards:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (1282560/1024000), Route is Internal
      Vector metric:
        ...
        Route tag is 555
```

The tag `555` should now appear in the topology table. Verify the offset list is applying:

```bash
R1# show ip eigrp topology 5.5.5.5/32 | include "Composite metric"
Composite metric is (1782560/1024000), route is Internal
```

The composite metric should be increased by 500000 due to the offset list (1024000 + 500000 = 1524000 for the second value, reflecting the offset applied).

---

### Challenge 3: The Phantom Penalty — Solution

**Symptom:** R1's offset list appears to be active, but the metric penalty is being applied to the wrong routes. Routes from R5 that should be penalized are unaffected, while other routes are unexpectedly inflated.

**Root Cause:** The route-map `MATCH_TAG` on R1 was modified to match tag `999` instead of the correct tag value `555`. Since R5 routes are tagged with `555`, they don't match the route-map and the offset list isn't applied to them.

**Solution:**

On **R1**, correct the tag value in the MATCH_TAG route-map:

```bash
R1# configure terminal
R1(config)# route-map MATCH_TAG permit 10
R1(config-route-map)# no match tag 999
R1(config-route-map)# match tag 555
R1(config-route-map)# exit
R1(config)# end
R1# write memory
```

**Verification:**

Verify the corrected route-map configuration:

```bash
R1# show route-map MATCH_TAG
route-map MATCH_TAG, permit, sequence 10
  Match clauses:
    tag 555
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```

Verify that the offset list is now correctly applied to routes tagged with `555`:

```bash
R1# show ip eigrp topology 5.5.5.5/32
EIGRP-IPv4 Topology Entry for AS 100 for 5.5.5.5/32
  State is Reply Pending, Query origin flag is 1, 1 Successor(s), FD is 1782560
  Descriptor Cards:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (1782560/1024000), Route is Internal
      ...
      Route tag is 555
```

The composite metric should now include the offset penalty (1024000 + 500000 = 1524000 for the second value). Other routes not tagged with `555` should return to their original metrics without the penalty.
