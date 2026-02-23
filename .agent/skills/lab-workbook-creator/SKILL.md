---
name: lab-workbook-creator
description: Generates the complete DeepSeek Standard lab artifact set for CCNP ENCOR GNS3 labs: workbook.md, initial-configs/, solutions/, topology.drawio, and setup_lab.py automation script via Netmiko telnet. Use when asked to "create a lab", "build lab N", "generate a workbook", "make a lab for [topic]", "build the lab files", or "generate the CCNP ENCOR lab for [chapter]".
metadata:
  author: CCNP ENCOR Labs Conductor
  version: 2.0.0
  category: document-creation
  tags: [ccnp, encor, gns3, cisco, lab, workbook, netmiko, dynamips]
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
8. **Solutions (Spoiler Alert!)** (REQUIRED - must cover ALL objectives)

### Solutions Section Requirements:

1. **Complete Coverage**: You MUST provide a step-by-step configuration solution for EVERY objective listed in the "Lab Challenge" section.
2. **Collapsible Formatting**: Every solution (both configurations and verification commands) MUST be wrapped in a collapsible `<details>` block to prevent students from seeing the answer prematurely.
3. **Cisco CLI Blocks**: All configurations and command outputs must be inside standard Markdown code blocks (` ```bash `).

### Example Format:

```markdown
## 8. Solutions (Spoiler Alert!)

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

9. Lab Completion Checklist
```

**Console Access Table** must include: | Device | Port | Connection Command |

---

## Fault Injection Integration

After generating the workbook, the **fault-injector** skill should be invoked to create automated fault injection scripts based on `challenges.md`.

### Automatic Integration
When generating a complete lab, the workflow should be:
1. Generate workbook.md
2. Invoke the `fault-injector` skill
3. Fault-injector reads `challenges.md` and the console access table
4. Generates Python scripts in `scripts/fault-injection/` directory
5. Updates workbook with instructions for running the scripts

### Fault-Injector Outputs
The fault-injector skill creates:
- `scripts/fault-injection/inject_scenario_01.py` - First fault
- `scripts/fault-injection/inject_scenario_02.py` - Second fault
- `scripts/fault-injection/inject_scenario_03.py` - Third fault
- `scripts/fault-injection/apply_solution.py` - Restore all devices
- `scripts/fault-injection/README.md` - Usage instructions

### Additional Workbook Section
Add a new section before "Lab Completion Checklist":

```markdown
## 10. Automated Fault Injection (Optional)

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
