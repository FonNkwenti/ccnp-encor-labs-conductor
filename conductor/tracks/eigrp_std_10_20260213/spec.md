# Track Spec: Implement EIGRP Lab 10: Named Mode Advanced Features

## Goal

Create a new EIGRP lab focused on Named Mode-only features that require IOS 15.x+, specifically
targeting the c7200 routers (R1 and R6). This properly relocates SHA-256 authentication from
Lab 05 (where it was impossible on c3725/IOS 12.4) to a platform that supports it.

## Objectives

1. **SHA-256 HMAC Authentication** — Configure between R1 and R6 over Tunnel8 using Named Mode
   `af-interface` sub-commands.
2. **Wide Metrics** — Enable `metric version 64bit` and `metric rib-scale 128` on R1 and R6.
3. **AF-Interface Tuning** — Configure per-interface hello/hold timers and passive-interface
   on R1 using `af-interface` sub-mode.

## Challenges

1. "The Auth Asymmetry" — SHA-256 password mismatch on R6 Tunnel8
2. "The Metric Mismatch" — Wide metrics removed from R6, creating version asymmetry
3. "The Silent Interface" — Passive-interface accidentally set on Fa1/0 instead of Loopback0

## Platform Constraint

Only R1 (c7200) and R6 (c7200) support Named Mode + SHA-256. R2-R5, R7 (c3725, IOS 12.4)
remain on Classic Mode and are not modified by this lab's objectives.

## Deliverables

- Full lab directory under `labs/eigrp/lab-10-named-mode/`
- workbook.md, challenges.md, README.md
- topology.drawio, topology.png
- setup_lab.py, scripts/refresh_lab.py
- initial-configs/ (R1-R7, derived from Lab 09 solutions)
- solutions/ (R1, R6 with objectives applied; others unchanged)
- scripts/fault_inject_{1,2,3}.py
- Chapter-level updates to README.md and baseline.yaml

## Acceptance Criteria

- [ ] Lab 10 directory has the full template structure
- [ ] `hmac-sha-256` appears only in Lab 10 files across all EIGRP labs
- [ ] 3 objectives and 3 challenges with matching fault scripts
- [ ] Initial configs derive from Lab 09 solutions (no hmac-sha-256 cascade)
