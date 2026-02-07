---
name: chapter-topics-creator
description: Generates a comprehensive set of lab topics/scenarios for a specific CCNP ENCOR technology chapter, ensuring complete blueprint coverage and creating the baseline.yaml.
---

# Chapter Lab Topics Creator Skill

## Purpose
This skill generates a strategic plan for a lab chapter, ensuring all exam objectives are covered through a progressive series of labs. It also creates the **baseline.yaml** file that defines shared topology and enables lab continuity.

## Usage
Provide the following inputs to the agent:
1.  **Technology**: e.g., "OSPF", "BGP"
2.  **Blueprint Objectives**: List of specific exam topics to cover.
3.  **Target Count**: Number of labs desired (default: 8-10).

## Output Structure
The agent will generate:
1. **README.md** - Chapter overview with blueprint coverage matrix
2. **baseline.yaml** - Shared topology definition (see schema below)

## baseline.yaml Schema

```yaml
chapter: [TECHNOLOGY]
version: 1.0

# Core devices - present in ALL labs
core_topology:
  devices:
    - name: R1
      platform: c7200|c3725
      role: [descriptive role]
      loopback0: [IP/mask]
      console_port: 5001
  links:
    - id: L1
      source: [Device:Interface]
      target: [Device:Interface]
      subnet: [network/mask]

# Optional devices - added for specific labs
optional_devices:
  - name: R4
    platform: c7200|c3725
    role: [role]
    loopback0: [IP/mask]
    console_port: 5004
    available_from: [lab number]
    purpose: [why needed]

optional_links:
  - id: L3
    source: [Device:Interface]
    target: [Device:Interface]
    subnet: [network/mask]
    available_from: [lab number]

# Lab progression
labs:
  - number: 1
    title: [Lab Title]
    difficulty: Foundation|Intermediate|Advanced
    time_minutes: [45-120]
    devices: [R1, R2, R3]  # List active devices
    objectives:
      - [objective 1]
      - [objective 2]
  - number: 2
    title: [Lab Title]
    devices: [R1, R2, R3]
    extends: 1  # Builds on previous lab
```

## Continuity Rules
1. **Core devices** maintain consistent IPs across ALL labs
2. **Optional devices** are pre-reserved with IPs but only activated when needed
3. **Labs declare which devices are active** - this determines GNS3 project scope
4. **Each lab extends the previous** - solutions become next lab's initial configs

## Prompt Template

```text
You are a CCNP ENCOR curriculum designer. Create a comprehensive lab topics blueprint for [TECHNOLOGY].

**TECHNOLOGY:** [e.g., OSPF, BGP, Network Security]
**EXAM OBJECTIVES:** [List from blueprint]
**NUMBER OF LABS:** [8-10]
**PROGRESSION:** Foundation → Intermediate → Advanced → Integration

**REQUIREMENTS:**
1. Cover ALL exam objectives
2. Progressive difficulty
3. Real-world scenarios
4. Time estimates (45-120 minutes per lab)
5. Clear skill progression path
6. Generate baseline.yaml with expandable topology

**TOPOLOGY GUIDELINES:**
- Core devices (3 minimum) for foundation labs
- Optional devices (up to 7 total) for advanced scenarios
- Pre-reserve IP addresses for all potential devices
- Each lab explicitly declares which devices are active

**OUTPUT FILES:**
1. README.md - Chapter overview and blueprint coverage
2. baseline.yaml - Topology definition following the schema above
```
