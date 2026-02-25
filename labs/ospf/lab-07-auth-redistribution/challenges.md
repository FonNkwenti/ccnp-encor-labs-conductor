# Lab 07: Challenges - OSPF Authentication & Redistribution

## Skynet Global: Advanced Security and Performance

### Challenge 1: The Invisible ASBR
On **R2**, when redistributing the partner's subnets, ensure the **Metric Value** is explicitly set to **100** for all routes, overriding the default OSPF value of 20.
- **Target**: R2.
- **Requirement**: Apply the metric value within the same route-map used for types.
- **Verification**: `show ip route ospf` on R3 should show the seed metric as 100 for E2 and 100 + path cost for E1.

### Challenge 2: The Silent Partner
Suppose the partner's R5 router stops participating in OSPF/EIGRP gracefully. Ensure that the **R2** router still advertises a **Default Route** into the OSPF domain, but only if the partner's network `10.25.0.0/30` is still up and active.
- **Target**: R2.
- **Requirement**: Use the `default-information originate` command with conditional logic (like a route-map or prefix-list).
- **Verification**: `show ip route ospf` on R3 should see a `O*E2` route only when the R2-R5 link is active.

### Challenge 3: Security Hardening
In addition to SHA authentication, configure **R1** and **R3** (Area 0) to use **Area Authentication** globally for Area 0, even though some interfaces are manually configured with key-chains.
- **Target**: R1, R3.
- **Requirement**: Use the `area 0 authentication` command.
- **Verification**: Ensure that the manual key-chains on the interfaces still take precedence and the neighbors stay up.

### Challenge 4: Metric Precision
Modify the **Cost** of the link between R1 and R3 (Area 0) to be **5000**. Observe how this change affects the path selection for the partner's **E1** route versus the **E2** route.
- **Target**: R1, R3.
- **Requirement**: Use the `ip ospf cost` command.
- **Verification**: Trace the path on R3 for 172.16.5.1 and 172.16.105.1.
