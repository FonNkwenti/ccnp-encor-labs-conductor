# Track Plan: Implement EIGRP Lab 10: Named Mode Advanced Features

## Tasks

- [x] **Create directory structure** — `labs/eigrp/lab-10-named-mode/` with subdirectories
  `initial-configs/`, `solutions/`, `scripts/`.

- [x] **Create README.md** — Lab overview with objectives and topology link.

- [x] **Create workbook.md** — Full Challenge-First format workbook with Skynet Global narrative,
  3 objectives (SHA-256 auth, wide metrics, af-interface tuning), verification cheatsheet,
  troubleshooting scenario, solutions, and completion checklist.

- [x] **Create challenges.md** — 3 challenges: Auth Asymmetry, Metric Mismatch, Silent Interface.

- [x] **Create initial-configs/** — R1-R7 configs derived from Lab 09 solutions (post cascade fix).

- [x] **Create solutions/** — R1 and R6 with Lab 10 objectives applied; R2, R3, R5, R7 unchanged.

- [x] **Create fault scripts** — fault_inject_1.py (password mismatch on R6),
  fault_inject_2.py (remove wide metrics on R6), fault_inject_3.py (passive on wrong interface).

- [x] **Create refresh_lab.py** — Standard refresh script for all 6 routers.

- [x] **Create setup_lab.py** — Standard setup script for all 6 routers.

- [x] **Copy topology** — topology.drawio from Lab 09, update title. Copy topology.png placeholder.

- [x] **Update chapter README.md** — Add Lab 10 row to coverage matrix and lab topics table.

- [x] **Update baseline.yaml** — Add Lab 10 entry and tunnel overlay.

- [x] **Create track scaffolding** — metadata.json, index.md, spec.md, plan.md.

- [x] **Update tracks.md** — Add Lab 10 track entry.
