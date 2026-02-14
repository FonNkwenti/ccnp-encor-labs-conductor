# CCNP ENCOR EIGRP Lab 09: Dual-Stack EIGRP Migration
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure EIGRP Named Mode for multi-address family support
- Implement EIGRP for IPv6 (Address Family IPv6)
- Understand the migration path from Classic Mode to Named Mode
- Verify dual-stack EIGRP adjacencies and route propagation
- Optimize EIGRP for IPv6 using summaries and stub features
- Troubleshoot IPv6 connectivity in an EIGRP domain

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
                        │ Fa1/0   │ Fa1/1            │
                        │         │                  │
           10.0.12.1/30 │         │ 10.0.12.2/30     │ 10.0.17.2/30
                        │    ┌────┴────────┐    ┌────┴────────┐
                        │    │     R2      │    │     R7      │
                        │    │   Branch    │    │ Summary Bdy │
                        │    │ 2.2.2.2/32  │    │ 7.7.7.7/32  │
                        │    └────┬────────┘    └─────────────┘
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
                                  ┌─────────────────┐
                                  │       R6        │
                                  │  VPN Endpoint   │
                                  │  6.6.6.6/32     │
                                  └────────┬────────┘
                                           │ Gi3/0 (Tunnel)
```

### Scenario Narrative
The **Skynet Global** network is entering its final phase of infrastructure modernization. To support the "NextGen Network" initiative, the entire EIGRP domain must be transitioned to a **Dual-Stack (IPv4/IPv6)** environment. 

The CTO has mandated the use of **EIGRP Named Mode** (also known as Multi-AF EIGRP) to simplify configuration and enable support for both address families under a single virtual instance. Your objective is to migrate all routers from the existing EIGRP Classic Mode to Named Mode without causing prolonged downtime, and then enable IPv6 routing across the entire topology.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 09 |
|--------|------|----------|-----------|---------------|
| R1 | Hub / Migration Lead | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R4 | CyberDyne OSPF | c3725 | 4.4.4.4/32 | No |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |
| R6 | VPN Endpoint | c7200 | 6.6.6.6/32 | No |
| R7 | Summary Boundary | c3725 | 7.7.7.7/32 | **Yes** |

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
| R1           | Fa1/1           | R4            | Fa0/0            | 10.0.14.0/30 |
| R1           | Gi3/0           | R6            | Gi3/0            | 10.0.16.0/30 |
| R1           | Fa0/0           | R7            | Fa0/0            | 10.0.17.0/30 |
| R1           | Tunnel8         | R6            | Tunnel8          | 172.16.16.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |
| R6 | 5006 | `telnet 127.0.0.1 5006` |
| R7 | 5007 | `telnet 127.0.0.1 5007` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 08.** Ensure that the GRE tunnel and previous redistribution/security settings are functional.

### R7 (Summary Boundary - Integration)
```bash
enable
configure terminal
hostname R7
interface Loopback0
 ip address 7.7.7.7 255.255.255.255
interface FastEthernet0/0
 ip address 10.0.17.2 255.255.255.252
 no shutdown
router eigrp 100
 network 7.7.7.7 0.0.0.0
 network 10.0.17.0 0.0.0.3
end
```

---

## 5. Lab Challenge: NextGen Dual-Stack Migration

### Objective 1: Transition to EIGRP Named Mode (R1)
Convert the existing EIGRP Classic configuration on R1 to Named Mode.
- Create a virtual instance named `SKYNET_CORE`.
- Migrate the IPv4 AS 100 settings into the `address-family ipv4 autonomous-system 100` sub-mode.
- Verify that EIGRP neighbors re-establish and all routes are present.

### Objective 2: Enable EIGRP for IPv6 (All Routers)
Deploy IPv6 addressing and EIGRP routing.
- **Addressing Scheme:** Use `2001:DB8:ACAD:<Device#>#::/64` for loopbacks and `2001:DB8:ACAD:<LinkID>::/64` for links.
- Enable `ipv6 unicast-routing` globally.
- Configure EIGRP Named Mode on all routers using the same instance name `SKYNET_CORE`.
- Establish IPv6 adjacencies over all active links (including the GRE Tunnel between R1 and R6).

### Objective 3: Dual-Stack Verification
- Verify that every router has a full IPv4 and IPv6 routing table.
- Confirm reachability to all loopbacks via both protocols.
- Use `show ip eigrp neighbors` and `show ipv6 eigrp neighbors` to confirm dual-stack adjacency.

