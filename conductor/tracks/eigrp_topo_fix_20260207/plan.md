# Implementation Plan: Fix EIGRP Lab Topology Diagrams (04-09)

## Phase 1: Audit & Baseline Verification [checkpoint: 9d4515a]
- [x] Task: Compare `labs/eigrp/baseline.yaml` with each workbook to define the precise logical topology for each lab. 0ac6c18
- [x] Task: Create a checklist of required elements (routers, interfaces, subnets) for each diagram. 0ac6c18
- [x] Task: Conductor - User Manual Verification 'Phase 1: Audit' (Protocol in workflow.md) 0ac6c18

## Phase 2: Diagram Generation & Export [checkpoint: 5c059d6]
- [x] Task: Update/Re-generate `topology.drawio` for Lab 04. 311dca4
- [x] Task: Update/Re-generate `topology.drawio` for Lab 05. d965d60
- [x] Task: Update/Re-generate `topology.drawio` for Lab 06. be8aad5
- [x] Task: Update/Re-generate `topology.drawio` for Lab 07 (Add R4 OSPF). 60d3099
- [x] Task: Update/Re-generate `topology.drawio` for Lab 08 (Add R6 VPN). 252aa7f
- [x] Task: Update/Re-generate `topology.drawio` for Lab 09 (Full Dual-Stack). f4dedd4
- [x] Task: Export all `.drawio` files to `.png` (200% zoom, transparent). fb40ce1
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md) 0ac6c18

## Phase 3: Documentation Sync
- [~] Task: Update lab `README.md` files (if applicable) to link/display the new PNG diagrams.
- [ ] Task: Final quality check against `drawio` skill standards.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Finalization' (Protocol in workflow.md)
