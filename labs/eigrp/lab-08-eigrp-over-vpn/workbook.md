# CCNP ENCOR EIGRP Lab 08: EIGRP over VPN Tunnel
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure GRE (Generic Routing Encapsulation) tunnels between routers
- Establish EIGRP adjacencies over virtual tunnel interfaces
- Adjust tunnel interface metrics (bandwidth/delay) for correct path selection
- Tune MTU and TCP MSS for GRE environments to prevent fragmentation
- Manage EIGRP split-horizon on multi-point or hub-and-spoke topologies
- Verify secure route exchange over a WAN emulation

---

## 2. Topology & Scenario

### ASCII Diagram
```
                                  ┌─────────────────┐
                                  │       R6        │
                                  │  VPN Endpoint   │
                                  │  6.6.6.6/32     │
                                  └────────┬────────┘
                                           │ Gi3/0
                                           │ 10.0.16.2/30
                                           │
                    ┌─────────────────┐    │ Gi3/0
                    │       R1        ├────┘
                    │   (Hub Router)  │ (WAN Link)
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1
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
To further enhance the reachability and security of the **Skynet Global** infrastructure, the network team is deploying a Virtual Private Network (VPN) solution to connect a new high-security endpoint router (**R6**). This site is connected to the Headquarters via a non-trusted service provider network.

As the Senior Network Engineer, your task is to establish a **GRE Tunnel** between the Hub (**R1**) and the VPN Endpoint (**R6**). Once the tunnel is established, you will run EIGRP over this virtual link to integrate R6 into the global routing table. You must ensure that the tunnel overhead is correctly accounted for by adjusting the **MTU** and **TCP MSS** settings, and tune the EIGRP metrics to ensure the tunnel is preferred for specific traffic while remaining a backup for others.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 08 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router / VPN Hub | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R6 | Secure VPN Endpoint | c7200 | 6.6.6.6/32 | **Yes** |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R6 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R5 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 07.** Ensure that redistribution and authentication are functional before deploying the GRE tunnel.

### R6 (VPN Endpoint - Integration)
```bash
enable
configure terminal
hostname R6
interface Loopback0
 ip address 6.6.6.6 255.255.255.255
interface GigabitEthernet3/0
 description Link to Headquarters
 ip address 10.0.16.2 255.255.255.252
 no shutdown
ip route 0.0.0.0 0.0.0.0 10.0.16.1
end
```

### R1 (Link to R6)
```bash
interface GigabitEthernet3/0
 description Link to R6 (Secure Site)
 ip address 10.0.16.1 255.255.255.252
 no shutdown
end
```

---

## 5. Lab Challenge: EIGRP over GRE Tunnel

### Objective 1: Establish GRE Tunnel (R1 <-> R6)
Create a point-to-point GRE tunnel between the Hub and the Secure Site.
- **R1 Tunnel Interface:** `Tunnel8`, Source `10.0.16.1`, Destination `10.0.16.2`, IP `172.16.16.1/30`.
- **R6 Tunnel Interface:** `Tunnel8`, Source `10.0.16.2`, Destination `10.0.16.1`, IP `172.16.16.2/30`.
- Verify pings across the tunnel IP addresses.

### Objective 2: Configure EIGRP over Tunnel
- Enable EIGRP AS 100 on the `Tunnel8` interfaces of R1 and R6.
- Ensure R6 advertises its Loopback0 (`6.6.6.6/32`).
- Verify that R1 learns the route to 6.6.6.6 via `Tunnel8`.

### Objective 3: Tunnel Optimization (MTU/MSS)
To prevent packet fragmentation caused by GRE encapsulation (24-byte overhead):
- On both R1 and R6 tunnel interfaces, set the **IP MTU** to `1400`.
- Configure the **TCP MSS** to `1360`.

### Objective 4: Metric Manipulation
- On R1 and R6, adjust the EIGRP interface **Delay** on `Tunnel8` to `5000` (tens of microseconds).
- Confirm that the tunnel interface is recognized by EIGRP but has a higher cost than physical paths (if any existed).

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show interface tunnel 8` | Verify tunnel is UP/UP and shows the correct source/destination. |
| `show ip eigrp neighbors` | Confirm EIGRP neighbor formed over the Tunnel interface. |
| `show ip route 6.6.6.6` | Verify R1 learns the route via Tunnel8. |
| `show ip interface tunnel 8 | include MTU` | Confirm MTU setting of 1400. |

---

## 7. Verification Cheatsheet

### 7.1 Verify Tunnel Adjacency
```bash
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   172.16.16.2             Tu8                      12 00:03:45   25   200  0  42
```

### 7.2 Verify Tunnel MTU/MSS
```bash
R1# show ip interface tunnel 8
Tunnel8 is up, line protocol is up
  Internet address is 172.16.16.1/30
  MTU is 1400 bytes
  ...
  TCP MSS foraging is enabled
  TCP MSS setting is 1360
```

---

## 8. Troubleshooting Scenario

### The Fault
The EIGRP neighbor relationship over the tunnel is flapping constantly. `debug ip packet` shows packets being dropped or ICMP "Fragmentation Needed" messages.

### The Mission
1. Investigate the physical interface MTU vs the tunnel MTU.
2. Ensure that the tunnel destination is reachable via a physical path and NOT via the tunnel itself (Recursive Routing!).
3. Check if the `ip split-horizon eigrp 100` command is needed (if this were a hub-and-spoke setup).
4. Restore stability to the tunnel adjacency.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1 & 2: Tunnel & EIGRP
```bash
! R1
interface Tunnel8
 ip address 172.16.16.1 255.255.255.252
 tunnel source 10.0.16.1
 tunnel destination 10.0.16.2
!
router eigrp 100
 network 172.16.16.0 0.0.0.3

! R6
interface Tunnel8
 ip address 172.16.16.2 255.255.255.252
 tunnel source 10.0.16.2
 tunnel destination 10.0.16.1
!
router eigrp 100
 network 172.16.16.0 0.0.0.3
 network 6.6.6.6 0.0.0.0
```

### Objective 3: MTU/MSS Optimization
```bash
interface Tunnel8
 ip mtu 1400
 ip tcp adjust-mss 1360
```

---

## 10. Lab Completion Checklist

- [ ] GRE Tunnel UP/UP between R1 and R6.
- [ ] EIGRP adjacency established over Tunnel8.
- [ ] R6 loopback (6.6.6.6) reachable from R1 via tunnel.
- [ ] MTU (1400) and MSS (1360) applied to tunnel interfaces.
- [ ] Troubleshooting challenge resolved.
