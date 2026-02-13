# **Chapter: EIGRP - Lab Topics Blueprint**

## **Chapter Overview**
EIGRP (Enhanced Interior Gateway Routing Protocol) is a Cisco-proprietary advanced distance vector routing protocol that forms a critical part of the CCNP ENCOR Infrastructure domain. This chapter covers configuration, optimization, troubleshooting, and migration scenarios for EIGRP in enterprise networks, including both IPv4 and IPv6 implementations.

## **Blueprint Coverage Matrix**
| Exam Objective | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 | L10 |
|----------------|----|----|----|----|----|----|----|----|----|-----|
| Configure EIGRP neighbor adjacencies | ✅ | ✅ |    |    |    |    |    |    |    |     |
| Implement EIGRP for IPv4/IPv6 | ✅ |    |    |    |    |    |    |    | ✅ |     |
| Configure EIGRP path selection |    | ✅ |    |    |    |    |    |    |    |     |
| Implement route summarization |    |    | ✅ |    |    |    |    |    |    |     |
| Configure EIGRP authentication |    |    |    | ✅ |    |    |    |    |    | ✅  |
| Implement EIGRP stub features |    |    |    | ✅ |    |    |    |    |    |     |
| Configure EIGRP over WAN/VPN |    |    |    |    |    |    |    | ✅ |    |     |
| Troubleshoot EIGRP operations |    |    |    |    |    |    | ✅ |    |    |     |
| Implement filtering/passive interfaces |    |    |    |    | ✅ |    |    |    |    |     |
| Dual-stack EIGRP migration |    |    |    |    |    |    |    |    | ✅ |     |
| EIGRP Named Mode / Wide metrics |    |    |    |    |    |    |    |    |    | ✅  |

## **Progressive Lab Topics**

### **Foundation Labs (1-3)**
| Lab # | Title | Primary Focus | Key Objectives | Prerequisites | Est. Time |
|-------|-------|---------------|----------------|---------------|-----------|
| **1** | Basic EIGRP Adjacency | Neighbor Discovery | • Configure EIGRP AS<br>• Verify neighbor table<br>• Passive interfaces | Basic IP routing, CLI | 45 min |
| **2** | Path Selection & Metrics | DUAL Algorithm | • Metric calculation<br>• Successor/Feasible Successor<br>• Variance & load balancing | Lab 1 completion | 60 min |
| **3** | Route Summarization | Table Optimization | • Manual summarization<br>• Query boundaries<br>• Route filtering | Lab 2 completion | 60 min |

### **Intermediate Labs (4-6)**
| Lab # | Title | Primary Focus | Key Objectives | Prerequisites | Est. Time |
|-------|-------|---------------|----------------|---------------|-----------|
| **4** | EIGRP Stub & WAN Opt | Network Stability | • Stub configuration<br>• WAN bandwidth control<br>• Timer adjustments | Lab 3 completion | 75 min |
| **5** | Authentication & Advanced | Security Features | • MD5 auth<br>• Route tagging<br>• Offset lists | Lab 4 completion | 75 min |
| **6** | Filtering & Control | Traffic Engineering | • Distribute-lists<br>• Passive interfaces<br>• Route-maps | Lab 5 completion | 60 min |

### **Advanced Labs (7-10)**
| Lab # | Title | Primary Focus | Key Objectives | Prerequisites | Est. Time |
|-------|-------|---------------|----------------|---------------|-----------|
| **7** | Active Process Simulation | Troubleshooting | • SIA conditions<br>• Query propagation<br>• Debug methodology | Lab 6 completion | 90 min |
| **8** | EIGRP over VPN Tunnel | Secure Transport | • GRE/IPsec integration<br>• Tunnel metrics<br>• Recursive routing | VPN fundamentals | 90 min |
| **9** | Dual-Stack EIGRP Migration | IPv6 Integration | • IPv6 EIGRP configuration<br>• Dual-stack verification<br>• Migration strategy | All previous labs | 120 min |
| **10** | Named Mode Advanced Features | Named Mode Hardening | • SHA-256 auth (af-interface)<br>• Wide metrics (64-bit)<br>• Per-interface tuning | Lab 9 completion | 75 min |

## **Skill Progression Path**
```
Basic Adjacency → Metric Calculation → Route Optimization → Network Stability → Security → Traffic Control → Advanced Troubleshooting → VPN Integration → Dual-Stack Migration → Named Mode Hardening
```

## **Cross-Chapter Dependencies**
- **Prerequisite**: IP addressing, subnetting, basic routing concepts
- **Shared with OSPF Chapter**: Route redistribution concepts
- **Shared with BGP Chapter**: Route filtering techniques
- **Shared with Security Chapter**: Authentication methods
