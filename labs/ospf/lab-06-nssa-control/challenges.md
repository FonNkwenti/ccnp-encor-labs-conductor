# Lab 06: Challenges - OSPF NSSA & Route Control

## Skynet Global: Area 4 Optimization

### Challenge 1: The Invisible Node
Configure Area 4 as an **NSSA** but ensure that **R4** receives **NO** inter-area or external routes from the backbone (except for a default route).
- **Target**: R1, R4.
- **Requirement**: Use the most efficient OSPF area type for this.
- **Verification**: `show ip route ospf` on R4 should only show its connected subnets and a default route.

### Challenge 2: The Researcher's Secret
Inject the `172.16.4.0/24` subnet into OSPF from R4 as a **Type 7 LSA**. Ensure that the **Metric Type** is set to **Type 1** (E1 equivalent) instead of the default Type 2.
- **Target**: R4.
- **Requirement**: Use a route-map if necessary, or specify the metric-type directly in the redistribution command.
- **Verification**: `show ip route ospf` on R2 should show the route with metric increments per hop.

### Challenge 3: Precision Summarization
The backbone routers (R1, R2, R3) have many subnets in Area 0 and Area 1. Summarize all Area 1 subnets (`10.23.0.0/24`, etc.) into a single `/24` summary before advertising them into Area 0.
- **Target**: R1.
- **Requirement**: Prevent routing table bloat in the core.
- **Verification**: `show ip ospf database summary` on R2.

### Challenge 4: Translation Point Control
In a multi-ABR scenario (simulated), you might want to force a specific ABR to perform the NSSA translation.
- **Target**: R1.
- **Requirement**: Ensure R1 is the primary translator even if another ABR is added to Area 4.
- **Verification**: Use the `nssa` sub-command options to specify translation.
