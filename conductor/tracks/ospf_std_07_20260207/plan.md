# Implementation Plan: Implement OSPF Lab 07

## Phase 1: Lab Design & Topology
- [x] Review `labs/ospf/baseline.yaml` (v1.1) for Lab 07 requirements.
- [x] Task: Confirm R1, R2, R3, R5 as `c7200` platforms.
- [x] Task: Design Skynet Global scenario: "Secure Backbone & External Partner Integration."
- [x] Task: Propose manual verification plan for Phase 1.

## Phase 2: Implementation & Artifact Generation
- [x] Task: Initialize directory `labs/ospf/lab-07-auth-redistribution/`.
- [x] Task: Generate `topology.drawio` with `generate_topo.py`.
- [x] Task: Create `initial-configs/` by chaining from OSPF Lab 06 solutions (adjusted for R5). 
- [x] Task: Implement `solutions/` including SHA auth and redistribution logic.
- [x] Task: Draft `workbook.md` in "Challenge-First" format with Skynet narrative.
- [x] Task: Add "Cabling & Connectivity Table" to Hardware Specifications.
- [x] Task: Create `setup_lab.py` automation for initial-configs.
- [x] Task: Propose manual verification plan for Phase 2.

## Phase 3: Verification & QA
- [x] Task: Create "Verification Cheatsheet" (SHA Auth, External Routes E1/E2).
- [x] Task: Validate `show ip ospf interface` for authentication status.
- [x] Task: Verify route redistribution and metric types (E1 vs E2).
- [x] Task: Conductor Checkpoint Protocol: Finalize track and attach Git Notes.
