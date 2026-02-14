# CCNP ENCOR EIGRP Lab 10: Named Mode Advanced Features
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure HMAC-SHA-256 authentication using EIGRP Named Mode `af-interface`
- Enable wide metrics (64-bit) for more granular path selection
- Tune per-interface hello/hold timers via `af-interface` sub-mode
- Configure passive-interface using Named Mode syntax
- Understand the differences between Classic Mode and Named Mode feature sets
- Verify Named Mode authentication and metric behavior

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
                    │   (Hub Router)  ├──────────────┐
                    │  Lo0: 1.1.1.1   │              │ Fa0/0
                    └───┬─────────┬───┘              │ 10.0.17.1/30
                        │ Fa1/0   │ Gi3/0            │
                        │         │ 10.0.16.1/30     │ 10.0.17.2/30
           10.0.12.1/30 │         │             ┌────┴────────┐
                        │         │             │     R7      │
                        │    ┌────┘             │ Summary Bdy │
                        │    │                  │ 7.7.7.7/32  │
                        │    │ 10.0.16.2/30     └─────────────┘
                        │    │ Gi3/0
                        │    ┌────────────┐
                        │    │     R6      │
                        │    │ VPN Endpoint │
                        │    │ 6.6.6.6/32  │
                        │    └────┬────────┘
                        │         │ Tunnel8
                        │         │ 172.16.16.0/30
                        │         │ (SHA-256 Auth)
                        │         │
           10.0.12.2/30 │
                   ┌────┴────────┐
                   │     R2      │
                   │   Branch    │
                   │ 2.2.2.2/32  │
                   └────┬────────┘
                        │ Fa0/1
                        │ 10.0.23.1/30
                        │
                        │ 10.0.23.2/30
                        │ Fa0/0
                 ┌──────┴─────────┐
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
The **Skynet Global** network has completed its dual-stack migration and is now entering the **Advanced Hardening Phase**. The CTO has identified that the GRE tunnel link between R1 and R6 — both running IOS 15.3 on the c7200 platform — is the ideal candidate for deploying **HMAC-SHA-256 authentication**, which is only available via EIGRP Named Mode's `af-interface` sub-commands.

Additionally, the engineering team wants to leverage **Wide Metrics** (64-bit) on the Named Mode routers to gain finer-grained path selection over high-bandwidth links, and to demonstrate **per-interface tuning** capabilities that Named Mode provides through its `af-interface` configuration hierarchy.

> **Platform Note:** Only R1 and R6 (c7200, IOS 15.3) support EIGRP Named Mode and SHA-256. R2-R5 and R7 (c3725, IOS 12.4) remain on Classic Mode and are not modified in this lab.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 10 |
|--------|------|----------|-----------|---------------|
| R1 | Hub / Named Mode Lead | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |
| R6 | VPN Endpoint | c7200 | 6.6.6.6/32 | No |
| R7 | Summary Boundary | c3725 | 7.7.7.7/32 | No |

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2-R5, R7 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R6 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.0.12.0/30 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.0.23.0/30 |
| R3           | Fa0/1           | R5            | Fa0/0            | 10.0.35.0/30 |
| R1           | Gi3/0           | R6            | Gi3/0            | 10.0.16.0/30 |
| R1           | Fa0/0           | R7            | Fa0/0            | 10.0.17.0/30 |
| R1           | Tunnel8         | R6            | Tunnel8          | 172.16.16.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |
| R6 | 5006 | `telnet 127.0.0.1 5006` |
| R7 | 5007 | `telnet 127.0.0.1 5007` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 09.** Ensure that the dual-stack EIGRP Named Mode configuration is functional before applying advanced hardening features.

---

## 5. Lab Challenge: Named Mode Advanced Hardening

### Objective 1: SHA-256 HMAC Authentication (R1 <-> R6 over Tunnel8)
Secure the EIGRP adjacency over the GRE tunnel using Named Mode SHA-256 authentication.
- On **R1** and **R6**, configure SHA-256 authentication under the `af-interface Tunnel8` sub-mode within the `SKYNET_CORE` Named Mode instance.
- Use the password `SkynetSHA256!`.
- Verify that the EIGRP adjacency re-establishes with authentication active.

