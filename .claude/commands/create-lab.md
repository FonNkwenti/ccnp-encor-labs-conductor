Create a complete lab package for: $ARGUMENTS

Follow `.agent/skills/lab-workbook-creator/SKILL.md` exactly for all workbook structure,
section formatting, artifact generation, and fault injection scripts.

## Additional project-specific steps

**Before generating anything:**
- Read `labs/[chapter]/baseline.yaml` for devices, IPs, console ports, and lab progression
- If Lab N > 1 and not a capstone: read Lab (N-1) `solutions/` — those become this lab's `initial-configs/`
- Read `reference-docs/350-401-exam-topics.md` to identify the exam domain bullets this lab maps to — use these for Section 1 (Concepts & Skills Covered)

**After the lab package is complete (skill Steps 1–7 done):**
1. Generate `challenges.md` — 4 standalone challenge exercises that extend the core lab tasks
2. If a conductor track exists for this lab: update `plan.md` to mark the lab complete per the workflow in `conductor/workflow.md`
