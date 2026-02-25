# Implementation Plan: Implement OSPF Lab 08

## Phase 1: Lab Design & Topology
- [x] Review `labs/ospf/baseline.yaml` (v1.1) for Lab 08 requirements.
- [x] Task: Confirm R1, R2, R3, R6 as `c7200` platforms for OSPFv3 AF support.
- [x] Task: Design Skynet Global scenario: "Global Dual-Stack Consolidation."
- [x] Task: Propose manual verification plan for Phase 1.

## Phase 2: Implementation & Artifact Generation
- [x] Task: Initialize directory `labs/ospf/lab-08-ospfv3-integration/`.
- [x] Task: Generate `topology.drawio` with `generate_topo.py`.
- [x] Task: Create `initial-configs/` by chaining from OSPF Lab 07 solutions (adjusted for R6 addition and R5 removal).
- [x] Task: Implement `solutions/` including OSPFv3 Address Families.
- [x] Task: Draft `workbook.md` in "Challenge-First" format with Skynet narrative.
- [x] Task: Add "Cabling & Connectivity Table" to Hardware Specifications.
- [x] Task: Create `setup_lab.py` automation for initial-configs.
- [x] Task: Propose manual verification plan for Phase 2.

## Phase 3: Verification & QA
- [x] Task: Create "Verification Cheatsheet" (OSPFv3 neighbors, AF status).
- [x] Task: Validate `show ospfv3 neighbor` and `show ospfv3 ipv6 neighbor`.
- [x] Task: Verify IPv4 and IPv6 routing tables.
- [x] Task: Conductor Checkpoint Protocol: Finalize track and attach Git Notes.
