Generate all labs for a chapter with proper chaining and continuity: $ARGUMENTS

## Purpose
Orchestrate the generation of an entire chapter, ensuring all labs share consistent topology and each lab builds on the previous lab's solution configs.

## Workflow

1. **Read baseline.yaml** for the chapter at `labs/<chapter>/baseline.yaml`

2. **Generate labs sequentially:**
   - **Lab 01 (foundation):** `initial-configs/` = base IPs from baseline's `core_topology`
   - **Lab N (N > 1):** `initial-configs/` = copy of Lab (N-1)'s `solutions/`
   - Add new devices only when declared in `baseline.yaml` (`available_from` field)

3. **For each lab**, use the `/create-lab` workflow to generate:
   - `workbook.md` with all required sections
   - `initial-configs/` and `solutions/`
   - `topology.drawio` (only showing devices active in that lab)
   - `setup_lab.py`
   - Fault injection scripts
   - Tests

4. **Chaining rules:**
   | Lab | initial-configs source | New devices |
   |-----|------------------------|-------------|
   | 01 | baseline core_topology (IP only) | Core devices |
   | 02 | Lab 01 solutions/ | None (unless declared) |
   | 03 | Lab 02 solutions/ | + devices with available_from: 3 |
   | ... | ... | ... |

5. **Post-generation validation checklist:**
   - [ ] All devices use IPs from baseline.yaml
   - [ ] Lab N initial-configs match Lab (N-1) solutions
   - [ ] New devices are only added when declared
   - [ ] No configs are removed between labs
   - [ ] Each topology.drawio shows correct devices per lab
   - [ ] Each topology.drawio follows Draw.io Standards in CLAUDE.md
   - [ ] IP consistency across all labs

6. **Arguments format:** `<chapter> [lab-range]`
   - `eigrp` — generate all labs defined in baseline.yaml
   - `ospf 5-8` — generate only labs 5 through 8
   - `bgp 1-3` — generate first 3 labs
