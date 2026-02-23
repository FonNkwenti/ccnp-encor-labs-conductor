# Changelog

All notable changes to the CCNP ENCOR (350-401) Lab Conductor project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **LESSONS_LEARNED.md** — Comprehensive reference guide capturing patterns, design decisions, and anti-patterns from CCNP ENCOR lab development. Covers:
  - DeepSeek Standard lab artifact structure
  - Lab chaining rule (only add, never remove)
  - baseline.yaml as source of truth
  - Skills architecture and progressive disclosure
  - GNS3 Apple Silicon constraints
  - Topology diagram standards and bypass-link patterns
  - Four-phase troubleshooting methodology
  - Workflow recommendations for new chapters
  - Common bugs and quick fixes

### Changed

- **All 7 Claude Code Skills Upgraded** — Aligned with official Claude Code skills guide standards:
  - Added `metadata` field (author, version, category, tags) to all skills
  - Rewrote `description` fields to include specific trigger phrases users would say
  - Applied progressive disclosure: extracted verbose content to `references/` folders
  - Reduced SKILL.md file sizes:
    - `cisco-troubleshooting-1`: 824 lines → ~430 lines
    - `drawio`: 318 lines → ~200 lines

- **Skills Refactored to Use Progressive Disclosure:**
  - `cisco-troubleshooting-1/references/diagnostic-commands.md` — full CLI command reference
  - `cisco-troubleshooting-1/references/incident-report-template.md` — 8-section incident report template
  - `drawio/references/drawio-xml-snippets.md` — all ready-to-paste XML snippets

### Fixed

- **Critical Skill Name Mismatch:** Fixed `cisco-troubleshooting` → `cisco-troubleshooting-1` to match folder name exactly (required by Claude Code skills spec)

---

## [2.0.0] — 2026-02-23

### Added

- **EIGRP/OSPF Complete Content Suite:**
  - EIGRP: Labs 01–10 with all fault-injection scripts
  - OSPF: Labs 01–02 complete, Labs 03–08 planned

- **Claude Code Memory & Skill Scaffolding:**
  - CLAUDE.md configuration with project-specific instructions
  - Scaffolded skill command shortcuts (create-lab, troubleshoot, chapter-build, etc.)

- **Draw.io Export Utilities:**
  - `generate_topo.py` — automated topology diagram generation from baseline.yaml
  - Batch PNG export utility for Draw.io diagrams (200% DPI for high-resolution output)

### Changed

- **Lab Workbook Creator Skill:**
  - Now generates setup_lab.py automation scripts using Netmiko telnet
  - Enforces collapsible `<details>` blocks for all solution configurations
  - Added verification cheatsheet requirement to every lab

- **Fault Injector Skill:**
  - Generates three fault injection scenarios per lab (inject_scenario_01.py, inject_scenario_02.py, inject_scenario_03.py)
  - Includes apply_solution.py for configuration restoration
  - Auto-generates README.md with usage instructions

- **Lab 04 (OSPF) Implementation:**
  - Multi-Area OSPF with ABR functionality
  - Standardized fault injection scripts
  - Complete collapsible solutions with all objectives covered

### Fixed

- **Troubleshooting Scenarios Section:**
  - Removed verbose inline troubleshooting scenarios from workbook template
  - Now generated separately by fault-injector skill for better modularity

### Deprecated

- Manual configuration loading (replaced by setup_lab.py automation)

---

## [1.5.0] — 2026-02-15

### Added

- **EIGRP Lab 06–10:** Complete implementation with traffic engineering and VPN overlay scenarios
- **Advanced EIGRP Features:**
  - Route authentication (MD5, HMAC-SHA-256)
  - GRE and IPsec tunnel overlays
  - Dual-stack IPv4/IPv6 EIGRP Named Mode
  - Traffic engineering with distribute-lists and route-maps

- **Baseline YAML Schema:**
  - Core topology definitions
  - Optional device/link support for progressive labs
  - Tunnel overlay definitions
  - Lab progression tracking

### Changed

- **Lab 05–06 Workbooks:**
  - Enhanced with real-world authentication scenarios
  - Added verification commands for tunnel status and adjacency stability
  - Expanded challenge objectives

---

## [1.4.0] — 2026-02-10

### Added

- **EIGRP Lab 03–04:** Path selection and advanced metric tuning
- **Challenge-First Format:** All lab workbooks restructured with:
  - Clear objectives and acceptance criteria
  - Step-by-step configuration instructions
  - Verification cheatsheet for quick validation
  - Collapsible solutions (spoiler-protected)

### Changed

- **Lab 01 Workbook Standardization:**
  - Refactored to Challenge-First format
  - Added Verification Cheatsheet section
  - Enhanced with Skynet Global scenario branding
  - Fixed section numbering for consistency

- **Lab 02 Workbook Updates:**
  - Updated to match Lab 01 standards
  - Enhanced path selection scenarios

### Fixed

- **Git Repository Recovery:** Reinitialize after accidental deletion
- **Topology Diagram Consistency:** Standardized cable labeling and device positioning

---

## [1.3.0] — 2026-02-05

### Added

