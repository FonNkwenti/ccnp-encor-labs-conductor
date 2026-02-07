---
name: lab-workbook-creator
description: Creates detailed, step-by-step lab workbooks for individual topics within a chapter, including topology, configuration, and verification.
---

# Lab Workbook Creator Skill

## Purpose
This skill converts a high-level lab topic into a detailed student workbook and instructor guide. It enforces a high-quality standard ("DeepSeek Standard") that prioritizes theoretical context, practical copy-pasteable configurations, structured verification methodology, and visual diagrams.

## Context-Aware Generation
This skill reads from the chapter's **baseline.yaml** to ensure consistency:
- Uses the defined topology and IP addressing
- Only includes devices listed for this lab number
- Previous lab's solutions become this lab's initial-configs

## Usage
Provide the following inputs to the agent:
1.  **Lab Number**: Sequence number (e.g., 3)
2.  **Chapter Path**: Path to chapter folder (contains baseline.yaml)
3.  **Previous Lab Path**: Path to previous lab's solutions/ folder (or null for Lab 01)

## Output Structure
The output will be a comprehensive set of files:
1.  **workbook.md** - All-in-one student workbook with:
    - Concepts & Skills Covered
    - Topology & Scenario (ASCII + narrative)
    - Hardware Specifications (from gns3 skill)
    - Base Configuration (COPY-PASTEABLE)
    - Configuration Tasks with Theory sections
    - Verification & Analysis Table
    - Troubleshooting Challenge
    - Completion Checklist
2.  **initial-configs/** - Starting configs (= previous lab solutions, or base for Lab 01)
3.  **solutions/** - Complete configs after all tasks
4.  **topology.drawio** - Visual diagram

## Continuity Rules

### For Lab 01 (Foundation):
```
initial-configs/ = Base IP config only (from baseline.yaml)
solutions/ = Config after completing all tasks
```

### For Lab N (N > 1):
```
initial-configs/ = Copy of Lab (N-1) solutions/
solutions/ = Config after completing all tasks
```

> [!IMPORTANT]
> **Never change existing IPs or interfaces** unless the lab objective requires it.
> The student's GNS3 project persists across labs - configs must be additive.

## Reading baseline.yaml

```python
# Pseudo-code for determining active devices
import yaml

baseline = yaml.load('baseline.yaml')
lab_number = 3  # Current lab

# Find lab definition
lab = next(l for l in baseline['labs'] if l['number'] == lab_number)
active_devices = lab['devices']  # e.g., [R1, R2, R3, R7]

# Get device details
for device_name in active_devices:
    # Check core first
    device = next((d for d in baseline['core_topology']['devices'] 
                   if d['name'] == device_name), None)
    if not device:
        # Check optional
        device = next((d for d in baseline['optional_devices'] 
                       if d['name'] == device_name), None)
    print(device)
```

## Prompt Template

```text
You are a CCNP ENCOR lab developer. Create a detailed lab workbook for:

**LAB NUMBER:** [N]
**CHAPTER:** [Technology]
**BASELINE FILE:** [Path to labs/[chapter]/baseline.yaml]
**PREVIOUS LAB:** [Path to labs/[chapter]/lab-(N-1)-*/solutions/ or "none" for Lab 01]

**CONTEXT REQUIREMENTS:**
1. Read baseline.yaml to get:
   - Active devices for this lab (from labs[N].devices)
   - Device IPs and interfaces (from core_topology + optional_devices)
   - Lab objectives (from labs[N].objectives)
2. If previous lab exists:
   - Copy solutions/ as this lab's initial-configs/
3. If Lab 01:
   - Generate base IP configs from baseline.yaml

**REQUIRED SECTIONS:**
1. Concepts & Skills Covered (from labs[N].objectives)

2. Topology & Scenario
   - ASCII diagram showing ONLY active devices
   - Narrative explaining the scenario

3. Hardware & Environment Specifications
   - Router Platform Table (from baseline.yaml device definitions)
   - Console Access Table
   - Cabling Table (from baseline.yaml links)

4. Base Configuration
   - For Lab 01: IP addressing only
   - For Lab N: Previous lab's solution configs

5. Configuration Tasks Workbook
   - **Task [N]: [Title]**
     - **Objective**: From labs[N].objectives
     - **Theory**: Explain the concept
     - **Step-by-Step**: Numbered commands

6. Verification & Analysis Table
   | Command | Expected Output | What it confirms |

7. Troubleshooting Challenge
   - Scenario, Symptoms, Root Cause, Fix

8. topology.drawio
   - Only active devices from this lab

**CONSTRAINTS:**
- **Hardware**: MUST use only c7200 or c3725 (per gns3 skill)
- **Consistency**: Use EXACT IPs from baseline.yaml
- **Additive Only**: Do not remove configs from previous lab
- **Theory Mandatory**: Each task needs explanation
```
