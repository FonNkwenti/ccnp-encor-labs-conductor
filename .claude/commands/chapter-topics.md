Generate a comprehensive lab topics blueprint and baseline topology for: $ARGUMENTS

## Purpose
Create the strategic plan for a new chapter, ensuring all exam objectives are covered through a progressive series of labs.

## Workflow

1. **Gather inputs:**
   - Technology chapter (e.g., OSPF, BGP, Security)
   - Relevant CCNP ENCOR 350-401 exam blueprint objectives
   - Target number of labs (default: 8-10)

2. **Design lab progression:**
   - Foundation → Intermediate → Advanced → Integration
   - Cover ALL relevant exam objectives
   - Real-world scenarios with time estimates (45-120 min per lab)
   - Clear skill progression path

3. **Generate `labs/<chapter>/baseline.yaml`** following this schema:
   ```yaml
   chapter: <TECHNOLOGY>
   version: 1.0
   core_topology:
     devices:
       - name: R1
         platform: c7200|c3725
         role: <descriptive role>
         loopback0: <IP/mask>
         console_port: 5001
     links:
       - id: L1
         source: <Device:Interface>
         target: <Device:Interface>
         subnet: <network/mask>
   optional_devices:
     - name: R4
       platform: c7200|c3725
       role: <role>
       loopback0: <IP/mask>
       console_port: 5004
       available_from: <lab number>
       purpose: <why needed>
   optional_links:
     - id: L3
       source: <Device:Interface>
       target: <Device:Interface>
       subnet: <network/mask>
       available_from: <lab number>
   labs:
     - number: 1
       title: <Lab Title>
       difficulty: Foundation|Intermediate|Advanced
       time_minutes: <45-120>
       devices: [R1, R2, R3]
       objectives:
         - <objective 1>
   ```

4. **Generate `labs/<chapter>/README.md`** with:
   - Chapter overview
   - Blueprint coverage matrix showing which labs cover which exam objectives
   - Lab progression table with difficulty levels

5. **Topology guidelines:**
   - Core devices (3 minimum) for foundation labs
   - Optional devices (up to 7 total) for advanced scenarios
   - Pre-reserve IP addresses for ALL potential devices
   - Each lab explicitly declares which devices are active
   - Follow GNS3 Constraints in CLAUDE.md (c7200/c3725 only)

6. **Continuity rules:**
   - Core devices maintain consistent IPs across ALL labs
   - Optional devices are pre-reserved with IPs but only activated when needed
   - Each lab extends the previous — solutions become next lab's initial configs