### Objective 2: Wide Metrics (R1 & R6)
Enable 64-bit wide metrics for more precise path selection on high-bandwidth links.
- On **R1** and **R6**, configure `metric version 64bit` under the `address-family ipv4` topology base.
- Configure `metric rib-scale 128` to ensure the 64-bit metrics fit within the RIB's 32-bit field.
- Verify the metric change using `show eigrp address-family ipv4 topology`.

### Objective 3: AF-Interface Tuning (R1)
Demonstrate per-interface configuration using Named Mode's `af-interface` sub-mode.
- On **R1**, configure hello interval of `10` seconds and hold time of `30` seconds on `af-interface FastEthernet1/0`.
- On **R1**, configure `af-interface Loopback0` as `passive-interface`.
- Verify that the modified timers are reflected in `show eigrp address-family ipv4 interfaces detail`.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show eigrp address-family ipv4 neighbors detail` | Verify SHA-256 authentication on Tunnel8 adjacency. |
| `show eigrp address-family ipv4 topology` | Verify wide metric values (larger composite metrics). |
| `show eigrp address-family ipv4 interfaces detail` | Confirm per-interface hello/hold timers and passive state. |
| `show eigrp protocols` | Verify metric version and rib-scale configuration. |

---

## 7. Verification Cheatsheet

### 7.1 Verify SHA-256 Authentication (R1 Perspective)
```bash
R1# show eigrp address-family ipv4 neighbors detail
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   172.16.16.2             Tu8                      12 00:05:22   25   200  0  44
   Version 15.3/3.0, Retrans: 0, Retries: 0, Prefixes: 2
   Topology-ids from peer - 0
   Authentication SHA-256
```

### 7.2 Verify Wide Metrics (R1 Perspective)
```bash
R1# show eigrp address-family ipv4 topology 6.6.6.6/32
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Topology Entry for AS(100)/ID(1.1.1.1)
  for 6.6.6.6/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 1966080
  Descriptor Blocks:
  172.16.16.2 (Tunnel8), from 172.16.16.2, Send flag is 0x0
      Composite metric is (1966080/655360), route is Internal
      ...
      Wide metric: [65536/1, 1966080/655360]
```

### 7.3 Verify AF-Interface Timers (R1 Perspective)
```bash
R1# show eigrp address-family ipv4 interfaces detail FastEthernet1/0
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Interfaces for AS(100)
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa1/0              1       0/0       0/0           15       0/0           50           0
  Hello-interval is 10, Hold-time is 30
  ...
```

---

## 8. Troubleshooting Scenario

### The Fault
After enabling SHA-256 authentication on R1's Tunnel8 interface, the EIGRP adjacency with R6 over the tunnel has dropped. R1 shows "authentication type mismatch" in debug output.

### The Mission
1. Check if R6 also has SHA-256 authentication configured under `af-interface Tunnel8`.
2. Verify the password matches on both sides.
3. Restore the authenticated adjacency and confirm route exchange over the tunnel.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: SHA-256 HMAC Authentication

<details>
<summary>Click to view R1 Configuration</summary>

```bash
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  af-interface Tunnel8
   authentication mode hmac-sha-256 SkynetSHA256!
  exit-af-interface
 exit-address-family
```
</details>

<details>
<summary>Click to view R6 Configuration</summary>

```bash
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  af-interface Tunnel8
   authentication mode hmac-sha-256 SkynetSHA256!
  exit-af-interface
 exit-address-family
```
</details>

### Objective 2: Wide Metrics

<details>
<summary>Click to view R1 Configuration</summary>

```bash
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  topology base
   metric version 64bit
   metric rib-scale 128
  exit-af-topology
 exit-address-family
```
</details>

<details>
<summary>Click to view R6 Configuration</summary>

```bash
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  topology base
   metric version 64bit
   metric rib-scale 128
  exit-af-topology
 exit-address-family
```
</details>

### Objective 3: AF-Interface Tuning

<details>
<summary>Click to view R1 Configuration</summary>

```bash
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  af-interface FastEthernet1/0
   hello-interval 10
   hold-time 30
  exit-af-interface
  af-interface Loopback0
   passive-interface
  exit-af-interface
 exit-address-family
