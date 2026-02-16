---
name: lab-workbook-creator
description: Creates detailed lab workbooks and automation scripts for loading initial configs into GNS3 routers via Netmiko telnet.
---

# Lab Workbook Creator Skill

## Purpose
This skill converts a high-level lab topic into a detailed student workbook and an automated setup script. It enforces a high-quality standard that prioritizes theoretical context, practical copy-pasteable configurations, and automation for environment readiness.

## Context-Aware Generation
This skill reads from the chapter's **baseline.yaml** to ensure consistency:
- Uses the defined topology and IP addressing.
- Only includes devices listed for this lab number.
- Previous lab's solutions become this lab's initial-configs.

## Output Structure
The output will be a comprehensive set of files:
1.  **workbook.md** - Student workbook with concepts, topology, cabling, and verification.
2.  **initial-configs/** - Starting configs.
3.  **solutions/** - Complete configs.
4.  **topology.drawio** - Visual diagram. **Must follow the drawio style guide** (see `.agent/skills/drawio/SKILL.md` Section 4).
5.  **setup_lab.py** - (NEW) Python automation script to load initial-configs via Netmiko.

## Topology Diagram Requirements
When generating `topology.drawio`, strictly follow the **Visual Style Guide** in `.agent/skills/drawio/SKILL.md`:
- **White connection lines** (`strokeColor=#FFFFFF`), never black.
- **Device labels** positioned to the **left** of router icons.
- **IP last octet labels** (`.1`, `.2`) placed near each router's interface endpoint.
- **Title** at the top center of the canvas.
- **Legend box** (black fill `#000000`, white text `#FFFFFF`) at the bottom-right.
- Use `generate_topo.py` when possible, or hand-craft XML following the reference snippets in the style guide.

## Automation Script Requirements (setup_lab.py)
The script must:
1.  Use `netmiko` with `device_type='cisco_ios_telnet'` to connect to the console ports defined in `baseline.yaml` or the workbook's Console Access Table.
2.  Loop through each active router in the lab.
3.  Load the corresponding `.cfg` file from `initial-configs/`.
4.  Provide a progress bar or clear logging for each device.
5.  Let Netmiko handle IOS CLI mode transitions automatically.

## Prompt Template

```text
You are a CCNP ENCOR lab developer. Create a detailed lab workbook and setup script for:

**LAB NUMBER:** [N]
**CHAPTER:** [Technology]
**BASELINE FILE:** [Path to baseline.yaml]
**PREVIOUS LAB:** [Path to solutions/ or "none"]

**CONTEXT REQUIREMENTS:**
1. Read baseline.yaml for:
   - Active devices, IPs, and Console Ports (e.g., 5001, 5002).
   - Lab objectives and links.
2. Generate all standard workbook sections.
3. **NEW: Generate setup_lab.py**
   - Implement a clean Python script using Netmiko (`device_type='cisco_ios_telnet'`) to push initial-configs.
   - Script should target localhost:[console_port].
   - Include a 'reset' logic: send 'erase startup-config', 'reload', or simply overwrite running-config.

**REQUIRED SECTIONS in workbook.md:**
1. Concepts & Skills Covered
2. Topology & Scenario
3. Hardware & Environment Specifications
4. Base Configuration
5. Lab Challenge: Core Implementation
6. Verification & Analysis
7. Verification Cheatsheet
8. **Troubleshooting Scenarios** (REQUIRED - minimum 3 scenarios)
9. **Solutions (Spoiler Alert!)** (REQUIRED - must cover ALL objectives)

### Solutions Section Requirements:

1. **Complete Coverage**: You MUST provide a step-by-step configuration solution for EVERY objective listed in the "Lab Challenge" section.
2. **Collapsible Formatting**: Every solution (both configurations and verification commands) MUST be wrapped in a collapsible `<details>` block to prevent students from seeing the answer prematurely.
3. **Cisco CLI Blocks**: All configurations and command outputs must be inside standard Markdown code blocks (` ```bash `).

### Example Format:

```markdown
## 9. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Objective 1: [Objective Title]

<details>
<summary>Click to view [Device] Configuration</summary>

```bash
! [Device]
router ospf 1
 ...
```
</details>

### Objective 2: [Objective Title]

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On [Device]
show ip route ospf
```
</details>
```

10. Lab Completion Checklist
```

## Troubleshooting Scenarios Requirements

**MANDATORY:** Each workbook MUST include at least **3 troubleshooting scenarios** in a dedicated section before the Solutions section.

### Each Scenario Must Include:

1. **Scenario Number & Title**: Clear identification (e.g., "Scenario 1: AS Number Mismatch")

2. **Problem Statement**: 
   - Brief description of the symptoms observed by the student
   - What appears to be broken (e.g., "R2 cannot form adjacency with R1")
   - Any error messages or missing outputs

3. **Mission**:
   - Clear directive on what the student needs to accomplish
   - Specific troubleshooting steps to follow
   - Which devices to investigate

4. **Success Criteria / Acceptance Criteria**:
   - Measurable outcomes that prove the issue is resolved
   - Specific commands and their expected outputs
   - Performance or connectivity tests to validate the fix

5. **Solution** (with Spoiler Protection):
   - Use a collapsible section or clear spoiler warning
   - Provide the exact configuration fix required
   - Explain WHY the misconfiguration caused the problem
   - Include verification commands showing the resolved state

### Scenario Categories to Include:

Target common misconfigurations such as:
- **Protocol Parameter Mismatches**: AS numbers, K-values, authentication keys, timers
- **Interface Issues**: Shutdown interfaces, passive interface misconfigurations, wrong IP addresses
- **Network Advertisement Errors**: Missing network statements, wrong wildcard masks, route filtering
- **Authentication Problems**: Mismatched keys, incorrect key-chains, missing authentication
- **Redistribution Issues**: Missing redistributions, wrong metrics, route loops

### Example Format:

```markdown
## 8. Troubleshooting Scenarios

> 🔧 **Practice Makes Perfect**: These scenarios test your ability to diagnose and resolve common EIGRP misconfigurations. Try to solve them WITHOUT looking at the solutions first!

### Scenario 1: Autonomous System Mismatch

**Problem Statement:**
After a recent configuration change, R2 is no longer forming an adjacency with R1. The output of `show ip eigrp neighbors` on R1 shows no neighbor on Fa1/0. R2's configuration shows `router eigrp 200` instead of the expected AS 100.

**Mission:**
1. Identify why the adjacency failed using appropriate debug or show commands
2. Correct the misconfiguration to align with the design requirements (AS 100)
3. Verify that the adjacency is re-established
4. Confirm that routes are being exchanged properly

**Success Criteria:**
- [ ] `show ip eigrp neighbors` on R1 displays R2 as a neighbor on Fa1/0
- [ ] `show ip route eigrp` on R1 shows routes learned from R2
- [ ] End-to-end ping from R1's Loopback0 to R2's Loopback0 succeeds

**Solution:**

<details>
<summary>⚠️ SPOILER ALERT - Click to reveal solution</summary>

**Root Cause:** EIGRP routers only form adjacencies when they are configured with matching Autonomous System numbers. R2 was configured with AS 200 while R1 uses AS 100.

**Fix:**
```bash
R2# configure terminal
R2(config)# no router eigrp 200
R2(config)# router eigrp 100
R2(config-router)# eigrp router-id 2.2.2.2
R2(config-router)# network 2.2.2.2 0.0.0.0
R2(config-router)# network 10.0.12.0 0.0.0.3
R2(config-router)# network 10.0.23.0 0.0.0.3
R2(config-router)# passive-interface Loopback0
R2(config-router)# no auto-summary
R2(config-router)# end
```

**Verification:**
```bash
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:00:12   25   200  0  3
```
</details>

### Scenario 2: [Next scenario...]
```

**Console Access Table** must include: | Device | Port | Connection Command |

---

## Fault Injection Integration

After generating the workbook with troubleshooting scenarios, the **fault-injector** skill should be invoked to create automated fault injection scripts.

### Automatic Integration
When generating a complete lab, the workflow should be:
1. Generate workbook.md with troubleshooting scenarios
2. Invoke the `fault-injector` skill
3. Fault-injector reads the workbook and console access table
4. Generates Python scripts in `scripts/fault-injection/` directory
5. Updates workbook with instructions for running the scripts

### Fault-Injector Outputs
The fault-injector skill creates:
- `scripts/fault-injection/inject_scenario_01.py` - First fault
- `scripts/fault-injection/inject_scenario_02.py` - Second fault
- `scripts/fault-injection/inject_scenario_03.py` - Third fault
- `scripts/fault-injection/apply_solution.py` - Restore all devices
- `scripts/fault-injection/README.md` - Usage instructions

### Workbook Updates
Each troubleshooting scenario should include a subsection:

```markdown
#### Automated Fault Injection

To automatically inject this fault into your lab environment:

\`\`\`bash
cd scripts/fault-injection
python3 inject_scenario_01.py
\`\`\`

To restore the correct configuration after troubleshooting:

\`\`\`bash
python3 apply_solution.py
\`\`\`
```

### Additional Workbook Section
Add a new section before "Lab Completion Checklist":

```markdown
## 11. Automated Fault Injection (Optional)

This lab includes automated scripts to inject troubleshooting scenarios into your running GNS3 environment.

**Prerequisites**:
- GNS3 project must be running
- All devices accessible via console ports
- Python 3.x installed

**Quick Start**:
\`\`\`bash
cd scripts/fault-injection
python3 inject_scenario_01.py  # Inject first fault
python3 apply_solution.py      # Restore configuration
\`\`\`

See `scripts/fault-injection/README.md` for detailed usage instructions.
```
