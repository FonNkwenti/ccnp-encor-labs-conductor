---
name: gns3
description: Interaction guide for GNS3 lab environment on Apple M1, focusing on host capabilities, supported nodes, and hardware templates.
---

# GNS3 Lab Skill (Apple M1)

## 1. Host Architecture & Constraints

This GNS3 environment runs on **Apple M1 (Silicon)** hardware.
- **Emulation Only:** Uses **Dynamips** for Cisco IOS.
- **No Virtualization:** Intel VT-x/VMware/VirtualBox VMs are **NOT supported**.
- **Images:** Strictly limited to `c7200` and `c3725` IOS images.

## 2. Hardware "Source of Truth" Templates

Use these tables as the strict reference for all lab generation.

### 2.1 Router Platform Definitions
| Platform | Role | RAM | IOS Image | Idle PC |
|----------|------|-----|-----------|---------|
| **c7200** | Core/Hub/Edge | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` | `0x60629004` |
| **c3725** | Branch/Spoke | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` | `0x60c09aa0` |

### 2.2 Slot Configurations
Define interfaces using these specific slots.

**c7200 Config:**
| Slot | Adapter | Description |
|------|---------|-------------|
| 0 | `C7200-IO-FE` | 1x FastEthernet (fa0/0) |
| 1 | `PA-2FE-TX` | 2x FastEthernet (fa1/0, fa1/1) |
| 2 | `PA-4T+` | 4x Serial Ports (s2/0 - s2/3) |
| 3 | `PA-GE` | 1x GigabitEthernet (gi3/0) |

**c3725 Config:**
| Slot | Adapter | Description |
|------|---------|-------------|
| 0 | `GT96100-FE` | 2x Onboard FastEthernet (fa0/0, fa0/1) |
| 1 | `NM-16ESW` | 16x Switch Ports (fa1/0 - fa1/15) - *Use for L2 Labs* |
| 2 | `NM-4T` | 4x Serial Ports (s2/0 - s2/3) |

### 2.3 Console Access
Standardize console ports to allow scriptable access.
_Base Port: 5000_

| Router | Console Port | Telnet Command |
|--------|--------------|----------------|
| R1 | 5001 | `telnet localhost 5001` |
| R2 | 5002 | `telnet localhost 5002` |
| R3 | 5003 | `telnet localhost 5003` |
| ... | ... | ... |

## 3. Supported Node Types (Non-IOS)
- **Unmanaged Switch**: Generic GNS3 switch for L2 connectivity.
- **VPCS**: Virtual PC Simulator for ping testing.

## 4. Design Rules for Lab Generation
1.  **No High-Speed Interfaces**: Do not use "100Gig" or "TenGig". Use "GigabitEthernet" (Slot 3 on c7200) or "FastEthernet".
2.  **No Incompatible Tech**: Do not include features requiring IOS-XR, NX-OS, or heavy containerization.
3.  **Physical Link Table**: Always define links explicitly.
    - Format: `Source Device:Intf <--> Target Device:Intf`
