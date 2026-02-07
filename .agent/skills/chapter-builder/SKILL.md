---
name: chapter-builder
description: Orchestrates generation of an entire chapter with shared topology and progressive configs, ensuring lab continuity.
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

## Validation Checklist

After generating labs, verify:
- [ ] All devices use IPs from baseline.yaml
- [ ] Lab N initial-configs match Lab (N-1) solutions
- [ ] New devices are only added when declared
- [ ] No configs are removed between labs
- [ ] topology.drawio shows correct devices per lab

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
