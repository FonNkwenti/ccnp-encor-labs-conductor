# Diagnostic Command Reference

Quick-reference CLI commands for each OSI layer and protocol. Use these during Phase III: Diagnostic Execution.

## Interface & Physical Layer (L1/L2)

```
show interfaces [interface-id]
show ip interface brief
show interfaces status
show interfaces trunk
show cdp neighbors detail
show mac address-table
show vlan brief
show spanning-tree
```

## Routing & Layer 3

```
show ip route
show ip route [prefix]
show ip protocols
show ip ospf neighbor
show ip ospf interface [intf]
show ip ospf database
show ip eigrp neighbors
show ip eigrp topology
show ip bgp summary
show ip bgp [prefix]
```

## Access Control & NAT

```
show ip access-lists
show access-lists
show ip nat translations
show ip nat statistics
```

## System & Logging

```
show version
show inventory
show logging
show running-config
show startup-config
show running-config | section [keyword]
```

## Debug Commands (use with caution — can impact performance)

```
debug ip routing
debug ip ospf events
debug ip ospf hello
debug ip eigrp
debug ip bgp
debug ip packet
```

Always `undebug all` after use.

---

## Baseline Comparison Table Template

| Component | Normal Behavior | Current Observation | Status |
|-----------|----------------|---------------------|--------|
| Interface Gi0/1 | Up/Up | Up/Up | ✓ OK |
| OSPF neighbor | FULL state | DOWN | ✗ FAULT |
| Routing table | N routes | N routes | ✓ OK |

---

## File Locations

| Resource | Path |
|----------|------|
| Netmiko utilities | `labs/common/tools/lab_utils.py` |
| Fault injection utility | `labs/common/tools/fault_utils.py` |
| Lab workbook | `labs/<chapter>/lab-NN-<slug>/workbook.md` |
| Challenges | `labs/<chapter>/lab-NN-<slug>/challenges.md` |
| Initial configs | `labs/<chapter>/lab-NN-<slug>/initial-configs/` |
| Solution configs | `labs/<chapter>/lab-NN-<slug>/solutions/` |
| Chapter baseline | `labs/<chapter>/baseline.yaml` |

---

## Scenario → Methodology Quick Map

| Scenario | Methodology | Rationale |
|----------|-------------|-----------|
| Can ping but can't browse | Top-Down | L3 works, issue in upper layers |
| New router, no connectivity | Bottom-Up | Likely physical/basic config |
| Remote site can't reach HQ | Follow Traffic Path | Multi-hop WAN scenario |
| One router works, similar one doesn't | Compare Configurations | Reference device available |
| Unknown: "it's slow" or "not working" | Divide and Conquer | Default for unclear layer |
