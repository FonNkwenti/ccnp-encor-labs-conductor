# Lab 08: Challenges - OSPFv3 Integration

## Skynet Global: Advanced Dual-Stack Scenarios

### Challenge 1: The Instance Divide
By default, OSPFv3 uses **Instance ID 0** for standard operations. Configure the R1-R6 link to use **Instance ID 10** for the IPv6 address family while maintaining Instance ID 0 for IPv4.
- **Target**: R1, R6.
- **Requirement**: Neighbors must form correctly on the new instance.
- **Verification**: `show ospfv3 interface GigabitEthernet3/0` should show different Instance IDs per AF.

### Challenge 2: The Silent Loopback
Configure the Loopback0 on **R3** to be **Passive** in OSPFv3, but only for the **IPv4** address family. The IPv6 address family must remain active.
- **Target**: R3.
- **Requirement**: Use the `passive-interface` command under the specific address family sub-mode.
- **Verification**: `show ospfv3 ipv4 interface Loopback0` should show passive status.

### Challenge 3: External Integration
Redistribute the **Connected** subnets of **R6** (specifically Loopback100 if you create one) into OSPFv3.
- **Target**: R6.
- **Requirement**: Ensure the routes appear in both IPv4 and IPv6 routing tables of R1.
- **Verification**: `show ip route ospf` and `show ipv6 route ospf` on R1.

### Challenge 4: Metric Precision (OSPFv3)
In OSPFv3, the cost can be set per address family. On **R1**, set the cost of the link to **R2** to **10** for IPv4 and **20** for IPv6.
- **Target**: R1.
- **Requirement**: Use the `ospfv3 cost` command with address family specification.
- **Verification**: `show ospfv3 interface FastEthernet1/0` and verify metrics in routing tables.
