# Track Plan: Remove SHA-256 from EIGRP Lab 05 + Cascade Fix

## Tasks

- [x] **Lab 05 workbook.md** — Remove SHA-256 from skills, diagram, narrative, objectives,
  cheatsheet, troubleshooting, solutions, and checklist. Renumber objectives and sections.

- [x] **Lab 05 challenges.md** — Remove Challenge 2 (SHA-256). Rename old Challenge 3 to
  Challenge 2 (Tagging). Create new Challenge 3 (Phantom Penalty — tag 999 vs 555).

- [x] **Lab 05 solutions** — Remove `ip authentication mode eigrp 100 hmac-sha-256` from
  R2.cfg (Fa0/1) and R3.cfg (Fa0/0).

- [x] **Lab 05 fault scripts** — Replace fault_inject_2.py (now injects tagging removal on R3).
  Replace fault_inject_3.py (now injects wrong tag match 999 on R1 MATCH_TAG route-map).

- [x] **Lab 05 README.md** — Remove "HMAC-SHA-256" from objectives list.

- [x] **Cascade fix Labs 06-09** — Remove `ip authentication mode eigrp 100 hmac-sha-256
  AdvancedSecurity256` from R2.cfg and R3.cfg in initial-configs/ and solutions/ (14 files).

- [x] **Chapter README.md** — Change `SHA-256/MD5 auth` to `MD5 auth` in Lab 05 row.

- [x] **Chapter baseline.yaml** — Change `Implement MD5/SHA authentication` to
  `Implement MD5 authentication`.
