# CCNP ENCOR (350-401) Lab Project

## Shared Context — Skills + Standards

@.agent/skills/memory/CLAUDE.md

## This Certification

- **Exam**: CCNP ENCOR (350-401)
- **Chapters**: EIGRP, OSPF, BGP, IP Services, Security, Automation, Integration
- **Audience**: Network engineers preparing for the CCNP core exam
- **Platform**: GNS3 on Apple Silicon (M1/M2/M3)

## Project Structure

@conductor/product.md
@conductor/workflow.md

## Lab Status

- **EIGRP**: Labs 01–10 complete (all with fault-injection scripts)
- **OSPF**: Labs 01–02 complete, Labs 03–08 planned
- **BGP, IP Services, Security, Automation, Integration**: Planned

See `conductor/tracks.md` for active chapter plans.

## How to Work on a Chapter

1. Check `conductor/tracks.md` for the active track
2. Read `labs/[chapter]/baseline.yaml` before generating anything
3. Use skills in this order:
   - `chapter-topics-creator` → for new chapters (creates baseline.yaml)
   - `chapter-builder` → to generate multiple labs at once
   - `lab-workbook-creator` → for a single lab
   - `fault-injector` → runs automatically after lab-workbook-creator

## Common Commands

```bash
# Update skills to latest from hub
git submodule update --remote .agent/skills
git add .agent/skills && git commit -m "chore: sync skills"

# Run a lab setup script
python3 labs/[chapter]/lab-NN-[name]/setup_lab.py

# Generate a topology diagram
python3 .agent/skills/drawio/scripts/generate_topo.py labs/[chapter]/lab-NN/baseline.yaml

# Run tests
pytest tests/ -v
```