```
</details>

---

## 10. Lab Completion Checklist

- [ ] SHA-256 authentication active on R1-R6 Tunnel8 adjacency.
- [ ] Wide metrics (64-bit) enabled on R1 and R6.
- [ ] Per-interface hello/hold timers configured on R1 Fa1/0.
- [ ] Loopback0 on R1 set as passive via af-interface.
- [ ] Troubleshooting challenge resolved.

---

## 11. Troubleshooting Solutions Appendix

### Challenge 1: The Auth Asymmetry — Solution

**Symptom:** After configuring SHA-256 authentication on both R1 and R6 for Tunnel8, the EIGRP adjacency over the tunnel drops.

**Root Cause:** The SHA-256 password on R6 was changed to `WRONG_PASSWORD` instead of matching R1's `SkynetSHA256!`.

**Solution:**

On **R6**, correct the password in the af-interface configuration:

```bash
R6# configure terminal
R6(config)# router eigrp SKYNET_CORE
R6(config-router)# address-family ipv4 autonomous-system 100
R6(config-router-af)# af-interface Tunnel8
R6(config-router-af-interface)# authentication mode hmac-sha-256 SkynetSHA256!
R6(config-router-af-interface)# exit-af-interface
R6(config-router-af)# exit-address-family
R6(config)# end
R6# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv4 neighbors detail
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   172.16.16.2             Tu8                      12 00:05:22   25   200  0  44
   Version 15.3/3.0, Retrans: 0, Retries: 0, Prefixes: 2
   Authentication SHA-256
```

The adjacency should re-establish with authentication type shown as SHA-256.

---

### Challenge 2: The Metric Mismatch — Solution

**Symptom:** R1 and R6 have an active EIGRP adjacency, but R1 reports routes from R6 with classic 32-bit metrics while R1's local routes use 64-bit wide metrics. This indicates a metric version mismatch.

**Root Cause:** Wide metrics (`metric version 64bit` and `metric rib-scale 128`) were removed from R6's topology base configuration, creating an asymmetry where R1 uses 64-bit and R6 uses classic 32-bit.

**Solution:**

On **R6**, re-enable wide metrics under the topology base:

```bash
R6# configure terminal
R6(config)# router eigrp SKYNET_CORE
R6(config-router)# address-family ipv4 autonomous-system 100
R6(config-router-af)# topology base
R6(config-router-af-topology)# metric version 64bit
R6(config-router-af-topology)# metric rib-scale 128
R6(config-router-af-topology)# exit-af-topology
R6(config-router-af)# exit-address-family
R6(config)# end
R6# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv4 topology 6.6.6.6/32
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Topology Entry for AS(100)/ID(1.1.1.1)
  for 6.6.6.6/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 1966080
  Descriptor Blocks:
  172.16.16.2 (Tunnel8), from 172.16.16.2, Send flag is 0x0
      Composite metric is (1966080/655360), route is Internal
      ...
      Wide metric: [65536/1, 1966080/655360]
```

Wide metrics should now appear in the topology table output, and routes from R6 should match R1's metric format.

---

### Challenge 3: The Silent Interface — Solution

**Symptom:** R1 suddenly loses its EIGRP adjacency with R2 over FastEthernet1/0. R1 can still ping R2's interface address, but `show eigrp address-family ipv4 neighbors` no longer shows R2 as a neighbor.

**Root Cause:** The `passive-interface` command was accidentally applied to `FastEthernet1/0` instead of `Loopback0`. Passive interfaces do not send EIGRP Hello packets, preventing neighbor adjacency formation.

**Solution:**

On **R1**, remove the passive-interface configuration from Fa1/0 and re-apply it to Loopback0:

```bash
R1# configure terminal
R1(config)# router eigrp SKYNET_CORE
R1(config-router)# address-family ipv4 autonomous-system 100
R1(config-router-af)# af-interface FastEthernet1/0
R1(config-router-af-interface)# no passive-interface
R1(config-router-af-interface)# exit-af-interface
R1(config-router-af)# af-interface Loopback0
R1(config-router-af-interface)# passive-interface
R1(config-router-af-interface)# exit-af-interface
R1(config-router-af)# exit-address-family
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv4 neighbors
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
```

The R2 neighbor should reappear in the neighbors table. Verify with:

```bash
R1# show eigrp address-family ipv4 interfaces detail FastEthernet1/0
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Interfaces for AS(100)
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa1/0              1       0/0       0/0           15       0/0           50           0
  ...
```

Loopback0 should be listed as passive:

```bash
R1# show eigrp address-family ipv4 interfaces detail Loopback0
...
Loopback0          0       0/0       0/0            -         -             -           0
  Passive Interface
```
