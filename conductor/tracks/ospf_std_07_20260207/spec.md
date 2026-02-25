# Track Specification: Implement OSPF Lab 07

## Goal
Create and implement OSPF Lab 07: Authentication & Redistribution, following the "Challenge-First" workbook guidelines and the "Skynet Global" scenario.

## Scope
- **Target Directory:** `labs/ospf/lab-07-auth-redistribution/`
- **Deliverables:**
    - `topology.drawio` (Topology diagram)
    - `workbook.md` (Challenge-First format)
    - `initial-configs/` (Base configurations)
    - `solutions/` (Full solution configurations)
- **Hardware Standard:**
    - R1, R2, R3, R5 MUST use `c7200` (IOS 15.x) as per updated `baseline.yaml`.
- **Content:**
    - MD5/SHA authentication (Area-based and interface-based).
    - Redistribution of external routes (EIGRP/Connected).
    - E1 vs E2 metric types and metric manipulation.
    - Skynet Global scenario narrative.

## Success Criteria
- Lab files exist in the target directory.
- Workbook matches `product-guidelines.md`.
- All `show` commands are accurate for IOS c7200/c3725.
