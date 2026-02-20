Systematically troubleshoot a Cisco network fault using structured methodology. Context: $ARGUMENTS

## Process — Structured Troubleshooting (4 Phases)

### Phase I: Problem Definition
- Transform the user's description into a precise technical problem statement.
- Clarify: exact symptoms, affected devices/subnets, timeline, recent changes.
- Document: symptoms, scope, timeline, baseline behavior.

### Phase II: Methodology Selection
Use this decision tree:
1. Physical problem (cable, power, hardware)? → **Bottom-Up**
2. Working device to compare against? → **Compare Configurations**
3. Clearly an application-layer problem? → **Top-Down**
4. Multi-hop routing/path issue? → **Follow the Traffic Path**
5. Otherwise → **Divide and Conquer** (default)

State which methodology was selected and why.

### Phase III: Diagnostic Execution
1. **Gather information** using appropriate `show` commands
2. **Establish baseline** — compare current state vs. normal operation
3. **Eliminate valid causes** — rule out functioning components systematically
4. **Hypothesize and test** — develop testable hypotheses, verify each:
   - Hypothesis → Test command → Expected result → Actual result → Conclusion
5. **Implement fix** or workaround
6. **Verify resolution** — test the specific symptoms from Phase I

### Phase IV: Resolution Report
Generate a report containing:
1. Incident summary
2. Methodology applied and rationale
3. Chronological diagnostic log with timestamps
4. Root cause analysis
5. Resolution actions (exact config commands)
6. Testing and verification results
7. Lessons learned and recommendations

## Important
- **Do NOT guess or randomly try commands** — stay methodical
- **Document everything** as you go
- Use `show` commands liberally (non-invasive)
- Use `debug` commands cautiously (can impact performance)
- If the user asks you NOT to fix it, only explain the root cause without revealing the solution
- Reference the lab's workbook, initial-configs, and solutions as needed for context
