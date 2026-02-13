# Track Spec: Remove SHA-256 from EIGRP Lab 05 + Cascade Fix

## Problem Statement

EIGRP Lab 05 Objective 2 asks students to configure HMAC-SHA-256 authentication between R2 and
R3. Both routers are c3725 running IOS 12.4, which does not support SHA-256 authentication.
SHA-256 for EIGRP requires Named Mode on IOS 15.x+.

The broken configuration (`ip authentication mode eigrp 100 hmac-sha-256 AdvancedSecurity256`)
was also carried forward into the initial-configs and solutions for Labs 06-09 on R2 and R3.

## Solution

1. **Lab 05**: Remove Objective 2 (SHA-256), renumber remaining objectives 3->2 and 4->3.
   Remove SHA-256 from workbook skills, diagram, narrative, cheatsheet, troubleshooting,
   solutions, and checklist. Replace Challenge 2 (SHA-256 fault) with the former Challenge 3
   (tagging fault), and create a new Challenge 3 (offset-list tag mismatch).

2. **Labs 06-09**: Remove the `ip authentication mode eigrp 100 hmac-sha-256` line from all
   R2.cfg and R3.cfg files (both initial-configs and solutions).

3. **Chapter-level**: Update `README.md` and `baseline.yaml` to remove SHA-256 references.

## Scope

- Lab 05: workbook.md, challenges.md, README.md, solutions/R2.cfg, solutions/R3.cfg,
  scripts/fault_inject_2.py, scripts/fault_inject_3.py
- Labs 06-09: R2.cfg and R3.cfg in initial-configs/ and solutions/ (14 files total)
- Chapter: README.md, baseline.yaml

## Acceptance Criteria

- [ ] No `hmac-sha-256` references exist in Labs 01-09
- [ ] Lab 05 has exactly 3 objectives and 3 challenges with matching fault scripts
- [ ] Labs 06-09 R2/R3 configs load cleanly without unsupported commands
