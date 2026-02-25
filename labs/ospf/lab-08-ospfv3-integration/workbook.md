# Lab 08: OSPFv3 Integration
## Skynet Global: Global Dual-Stack Consolidation

### Scenario
Skynet Global is transitioning its entire infrastructure to support both IPv4 and IPv6 protocols simultaneously. As the lead network architect, you have been tasked with migrating the existing OSPFv2 deployment to **OSPFv3**. 

OSPFv3 is uniquely capable of supporting both IPv4 and IPv6 through **Address Families**. Your goal is to establish a unified dual-stack routing domain that provides seamless connectivity for both address spaces across the backbone and branch segments.

### Objectives
1. **IPv6 Foundation**: Enable IPv6 unicast routing across all routers and configure global unicast addresses on all relevant interfaces.
2. **OSPFv3 Migration**: Transition the core backbone (R1, R2, R3) and the new Border Node (R6) to OSPFv3.
3. **Dual-Stack Adjacencies**: Establish OSPFv3 neighbor adjacencies that carry both IPv4 and IPv6 routing information over the same physical links.
4. **Address Family Support**: Configure the OSPFv3 process to support the `ipv4 unicast` and `ipv6 unicast` address families.
5. **Multi-Area Verification**: Ensure that inter-area routing (Area 0 and Area 1) functions correctly for both address families.

---

### Hardware Specifications
| Device | Role | Platform | Image |
|--------|------|----------|-------|
| R1 | Hub/ABR | c7200 | IOS 15.x |
| R2 | Backbone | c7200 | IOS 15.x |
| R3 | Branch | c7200 | IOS 15.x |
| R6 | Dual-Stack Border | c7200 | IOS 15.x |

#### Cabling & Connectivity
| Local Interface | Local Device | Remote Device | Remote Interface | IPv4 Subnet | IPv6 Subnet |
|-----------------|--------------|---------------|------------------|-------------|-------------|
| Fa1/0 | R1 | R2 | Fa0/0 | 10.12.0.0/30 | 2001:DB8:12::/64 |
| Fa1/1 | R1 | R3 | Fa1/0 | 10.13.0.0/30 | 2001:DB8:13::/64 |
| Gi3/0 | R1 | R6 | Gi3/0 | 10.16.0.0/30 | 2001:DB8:16::/64 |
| Fa1/0 | R2 | R3 | Fa0/0 | 10.23.0.0/30 | 2001:DB8:23::/64 |

---

### Challenge Tasks

#### Task 1: OSPFv3 Process and Router-ID
- Initialize the OSPFv3 process `1` on all routers.
- Manually configure a **Router-ID** for each device (e.g., R1 = 10.1.1.1). Note that OSPFv3 still uses a 32-bit value for the Router-ID even in IPv6-only environments.
- **Verification**: `show ospfv3` should display the process and configured ID.

#### Task 2: Address Family Configuration
- Inside the OSPFv3 process, enable support for the `ipv4 unicast` and `ipv6 unicast` address families.
- Configure the `auto-cost reference-bandwidth 1000` under each address family to maintain consistent metric calculation.
- **Verification**: `show ospfv3 address-family` (if available) or check running-config.

#### Task 3: Interface Activation
- Enable OSPFv3 on the physical and loopback interfaces using the `ospfv3 <process> <af> area <area>` command.
- Do NOT use the legacy OSPFv2 `network` statements or the `ipv6 ospf` command.
- Ensure the R1-R2 and R1-R3 links are in **Area 0**, and the R2-R3 link is in **Area 1**.
- **Verification**: `show ospfv3 neighbor` should show adjacencies for both IPv4 and IPv6.

#### Task 4: Dual-Stack Verification
- Verify that both IPv4 and IPv6 routing tables contain routes to all other routers' loopbacks.
- **Verification**: `show ip route ospf` and `show ipv6 route ospf`.

---

### Verification Cheatsheet
| Check | Command |
|-------|---------|
| OSPFv3 Neighbors | `show ospfv3 neighbor` |
| OSPFv3 Interface | `show ospfv3 interface <intf>` |
| IPv4 Routing Table | `show ip route ospf` |
| IPv6 Routing Table | `show ipv6 route ospf` |
| OSPFv3 Database | `show ospfv3 database` |

---

### Solutions
<details>
<summary>Click to view R1 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface Loopback0
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
!
router ospfv3 1
 router-id 10.1.1.1
 !
 address-family ipv4 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
 !
 address-family ipv6 unicast
  auto-cost reference-bandwidth 1000
 exit-address-family
```
</details>

<details>
<summary>Click to view R6 Interface Config</summary>

```bash
interface GigabitEthernet3/0
 ospfv3 1 ipv4 area 0
 ospfv3 1 ipv6 area 0
```
</details>
