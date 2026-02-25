# Project Self-Improvement Log (Process Lessons)

This file captures patterns, rules, and lessons learned from user corrections regarding workflow and agent behavior. 

## Rules for Self-Correction
1. **Rule Creation:** Write rules that prevent the same mistake.
2. **Ruthless Iteration:** Refine rules until mistake rate drops.

---

## Lessons & Rules

### [2026-02-24] Workflow Strategy Adoption
- **Lesson:** Identified gap between standard Conductor and "Claude Code" style orchestration.
- **Rule:** Adopt "Plan Node Default" and "Subagent Strategy" for all non-trivial tasks.
- **Rule:** Maintain "Demand Elegance" as a check before implementation phases.
- **Rule:** When the user asks for "Gap Analysis," provide a structured report comparing CC and Conductor instead of jumping to implementation.
- **Rule:** After any user correction (e.g., "undo any changes made"), immediately restore the state and pivot to the user's preferred approach (e.g., "plan first").

### [2026-02-24] File Modification Safety
- **Rule:** Never modify files when explicitly asked to "review and plan" or "prepare a report."
- **Rule:** Use `git restore` and `rm -rf` to cleanly undo accidental file modifications if requested.
