# Lab 07: OSPF Authentication & Redistribution
## Skynet Global: Secure Backbone & Partner Integration

### Scenario
The Skynet Global backbone is expanding, and security is now a top priority. To prevent unauthorized devices from participating in the OSPF process, you must implement **HMAC-SHA-256** authentication across the core backbone links (Area 0).

Additionally, a recent acquisition has brought a new partner network (**R5**) into the fold. R5 uses **EIGRP** internally. You are tasked with redistributing the partner's research subnets into the Skynet OSPF domain. To ensure correct path selection, you must demonstrate the difference between **External Type 1 (E1)** and **External Type 2 (E2)** metrics.

### Objectives
1. **Core Security**: Implement HMAC-SHA-256 authentication on the R1-R2 and R1-R3 links (Area 0).
2. **Legacy Security**: Implement MD5 authentication on the R2-R3 link (Area 1).
3. **Partner Integration**: Redistribute EIGRP routes from R5 into the OSPF domain on R2.
4. **Metric Manipulation**: 
    - Advertise the `172.16.5.0/24` subnet as **Type 1 (E1)**.
    - Advertise the `172.16.105.0/24` subnet as **Type 2 (E2)**.
5. **Path Verification**: Verify how internal routers (R3) see the different external route types and how metrics are calculated.

---

### Hardware Specifications
| Device | Role | Platform | Image |
|--------|------|----------|-------|
| R1 | Hub/ABR | c7200 | IOS 15.x |
| R2 | Backbone/ASBR | c7200 | IOS 15.x |
| R3 | Branch | c7200 | IOS 15.x |
| R5 | External Partner| c7200 | IOS 15.x |

#### Cabling & Connectivity
| Local Interface | Local Device | Remote Device | Remote Interface | Subnet |
|-----------------|--------------|---------------|------------------|--------|
| Fa1/0 | R1 | R2 | Fa0/0 | 10.12.0.0/30 |
| Fa1/1 | R1 | R3 | Fa1/0 | 10.13.0.0/30 |
| Fa1/0 | R2 | R3 | Fa0/0 | 10.23.0.0/30 |
| Fa1/1 | R2 | R5 | Fa0/0 | 10.25.0.0/30 |

---

### Challenge Tasks

#### Task 1: Backbone HMAC-SHA Authentication
- Create a key-chain named `OSPF_AUTH` with key ID `1` and a strong key-string.
- Set the cryptographic algorithm to `hmac-sha-256`.
- Apply this key-chain to the Area 0 interfaces on **R1**, **R2**, and **R3**.
- **Verification**: `show ip ospf interface` should show SHA authentication is enabled. OSPF adjacencies must remain in `FULL` state.

#### Task 2: Area 1 MD5 Authentication
- Configure **Area 1** (R2-R3 link) to use MD5 authentication.
- Enable authentication at the area level on R2 and R3.
- Specify the MD5 key on the interfaces connecting R2 and R3.
- **Verification**: Check `show ip ospf neighbor` to ensure the adjacency is up.

#### Task 3: Partner Redistribution
- On **R2**, configure an EIGRP process to neighbor with **R5**.
- Redistribute the EIGRP routes into OSPF.
- Use a **route-map** to distinguish between the two research subnets:
    - Subnet `172.16.5.0/24` must be redistributed as **Metric Type 1**.
    - Subnet `172.16.105.0/24` must be redistributed as **Metric Type 2**.
- **Verification**: `show ip ospf database external` on R1 and R3.

#### Task 4: Metric Analysis
- On **R3**, examine the routing table for the redistributed routes.
- Compare the metrics for the E1 vs E2 routes.
- **Verification**: Notice how the E1 metric increases as it traverses the network, while the E2 metric remains at the seed value (unless otherwise configured).

---

### Verification Cheatsheet
| Check | Command |
|-------|---------|
| OSPF Neighbors | `show ip ospf neighbor` |
| Interface Auth | `show ip ospf interface <intf>` |
| External Routes | `show ip route ospf | include E1|E2` |
| OSPF Database | `show ip ospf database external` |
| EIGRP Neighbors | `show ip eigrp neighbors` |

---

### Solutions
<details>
<summary>Click to view R1 Authentication Config</summary>

```bash
key chain OSPF_AUTH
 key 1
  key-string SkynetSecure123
  cryptographic-algorithm hmac-sha-256
!
interface FastEthernet1/0
 ip ospf authentication key-chain OSPF_AUTH
```
</details>

<details>
<summary>Click to view R2 Redistribution Config</summary>

```bash
route-map REDIST_EIGRP permit 10
 match ip address prefix-list PL_E1
 set metric-type type-1
!
router ospf 1
 redistribute eigrp 100 subnets route-map REDIST_EIGRP
```
</details>
