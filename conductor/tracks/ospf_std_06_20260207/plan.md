# Implementation Plan: Implement OSPF Lab 06

## Phase 1: Lab Design & Topology
- [x] Review updated `labs/ospf/baseline.yaml` (v1.1) for Lab 06 requirements.
- [x] Task: Confirm R1, R2, R3, R4 as `c7200` platforms for advanced NSSA feature support.
- [x] Task: Design Skynet Global scenario narrative: "Area 4 NSSA Migration for Secure Research Node."
- [x] Task: Propose manual verification plan for Phase 1.

## Phase 2: Implementation & Artifact Generation
- [x] Task: Initialize directory `labs/ospf/lab-06-nssa-control/`.
- [x] Task: Generate `topology.drawio` with `generate_topo.py` using white lines and Cisco icons.
- [x] Task: Create `initial-configs/` by chaining from OSPF Lab 05 solutions.
- [x] Task: Implement `solutions/` including NSSA, Type 7/5 translation, and area summarization.
- [x] Task: Draft `workbook.md` in "Challenge-First" format with Skynet narrative.
- [x] Task: Add "Cabling & Connectivity Table" to Hardware Specifications.
- [x] Task: Create `setup_lab.py` automation for initial-configs.
- [x] Task: Propose manual verification plan for Phase 2.

## Phase 3: Verification & QA
- [x] Task: Create "Verification Cheatsheet" (LSA Type 7 verification, Summaries).
- [x] Task: Validate `show ip ospf database nssa-external` commands for Type 7 LSAs.
- [x] Task: Verify LSA translation on the ABR (R1).
- [x] Task: Conductor Checkpoint Protocol: Finalize track and attach Git Notes.
