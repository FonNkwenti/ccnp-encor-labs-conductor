# **Chapter: OSPF - Lab Topics Blueprint**

## **Chapter Overview**
OSPF (Open Shortest Path First) is a link-state routing protocol that is the industry standard for interior gateway routing in large-scale enterprise networks. This chapter covers the fundamental and advanced aspects of OSPFv2 (IPv4) and OSPFv3 (IPv6), including neighbor adjacency, area types, path selection, summarization, and redistribution.

## **Blueprint Coverage Matrix**
| Exam Objective | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 |
|----------------|----|----|----|----|----|----|----|----|
| OSPFv2/v3 Neighbor Adjacencies | ✅ |    |    |    |    |    |    | ✅ |
| Network Types (P2P, Broadcast) |    | ✅ |    |    |    |    |    |    |
| Path Selection (Cost, Ref BW)  |    |    | ✅ |    |    |    |    |    |
| Multi-Area OSPF Configuration  |    |    |    | ✅ |    |    |    |    |
| Stub, Totally Stubby Areas     |    |    |    |    | ✅ |    |    |    |
| NSSA Areas & Type 7 LSAs       |    |    |    |    |    | ✅ |    |    |
| Summarization & Filtering      |    |    |    |    |    | ✅ |    |    |
| Authentication & Redistribution|    |    |    |    |    |    | ✅ |    |
| OSPFv3 Dual-Stack              |    |    |    |    |    |    |    | ✅ |

## **Progressive Lab Topics**

### **Foundation Labs (1-3)**
| Lab # | Title | Primary Focus | Key Objectives | Est. Time |
|-------|-------|---------------|----------------|-----------|
| **1** | Basic OSPF Adjacency | Neighbor Discovery | • Enable OSPFv2 on interfaces<br>• Verify neighbor states (Full/DR/BDR)<br>• Router-ID assignment | 45 min |
| **2** | OSPF Network Types | Media Optimization | • P2P vs. Broadcast behavior<br>• DR/BDR election control<br>• Priority tuning | 60 min |
| **3** | Path Selection & Metrics | Cost Control | • Interface cost manual setting<br>• Reference bandwidth adjustment<br>• Equal-cost multi-path (ECMP) | 60 min |

### **Intermediate Labs (4-6)**
| Lab # | Title | Primary Focus | Key Objectives | Est. Time |
|-------|-------|---------------|----------------|-----------|
| **4** | Multi-Area OSPF | Hierarchical Design | • Inter-area routing<br>• ABR/ASBR roles<br>• LSA Type 1, 2, and 3 verification | 75 min |
| **5** | OSPF Special Area Types | LSDB Optimization | • Stub area configuration<br>• Totally Stubby Area (Cisco-proprietary)<br>• Default route injection | 75 min |
| **6** | NSSA & Route Control | Advanced Scenarios | • NSSA configuration<br>• Type 7 to Type 5 translation<br>• Inter-area summarization | 90 min |

### **Advanced Labs (7-8)**
| Lab # | Title | Primary Focus | Key Objectives | Est. Time |
|-------|-------|---------------|----------------|-----------|
| **7** | Security & Integration | Redistribution | • MD5/SHA authentication<br>• Redistribute EIGRP into OSPF<br>• External route types (E1/E2) | 90 min |
| **8** | OSPFv3 Integration | IPv6 Connectivity | • OSPFv3 for IPv4 and IPv6<br>• Multi-stack configuration<br>• Link-local address neighbor discovery | 120 min |

## **Skill Progression Path**
```
Area 0 Adjacency → Network Types → Cost Tuning → Multi-Area Hierarchy → Stub Areas → NSSA → Redistribution → OSPFv3 Dual-Stack
```

## **Cross-Chapter Dependencies**
- **Prerequisite**: EIGRP Chapter (for redistribution scenarios in Lab 7)
- **Shared with BGP Chapter**: Routing hierarchy concepts
- **Shared with Security Chapter**: Authentication mechanisms
