# Track Specification: Implement OSPF Lab 06

## Goal
Create and implement OSPF Lab 06: NSSA & Route Control, following the "Challenge-First" workbook guidelines and the "Skynet Global" scenario.

## Scope
- **Target Directory:** `labs/ospf/lab-06-nssa-control/`
- **Deliverables:**
    - `topology.drawio` (Topology diagram)
    - `workbook.md` (Challenge-First format)
    - `initial-configs/` (Base configurations)
    - `solutions/` (Full solution configurations)
- **Hardware Standard:**
    - R1, R2, R3, R4 MUST use `c7200` (IOS 15.x) as per updated `baseline.yaml`.
    - `c3725` reserved only for simple stubs if applicable.
- **Content:**
    - Not-So-Stubby Areas (NSSA).
    - Type 7 to Type 5 translation.
    - Inter-area summarization (ABR LSA Type 3 filtering/summarization).
    - Skynet Global scenario narrative.

## Success Criteria
- Lab files exist in the target directory.
- Workbook matches `product-guidelines.md`.
- All `show` commands are accurate for IOS c7200/c3725.
