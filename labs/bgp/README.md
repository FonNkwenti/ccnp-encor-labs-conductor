# **Chapter: BGP - Lab Topics Blueprint**

## **Chapter Overview**
BGP (Border Gateway Protocol) is the de facto standard for inter-domain routing and a critical component of the CCNP ENCOR Infrastructure domain. This chapter focuses on exam objective **3.2.c**: configuring and verifying eBGP between directly connected neighbors, including best path selection algorithm and neighbor relationships. Labs progress from basic eBGP peering through advanced topics like route reflectors, traffic engineering, and MP-BGP, using a realistic multi-AS enterprise/ISP topology.

## **Blueprint Coverage Matrix**
| Exam Objective | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 | L10 |
|----------------|----|----|----|----|----|----|----|----|----|-----|
| Configure eBGP neighbor relationships | ✅ | ✅ |    |    |    |    | ✅ |    |    |     |
| BGP best path selection algorithm |    | ✅ |    |    | ✅ |    | ✅ |    |    |     |
| Configure iBGP peering & next-hop-self |    |    | ✅ |    |    |    |    | ✅ |    |     |
| Implement BGP route filtering |    |    |    | ✅ | ✅ | ✅ |    |    | ✅ |     |
| Configure AS-path manipulation |    |    |    |    | ✅ |    | ✅ |    |    |     |
| Implement BGP communities & policy |    |    |    |    |    | ✅ | ✅ |    |    |     |
| Configure BGP multihoming & TE |    |    |    |    |    |    | ✅ |    |    |     |
| Implement route reflectors |    |    |    |    |    |    |    | ✅ |    |     |
| Configure BGP authentication & security |    |    |    |    |    |    |    |    | ✅ |     |
| Configure MP-BGP address families |    |    |    |    |    |    |    |    |    | ✅  |
| BGP-IGP redistribution |    |    |    |    |    |    |    |    |    | ✅  |

## **Topology Overview**

**Multi-AS Enterprise/ISP Triangle** — 3 core routers (all labs) + 4 optional devices (added progressively):

| Device | Platform | Role | AS | Loopback | Available |
|--------|----------|------|----|----------|-----------|
| R1 | c7200 | Enterprise Edge | 65001 | 172.16.1.1/32 | All labs |
| R2 | c7200 | ISP-A | 65002 | 172.16.2.2/32 | All labs |
| R3 | c7200 | ISP-B | 65003 | 172.16.3.3/32 | All labs |
| R4 | c3725 | Enterprise Internal | 65001 | 172.16.4.4/32 | Lab 3+ |
| R5 | c3725 | Downstream Customer | 65004 | 172.16.5.5/32 | Lab 6+ |
| R6 | c7200 | Enterprise Edge 2 | 65001 | 172.16.6.6/32 | Lab 8+ |
| R7 | c3725 | Remote Customer | 65005 | 172.16.7.7/32 | Lab 10 |

## **Progressive Lab Topics**

### **Foundation Labs (1-3)**
| Lab # | Title | Primary Focus | Key Objectives | Prerequisites | Est. Time |
|-------|-------|---------------|----------------|---------------|-----------|
| **1** | Basic eBGP Peering | Neighbor States | - Configure eBGP neighbors<br>- Network statement advertisement<br>- BGP table vs routing table | Basic IP routing, CLI | 45 min |
| **2** | BGP Path Selection Algorithm | Best Path | - Weight & Local Preference<br>- AS-Path length<br>- MED comparison | Lab 1 completion | 60 min |
| **3** | iBGP Fundamentals & Next-Hop-Self | Internal BGP | - iBGP peering via loopbacks<br>- Split-horizon rule<br>- next-hop-self configuration | Lab 2 completion | 60 min |

### **Intermediate Labs (4-6)**
| Lab # | Title | Primary Focus | Key Objectives | Prerequisites | Est. Time |
|-------|-------|---------------|----------------|---------------|-----------|
| **4** | Route Filtering with Prefix-Lists | Inbound/Outbound Filtering | - ip prefix-list configuration<br>- distribute-lists on BGP neighbors<br>- Soft reconfiguration | Lab 3 completion | 75 min |
| **5** | AS-Path Manipulation & Route-Maps | Traffic Influence | - AS-path access-lists<br>- Route-map match/set clauses<br>- AS-path prepending | Lab 4 completion | 75 min |
| **6** | BGP Communities & Policy Control | Policy Framework | - Standard/extended communities<br>- Well-known communities (no-export, no-advertise)<br>- Community-based route-maps | Lab 5 completion | 75 min |

### **Advanced Labs (7-10)**
| Lab # | Title | Primary Focus | Key Objectives | Prerequisites | Est. Time |
|-------|-------|---------------|----------------|---------------|-----------|
| **7** | Multihoming & Traffic Engineering | Dual-Homed Design | - Outbound TE with Local Pref<br>- Inbound TE with AS-path prepend/MED<br>- Conditional default origination | Lab 6 completion | 90 min |
| **8** | Route Reflectors & iBGP Scaling | iBGP Scalability | - Route reflector configuration<br>- Cluster-id & originator-id<br>- Full-mesh elimination | Lab 7 completion | 90 min |
| **9** | BGP Authentication & Security | Session Hardening | - MD5 authentication<br>- TTL Security (GTSM)<br>- Maximum-prefix limits | Lab 8 completion | 75 min |
| **10** | MP-BGP & Enterprise Integration | Dual-Stack & Redistribution | - IPv4/IPv6 address families<br>- BGP-IGP redistribution<br>- End-to-end enterprise connectivity | Lab 9 completion | 120 min |

## **Skill Progression Path**
```
eBGP Peering → Path Selection → iBGP Fundamentals → Route Filtering → AS-Path Manipulation → Communities & Policy → Multihoming & TE → Route Reflectors → Authentication & Security → MP-BGP & Integration
```

## **Cross-Chapter Dependencies**
- **Prerequisite**: IP addressing, subnetting, basic routing concepts, IGP familiarity
- **Shared with EIGRP Chapter**: Route filtering techniques, redistribution concepts
- **Shared with OSPF Chapter**: IGP underlying reachability for iBGP next-hops, redistribution
- **Shared with Security Chapter**: Authentication methods (MD5), TTL security
