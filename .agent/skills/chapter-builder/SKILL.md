---
name: chapter-builder
description: Orchestrates generation of a complete CCNP ENCOR lab chapter, chaining initial-configs from each lab's solutions/ into the next and maintaining topology consistency from baseline.yaml. Use when asked to "generate all labs", "build the EIGRP chapter", "create labs 1 through 9", "rebuild the chapter with chaining", or "run the full chapter builder for [technology]".
metadata:
  author: CCNP ENCOR Labs Conductor
  version: 2.0.0
  category: workflow-automation
  tags: [ccnp, encor, gns3, cisco, chapter, lab-generation, chaining]
---

# Chapter Builder Skill

## Purpose
This skill orchestrates the generation of an **entire chapter** with proper lab continuity. It ensures:
- All labs share consistent topology from baseline.yaml
- Each lab builds on the previous lab's solution configs
- Device additions are handled seamlessly

## When to Use
Use this skill when you need to generate **multiple labs at once** or regenerate a chapter with proper chaining.

## Workflow

```
1. Read baseline.yaml for chapter
2. Generate Lab 01 (foundation)
   - initial-configs/ = base IP from baseline
   - solutions/ = completed config
3. For each subsequent lab (N = 2, 3, ...):
   - initial-configs/ = copy of Lab (N-1) solutions/
   - Add new devices if labs[N].devices includes them
   - solutions/ = completed config
4. Verify all labs chain correctly
```

## Usage

```text
Generate all labs for [CHAPTER] chapter.

**CHAPTER:** [e.g., EIGRP, OSPF]
**CHAPTER PATH:** labs/[chapter]/
**LABS TO GENERATE:** [all | 1-3 | 5-9]

**WORKFLOW:**
1. Load baseline.yaml
2. For each lab number:
   a. Identify active devices from labs[N].devices
   b. Get initial-configs:
      - Lab 01: Generate from baseline core_topology
      - Lab N: Copy from Lab (N-1) solutions/
   c. Use lab-workbook-creator skill to generate:
      - workbook.md
      - initial-configs/
      - solutions/
      - topology.drawio
   d. Verify solutions contain all required configs
3. Post-generation validation:
   - Confirm IP consistency across all labs
   - Verify config chaining is correct
```

## Chaining Rules

| Lab | initial-configs source | New devices |
|-----|------------------------|-------------|
| 01 | baseline core_topology (IP only) | R1, R2, R3 |
| 02 | Lab 01 solutions/ | None |
| 03 | Lab 02 solutions/ | + R7 |
| 04 | Lab 03 solutions/ | + R5 |
| ... | ... | ... |

## Topology Diagram Requirements
All generated `topology.drawio` files **must** follow the Visual Style Guide in `.agent/skills/drawio/SKILL.md` Section 4:
- White connection lines (`strokeColor=#FFFFFF`), never black.
- Device labels to the left of icons.
- IP last octet labels (`.1`, `.2`) near each router interface.
- Title at top center, legend box (black fill, white text) at bottom-right.

Use `.agent/skills/drawio/scripts/generate_topo.py` for automated generation.

## Validation Checklist

After generating labs, verify:
- [ ] All devices use IPs from baseline.yaml
- [ ] Lab N initial-configs match Lab (N-1) solutions
- [ ] New devices are only added when declared
- [ ] No configs are removed between labs
- [ ] topology.drawio shows correct devices per lab
- [ ] topology.drawio follows the drawio Visual Style Guide (white links, left labels, IP octets, legend)

## Example Invocation

```text
Use the chapter-builder skill to generate all EIGRP labs.

Chapter path: labs/eigrp/
Generate: all (labs 1-9)

Follow the workflow:
1. Read labs/eigrp/baseline.yaml
2. Generate each lab using lab-workbook-creator
3. Ensure proper chaining between labs
```