### Objective 4: Optimization & Advanced AF Features
- On **R7**, configure a summary route for the 10.0.0.0/8 range towards R1 using the AF sub-mode commands.
- On **R5**, verify that the stub configuration is active for both IPv4 and IPv6 families.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show eigrp address-family ipv4 neighbors` | Verify IPv4 neighbors in Named Mode. |
| `show eigrp address-family ipv6 neighbors` | Verify IPv6 neighbors in Named Mode. |
| `show ipv6 route eigrp` | Confirm IPv6 routes are learned across the domain. |
| `ping ipv6 <address>` | Successful end-to-end reachability. |

---

## 7. Verification Cheatsheet

### 7.1 Verify IPv4 Named Mode Neighbors
```bash
R1# show eigrp address-family ipv4 neighbors
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    12 00:10:25   15   200  0  55
```
*Verify: Neighbor is learned under the virtual instance 'SKYNET_CORE'.*

### 7.2 Verify IPv6 Named Mode Neighbors
```bash
R1# show eigrp address-family ipv6 neighbors
EIGRP-IPv6 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C802:12FF:FE34:0  Fa1/0                    14 00:05:12   20   200  0  12
```
*Verify: IPv6 neighbor is established via Link-Local address.*

### 7.3 Verify Dual-Stack Topology Table
```bash
R1# show eigrp address-family ipv4 topology 5.5.5.5/32
R1# show eigrp address-family ipv6 topology 2001:DB8:ACAD:5::5/128
```
*Verify: Both IPv4 and IPv6 loopbacks are present in the topology table.*

### 7.4 Verify IPv6 Reachability
```bash
R1# ping ipv6 2001:DB8:ACAD:5::5
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2001:DB8:ACAD:5::5, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/24/32 ms
```

---

## 8. Troubleshooting Scenario

### The Fault
After enabling IPv6 on R6, the router cannot form an EIGRP adjacency with R1 over the GRE tunnel, even though the IPv4 adjacency is perfectly stable.

### The Mission
1. Check if an IPv6 address was assigned to the `Tunnel8` interface.
2. Verify if `ipv6 unicast-routing` is enabled on R6.
3. Ensure the `address-family ipv6` is active under the EIGRP Named Mode instance on both sides.
4. Check if any previous MTU/MSS settings are interfering with IPv6 neighbor discovery packets (which are larger than IPv4).

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: Migration to Named Mode

<details>
<summary>Click to view R1 Configuration</summary>

```bash
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  network 1.1.1.1 0.0.0.0
  network 10.0.12.0 0.0.0.3
  network 172.16.16.0 0.0.0.3
  topology base
  exit-af-topology
 exit-address-family
```
</details>

### Objective 2: Enable EIGRP for IPv6

<details>
<summary>Click to view R1 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface FastEthernet1/0
 ipv6 address 2001:DB8:ACAD:12::1/64
 ipv6 enable
!
interface Tunnel8
 ipv6 address 2001:DB8:ACAD:88::1/64
 ipv6 enable
!
router eigrp SKYNET_CORE
 address-family ipv6 autonomous-system 100
  topology base
  exit-af-topology
 exit-address-family
```
</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface FastEthernet0/0
 ipv6 address 2001:DB8:ACAD:12::2/64
 ipv6 enable
!
interface FastEthernet0/1
 ipv6 address 2001:DB8:ACAD:23::1/64
 ipv6 enable
!
router eigrp SKYNET_CORE
 address-family ipv6 autonomous-system 100
  topology base
  exit-af-topology
 exit-address-family
```
</details>

<details>
<summary>Click to view R6 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface GigabitEthernet3/0
 ipv6 address 2001:DB8:ACAD:16::2/64
 ipv6 enable
!
interface Tunnel8
 ipv6 address 2001:DB8:ACAD:88::2/64
 ipv6 enable
!
router eigrp SKYNET_CORE
 address-family ipv6 autonomous-system 100
  topology base
  exit-af-topology
 exit-address-family
```
</details>

---

## 10. Lab Completion Checklist

- [ ] R1 migrated to Named Mode.
- [ ] IPv6 connectivity established globally.
- [ ] Dual-stack EIGRP adjacencies verified on all links.
- [ ] GRE Tunnel supports both IPv4 and IPv6 traffic.
- [ ] Troubleshooting challenge resolved.

---

