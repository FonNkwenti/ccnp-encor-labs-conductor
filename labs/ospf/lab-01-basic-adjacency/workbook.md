# CCNP ENCOR OSPF Lab 01: Basic OSPF Adjacency
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure OSPFv2 router process and router-id
- Enable OSPF on interfaces using network statements
- Understand OSPF neighbor states (Down → Full)
- Verify DR/BDR election on broadcast segments
- Implement passive interfaces for loopbacks
- Interpret OSPF neighbor and LSDB output

---

## 2. Topology & Scenario

### ASCII Diagram
```
                         Area 0 (Backbone)
        ┌────────────────────────────────────────────┐
        │                                            │
        │     ┌─────────────────┐                    │
        │     │       R1        │                    │
        │     │   (Hub/ABR)     │                    │
        │     │ Lo0: 10.1.1.1   │                    │
        │     └───┬─────────┬───┘                    │
        │         │ Fa1/0   │ Fa1/1                  │
        │         │         │                        │
        │  10.12.0.1/30     10.13.0.1/30            │
        │         │              │                   │
        │  10.12.0.2/30     10.13.0.2/30            │
        │         │ Fa0/0        │ Fa0/1            │
        │    ┌────┴────┐    ┌────┴────┐             │
        │    │   R2    │    │   R3    │             │
        │    │Backbone │────│ Branch  │             │
        │    │10.2.2.2 │    │10.3.3.3 │             │
        │    └────┬────┘    └─────────┘             │
        │         │ Fa0/1                           │
        │         │                                  │
        │  10.23.0.1/30 ←→ 10.23.0.2/30 (R3:Fa0/0) │
        │                                            │
        └────────────────────────────────────────────┘
```

### Scenario Narrative
You are deploying OSPF in a new enterprise backbone. Three routers form a fully-meshed triangle in Area 0. Your goals are to establish full OSPF adjacency on all links and observe DR/BDR behavior on the broadcast segments.

### Device Role Table
| Device | Role | Platform | Loopback0 | OSPF Router-ID |
|--------|------|----------|-----------|----------------|
| R1 | Hub/ABR | c7200 | 10.1.1.1/32 | 10.1.1.1 |
| R2 | Backbone Router | c3725 | 10.2.2.2/32 | 10.2.2.2 |
| R3 | Branch Router | c3725 | 10.3.3.3/32 | 10.3.3.3 |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 6001 | `telnet localhost 6001` |
| R2 | 6002 | `telnet localhost 6002` |
| R3 | 6003 | `telnet localhost 6003` |

### Cabling Table
| Link ID | Source:Interface | Target:Interface | Subnet | Description |
|---------|------------------|------------------|--------|-------------|
| L1 | R1:Fa1/0 | R2:Fa0/0 | 10.12.0.0/30 | Backbone Link 1 |
| L2 | R2:Fa0/1 | R3:Fa0/0 | 10.23.0.0/30 | Branch Link |
| L3 | R1:Fa1/1 | R3:Fa0/1 | 10.13.0.0/30 | Backbone Link 2 |

---

## 4. Base Configuration

> ⚠️ **Apply these configurations BEFORE starting OSPF tasks**

### R1 (Hub/ABR)
```bash
enable
configure terminal
!
hostname R1
!
interface Loopback0
 ip address 10.1.1.1 255.255.255.255
 no shutdown
!
interface FastEthernet1/0
 description Link to R2
 ip address 10.12.0.1 255.255.255.252
 no shutdown
!
interface FastEthernet1/1
 description Link to R3
 ip address 10.13.0.1 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R2 (Backbone Router)
```bash
enable
configure terminal
!
hostname R2
!
interface Loopback0
 ip address 10.2.2.2 255.255.255.255
 no shutdown
!
interface FastEthernet0/0
 description Link to R1
 ip address 10.12.0.2 255.255.255.252
 no shutdown
!
interface FastEthernet0/1
 description Link to R3
 ip address 10.23.0.1 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R3 (Branch Router)
```bash
enable
configure terminal
!
hostname R3
!
interface Loopback0
 ip address 10.3.3.3 255.255.255.255
 no shutdown
!
interface FastEthernet0/0
 description Link to R2
 ip address 10.23.0.2 255.255.255.252
 no shutdown
!
interface FastEthernet0/1
 description Link to R1
 ip address 10.13.0.2 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### Pre-Lab Verification
```bash
! From R1:
ping 10.12.0.2
ping 10.13.0.2

! From R2:
ping 10.12.0.1
ping 10.23.0.2
```

---

## 5. Configuration Tasks Workbook

### Task 1: Enable OSPF Process and Router-ID

**Objective:** Configure OSPF process 1 on all routers with explicit router-IDs.

**Theory:**
OSPF uses a 32-bit Router-ID to uniquely identify each router in the OSPF domain. The Router-ID is selected in this priority order:
1. Manually configured `router-id` command
2. Highest IP on any loopback interface
3. Highest IP on any active interface

Best practice: Always set the router-id explicitly to avoid unpredictable behavior.

**Step-by-Step:**

**On R1:**
```bash
configure terminal
!
router ospf 1
 router-id 10.1.1.1