- **EIGRP Lab 05:** Authentication & Advanced Configurations
  - MD5 authentication between neighbors
  - Passive interface configurations
  - Route filtering with distribute-lists
  - Complete fault injection scenarios

### Changed

- **Lab Design Process:**
  - Implemented baseline.yaml as configuration source of truth
  - Established lab chaining pattern (Lab N initial-configs = Lab N-1 solutions)
  - Formalized topology versioning

---

## [1.2.0] — 2026-01-28

### Added

- **EIGRP Lab 03:** Path Selection & Metrics
- **EIGRP Lab 04:** Advanced Features & Tuning
- **Topology Diagrams:** All labs now include Draw.io diagrams with:
  - Cisco mxgraph icons (blue fill, white connections)
  - IP address last-octet labels on all links
  - Smart label placement (empty-side rule)
  - Legend boxes with protocol information

### Changed

- **Lab Workbook Structure:**
  - Standardized across all labs
  - Added Hardware & Environment Specifications section
  - Enhanced Console Access Table with telnet commands

---

## [1.1.0] — 2026-01-20

### Added

- **EIGRP Lab 02:** Path Selection
  - Feasible Successor concepts
  - Metric calculations
  - Variance configuration
  - Challenge scenarios with verification

### Changed

- **Lab 01 Enhancement:**
  - Added detailed verification commands
  - Expanded concepts section
  - Improved topology documentation

---

## [1.0.0] — 2026-01-15

### Added

- **Project Initialization:**
  - CCNP ENCOR (350-401) lab series for Apple Silicon (GNS3 Dynamips)
  - Project structure with chapters and lab progression
  - CLAUDE.md with project guidelines

- **EIGRP Chapter (Labs 01–10):**
  - **Lab 01:** EIGRP Fundamentals & Basic Adjacency
    - Three-router topology (R1, R2, R3)
    - Basic EIGRP configuration and adjacency formation
    - Verification commands
    - Initial fault injection scenarios

- **DeepSeek Standard Lab Format:**
  - workbook.md with concepts, objectives, verification, solutions
  - initial-configs/ and solutions/ directory structure
  - topology.drawio network diagrams
  - setup_lab.py Netmiko automation scripts
  - Fault injection scripts (inject_scenario_01.py, apply_solution.py)

- **Core Skills:**
  - `lab-workbook-creator` — generates complete lab artifacts
  - `fault-injector` — creates troubleshooting scenarios
  - `chapter-builder` — orchestrates multi-lab chapter generation
  - `chapter-topics-creator` — designs lab blueprint and baseline.yaml
  - `drawio` — topology diagram standards and workflows
  - `cisco-troubleshooting-1` — structured troubleshooting methodology
  - `gns3` — Apple Silicon platform reference (c7200, c3725, Dynamips)

- **Documentation:**
  - README.md with project overview
  - conductor/product.md — product definition and goals
  - conductor/workflow.md — project workflow and task lifecycle
  - Reference docs for GNS3 setup and Cisco terminology

- **GitHub Actions & CI/CD Preparation:**
  - Git configuration for test-driven development
  - Plan-based task tracking system

### Notes

- Project uses GNS3 Emulation on Apple Silicon with Dynamips only
- All routers use Cisco c7200 or c3725 IOS images
- Console access standardized to ports 5001–5007 for scriptability
- All labs follow "Lab Chaining" pattern: each lab's solutions become the next lab's initial configs
- Exam-aligned terminology enforced (Feasible Successor, Administrative Distance, Dead Interval, etc.)

---

## Version Legend

- **[Unreleased]** — Work in progress, not yet released
- **[2.0.0]** — Major milestone: complete EIGRP content, fault injection automation, and Azure/production readiness
- **[1.x.x]** — Progressive lab implementation (EIGRP Labs 01–10)
- **[1.0.0]** — Initial release: EIGRP Lab 01 + core infrastructure

---

## How to Contribute

When adding new content or fixes:

1. **Lab Content:** Reference `LESSONS_LEARNED.md` for patterns and standards
2. **Skills Changes:** Ensure compliance with `reference-docs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf`
3. **Commit Messages:** Use conventional commits (feat:, fix:, refactor:, docs:, chore:)
4. **Versioning:** Increment version numbers per Semantic Versioning (MAJOR.MINOR.PATCH)

---

## Release History Summary

| Version | Date | Focus | Labs |
|---------|------|-------|------|
| 2.0.0 | 2026-02-23 | Skills compliance, automation | EIGRP 1-10, OSPF 1-2 |
| 1.5.0 | 2026-02-15 | Advanced EIGRP features | EIGRP 6-10 |
| 1.4.0 | 2026-02-10 | Challenge-first format | EIGRP 1-4 |
| 1.3.0 | 2026-02-05 | Authentication & chaining | EIGRP 5 |
| 1.2.0 | 2026-01-28 | Topology diagrams | EIGRP 3-4 |
| 1.1.0 | 2026-01-20 | Path selection | EIGRP 2 |
| 1.0.0 | 2026-01-15 | Initial release | EIGRP 1 |

---

**For detailed project decisions and lessons learned, see [LESSONS_LEARNED.md](LESSONS_LEARNED.md)**

**Last Updated:** February 23, 2026