## 11. Troubleshooting Solutions Appendix

### Challenge 1: The Invisible AF (Unicast Routing) — Solution

**Symptom:** EIGRP Named Mode `address-family ipv6` is configured on R1 and R2 with IPv6 addresses assigned to interfaces. However, `show ipv6 eigrp neighbors` is empty, and the router won't allow certain IPv6 configuration modes.

**Root Cause:** The global `ipv6 unicast-routing` command is not enabled on one or both routers. Without this, IPv6 forwarding is disabled, and the router treats IPv6 interfaces as down for routing purposes.

**Solution:**

Enable IPv6 unicast routing globally on both R1 and R2:

```bash
R1# configure terminal
R1(config)# ipv6 unicast-routing
R1(config)# end
R1# write memory

R2# configure terminal
R2(config)# ipv6 unicast-routing
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R1# show ipv6 eigrp neighbors
EIGRP-IPv6 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C802:12FF:FE34:0  Fa1/0                    14 00:05:12   20   200  0  12
```

IPv6 neighbors should now appear in the neighbors table.

---

### Challenge 2: Named Mode Identity Crisis — Solution

**Symptom:** R1 and R2 have established an IPv4 adjacency, but the IPv6 adjacency won't form. `show eigrp address-family ipv6 neighbors` shows nothing. Physical and IPv6 connectivity work (pings succeed).

**Root Cause:** The IPv6 address-family is not configured under the Named Mode instance with the same AS number. The IPv4 AS is 100, but the IPv6 AS may be misconfigured or missing entirely.

**Solution:**

Check the EIGRP configuration on R2:

```bash
R2# show running-config | section "router eigrp"
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  ...
 exit-address-family
 !
 address-family ipv6 autonomous-system 200
  ...
 exit-address-family
```

The IPv6 AS is 200 instead of 100. Correct it:

```bash
R2# configure terminal
R2(config)# router eigrp SKYNET_CORE
R2(config-router)# no address-family ipv6 autonomous-system 200
R2(config-router)# address-family ipv6 autonomous-system 100
R2(config-router-af)# topology base
R2(config-router-af-topology)# exit-af-topology
R2(config-router-af)# exit-address-family
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv6 neighbors
EIGRP-IPv6 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C802:23FF:FE34:1  Fa1/0                    14 00:05:30   18   200  0  15
```

IPv6 adjacencies should now form.

---

### Challenge 3: Tunnel Vision (IPv6 over GRE) — Solution

**Symptom:** The GRE tunnel between R1 and R6 works for IPv4, but EIGRP IPv6 routes from R6 are not appearing on R1. `show ipv6 route eigrp` on R1 shows no routes via the tunnel.

**Root Cause:** The tunnel interface does not have an IPv6 address configured, or the IPv6 address-family is not configured on the tunnel interface in the EIGRP process.

**Solution:**

Check the tunnel configuration on R6:

```bash
R6# show interface Tunnel8
Tunnel8 is up, line protocol is up
 Internet address is 172.16.16.2, 0x1
 (no IPv6 address assigned)
```

Add an IPv6 address to the tunnel:

```bash
R6# configure terminal
R6(config)# interface Tunnel8
R6(config-if)# ipv6 address 2001:DB8:ACAD:88::2/64
R6(config-if)# ipv6 enable
R6(config-if)# exit
R6(config)# end
R6# write memory
```

Verify EIGRP is advertising the tunnel in the IPv6 address-family. Ensure the network statement includes the tunnel subnet:

```bash
R6# show running-config | section "router eigrp"
router eigrp SKYNET_CORE
 address-family ipv6 autonomous-system 100
  ...
```

If there's no network statement for the tunnel, the tunnel won't be advertised. Add it if missing:

```bash
R6# configure terminal
R6(config)# router eigrp SKYNET_CORE
R6(config-router)# address-family ipv6 autonomous-system 100
R6(config-router-af)# network 2001:DB8:ACAD:88::/64
R6(config-router-af)# exit-address-family
R6(config)# end
R6# write memory
```

**Verification:**

```bash
R1# show ipv6 route eigrp
D   2001:DB8:ACAD:6::6/128 [90/2956800]
     via FE80::C806:16FF:FE00:0, Tunnel8

R1# ping ipv6 2001:DB8:ACAD:6::6
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2001:DB8:ACAD:6::6, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/24/32 ms
```

IPv6 routes from R6 should now appear in R1's routing table.