!
end
```

**On R2:**
```bash
configure terminal
!
router ospf 1
 router-id 10.2.2.2
!
end
```

**On R3:**
```bash
configure terminal
!
router ospf 1
 router-id 10.3.3.3
!
end
```

---

### Task 2: Advertise Networks into OSPF Area 0

**Objective:** Add all interfaces to OSPF Area 0 using network statements.

**Theory:**
The `network` command uses wildcard masks to match interfaces. When an interface's IP matches, OSPF:
- Sends Hello packets on that interface
- Advertises the network in LSAs
- Attempts to form adjacencies with neighbors

Area 0 is the backbone area - all other areas must connect to it.

**Step-by-Step:**

**On R1:**
```bash
configure terminal
!
router ospf 1
 network 10.1.1.1 0.0.0.0 area 0
 network 10.12.0.0 0.0.0.3 area 0
 network 10.13.0.0 0.0.0.3 area 0
 passive-interface Loopback0
!
end
```

**On R2:**
```bash
configure terminal
!
router ospf 1
 network 10.2.2.2 0.0.0.0 area 0
 network 10.12.0.0 0.0.0.3 area 0
 network 10.23.0.0 0.0.0.3 area 0
 passive-interface Loopback0
!
end
```

**On R3:**
```bash
configure terminal
!
router ospf 1
 network 10.3.3.3 0.0.0.0 area 0
 network 10.13.0.0 0.0.0.3 area 0
 network 10.23.0.0 0.0.0.3 area 0
 passive-interface Loopback0
!
end
```

---

### Task 3: Verify OSPF Adjacencies and DR/BDR Election

**Objective:** Confirm all neighbors are in FULL state and understand DR/BDR roles.

**Theory:**
On broadcast/multi-access networks, OSPF elects:
- **DR (Designated Router)**: Reduces LSA flooding; all routers sync with DR
- **BDR (Backup DR)**: Takes over if DR fails
- **DROTHER**: All other routers on the segment

Election is based on:
1. Highest OSPF priority (default 1, range 0-255)
2. Highest Router-ID (tiebreaker)

Note: Point-to-point links do NOT elect DR/BDR.

**Verification Commands:**
```bash
! On all routers
show ip ospf neighbor

! Check DR/BDR on specific interface
show ip ospf interface FastEthernet1/0

! View OSPF database
show ip ospf database
```

**Expected Output (R1):**
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.2.2.2          1   FULL/BDR        00:00:38    10.12.0.2       Fa1/0
10.3.3.3          1   FULL/BDR        00:00:35    10.13.0.2       Fa1/1
```

---

## 6. Verification & Analysis Table

| Command | Expected Output | What It Confirms |
|---------|----------------|------------------|
| `show ip ospf neighbor` | 2 neighbors in FULL state on each router | Adjacencies established |
| `show ip ospf interface brief` | All interfaces in Area 0 | Correct area assignment |
| `show ip route ospf` | O routes to other loopbacks | OSPF routes learned |
| `show ip ospf database` | Router LSAs for all 3 routers | LSDB synchronized |
| `ping 10.2.2.2 source 10.1.1.1` | 100% success | End-to-end reachability |
| `show ip protocols` | OSPF 1, Router ID correct | Process configuration |

---

## 7. Troubleshooting Challenge

### Scenario
After completing all tasks, R2's OSPF adjacencies suddenly drop. Users report connectivity loss.

### Symptoms
- `show ip ospf neighbor` on R1 shows no neighbor with R2
- R1 can still ping R2's directly connected interface (10.12.0.2)
- `show ip ospf interface Fa0/0` on R2 shows "No OSPF configuration"

### Diagnostic Commands
```bash
! On R2
show ip ospf interface brief
show run | section router ospf
show ip ospf
```

### Root Cause
Someone removed the `network 10.12.0.0 0.0.0.3 area 0` statement from R2's OSPF configuration.

### Fix
```bash
! On R2
configure terminal
router ospf 1
 network 10.12.0.0 0.0.0.3 area 0
end
```

### Verification
```bash
! Wait 10-30 seconds for adjacency
show ip ospf neighbor
! Should show R1 in FULL state
```

---

## 8. Lab Completion Checklist

- [ ] OSPF process 1 configured on all three routers
- [ ] Router-IDs set to loopback addresses (10.x.x.x)
- [ ] All physical links and loopbacks in Area 0
- [ ] Loopback0 is passive on all routers
- [ ] `show ip ospf neighbor` shows 2 FULL adjacencies per router
- [ ] DR/BDR election observed on each segment
- [ ] All loopback routes visible via `show ip route ospf`
- [ ] Troubleshooting challenge completed
